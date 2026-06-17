import os
import io
import tempfile
import requests
import logging
import os.path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)

# Scopes for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Path to the client secret file
CLIENT_SECRET_FILE = os.getenv('GOOGLE_DRIVE_CREDENTIALS', 'client_secret.json')
TOKEN_FILE = 'token.json'

# The ID of the Google Drive folder where you want to backup artworks
TARGET_FOLDER_ID = os.getenv('GOOGLE_DRIVE_BACKUP_FOLDER_ID', 'your_folder_id_here')

import json

def get_drive_service():
    """Authenticates and returns the Google Drive API service instance."""
    creds = None
    
    # 1. Try to load from Environment Variable (Production)
    token_json_str = os.getenv('GOOGLE_OAUTH_TOKEN_JSON')
    if token_json_str:
        try:
            token_info = json.loads(token_json_str)
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        except Exception as e:
            logger.error(f"Failed to parse GOOGLE_OAUTH_TOKEN_JSON: {e}")

    # 2. Try to load from Local File (Development)
    elif os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    try:
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # If we have client secret in env var, use it
                client_secret_str = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET_JSON')
                if client_secret_str:
                    client_config = json.loads(client_secret_str)
                    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Only save to file if we are running locally (not using env vars)
            if not token_json_str:
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())

        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Error authenticating with Google Drive: {e}")
        return None

def get_or_create_folder(service, folder_name: str, parent_id: str) -> str:
    """
    Checks if a subfolder exists inside the parent folder. 
    If it exists, returns its ID. If not, creates it and returns the new ID.
    """
    try:
        # Search for the folder in the specified parent
        query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(
            q=query, 
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora="allDrives"
        ).execute()
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
            folder = service.files().create(body=file_metadata, fields='id', supportsAllDrives=True).execute()
            logger.info(f"Created subfolder: '{folder_name}' with ID: {folder.get('id')}")
            return folder.get('id')
    except Exception as e:
        logger.error(f"Error finding/creating folder {folder_name}: {e}")
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
            logger.error(f"Could not resolve subfolder ID for {target_subfolder_name}.")
            return None

        # 4. Upload the file to the targeted subfolder
        file_metadata = {
            'name': final_file_name,
            'parents': [subfolder_id]
        }
        
        media = MediaFileUpload(temp_path, mimetype=mime_type, resumable=True)
        try:
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()
            
            file_id = file.get('id')
            logger.info(f"Successfully backed up '{final_file_name}' to Google Drive folder '{target_subfolder_name}' with ID: {file_id}")
            return file_id
        finally:
            # Force close the file handle so Windows allows deletion
            if hasattr(media, '_fd') and media._fd:
                media._fd.close()
        
    except Exception as e:
        logger.error(f"An error occurred while uploading to Google Drive: {e}")
        return None
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {temp_path}: {e}")
