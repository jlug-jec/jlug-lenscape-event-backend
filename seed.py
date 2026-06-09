"""
Seed Firestore with sample categories, users, and artworks.
Run:  python seed.py
"""

from datetime import datetime, timedelta
from database import (
    users_col, artworks_col, categories_col, banned_users_col, _db
)


def _clear(collection_name):
    """Delete every document in a collection."""
    for snap in _db.collection(collection_name).stream():
        snap.reference.delete()


def seed_db():
    print("Starting Firestore seeding...")

    # Clear existing data
    for name in ["users", "artworks", "categories", "banned_users"]:
        _clear(name)
    print("Cleared existing collections.")

    # 1. Categories
    categories = [
        {"name": "photography"},
        {"name": "filmmaking"},
        {"name": "animation"},
        {"name": "digital-art"},
        {"name": "illustration"},
        {"name": "motion-graphics"},
        {"name": "other"},
    ]
    categories_col.insert_many(categories)
    print("Seeded artwork categories.")

    # 2. Users (use fixed doc ids)
    users = [
        {
            "_id": "user_alex",
            "name": "Alex Chen",
            "email": "alex@college.edu",
            "college": "JNEC",
            "branch": "Information Technology",
            "year": "3rd Year",
            "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=alex",
            "bio": "Pixel pusher and retro-futuristic explorer.",
            "votedCategories": ["photography"],
            "commentedArtworks": [],
            "achievements": [
                {
                    "id": "ach1",
                    "title": "Creative Pioneer",
                    "description": "Submitted your first artwork to the gallery",
                    "icon": "🚀",
                    "unlockedAt": datetime.utcnow() - timedelta(days=28),
                }
            ],
            "joinedDate": datetime.utcnow() - timedelta(days=30),
            "isBanned": False,
            "isAdmin": False,
        },
        {
            "_id": "user_sarah",
            "name": "Sarah Kim",
            "email": "sarah@college.edu",
            "college": "Delhi Technological University",
            "branch": "Electronics",
            "year": "2nd Year",
            "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=sarah",
            "bio": "Cinematographer and street photographer.",
            "votedCategories": ["digital-art"],
            "commentedArtworks": [],
            "achievements": [],
            "joinedDate": datetime.utcnow() - timedelta(days=25),
            "isBanned": False,
            "isAdmin": False,
        },
    ]
    for user in users:
        users_col.insert_one(user)
    print("Seeded user profiles.")

    # 3. Artworks
    def artist(uid, users_list):
        u = next(x for x in users_list if x["_id"] == uid)
        return {
            "id": u["_id"], "name": u["name"], "email": u["email"],
            "college": u["college"], "branch": u["branch"], "year": u["year"],
            "avatar": u["avatar"], "bio": u["bio"], "joinedDate": u["joinedDate"],
        }

    artworks = [
        {
            "title": "Digital Horizon",
            "description": "A 3D simulation of a neon synthwave grid extending into infinity.",
            "category": "digital-art",
            "imageUrl": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1200",
            "thumbnailUrl": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600",
            "videoUrl": None,
            "artist": artist("user_alex", users),
            "votes": 42, "voters": ["user_sarah"], "comments": [],
            "createdAt": datetime.utcnow() - timedelta(days=20),
            "status": "approved",
        },
        {
            "title": "Neon Dreams",
            "description": "Street-level long exposure photography of Tokyo in the rain.",
            "category": "photography",
            "imageUrl": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1200",
            "thumbnailUrl": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600",
            "videoUrl": None,
            "artist": artist("user_sarah", users),
            "votes": 38, "voters": ["user_alex"], "comments": [],
            "createdAt": datetime.utcnow() - timedelta(days=18),
            "status": "approved",
        },
        {
            "title": "Unreleased Cyber Dreams",
            "description": "Concept art pending review by the Jlug administrators.",
            "category": "digital-art",
            "imageUrl": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=1200",
            "thumbnailUrl": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=600",
            "videoUrl": None,
            "artist": artist("user_alex", users),
            "votes": 0, "voters": [], "comments": [],
            "createdAt": datetime.utcnow() - timedelta(days=2),
            "status": "pending",
        },
    ]
    artworks_col.insert_many(artworks)
    print("Seeded sample artworks.")
    print("Firestore seeding completed successfully!")


if __name__ == "__main__":
    seed_db()
