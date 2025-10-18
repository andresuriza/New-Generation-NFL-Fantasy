from typing import Dict, List
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status

from models.media import Media, MediaCreate, MediaUpdate, MediaResponse


class MediaService:
    def __init__(self):
        self._db: Dict[UUID, Media] = {}

    def crear(self, media: MediaCreate) -> MediaResponse:
        if media.equipo_id in self._db:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un registro de media para este equipo")
        now = datetime.now()
        nuevo = Media(equipo_id=media.equipo_id, url=media.url, generado_en=now, creado_en=now)
        self._db[media.equipo_id] = nuevo
        return MediaResponse.from_orm(nuevo)

    def listar(self) -> List[MediaResponse]:
        return [MediaResponse.from_orm(m) for m in self._db.values()]

    def obtener(self, equipo_id: UUID) -> MediaResponse:
        if equipo_id not in self._db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró media para este equipo")
        return MediaResponse.from_orm(self._db[equipo_id])

    def actualizar(self, equipo_id: UUID, media_update: MediaUpdate) -> MediaResponse:
        if equipo_id not in self._db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró media para este equipo")
        media_actual = self._db[equipo_id]
        update_data = media_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(media_actual, field, value)
        if "url" in update_data:
            media_actual.generado_en = datetime.now()
        self._db[equipo_id] = media_actual
        return MediaResponse.from_orm(media_actual)

    def eliminar(self, equipo_id: UUID) -> None:
        if equipo_id not in self._db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró media para este equipo")
        del self._db[equipo_id]

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
