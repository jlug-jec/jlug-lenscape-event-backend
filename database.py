"""
Firestore-backed data layer for Lenscape.

Replaces MongoDB/PyMongo. Exposes collection objects that mimic the small
subset of the PyMongo API the app uses (find_one, find, insert_one,
update_one, delete_one, count_documents, insert_many, create_index) so the
rest of the codebase needs almost no changes.

Simple queries are pushed down to Firestore so reads scale with matching
documents instead of total collection size. Only unsupported compatibility
filters fall back to Python-side filtering.
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
try:
    from google.cloud.firestore_v1 import FieldFilter
except ImportError:  # pragma: no cover - older google-cloud-firestore fallback
    FieldFilter = None
from dotenv import load_dotenv

load_dotenv()

# ── Initialize Firebase Admin ────────────────────────────────────────────────
# Two ways to provide credentials:
#  1. FIREBASE_SERVICE_ACCOUNT_JSON  → full JSON string (best for cloud hosts)
#  2. FIREBASE_SERVICE_ACCOUNT       → path to the JSON file (best for local dev)
SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
SERVICE_ACCOUNT_PATH = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT",
    "lenscape-25955-firebase-adminsdk-fbsvc-2e02180c2c.json",
)

if not firebase_admin._apps:
    if SERVICE_ACCOUNT_JSON:
        cred = credentials.Certificate(json.loads(SERVICE_ACCOUNT_JSON))
    else:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

_db = firestore.client()

# Expose firebase auth for verifying Google ID tokens
fb_auth = firebase_auth


# ── Result objects (mimic PyMongo return shapes) ─────────────────────────────
class _InsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class _UpdateResult:
    def __init__(self, matched_count):
        self.matched_count = matched_count


class _DeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


class _Cursor:
    """Iterable wrapper supporting .sort() chaining like a PyMongo cursor."""
    def __init__(self, docs):
        self._docs = docs

    def sort(self, field, direction=1):
        self._docs.sort(
            key=lambda d: (
                FirestoreCollection._get_field(d, field) is None,
                FirestoreCollection._get_field(d, field),
            ),
            reverse=(direction == -1),
        )
        return self

    def __iter__(self):
        return iter(self._docs)

    def __len__(self):
        return len(self._docs)


# ── Collection wrapper ───────────────────────────────────────────────────────
class FirestoreCollection:
    _SUPPORTED_OPERATORS = {
        "$ne": "!=",
        "$gt": ">",
        "$gte": ">=",
        "$lt": "<",
        "$lte": "<=",
        "$in": "in",
        "$array_contains": "array_contains",
        "$array_contains_any": "array_contains_any",
    }

    def __init__(self, name):
        self.name = name
        self.col = _db.collection(name)

    # -- helpers --
    def _doc_to_dict(self, snap):
        data = snap.to_dict() or {}
        data["_id"] = snap.id
        return data

    def _all(self):
        return [self._doc_to_dict(s) for s in self.col.stream()]

    def _where(self, query_ref, field, op, value):
        if FieldFilter is not None:
            return query_ref.where(filter=FieldFilter(field, op, value))
        return query_ref.where(field, op, value)

    def _build_query(self, query):
        query_ref = self.col
        post_filters = {}

        for key, value in query.items():
            if key == "_id":
                post_filters[key] = value
                continue

            # Firestore cannot query into arrays of maps like comments.userId.
            if key == "comments.userId":
                post_filters[key] = value
                continue

            if isinstance(value, dict):
                if len(value) != 1:
                    post_filters[key] = value
                    continue

                op_key, op_value = next(iter(value.items()))
                firestore_op = self._SUPPORTED_OPERATORS.get(op_key)
                if firestore_op is None:
                    post_filters[key] = value
                    continue

                query_ref = self._where(query_ref, key, firestore_op, op_value)
            else:
                query_ref = self._where(query_ref, key, "==", value)

        return query_ref, post_filters

    def _query_docs(self, query=None, limit=None):
        query = query or {}

        if "_id" in query and isinstance(query["_id"], str):
            snap = self.col.document(query["_id"]).get()
            if not snap.exists:
                return []
            doc = self._doc_to_dict(snap)
            rest = {k: v for k, v in query.items() if k != "_id"}
            return [doc] if self._match(doc, rest) else []

        query_ref, post_filters = self._build_query(query)
        server_limit = limit if not post_filters else None
        if server_limit is not None:
            query_ref = query_ref.limit(server_limit)

        docs = [self._doc_to_dict(s) for s in query_ref.stream()]
        if post_filters:
            docs = [d for d in docs if self._match(d, post_filters)]
            if limit is not None:
                docs = docs[:limit]
        return docs

    @staticmethod
    def _aggregation_count_value(result):
        first = result[0]
        if isinstance(first, (list, tuple)):
            first = first[0]
        return int(first.value)

    def _count_server_query(self, query_ref):
        try:
            aggregation = query_ref.count()
        except AttributeError:
            return sum(1 for _ in query_ref.stream())
        try:
            return self._aggregation_count_value(aggregation.get())
        except (AttributeError, TypeError, IndexError, ValueError):
            return sum(1 for _ in query_ref.stream())

    @staticmethod
    def _get_field(doc, key):
        cur = doc
        for part in key.split("."):
            if isinstance(cur, dict):
                cur = cur.get(part)
            else:
                return None
        return cur

    @staticmethod
    def _set_field(doc, key, value):
        parts = key.split(".")
        cur = doc
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
        cur[parts[-1]] = value

    def _match(self, doc, query):
        for k, v in query.items():
            # operator dicts e.g. {"$ne": "other"}
            if isinstance(v, dict):
                if "$ne" in v:
                    if self._get_field(doc, k) == v["$ne"]:
                        return False
                    continue
            # special case: array of comment objects
            if k == "comments.userId":
                comments = doc.get("comments", []) or []
                if not any(c.get("userId") == v for c in comments):
                    return False
                continue
            if self._get_field(doc, k) != v:
                return False
        return True

    # -- read --
    def find_one(self, query=None):
        query = query or {}
        docs = self._query_docs(query, limit=1)
        return docs[0] if docs else None

    def find(self, query=None):
        query = query or {}
        return _Cursor(self._query_docs(query))

    def count_documents(self, query=None):
        query = query or {}
        if "_id" in query or "comments.userId" in query:
            return len(self._query_docs(query))

        query_ref, post_filters = self._build_query(query)
        if post_filters:
            return len(self._query_docs(query))
        return self._count_server_query(query_ref)

    # -- write --
    def insert_one(self, doc):
        doc = dict(doc)
        _id = doc.pop("_id", None)
        if _id is not None:
            self.col.document(str(_id)).set(doc)
            return _InsertResult(str(_id))
        ref = self.col.document()
        ref.set(doc)
        return _InsertResult(ref.id)

    def insert_many(self, docs):
        for d in docs:
            self.insert_one(d)

    def _apply_update(self, doc, update):
        doc = dict(doc)
        for op, fields in update.items():
            if op == "$set":
                for k, v in fields.items():
                    self._set_field(doc, k, v)
            elif op == "$inc":
                for k, v in fields.items():
                    self._set_field(doc, k, (self._get_field(doc, k) or 0) + v)
            elif op == "$push":
                for k, v in fields.items():
                    arr = list(self._get_field(doc, k) or [])
                    arr.append(v)
                    self._set_field(doc, k, arr)
        return doc

    def update_one(self, query, update, upsert=False):
        target = self.find_one(query)
        if not target:
            if upsert:
                base = {k: v for k, v in query.items() if not isinstance(v, dict)}
                base = self._apply_update(base, update)
                self.insert_one(base)
                return _UpdateResult(0)
            return _UpdateResult(0)
        doc_id = target["_id"]
        new_doc = self._apply_update(target, update)
        new_doc.pop("_id", None)
        self.col.document(doc_id).set(new_doc)
        return _UpdateResult(1)

    def delete_one(self, query):
        target = self.find_one(query)
        if not target:
            return _DeleteResult(0)
        self.col.document(target["_id"]).delete()
        return _DeleteResult(1)

    # -- compatibility no-op --
    def create_index(self, *args, **kwargs):
        return None


# ── Collections ──────────────────────────────────────────────────────────────
users_col = FirestoreCollection("users")
artworks_col = FirestoreCollection("artworks")
categories_col = FirestoreCollection("categories")
banned_users_col = FirestoreCollection("banned_users")
admins_col = FirestoreCollection("admins")


def init_db():
    """Seed default categories if the collection is empty."""
    try:
        if categories_col.count_documents({}) == 0:
            default_categories = [
                {"name": "photography"},
                {"name": "filmmaking"},
                {"name": "animation"},
                {"name": "digital-art"},
                {"name": "illustration"},
                {"name": "motion-graphics"},
                {"name": "other"},
            ]
            categories_col.insert_many(default_categories)
            print("Successfully initialized default art categories in Firestore.")
        else:
            print("Firestore connected. Categories already initialized.")
    except Exception as e:
        print(f"Error initializing database: {e}")
