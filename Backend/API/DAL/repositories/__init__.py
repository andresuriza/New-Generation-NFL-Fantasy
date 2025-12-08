"""
Repositories Package

Contains all repository classes for database operations following the repository pattern.
Each repository provides CRUD operations and query methods for a specific entity.

Available repositories:
- usuario_repository: User operations
- liga_repository: League operations
- equipo_repository: NFL team operations
- equipo_fantasy_repository: Fantasy team operations
- jugador_repository: Player operations
- temporada_repository: Season operations
- media_repository: Media operations
- noticia_jugador_repository: Player news operations
"""

from .base import BaseRepository
from .usuario_repository import usuario_repository
from .liga_repository import liga_repository, liga_miembro_repository, liga_cupo_repository
from .equipo_repository import equipo_repository
from .equipo_fantasy_repository import equipo_fantasy_repository, equipo_fantasy_audit_repository
from .jugador_repository import jugador_repository
from .temporada_repository import temporada_repository, temporada_semana_repository
from .media_repository import media_repository
from .noticia_jugador_repository import noticia_jugador_repository
from .db_context import db_context

__all__ = [
    'BaseRepository',
    'usuario_repository',
    'liga_repository',
    'liga_miembro_repository',
    'liga_cupo_repository',
    'equipo_repository',
    'equipo_fantasy_repository',
    'equipo_fantasy_audit_repository',
    'jugador_repository',
    'temporada_repository',
    'temporada_semana_repository',
    'media_repository',
    'noticia_jugador_repository',
    'db_context',
]
