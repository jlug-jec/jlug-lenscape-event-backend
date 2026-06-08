import os
import time
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Import database collections and setup
from database import init_db, users_col, artworks_col, categories_col, banned_users_col
from auth import require_auth, admin_only

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for frontend integration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Rate Limiter setup using local in-memory storage to prevent crash spikes
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per minute", "10000 per day"],
    storage_uri="memory://"
)

# Configure Cloudinary if credentials exist
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True
    )
    print("Cloudinary configured successfully.")
else:
    print("Warning: Cloudinary credentials missing. File uploads will fallback to text URLs.")

# Initialize MongoDB index configurations
init_db()

# --- Helper Functions ---

def serialize_doc(doc):
    """
    Helper to convert MongoDB objects and dates to JSON-friendly format.
    """
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    
    serialized = dict(doc)
    if "_id" in serialized:
        serialized["id"] = str(serialized["_id"])
        del serialized["_id"]
        
    for k, v in serialized.items():
        if isinstance(v, datetime):
            serialized[k] = v.isoformat() + "Z"
        elif isinstance(v, dict):
            serialized[k] = serialize_doc(v)
        elif isinstance(v, list):
            serialized[k] = [serialize_doc(item) if isinstance(item, dict) else item for item in v]
            
    return serialized

def check_and_unlock_achievements(user_id):
    """
    Scans database to unlock creator badges dynamically based on user interactions.
    """
    user = users_col.find_one({"_id": user_id})
    if not user:
        return []
        
    unlocked_ids = [ach["id"] for ach in user.get("achievements", [])]
    new_achievements = list(user.get("achievements", []))
    
    # 1. Creative Pioneer: First submission
    user_submissions_count = artworks_col.count_documents({"artist.id": user_id})
    if user_submissions_count > 0 and "ach1" not in unlocked_ids:
        new_achievements.append({
            "id": "ach1",
            "title": "Creative Pioneer",
            "description": "Submitted your first artwork to the gallery",
            "icon": "🚀",
            "unlockedAt": datetime.utcnow()
        })
        
    # 2. Art Critic: Left a comment
    # Count if user has commented on any approved artworks
    comment_count = artworks_col.count_documents({"comments.userId": user_id})
    if comment_count > 0 and "ach2" not in unlocked_ids:
        new_achievements.append({
            "id": "ach2",
            "title": "Art Critic",
            "description": "Left a thoughtful comment on another student's artwork",
            "icon": "💬",
            "unlockedAt": datetime.utcnow()
        })
        
    # 3. Grand Patron: Voted in at least 3 distinct categories
    voted_cats = user.get("votedCategories", [])
    if len(voted_cats) >= 3 and "ach3" not in unlocked_ids:
        new_achievements.append({
            "id": "ach3",
            "title": "Grand Patron",
            "description": "Voted in at least 3 distinct categories",
            "icon": "👑",
            "unlockedAt": datetime.utcnow()
        })
        
    # 4. Polymath: Voted in all available categories
    all_cats = [cat["name"] for cat in categories_col.find({"name": {"$ne": "other"}})]
    voted_main_cats = [c for c in voted_cats if c != "other"]
    if len(all_cats) > 0 and len(voted_main_cats) >= len(all_cats) and "ach4" not in unlocked_ids:
        new_achievements.append({
            "id": "ach4",
            "title": "Polymath",
            "description": "Voted in all available artwork categories",
            "icon": "🔮",
            "unlockedAt": datetime.utcnow()
        })
        
    if len(new_achievements) != len(user.get("achievements", [])):
        users_col.update_one({"_id": user_id}, {"$set": {"achievements": new_achievements}})

# --- API Endpoints ---

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "lenscape-api"}), 200

# 1. Categories Endpoints
@app.route("/api/categories", methods=["GET"])
def get_categories():
    categories = list(categories_col.find())
    return jsonify([cat["name"] for cat in categories]), 200

