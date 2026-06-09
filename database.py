import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/lenscape")

# Initialize MongoDB client with robust connection pooling and cert verification fixes
client = MongoClient(
    MONGO_URI,
    maxPoolSize=200,
    minPoolSize=10,
    maxIdleTimeMS=30000,
    waitQueueTimeoutMS=2500,
    tlsCAFile=certifi.where()
)
db = client.get_database()

# Collections
users_col = db["users"]
artworks_col = db["artworks"]
categories_col = db["categories"]
banned_users_col = db["banned_users"]
admins_col = db["admins"]          # Admin credentials store

def init_db():
    """
    Initialize indexes and default configurations in MongoDB.
    """
    try:
        users_col.create_index("email", unique=True)
        artworks_col.create_index("createdAt")
        artworks_col.create_index("category")
        artworks_col.create_index("status")
        artworks_col.create_index("artist.id")
        admins_col.create_index("email", unique=True)

        # Populate initial categories if empty
        if categories_col.count_documents({}) == 0:
            default_categories = [
                {"name": "photography"},
                {"name": "filmmaking"},
                {"name": "animation"},
                {"name": "digital-art"},
                {"name": "illustration"},
                {"name": "motion-graphics"},
                {"name": "other"}
            ]
            categories_col.insert_many(default_categories)
            print("Successfully initialized default art categories in MongoDB.")
    except Exception as e:
        print(f"Error initializing database: {e}")
