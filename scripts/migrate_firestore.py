#!/usr/bin/env python3
"""
Copy Lenscape Firestore collections from one Firebase project to another.

The script is intentionally dry-run by default. Pass --execute to write data.
It preserves document IDs and copies only the top-level collections used by the
backend unless --collections is provided.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Iterable, List, Optional

import firebase_admin
from firebase_admin import credentials, firestore


DEFAULT_COLLECTIONS = ("users", "artworks", "categories", "banned_users", "admins")
DEFAULT_BATCH_SIZE = 400


def _env(name: str) -> Optional[str]:
    value = os.getenv(name)
    return value if value else None


def _credential_from_source(label: str, path: Optional[str], json_value: Optional[str]):
    if path and json_value:
        raise ValueError(f"{label}: provide either a credential path or JSON, not both")

    if json_value:
        try:
            parsed = json.loads(json_value)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{label}: credential JSON is invalid: {exc}") from exc
        return credentials.Certificate(parsed)

    if path:
        return credentials.Certificate(path)

    raise ValueError(f"{label}: missing service account credential")


def _init_app(name: str, credential):
    existing = next((app for app in firebase_admin._apps.values() if app.name == name), None)
    if existing:
        return existing
    return firebase_admin.initialize_app(credential, name=name)


def _parse_collection_list(raw: Optional[str]) -> List[str]:
    if not raw:
        return list(DEFAULT_COLLECTIONS)
    collections = [part.strip() for part in raw.split(",") if part.strip()]
    if not collections:
        raise ValueError("At least one collection name is required")
    return collections


def _commit_batch(batch, pending_writes: int, execute: bool) -> int:
    if execute and pending_writes:
        batch.commit()
    return 0


def _copy_collection(
    source_db,
    dest_db,
    collection_name: str,
    batch_size: int,
    execute: bool,
    merge: bool,
) -> int:
    source_ref = source_db.collection(collection_name)
    dest_ref = dest_db.collection(collection_name)
    batch = dest_db.batch()
    pending_writes = 0
    copied = 0

    for snap in source_ref.stream():
        data = snap.to_dict() or {}
        copied += 1

        if execute:
            batch.set(dest_ref.document(snap.id), data, merge=merge)
            pending_writes += 1

            if pending_writes >= batch_size:
                pending_writes = _commit_batch(batch, pending_writes, execute)
                batch = dest_db.batch()

    _commit_batch(batch, pending_writes, execute)
    return copied


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Migrate Lenscape Firestore top-level collections between Firebase projects."
    )
    parser.add_argument(
        "--source-credentials",
        default=_env("SOURCE_FIREBASE_SERVICE_ACCOUNT"),
        help="Path to the source Firebase service account JSON file.",
    )
    parser.add_argument(
        "--source-credentials-json",
        default=_env("SOURCE_FIREBASE_SERVICE_ACCOUNT_JSON"),
        help="Source service account JSON string. Prefer env vars over shell history.",
    )
    parser.add_argument(
        "--dest-credentials",
        default=_env("DEST_FIREBASE_SERVICE_ACCOUNT"),
        help="Path to the destination Firebase service account JSON file.",
    )
    parser.add_argument(
        "--dest-credentials-json",
        default=_env("DEST_FIREBASE_SERVICE_ACCOUNT_JSON"),
        help="Destination service account JSON string. Prefer env vars over shell history.",
    )
    parser.add_argument(
        "--collections",
        default=_env("FIRESTORE_MIGRATION_COLLECTIONS"),
        help=(
            "Comma-separated collection names to migrate. "
            f"Default: {','.join(DEFAULT_COLLECTIONS)}"
        ),
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=int(_env("FIRESTORE_MIGRATION_BATCH_SIZE") or DEFAULT_BATCH_SIZE),
        help=f"Firestore write batch size. Default: {DEFAULT_BATCH_SIZE}. Max: 500.",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge into existing destination docs instead of replacing each migrated doc.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write destination data. Without this flag the script only reads/counts.",
    )
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.batch_size < 1 or args.batch_size > 500:
        parser.error("--batch-size must be between 1 and 500")

    try:
        collections = _parse_collection_list(args.collections)
        source_cred = _credential_from_source(
            "source", args.source_credentials, args.source_credentials_json
        )
        dest_cred = _credential_from_source(
            "destination", args.dest_credentials, args.dest_credentials_json
        )
    except ValueError as exc:
        parser.error(str(exc))

    source_app = _init_app("lenscape-migration-source", source_cred)
    dest_app = _init_app("lenscape-migration-destination", dest_cred)
    source_db = firestore.client(app=source_app)
    dest_db = firestore.client(app=dest_app)

    mode = "EXECUTE" if args.execute else "DRY RUN"
    print(f"Firestore migration mode: {mode}")
    print(f"Collections: {', '.join(collections)}")
    if args.execute:
        print("Destination writes are enabled.")
    else:
        print("No destination writes will be made. Re-run with --execute to migrate.")

    total = 0
    for collection_name in collections:
        copied = _copy_collection(
            source_db=source_db,
            dest_db=dest_db,
            collection_name=collection_name,
            batch_size=args.batch_size,
            execute=args.execute,
            merge=args.merge,
        )
        total += copied
        action = "migrated" if args.execute else "would migrate"
        print(f"{collection_name}: {action} {copied} document(s)")

    print(f"Total: {total} document(s)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Migration failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
