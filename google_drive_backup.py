import os
import io
import tempfile
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# Scopes for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Path to the service account key file
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_DRIVE_CREDENTIALS', 'path/to/your/credentials.json')

# The ID of the Google Drive folder where you want to backup artworks
TARGET_FOLDER_ID = os.getenv('GOOGLE_DRIVE_BACKUP_FOLDER_ID', 'your_folder_id_here')

def get_drive_service():
    """Authenticates and returns the Google Drive API service instance."""
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error authenticating with Google Drive: {e}")
        return None

def get_or_create_folder(service, folder_name: str, parent_id: str) -> str:
    """
    Checks if a subfolder exists inside the parent folder. 
    If it exists, returns its ID. If not, creates it and returns the new ID.
    """
    try:
        # Search for the folder in the specified parent
        query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])

        if items:
            return items[0].get('id')
        else:
            # Create the folder if it doesn't exist
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            folder = service.files().create(body=file_metadata, fields='id').execute()
            print(f"Created subfolder: '{folder_name}' with ID: {folder.get('id')}")
            return folder.get('id')
    except Exception as e:
        print(f"Error finding/creating folder {folder_name}: {e}")
        return None

def backup_artwork_to_drive(file_url: str, full_name: str, name_of_artwork: str, file_type: str, mime_type: str, is_cover_photo: bool = False) -> str:
    """
    Uploads an artwork to specific Google Drive subfolders ('photos' or 'videos') based on file_type.
    
    Args:
        file_url: The URL to download the file from.
        full_name: The user's full name.
        name_of_artwork: The artwork's name.
        file_type: 'photo' or 'video'.
        mime_type: The mime type of the file (e.g., 'image/jpeg', 'video/mp4').
        is_cover_photo: If True and file_type is 'video', it formats the name as a cover photo.
        
    Returns:
        The ID of the uploaded file on Google Drive, or None if failed.
    """
    service = get_drive_service()
    if not service:
        return None
        
    temp_path = None
    try:
        # Download the file to a temporary location
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp_file.write(chunk)
            temp_path = tmp_file.name

        # Clean inputs to prevent issues with slashes or weird characters in names
        safe_full_name = full_name.replace("/", "_").replace("\\", "_")
        safe_artwork_name = name_of_artwork.replace("/", "_").replace("\\", "_")

        # 1. Format the file name
        base_name = f"{safe_full_name}_{safe_artwork_name}"
        if is_cover_photo:
            file_name = f"{base_name}(cover_photo)"
        else:
            file_name = base_name

        # Determine extension based on mime type
        ext = ""
        if mime_type == 'image/jpeg' or mime_type == 'image/jpg':
            ext = ".jpg"
        elif mime_type == 'image/png':
            ext = ".png"
        elif mime_type == 'video/mp4':
            ext = ".mp4"
        elif mime_type == 'video/x-matroska' or mime_type == 'video/mkv':
            ext = ".mkv"
            
        final_file_name = f"{file_name}{ext}"

        # 2. Determine target subfolder ('photos' or 'videos')
        target_subfolder_name = 'photos' if file_type == 'photo' else 'videos'
        
        # 3. Get or create the subfolder ID
        subfolder_id = get_or_create_folder(service, target_subfolder_name, TARGET_FOLDER_ID)
        
        if not subfolder_id:
            print(f"Could not resolve subfolder ID for {target_subfolder_name}.")
            return None

        # 4. Upload the file to the targeted subfolder
        file_metadata = {
            'name': final_file_name,
            'parents': [subfolder_id]
        }
        
        media = MediaFileUpload(temp_path, mimetype=mime_type, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file_id = file.get('id')
        print(f"Successfully backed up '{final_file_name}' to Google Drive folder '{target_subfolder_name}' with ID: {file_id}")
        return file_id
        
    except Exception as e:
        print(f"An error occurred while uploading to Google Drive: {e}")
        return None
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"Failed to clean up temp file {temp_path}: {e}")