@app.route("/api/categories", methods=["POST"])
@admin_only
def add_category():
    data = request.get_json() or {}
    name = data.get("category", "").strip().lower().replace(" ", "-")
    if not name:
        return jsonify({"error": "Category name is required"}), 400
        
    if categories_col.find_one({"name": name}):
        return jsonify({"error": "Category already exists"}), 400
        
    categories_col.insert_one({"name": name})
    return jsonify({"success": True, "category": name}), 201

@app.route("/api/categories/<name>", methods=["DELETE"])
@admin_only
def delete_category(name):
    result = categories_col.delete_one({"name": name.strip().lower()})
    if result.deleted_count == 0:
        return jsonify({"error": "Category not found"}), 404
    return jsonify({"success": True}), 200

# 2. Users / Profile Endpoints
@app.route("/api/users/profile", methods=["GET"])
@require_auth
def get_profile():
    user = users_col.find_one({"_id": g.user_id})
    if not user:
        return jsonify({"registered": False, "message": "Profile not created yet"}), 404
        
    serialized_user = serialize_doc(user)
    # Append user's submissions
    submissions = list(artworks_col.find({"artist.id": g.user_id}))
    serialized_user["submissions"] = serialize_doc(submissions)
    
    return jsonify(serialized_user), 200

@app.route("/api/users/profile", methods=["POST"])
@require_auth
def update_profile():
    # Supports JSON or Multipart form (for avatar upload)
    data = {}
    avatar_url = None
    
    if request.is_json:
        data = request.get_json() or {}
        avatar_url = data.get("avatar")
    else:
        # Form-data
        data = request.form.to_dict()
        avatar_file = request.files.get("avatarFile")
        if avatar_file and CLOUDINARY_CLOUD_NAME:
            try:
                upload_result = cloudinary.uploader.upload(avatar_file, folder="lenscape/avatars")
                avatar_url = upload_result.get("secure_url")
            except Exception as e:
                return jsonify({"error": f"Failed to upload avatar: {str(e)}"}), 500
        else:
            avatar_url = data.get("avatar")

    name = data.get("name", "").strip()
    college = data.get("college", "").strip()
    branch = data.get("branch", "").strip()
    year = data.get("year", "1st Year").strip()
    bio = data.get("bio", "").strip()
    
    if not name or not college or not branch:
        return jsonify({"error": "Name, college, and branch are required fields"}), 400

    existing_user = users_col.find_one({"_id": g.user_id})
    
    profile_data = {
        "name": name,
        "email": g.user_email if g.user_email else data.get("email", "").strip().lower(),
        "college": college,
        "branch": branch,
        "year": year,
        "bio": bio,
        "avatar": avatar_url or (existing_user.get("avatar") if existing_user else None)
    }

    if not existing_user:
        # Create profile
        profile_data.update({
            "_id": g.user_id,
            "votedCategories": [],
            "commentedArtworks": [],
            "achievements": [],
            "joinedDate": datetime.utcnow(),
            "isBanned": False,
            "isAdmin": g.is_admin
        })
        users_col.insert_one(profile_data)
    else:
        # Update existing profile
        users_col.update_one({"_id": g.user_id}, {"$set": profile_data})
        
    # Refresh user
    user = users_col.find_one({"_id": g.user_id})
    return jsonify(serialize_doc(user)), 200

# 3. Artwork Endpoints
@app.route("/api/artworks", methods=["GET"])
def get_artworks():
    # Only return approved artworks for public feed
    artworks = list(artworks_col.find({"status": "approved"}).sort("createdAt", -1))
    return jsonify(serialize_doc(artworks)), 200

@app.route("/api/artworks/pending", methods=["GET"])
@admin_only
def get_pending_artworks():
    artworks = list(artworks_col.find({"status": "pending"}).sort("createdAt", -1))
    return jsonify(serialize_doc(artworks)), 200

