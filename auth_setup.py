import os
from dotenv import load_dotenv

load_dotenv()

from google_drive_backup import get_drive_service

def main():
    print("Starting Google Drive OAuth Flow...")
    service = get_drive_service()
    if service:
        print("\n✅ Successfully authenticated! token.json has been created.")
        print("Your Google Drive backup system is now ready.")
    else:
        print("\n❌ Authentication failed.")

if __name__ == '__main__':
    main()
