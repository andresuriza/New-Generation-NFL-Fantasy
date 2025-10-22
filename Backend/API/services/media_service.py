"""
Business logic service for Media operations with separation of concerns
"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.media import MediaCreate, MediaUpdate, MediaResponse
from models.database_models import MediaDB
from repositories.media_repository import media_repository
from services.validation_service import validation_service

def _to_media_response(media: MediaDB) -> MediaResponse:
    return MediaResponse.model_validate(media, from_attributes=True)

class MediaService:
    """Service for Media CRUD operations"""
    
    def crear(self, db: Session, media: MediaCreate) -> MediaResponse:
        """Create media for a team"""
        # Validate team exists
        from ..repositories.equipo_repository import equipo_repository
        equipo = equipo_repository.get(db, media.equipo_id)
        if not equipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Equipo no encontrado"
            )
        
        # Check if media already exists for this team
        if media_repository.exists_for_equipo(db, media.equipo_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un registro de media para este equipo"
            )
        
        nuevo_media = media_repository.create(db, media)
        return _to_media_response(nuevo_media)

    def listar(self, db: Session, limit: int = 100) -> List[MediaResponse]:
        """List recent media"""
        medias = media_repository.get_recent_media(db, limit)
        return [_to_media_response(m) for m in medias]

    def obtener(self, db: Session, equipo_id: UUID) -> MediaResponse:
        """Get media by team ID"""
        media = media_repository.get_by_equipo(db, equipo_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró media para este equipo"
            )
        return _to_media_response(media)

    def actualizar(self, db: Session, equipo_id: UUID, media_update: MediaUpdate) -> MediaResponse:
        """Update media for a team"""
        media = media_repository.get_by_equipo(db, equipo_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró media para este equipo"
            )
        
        # Update generado_en if URL is being changed
        if media_update.url and media_update.url != media.url:
            from datetime import datetime
            media.generado_en = datetime.now()
        
        updated_media = media_repository.update(db, media, media_update)
        return _to_media_response(updated_media)

    def eliminar(self, db: Session, equipo_id: UUID) -> bool:
        """Delete media for a team"""
        if not media_repository.exists_for_equipo(db, equipo_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró media para este equipo"
            )
        return media_repository.delete_by_equipo(db, equipo_id)

    def subir_imagen(self, equipo_id: UUID, filename: str) -> MediaResponse:
        imagen_url = f"/media/equipos/{equipo_id}/{filename}"
        now = datetime.now()
        if equipo_id in self._db:
            self._db[equipo_id].url = imagen_url
            self._db[equipo_id].generado_en = now
        else:
            self._db[equipo_id] = Media(equipo_id=equipo_id, url=imagen_url, generado_en=now, creado_en=now)
        return MediaResponse.from_orm(self._db[equipo_id])

    def equipos_con_media(self) -> List[UUID]:
        return list(self._db.keys())

    def generar_imagen(self, equipo_id: UUID) -> MediaResponse:
        now = datetime.now()
        imagen_generada_url = f"/media/equipos/{equipo_id}/generated_{int(now.timestamp())}.png"
        if equipo_id in self._db:
            self._db[equipo_id].url = imagen_generada_url
            self._db[equipo_id].generado_en = now
        else:
            self._db[equipo_id] = Media(equipo_id=equipo_id, url=imagen_generada_url, generado_en=now, creado_en=now)
        return MediaResponse.from_orm(self._db[equipo_id])


media_service = MediaService()
