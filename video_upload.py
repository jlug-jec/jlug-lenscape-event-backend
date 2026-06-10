"""
Video upload utilities for Cloudinary
Handles video and cover image uploads for cinematography and motion graphics
"""
import cloudinary
import cloudinary.uploader
from werkzeug.utils import secure_filename
import os
import tempfile

def allowed_video_file(filename):
    """Check if file is an allowed video format"""
    ALLOWED_EXTENSIONS = {'mp4', 'mkv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image_file(filename):
    """Check if file is an allowed image format"""
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_video_to_cloudinary(video_file, artwork_id):
    """
    Upload video to Cloudinary
    
    Args:
        video_file: FileStorage object from Flask request
        artwork_id: Unique identifier for the artwork
        
    Returns:
        dict: Contains video_url, duration, format, size
    """
    try:
        # Save video temporarily
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, secure_filename(video_file.filename))
        video_file.save(temp_path)
        
        # Upload to Cloudinary with video-specific settings
        result = cloudinary.uploader.upload(
            temp_path,
            resource_type="video",
            public_id=f"lenscape/videos/{artwork_id}",
            folder="lenscape/videos",
            overwrite=True,
            # Video transformation settings
            eager=[
                # Generate a web-optimized version (1080p)
                {
                    "width": 1920,
                    "height": 1080,
                    "crop": "limit",
                    "quality": "auto",
                    "fetch_format": "auto"
                }
            ],
            eager_async=False,  # Wait for transformations
            # Metadata
            context=f"artwork_id={artwork_id}",
        )
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return {
            'success': True,
            'video_url': result['secure_url'],
            'duration': result.get('duration'),  # Duration in seconds
            'format': result.get('format'),
            'size': result.get('bytes'),
            'public_id': result.get('public_id'),
            'resource_type': 'video'
        }
        
    except Exception as e:
        # Clean up temp file on error
        try:
            if 'temp_path' in locals():
                os.remove(temp_path)
        except:
            pass
        
        return {
            'success': False,
            'error': str(e)
        }

def upload_cover_image_to_cloudinary(cover_file, artwork_id):
    """
    Upload cover/thumbnail image to Cloudinary
    
    Args:
        cover_file: FileStorage object from Flask request
        artwork_id: Unique identifier for the artwork
        
    Returns:
        dict: Contains image_url, thumbnail_url, width, height
    """
    try:
        # Save image temporarily
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, secure_filename(cover_file.filename))
        cover_file.save(temp_path)
        
        # Upload to Cloudinary with image-specific settings
        result = cloudinary.uploader.upload(
            temp_path,
            resource_type="image",
            public_id=f"lenscape/covers/{artwork_id}",
            folder="lenscape/covers",
            overwrite=True,
            # Image transformation settings
            eager=[
                # Thumbnail version (400x300)
                {
                    "width": 400,
                    "height": 300,
                    "crop": "fill",
                    "gravity": "auto",
                    "quality": "auto",
                    "fetch_format": "auto"
                },
                # Medium version (800x600)
                {
                    "width": 800,
                    "height": 600,
                    "crop": "limit",
                    "quality": "auto",
                    "fetch_format": "auto"
                }
            ],
            eager_async=False,
            # Metadata
            context=f"artwork_id={artwork_id}",
        )
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        # Get thumbnail URL from eager transformations
        thumbnail_url = None
        if result.get('eager') and len(result['eager']) > 0:
            thumbnail_url = result['eager'][0]['secure_url']
        
        return {
            'success': True,
            'image_url': result['secure_url'],
            'thumbnail_url': thumbnail_url or result['secure_url'],
            'width': result.get('width'),
            'height': result.get('height'),
            'public_id': result.get('public_id'),
            'resource_type': 'image'
        }
        
    except Exception as e:
        # Clean up temp file on error
        try:
            if 'temp_path' in locals():
                os.remove(temp_path)
        except:
            pass
        
        return {
            'success': False,
            'error': str(e)
        }

def delete_video_from_cloudinary(public_id):
    """Delete video from Cloudinary"""
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type="video")
        return result.get('result') == 'ok'
    except:
        return False

def delete_image_from_cloudinary(public_id):
    """Delete image from Cloudinary"""
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
        return result.get('result') == 'ok'
    except:
        return False
