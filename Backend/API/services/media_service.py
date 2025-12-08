"""
Business logic service for Media operations with separation of concerns
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from models.media import MediaCreate, MediaUpdate, MediaResponse
from models.database_models import MediaDB
from repositories.media_repository import media_repository
def _to_media_response(media: MediaDB) -> MediaResponse:
    return MediaResponse.model_validate(media, from_attributes=True)

class MediaService:
    """Service for Media CRUD operations"""
    
    def crear(self,media: MediaCreate) -> MediaResponse:
        """Create media for a team
        
        Raises:
            ValueError: If team doesn't exist or media already exists
        """
        # Validate team exists
        from ..repositories.equipo_repository import equipo_repository
        equipo = equipo_repository.get(media.equipo_id)
        if not equipo:
            raise ValueError("Equipo no encontrado")
        
        # Check if media already exists for this team
        if media_repository.exists_for_equipo(media.equipo_id):
            raise ValueError("Ya existe un registro de media para este equipo")
        
        nuevo_media = media_repository.create(media)
        return _to_media_response(nuevo_media)

    def listar(self, limit: int = 100) -> List[MediaResponse]:
        """List recent media"""
        medias = media_repository.get_recent_media(limit)
        return [_to_media_response(m) for m in medias]

    def obtener(self, equipo_id: UUID) -> Optional[MediaResponse]:
        """Get media by team ID
        
        Returns:
            MediaResponse if found, None if not found
        """
        media = media_repository.get_by_equipo(equipo_id)
        if not media:
            return None
        return _to_media_response(media)

    def actualizar(self, equipo_id: UUID, media_update: MediaUpdate) -> Optional[MediaResponse]:
        """Update media for a team
        
        Returns:
            MediaResponse if successful, None if not found
        """
        media = media_repository.get_by_equipo(equipo_id)
        if not media:
            return None
        
        # Update generado_en if URL is being changed
        if media_update.url and media_update.url != media.url:
            media.generado_en = datetime.now()
        
        updated_media = media_repository.update(media, media_update)
        return _to_media_response(updated_media)

    def eliminar(self, equipo_id: UUID) -> bool:
        """Delete media for a team
        
        Returns:
            True if deleted successfully, False if not found
        """
        if not media_repository.exists_for_equipo(equipo_id):
            return False
        return media_repository.delete_by_equipo(equipo_id)

    def subir_imagen(self, equipo_id: UUID, filename: str) -> MediaResponse:
        """Create media entry for uploaded image
        
        Args:
            db: Database session
            equipo_id: Team ID
            filename: Uploaded file name
            
        Returns:
            MediaResponse with uploaded image URL
        """
        imagen_url = f"/media/equipos/{equipo_id}/{filename}"
        
        # Check if media already exists for this team
        existing_media = media_repository.get_by_equipo(equipo_id)
        
        if existing_media:
            # Update existing media
            update_data = MediaUpdate(url=imagen_url)
            updated_media = media_repository.update(existing_media, update_data)
            return _to_media_response(updated_media)
        else:
            # Create new media
            media_data = MediaCreate(
                equipo_id=equipo_id,
                url=imagen_url
            )
            new_media = media_repository.create(media_data)
            return _to_media_response(new_media)

    def equipos_con_media(self) -> List[UUID]:
        """Get list of team IDs that have media
        
        Returns:
            List of team IDs that have media entries
        """
        return media_repository.get_equipos_with_media()

    def generar_imagen(self, equipo_id: UUID) -> MediaResponse:
        """Generate AI image for team
        
        Returns:
            MediaResponse with generated image URL
        """
        now = datetime.now()
        imagen_generada_url = f"/media/equipos/{equipo_id}/generated_{int(now.timestamp())}.png"
        
        # Check if media already exists for this team
        existing_media = media_repository.get_by_equipo(equipo_id)
        
        if existing_media:
            # Update existing media
            update_data = MediaUpdate(url=imagen_generada_url)
            updated_media = media_repository.update(existing_media, update_data)
            return _to_media_response(updated_media)
        else:
            # Create new media
            media_data = MediaCreate(
                equipo_id=equipo_id,
                url=imagen_generada_url
            )
            new_media = media_repository.create(media_data)
            return _to_media_response(new_media)


media_service = MediaService()
