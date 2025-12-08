"""
Media validation service
"""
import re
from typing import Optional
from uuid import UUID

from models.database_models import MediaDB
from exceptions.business_exceptions import NotFoundError, ValidationError, ConflictError
from DAL.repositories.media_repository import MediaRepository

class MediaValidator:
    """Validation service for Media model"""
    
    @staticmethod
    def validate_exists(media_id: UUID) -> MediaDB:
        """Validate that media exists"""
        media = MediaRepository().get(media_id)
        if not media:
            raise NotFoundError("Media no encontrado")
        return media
    
    @staticmethod
    def validate_url_format(url: str) -> None:
        """Validate media URL format"""
        if not url or not url.strip():
            raise ValidationError("La URL es requerida")
        
        # Basic URL validation
        url_pattern = r'^https?:\/\/[^\s<>"{}|\\^`\[\]]+$'
        if not re.match(url_pattern, url.strip()):
            raise ValidationError("Formato de URL inválido")
        
        if len(url.strip()) > 500:
            raise ValidationError("La URL no puede tener más de 500 caracteres")
    
    @staticmethod
    def validate_image_url_format(url: str) -> None:
        """Validate image URL format specifically"""
        MediaValidator.validate_url_format(url)
        
        # Check for image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']
        url_lower = url.lower()
        
        if not any(url_lower.endswith(ext) for ext in image_extensions):
            raise ValidationError(f"URL debe terminar con una extensión de imagen válida: {', '.join(image_extensions)}")
    
    @staticmethod
    def validate_video_url_format(url: str) -> None:
        """Validate video URL format specifically"""
        MediaValidator.validate_url_format(url)
        
        # Check for video extensions or video platforms
        video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
        video_platforms = ['youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com']
        
        url_lower = url.lower()
        
        is_video_file = any(url_lower.endswith(ext) for ext in video_extensions)
        is_video_platform = any(platform in url_lower for platform in video_platforms)
        
        if not is_video_file and not is_video_platform:
            raise ValidationError("URL debe ser un archivo de video válido o de una plataforma de video soportada")
    
    @staticmethod
    def validate_tipo_media(tipo: str) -> None:
        """Validate media type"""
        valid_types = ["imagen", "video", "thumbnail", "logo", "banner"]
        if tipo not in valid_types:
            raise ValidationError(f"Tipo de media inválido. Tipos válidos: {', '.join(valid_types)}")
    
    @staticmethod
    def validate_descripcion_format(descripcion: Optional[str]) -> None:
        """Validate media description format"""
        if descripcion is not None and descripcion.strip():
            if len(descripcion.strip()) > 255:
                raise ValidationError("La descripción no puede tener más de 255 caracteres")
    
    @staticmethod
    def validate_alt_text_format(alt_text: Optional[str]) -> None:
        """Validate alt text format"""
        if alt_text is not None and alt_text.strip():
            if len(alt_text.strip()) > 200:
                raise ValidationError("El texto alternativo no puede tener más de 200 caracteres")
    
    @staticmethod
    def validate_file_size(file_size_kb: Optional[int]) -> None:
        """Validate file size in KB"""
        if file_size_kb is not None:
            if file_size_kb < 0:
                raise ValidationError("El tamaño del archivo no puede ser negativo")
            
            # Max 10MB for images, 100MB for videos
            max_size_kb = 10240  # 10MB default
            if file_size_kb > max_size_kb:
                raise ValidationError(f"El archivo no puede exceder {max_size_kb}KB")
    
    @staticmethod
    def validate_dimensions(width: Optional[int], height: Optional[int]) -> None:
        """Validate image dimensions"""
        if width is not None:
            if width < 1 or width > 10000:
                raise ValidationError("El ancho debe estar entre 1 y 10000 píxeles")
        
        if height is not None:
            if height < 1 or height > 10000:
                raise ValidationError("La altura debe estar entre 1 y 10000 píxeles")
    
    @staticmethod
    def validate_url_unique(url: str, exclude_id: Optional[UUID] = None) -> None:
        """Validate that URL is unique"""
        existing_media = MediaRepository().get_by_url(url, exclude_id)
        if existing_media:
            raise ConflictError("La URL ya está registrada")
    
    @staticmethod
    def validate_media_active(media: MediaDB) -> None:
        """Validate that media is active"""
        if hasattr(media, 'activo') and not media.activo:
            raise ValidationError("El media no está activo")
    
    @staticmethod
    def validate_media_accessibility(url: str) -> None:
        """Validate that media URL is accessible (basic validation)"""
        # This could be expanded to actually check if the URL is accessible
        # For now, we'll just validate the format
        MediaValidator.validate_url_format(url)
        
        # Check for suspicious URLs
        suspicious_patterns = ['localhost', '127.0.0.1', 'internal', 'admin']
        url_lower = url.lower()
        
        for pattern in suspicious_patterns:
            if pattern in url_lower:
                raise ValidationError(f"URL no puede contener '{pattern}'")


# Create validator instance
media_validator = MediaValidator()