# 3. Cloudinary Signed Upload Endpoint
@app.route("/api/cloudinary/signature", methods=["GET"])
@require_auth
@limiter.limit("10 per minute")
def get_cloudinary_signature():
    if not CLOUDINARY_API_SECRET:
        return jsonify({"error": "Cloudinary credentials not configured on backend"}), 500
        
    timestamp = int(time.time())
    params = {
        "timestamp": timestamp,
        "folder": "lenscape/gallery"
    }
    try:
        signature = cloudinary.utils.api_sign_request(
            params,
            CLOUDINARY_API_SECRET
        )
        return jsonify({
            "signature": signature,
            "timestamp": timestamp,
            "folder": "lenscape/gallery",
            "cloud_name": CLOUDINARY_CLOUD_NAME,
            "api_key": CLOUDINARY_API_KEY
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed generating signature: {str(e)}"}), 500

# 4. Artwork Endpoints
@app.route("/api/artworks", methods=["POST"])
@require_auth
@limiter.limit("3 per minute")
def submit_artwork():
    # Check if user is registered in db
    user = users_col.find_one({"_id": g.user_id})
    if not user:
        return jsonify({"error": "Complete your profile signature first before submitting art"}), 400
        
    data = request.get_json() or {}
    image_url = data.get("imageUrl")
    video_url = data.get("videoUrl")
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    category = data.get("category", "").strip().lower()

    if not title or not description or not category or not image_url:
        return jsonify({"error": "Title, description, category, and imageUrl are required"}), 400

    # Validate category exists
    if not categories_col.find_one({"name": category}):
        return jsonify({"error": f"Category '{category}' does not exist"}), 400

    artwork_doc = {
        "title": title,
        "description": description,
        "category": category,
        "imageUrl": image_url,
        "thumbnailUrl": image_url,
        "videoUrl": video_url or None,
        "artist": {
            "id": user["_id"],
            "name": user["name"],
            "email": user["email"],
            "college": user["college"],
            "branch": user["branch"],
            "year": user["year"],
            "avatar": user["avatar"],
            "bio": user["bio"],
            "joinedDate": user["joinedDate"]
        },
        "votes": 0,
        "voters": [],
        "comments": [],
        "createdAt": datetime.utcnow(),
        "status": "approved" if g.is_admin else "pending"  # Admin uploads auto-approved
    }

    result = artworks_col.insert_one(artwork_doc)
    artwork_doc["id"] = str(result.inserted_id)
    
    # Check achievements for submitter
    check_and_unlock_achievements(g.user_id)
    
    return jsonify(serialize_doc(artwork_doc)), 201

@app.route("/api/artworks/<artwork_id>/vote", methods=["POST"])
@require_auth
@limiter.limit("10 per minute")
def vote_artwork(artwork_id):
    from bson import ObjectId
    try:
        art_oid = ObjectId(artwork_id)
    except:
        return jsonify({"error": "Invalid artwork ID format"}), 400

    artwork = artworks_col.find_one({"_id": art_oid, "status": "approved"})
    if not artwork:
        return jsonify({"error": "Approved artwork not found"}), 404

    # Enforce voting rules: 1 vote per category per user
    user = users_col.find_one({"_id": g.user_id})
    if not user:
        return jsonify({"error": "Please complete user signature first"}), 400

    category = artwork["category"]
    if category in user.get("votedCategories", []):
        return jsonify({"error": f"You have already voted in the '{category}' category. 1 vote allowed per domain."}), 400

    # Register Vote
    artworks_col.update_one(
        {"_id": art_oid},
        {
            "$inc": {"votes": 1},
            "$push": {"voters": g.user_id}
        }
    )
    users_col.update_one(
        {"_id": g.user_id},
        {"$push": {"votedCategories": category}}
    )

    # Check and trigger achievements
    check_and_unlock_achievements(g.user_id)

    return jsonify({"success": True, "category": category}), 200

@app.route("/api/artworks/<artwork_id>/comment", methods=["POST"])
@require_auth
@limiter.limit("5 per minute")
def comment_artwork(artwork_id):
    from bson import ObjectId
    try:
        art_oid = ObjectId(artwork_id)
    except:
        return jsonify({"error": "Invalid artwork ID format"}), 400

    artwork = artworks_col.find_one({"_id": art_oid, "status": "approved"})
    if not artwork:
        return jsonify({"error": "Approved artwork not found"}), 404

    user = users_col.find_one({"_id": g.user_id})
    if not user:
        return jsonify({"error": "Please complete user signature first"}), 400

    # Rule: 1 comment per artwork per user
    already_commented = any(c["userId"] == g.user_id for c in artwork.get("comments", []))
    if already_commented:
        return jsonify({"error": "You have already commented on this artwork. Only 1 comment is allowed."}), 400

    data = request.get_json() or {}
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"error": "Comment content cannot be empty"}), 400

    comment_doc = {
        "id": "comment_" + str(int(datetime.utcnow().timestamp() * 1000)),
        "artworkId": artwork_id,
        "userId": g.user_id,
        "userName": user["name"],
        "content": content,
        "createdAt": datetime.utcnow()
    }

    # Add comment to artwork
    artworks_col.update_one(
        {"_id": art_oid},
        {"$push": {"comments": comment_doc}}
    )

    # Check achievements
    check_and_unlock_achievements(g.user_id)

    return jsonify(serialize_doc(comment_doc)), 201

