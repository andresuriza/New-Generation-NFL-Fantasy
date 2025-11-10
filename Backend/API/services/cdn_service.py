"""
CDN Service for handling image uploads and storage
"""
import os
import uuid
import shutil
from typing import Optional, Tuple
from pathlib import Path
from PIL import Image
import requests
from io import BytesIO

class CDNService:
    """Service for managing image uploads and storage"""
    
    # Base directories for image storage
    BASE_DIR = "/app/imgs"
    PICS_DIR = os.path.join(BASE_DIR, "pics")
    THUMBNAILS_DIR = os.path.join(BASE_DIR, "thumbnails")
    
    # Thumbnail settings
    THUMBNAIL_SIZE = (150, 150)
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    
    def __init__(self):
        """Initialize CDN service and ensure directories exist"""
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create image directories if they don't exist"""
        os.makedirs(self.PICS_DIR, exist_ok=True)
        os.makedirs(self.THUMBNAILS_DIR, exist_ok=True)
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        return Path(filename).suffix.lower()
    
    def _is_valid_extension(self, filename: str) -> bool:
        """Check if file has a valid image extension"""
        ext = self._get_file_extension(filename)
        return ext in self.ALLOWED_EXTENSIONS
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename while preserving extension"""
        ext = self._get_file_extension(original_filename)
        unique_name = f"{uuid.uuid4()}{ext}"
        return unique_name
    
    def save_image_from_url(self, image_url: str, entity_type: str = "jugador") -> Tuple[str, str]:
        """
        Download image from URL and save it locally with thumbnail.
        
        Args:
            image_url: URL of the image to download
            entity_type: Type of entity (jugador, equipo, usuario, etc.)
            
        Returns:
            Tuple of (image_path, thumbnail_path) - relative paths to stored images
            
        Raises:
            ValueError: If URL is invalid or image cannot be downloaded
        """
        try:
            # Headers to avoid 403 Forbidden errors
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.google.com/'
            }
            
            # Download image from URL
            response = requests.get(image_url, timeout=10, headers=headers)
            response.raise_for_status()
            
            # Validate content type
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                raise ValueError(f"URL does not point to an image: {content_type}")
            
            # Generate unique filename
            original_filename = image_url.split('/')[-1].split('?')[0]
            if not self._is_valid_extension(original_filename):
                original_filename += '.jpg'  # Default to jpg if no valid extension
            
            unique_filename = self._generate_unique_filename(original_filename)
            
            # Open image with PIL
            image = Image.open(BytesIO(response.content))
            
            # Save original image
            image_path = os.path.join(self.PICS_DIR, unique_filename)
            image.save(image_path, quality=85, optimize=True)
            
            # Generate and save thumbnail
            thumbnail_filename = f"thumb_{unique_filename}"
            thumbnail_path = os.path.join(self.THUMBNAILS_DIR, thumbnail_filename)
            
            # Create thumbnail
            thumbnail = image.copy()
            thumbnail.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            thumbnail.save(thumbnail_path, quality=85, optimize=True)
            
            # Return relative paths
            relative_image_path = f"/imgs/pics/{unique_filename}"
            relative_thumbnail_path = f"/imgs/thumbnails/{thumbnail_filename}"
            
            return relative_image_path, relative_thumbnail_path
            
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error al descargar imagen desde URL: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error al procesar imagen: {str(e)}")
    
    def save_uploaded_file(self, file_content: bytes, filename: str, entity_type: str = "jugador") -> Tuple[str, str]:
        """
        Save uploaded file content and generate thumbnail.
        
        Args:
            file_content: Binary content of the uploaded file
            filename: Original filename
            entity_type: Type of entity (jugador, equipo, usuario, etc.)
            
        Returns:
            Tuple of (image_path, thumbnail_path) - relative paths to stored images
            
        Raises:
            ValueError: If file is invalid or cannot be processed
        """
        try:
            # Validate file extension
            if not self._is_valid_extension(filename):
                raise ValueError(f"Extensión de archivo no permitida. Use: {', '.join(self.ALLOWED_EXTENSIONS)}")
            
            # Generate unique filename
            unique_filename = self._generate_unique_filename(filename)
            
            # Open image with PIL
            image = Image.open(BytesIO(file_content))
            
            # Save original image
            image_path = os.path.join(self.PICS_DIR, unique_filename)
            image.save(image_path, quality=85, optimize=True)
            
            # Generate and save thumbnail
            thumbnail_filename = f"thumb_{unique_filename}"
            thumbnail_path = os.path.join(self.THUMBNAILS_DIR, thumbnail_filename)
            
            # Create thumbnail
            thumbnail = image.copy()
            thumbnail.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            thumbnail.save(thumbnail_path, quality=85, optimize=True)
            
            # Return relative paths
            relative_image_path = f"/imgs/pics/{unique_filename}"
            relative_thumbnail_path = f"/imgs/thumbnails/{thumbnail_filename}"
            
            return relative_image_path, relative_thumbnail_path
            
        except Exception as e:
            raise ValueError(f"Error al procesar archivo subido: {str(e)}")
    
    def delete_image(self, image_path: str) -> bool:
        """
        Delete an image and its thumbnail.
        
        Args:
            image_path: Relative path to the image (e.g., /imgs/pics/image.jpg)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Convert relative path to absolute
            abs_image_path = os.path.join("/app", image_path.lstrip('/'))
            
            # Delete main image
            if os.path.exists(abs_image_path):
                os.remove(abs_image_path)
            
            # Delete thumbnail
            filename = os.path.basename(abs_image_path)
            thumbnail_path = os.path.join(self.THUMBNAILS_DIR, f"thumb_{filename}")
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            
            return True
            
        except Exception as e:
            print(f"Error al eliminar imagen: {str(e)}")
            return False
    
    def get_image_url(self, relative_path: str, base_url: str = "") -> str:
        """
        Get full URL for an image.
        
        Args:
            relative_path: Relative path to the image
            base_url: Base URL of the server (optional)
            
        Returns:
            Full URL to the image
        """
        if base_url:
            return f"{base_url.rstrip('/')}{relative_path}"
        return relative_path


# Create service instance
cdn_service = CDNService()
