import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

print("Testing with default settings:")
try:
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')
    print("Success with default!")
except Exception as e:
    print(f"Failed default: {e}")

print("\nTesting with tlsAllowInvalidCertificates=True:")
try:
    client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
    client.admin.command('ping')
    print("Success with tlsAllowInvalidCertificates!")
except Exception as e:
    print(f"Failed tlsAllowInvalidCertificates: {e}")