# 4. Admin Curation Actions
@app.route("/api/artworks/<artwork_id>/approve", methods=["POST"])
@admin_only
def approve_artwork(artwork_id):
    from bson import ObjectId
    try:
        art_oid = ObjectId(artwork_id)
    except:
        return jsonify({"error": "Invalid artwork ID"}), 400

    result = artworks_col.update_one({"_id": art_oid}, {"$set": {"status": "approved"}})
    if result.matched_count == 0:
        return jsonify({"error": "Artwork not found"}), 404

    # Trigger achievement checklist updates for the artist of the approved artwork
    artwork = artworks_col.find_one({"_id": art_oid})
    if artwork and "artist" in artwork:
        check_and_unlock_achievements(artwork["artist"]["id"])

    return jsonify({"success": True}), 200

@app.route("/api/artworks/<artwork_id>/reject", methods=["POST"])
@admin_only
def reject_artwork(artwork_id):
    from bson import ObjectId
    try:
        art_oid = ObjectId(artwork_id)
    except:
        return jsonify({"error": "Invalid artwork ID"}), 400

    result = artworks_col.update_one({"_id": art_oid}, {"$set": {"status": "rejected"}})
    if result.matched_count == 0:
        return jsonify({"error": "Artwork not found"}), 404
    return jsonify({"success": True}), 200

# 5. User Ban Management
@app.route("/api/admin/users", methods=["GET"])
@admin_only
def get_all_users():
    users = list(users_col.find())
    return jsonify(serialize_doc(users)), 200

@app.route("/api/admin/users/<user_id>/ban", methods=["POST"])
@admin_only
def ban_user(user_id):
    if user_id == "user_admin":
        return jsonify({"error": "Cannot ban administrator account"}), 400

    # Add to banned_users list
    banned_users_col.update_one(
        {"userId": user_id},
        {"$set": {"userId": user_id, "bannedAt": datetime.utcnow()}},
        upsert=True
    )
    # Set status flag
    users_col.update_one({"_id": user_id}, {"$set": {"isBanned": True}})
    
    return jsonify({"success": True}), 200

@app.route("/api/admin/users/<user_id>/unban", methods=["POST"])
@admin_only
def unban_user(user_id):
    banned_users_col.delete_one({"userId": user_id})
    users_col.update_one({"_id": user_id}, {"$set": {"isBanned": False}})
    return jsonify({"success": True}), 200

# 6. Global Error Handlers
@app.errorhandler(Exception)
def handle_exception(e):
    """
    Global catch-all error handler returning structured JSON error details.
    """
    app.logger.error(f"Unhandled server error: {str(e)}")
    return jsonify({
        "error": "An unexpected server error occurred",
        "details": str(e)
    }), 500

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=(os.getenv("FLASK_ENV") == "development"))
