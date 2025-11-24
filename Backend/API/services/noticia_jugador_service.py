"""
Business logic service for NoticiaJugador (Player News) operations
"""
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from models.jugador import (
    NoticiaJugadorCreate, 
    NoticiaJugadorResponse, 
    NoticiaJugadorConAutor
)
from models.database_models import NoticiaJugadorDB
from repositories.noticia_jugador_repository import noticia_jugador_repository
from repositories.jugador_repository import jugador_repository
from validators.jugador_validator import JugadorValidator
from exceptions.business_exceptions import ValidationError


def _to_noticia_response(noticia: NoticiaJugadorDB) -> NoticiaJugadorResponse:
    """Convert database model to response model"""
    return NoticiaJugadorResponse.model_validate(noticia)


def _to_noticia_con_autor_response(noticia: NoticiaJugadorDB) -> NoticiaJugadorConAutor:
    """Convert database model to response with author info"""
    return NoticiaJugadorConAutor(
        id=noticia.id,
        jugador_id=noticia.jugador_id,
        texto=noticia.texto,
        es_lesion=noticia.es_lesion,
        resumen=noticia.resumen,
        designacion=noticia.designacion,
        creado_en=noticia.creado_en,
        creado_por=noticia.creado_por,
        autor_nombre=noticia.autor.nombre,
        autor_alias=noticia.autor.alias
    )


class NoticiaJugadorService:
    """Service for player news operations"""
    
    def crear_noticia(
        self, 
        db: Session, 
        jugador_id: UUID, 
        noticia_data: NoticiaJugadorCreate, 
        author_id: UUID
    ) -> NoticiaJugadorResponse:
        """
        Create a new player news item.
        
        Business rules:
        - Player must exist and be active
        - If es_lesion is True, resumen and designacion are required
        - Text must be between 10-300 characters
        - Resumen must be between 1-30 characters (if provided)
        - Author must be an administrator
        - Audit information is automatically recorded
        """
        
        # Validate player exists and is active
        jugador = JugadorValidator.validate_exists(db, jugador_id)
        if not jugador.activo:
            raise ValidationError(f"El jugador con ID {jugador_id} no está activo")
        
        # Validate injury news requirements
        if noticia_data.es_lesion:
            if not noticia_data.resumen:
                raise ValidationError("El resumen es requerido para noticias de lesión")
            if not noticia_data.designacion:
                raise ValidationError("La designación es requerida para noticias de lesión")
            if len(noticia_data.resumen) > 30:
                raise ValidationError("El resumen no puede exceder 30 caracteres")
        else:
            # For non-injury news, clear injury-specific fields
            noticia_data.resumen = None
            noticia_data.designacion = None
        
        # Create the news item
        nueva_noticia = noticia_jugador_repository.create_with_author(
            db, jugador_id, noticia_data, author_id
        )
        
        return _to_noticia_response(nueva_noticia)
    
    def obtener_noticias_jugador(
        self, 
        db: Session, 
        jugador_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        incluir_autor: bool = False
    ) -> List[NoticiaJugadorResponse | NoticiaJugadorConAutor]:
        """Get all news for a specific player"""
        
        # Validate player exists
        JugadorValidator.validate_exists(db, jugador_id)
        
        if incluir_autor:
            noticias = noticia_jugador_repository.get_by_jugador_with_author(
                db, jugador_id, skip, limit
            )
            return [_to_noticia_con_autor_response(noticia) for noticia in noticias]
        else:
            noticias = noticia_jugador_repository.get_by_jugador_id(
                db, jugador_id, skip, limit
            )
            return [_to_noticia_response(noticia) for noticia in noticias]
    
    def obtener_noticia_por_id(
        self, 
        db: Session, 
        noticia_id: UUID,
        incluir_autor: bool = False
    ) -> NoticiaJugadorResponse | NoticiaJugadorConAutor:
        """Get a specific news item by ID"""
        
        if incluir_autor:
            noticia = noticia_jugador_repository.get_with_author(db, noticia_id)
            if not noticia:
                raise ValidationError(f"No se encontró la noticia con ID {noticia_id}")
            return _to_noticia_con_autor_response(noticia)
        else:
            noticia = noticia_jugador_repository.get(db, noticia_id)
            if not noticia:
                raise ValidationError(f"No se encontró la noticia con ID {noticia_id}")
            return _to_noticia_response(noticia)
    
    def obtener_noticias_lesiones_recientes(
        self, 
        db: Session, 
        days: int = 7, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[NoticiaJugadorConAutor]:
        """Get recent injury news from the last N days"""
        
        noticias = noticia_jugador_repository.get_recent_injury_news(db, days, skip, limit)
        return [_to_noticia_con_autor_response(noticia) for noticia in noticias]


# Create service instance
noticia_jugador_service = NoticiaJugadorService()