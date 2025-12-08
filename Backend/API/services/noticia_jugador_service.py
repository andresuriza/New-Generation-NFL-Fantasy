"""
Business logic service for NoticiaJugador (Player News) operations
"""
from typing import List
from uuid import UUID

from models.jugador import (
    NoticiaJugadorCreate, 
    NoticiaJugadorResponse, 
    NoticiaJugadorConAutor
)
from models.database_models import NoticiaJugadorDB
from DAL.repositories.noticia_jugador_repository import noticia_jugador_repository
from DAL.repositories.jugador_repository import jugador_repository
from DAL.repositories.usuario_repository import usuario_repository
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
        
        # Validate all requirements for creating player news
        jugador = JugadorValidator.validate_for_create_noticia(
            jugador_id,
            noticia_data.es_lesion,
            noticia_data.resumen,
            noticia_data.designacion
        )
        
        # Validate author exists and is administrator
        author = usuario_repository.get(author_id)
        if not author:
            raise ValidationError(f"El usuario autor con ID {author_id} no existe")
        if author.rol.value != "administrador":
            raise ValidationError("Solo los administradores pueden crear noticias de jugadores")
        if author.estado.value != "activa":
            raise ValidationError("El usuario autor debe estar activo")
        
        # For non-injury news, clear injury-specific fields
        if not noticia_data.es_lesion:
            noticia_data.resumen = None
            noticia_data.designacion = None
        
        # Create the news item
        nueva_noticia = noticia_jugador_repository.create_with_author(
            jugador_id, noticia_data, author_id
        )
        
        return _to_noticia_response(nueva_noticia)
    
    def obtener_noticias_jugador(
        self, 
        jugador_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        incluir_autor: bool = False
    ) -> List[NoticiaJugadorResponse | NoticiaJugadorConAutor]:
        """Get all news for a specific player"""
        
        # Validate player exists
        JugadorValidator.validate_exists(jugador_id)
        
        if incluir_autor:
            noticias = noticia_jugador_repository.get_by_jugador_with_author(
                jugador_id, skip, limit
            )
            return [_to_noticia_con_autor_response(noticia) for noticia in noticias]
        else:
            noticias = noticia_jugador_repository.get_by_jugador_id(
                jugador_id, skip, limit
            )
            return [_to_noticia_response(noticia) for noticia in noticias]
    
    def obtener_noticia_por_id(
        self, 
        noticia_id: UUID,
        incluir_autor: bool = False
    ) -> NoticiaJugadorResponse | NoticiaJugadorConAutor:
        """Get a specific news item by ID"""
        
        if incluir_autor:
            noticia = noticia_jugador_repository.get_with_author(noticia_id)
            if not noticia:
                raise ValidationError(f"No se encontró la noticia con ID {noticia_id}")
            return _to_noticia_con_autor_response(noticia)
        else:
            noticia = noticia_jugador_repository.get(noticia_id)
            if not noticia:
                raise ValidationError(f"No se encontró la noticia con ID {noticia_id}")
            return _to_noticia_response(noticia)
    
    def obtener_noticias_lesiones_recientes(
        self, 
        days: int = 7, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[NoticiaJugadorConAutor]:
        """Get recent injury news from the last N days"""
        
        noticias = noticia_jugador_repository.get_recent_injury_news(days, skip, limit)
        return [_to_noticia_con_autor_response(noticia) for noticia in noticias]


# Create service instance
noticia_jugador_service = NoticiaJugadorService()