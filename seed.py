import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

import certifi
# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/lenscape")
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.get_database()

users_col = db["users"]
artworks_col = db["artworks"]
categories_col = db["categories"]
banned_users_col = db["banned_users"]

def seed_db():
    print("Starting database seeding...")

    # Clear existing data
    users_col.delete_many({})
    artworks_col.delete_many({})
    categories_col.delete_many({})
    banned_users_col.delete_many({})
    print("Cleared existing collections.")

    # 1. Insert Categories
    categories = [
        {"name": "photography"},
        {"name": "filmmaking"},
        {"name": "animation"},
        {"name": "digital-art"},
        {"name": "illustration"},
        {"name": "motion-graphics"},
        {"name": "other"}
    ]
    categories_col.insert_many(categories)
    print("Seeded artwork categories.")

    # 2. Insert Users
    users = [
        {
            "_id": "user_admin",
            "name": "Jlug Admin",
            "email": "admin@jlug.club",
            "college": "Jawaharlal Nehru Engineering College",
            "branch": "Computer Science",
            "year": "4th Year",
            "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=admin",
            "bio": "Jlug Club Lead & Lenscape Curator.",
            "votedCategories": [],
            "commentedArtworks": [],
            "achievements": [],
            "joinedDate": datetime.utcnow() - timedelta(days=150),
            "isBanned": False,
            "isAdmin": True
        },
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
            "commentedArtworks": ["artwork_2"],
            "achievements": [
                {
                    "id": "ach1",
                    "title": "Creative Pioneer",
                    "description": "Submitted your first artwork to the gallery",
                    "icon": "🚀",
                    "unlockedAt": datetime.utcnow() - timedelta(days=28)
                }
            ],
            "joinedDate": datetime.utcnow() - timedelta(days=30),
            "isBanned": False,
            "isAdmin": False
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
            "commentedArtworks": ["artwork_1"],
            "achievements": [
                {
                    "id": "ach1",
                    "title": "Creative Pioneer",
                    "description": "Submitted your first artwork to the gallery",
                    "icon": "🚀",
                    "unlockedAt": datetime.utcnow() - timedelta(days=24)
                },
                {
                    "id": "ach2",
                    "title": "Art Critic",
                    "description": "Left a thoughtful comment on another student's artwork",
                    "icon": "💬",
                    "unlockedAt": datetime.utcnow() - timedelta(days=23)
                }
            ],
            "joinedDate": datetime.utcnow() - timedelta(days=25),
            "isBanned": False,
            "isAdmin": False
        }
    ]

    for user in users:
        users_col.insert_one(user)
    print("Seeded user profiles.")

    # 3. Seed Artworks (linked to seeded user information)
    artworks = [
        {
            "title": "Digital Horizon",
            "description": "A 3D simulation of a neon synthwave grid extending into infinity. Created using custom WebGL shaders and procedural noise. The piece aims to represent the endless landscapes of digital memories.",
            "category": "digital-art",
            "imageUrl": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1200",
            "thumbnailUrl": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600",
            "videoUrl": None,
            "artist": {
                "id": "user_alex",
                "name": "Alex Chen",
                "email": "alex@college.edu",
                "college": "JNEC",
                "branch": "Information Technology",
                "year": "3rd Year",
                "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=alex",
                "bio": "Pixel pusher and retro-futuristic explorer.",
                "joinedDate": users[1]["joinedDate"]
            },
            "votes": 42,
            "voters": ["user_sarah"],
            "comments": [
                {
                    "id": "comment_1",
                    "artworkId": "artwork_1",
                    "userId": "user_sarah",
                    "userName": "Sarah Kim",
                    "content": "The lighting on the neon grid is absolutely spectacular! Love the retro Y2K grid vibe.",
                    "createdAt": datetime.utcnow() - timedelta(days=7)
                }
            ],
            "createdAt": datetime.utcnow() - timedelta(days=20),
            "status": "approved"
        },
        {
            "title": "Neon Dreams",
            "description": "Street-level long exposure photography of Tokyo in the rain, focusing on neon light reflections on wet pavement. Highlights the moody, cyberpunk energy of urban architectures.",
            "category": "photography",
            "imageUrl": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1200",
            "thumbnailUrl": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600",
            "videoUrl": None,
            "artist": {
                "id": "user_sarah",
                "name": "Sarah Kim",
                "email": "sarah@college.edu",
                "college": "Delhi Technological University",
                "branch": "Electronics",
                "year": "2nd Year",
                "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=sarah",
                "bio": "Cinematographer and street photographer.",
                "joinedDate": users[2]["joinedDate"]
            },
            "votes": 38,
            "voters": ["user_alex"],
            "comments": [
                {
                    "id": "comment_2",
                    "artworkId": "artwork_2",
                    "userId": "user_alex",
                    "userName": "Alex Chen",
                    "content": "Wow, the reflection details in the puddles are crisp! What camera settings did you use?",
                    "createdAt": datetime.utcnow() - timedelta(days=6)
                }
            ],
            "createdAt": datetime.utcnow() - timedelta(days=18),
            "status": "approved"
        },
        {
            "title": "Cyberpunk Corridor",
            "description": "A cinematic high-pace short film showing a student navigating a futuristic college campus. Captures elements of retro-futurism and digital dystopia.",
            "category": "filmmaking",
            "imageUrl": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1200",
            "thumbnailUrl": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=600",
            "videoUrl": "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "artist": {
                "id": "user_sarah",
                "name": "Sarah Kim",
                "email": "sarah@college.edu",
                "college": "Delhi Technological University",
                "branch": "Electronics",
                "year": "2nd Year",
                "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=sarah",
                "bio": "Cinematographer and street photographer.",
                "joinedDate": users[2]["joinedDate"]
            },
            "votes": 56,
            "voters": [],
            "comments": [],
            "createdAt": datetime.utcnow() - timedelta(days=15),
            "status": "approved"
        },
        {
            "title": "Chrome Spheres",
            "description": "An interactive 3D HTML5 animation featuring bouncing chrome-plated spheres that distort and morph on collision. Illustrates physical energy transfer in liquid mercury.",
            "category": "animation",
            "imageUrl": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200",
            "thumbnailUrl": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600",
            "videoUrl": None,
            "artist": {
                "id": "user_alex",
                "name": "Alex Chen",
                "email": "alex@college.edu",
                "college": "JNEC",
                "branch": "Information Technology",
                "year": "3rd Year",
                "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=alex",
                "bio": "Pixel pusher and retro-futuristic explorer.",
                "joinedDate": users[1]["joinedDate"]
            },
            "votes": 72,
            "voters": [],
            "comments": [],
            "createdAt": datetime.utcnow() - timedelta(days=10),
            "status": "approved"
        },
        {
            "title": "Surrealist Flora",
            "description": "A digital vector illustration reimagining botanical forms as robotic cybernetic organisms. Drawn by hand using graphic tablet and metallic brush configurations.",
            "category": "illustration",
            "imageUrl": "https://images.unsplash.com/photo-1549490349-8643362247b5?w=1200",
            "thumbnailUrl": "https://images.unsplash.com/photo-1549490349-8643362247b5?w=600",
            "videoUrl": None,
            "artist": {
                "id": "user_alex",
                "name": "Alex Chen",
                "email": "alex@college.edu",
                "college": "JNEC",
                "branch": "Information Technology",
                "year": "3rd Year",
                "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=alex",
                "bio": "Pixel pusher and retro-futuristic explorer.",
                "joinedDate": users[1]["joinedDate"]
            },
            "votes": 21,
            "voters": [],
            "comments": [],
            "createdAt": datetime.utcnow() - timedelta(days=8),
            "status": "approved"
        },
        {
            "title": "Liquid Metal Kinetic",
            "description": "A dynamic looping GIF showing fluid chrome metal structures flowing around a wireframe core. Created in Cinema 4D.",
            "category": "motion-graphics",
            "imageUrl": "https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=1200",
            "thumbnailUrl": "https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=600",
            "videoUrl": None,
            "artist": {
                "id": "user_sarah",
                "name": "Sarah Kim",
                "email": "sarah@college.edu",
                "college": "Delhi Technological University",
                "branch": "Electronics",
                "year": "2nd Year",
                "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=sarah",
                "bio": "Cinematographer and street photographer.",
                "joinedDate": users[2]["joinedDate"]
            },
            "votes": 29,
            "voters": [],
            "comments": [],
            "createdAt": datetime.utcnow() - timedelta(days=5),
            "status": "approved"
        },
        {
            "title": "Unreleased Cyber Dreams",
            "description": "A concept art of a futuristic museum exhibition. This submission is currently pending review by the Jlug administrators.",
            "category": "digital-art",
            "imageUrl": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=1200",
            "thumbnailUrl": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=600",
            "videoUrl": None,
            "artist": {
                "id": "user_alex",
                "name": "Alex Chen",
                "email": "alex@college.edu",
                "college": "JNEC",
                "branch": "Information Technology",
                "year": "3rd Year",
                "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=alex",
                "bio": "Pixel pusher and retro-futuristic explorer.",
                "joinedDate": users[1]["joinedDate"]
            },
            "votes": 0,
            "voters": [],
            "comments": [],
            "createdAt": datetime.utcnow() - timedelta(days=2),
            "status": "pending"
        }
    ]

    artworks_col.insert_many(artworks)
    print("Seeded sample artworks.")
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_db()
