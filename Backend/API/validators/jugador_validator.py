"""
Jugador validation service
"""
import re
from typing import Optional
from uuid import UUID
from DAL.repositories.jugador_repository import JugadorRepository

from models.database_models import JugadoresDB, EquipoDB, PosicionJugadorEnum
from exceptions.business_exceptions import NotFoundError, ValidationError, ConflictError


class JugadorValidator:
    """Validation service for Jugador model"""
    
    @staticmethod
    def validate_exists( jugador_id: UUID) -> JugadoresDB:
        """Validate that a player exists"""
        jugador = JugadorRepository().get(jugador_id)
        if not jugador:
            raise NotFoundError("Jugador no encontrado")
        return jugador
    
    @staticmethod
    def validate_nombre_format(nombre: str) -> None:
        """Validate player name format"""
        if not nombre or not nombre.strip():
            raise ValidationError("El nombre del jugador es requerido")
        
        if len(nombre.strip()) < 2:
            raise ValidationError("El nombre del jugador debe tener al menos 2 caracteres")
        
        if len(nombre.strip()) > 100:
            raise ValidationError("El nombre del jugador no puede tener más de 100 caracteres")
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-ZÀ-ÿ\s\-'\.]+$", nombre.strip()):
            raise ValidationError("El nombre del jugador contiene caracteres inválidos")
    
    @staticmethod
    def validate_email_format(email: str) -> None:
        """Validate player email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Formato de email inválido")
    
    @staticmethod
    def validate_email_unique(email: str, exclude_id: Optional[UUID] = None) -> None:
        """Validate that email is unique"""
        existing_player = JugadorRepository().get_by_email(email, exclude_id)
        if existing_player:
            raise ConflictError("Email ya registrado")
    
    @staticmethod
    def validate_dorsal_format(dorsal: Optional[int]) -> None:
        """Validate jersey number format"""
        if dorsal is not None:
            if dorsal < 0:
                raise ValidationError("El dorsal no puede ser negativo")
            
            if dorsal > 99:
                raise ValidationError("El dorsal no puede ser mayor a 99")
    
    @staticmethod
    def validate_dorsal_unique_in_team(equipo_id: UUID, dorsal: int, exclude_id: Optional[UUID] = None) -> None:
        """Validate that jersey number is unique within the team"""
        existing_player = JugadorRepository().get_by_dorsal_and_equipo(dorsal, equipo_id, exclude_id)
        if existing_player:
            raise ConflictError("Ya existe un jugador con ese dorsal en el equipo")
    
    
    @staticmethod
    def validate_posicion(posicion: str) -> None:
        """Validate player position"""
        try:
            PosicionJugadorEnum(posicion)
        except ValueError:
            valid_positions = [pos.value for pos in PosicionJugadorEnum]
            raise ValidationError(f"Posición inválida. Posiciones válidas: {', '.join(valid_positions)}")
    
    @staticmethod
    def validate_altura_format(altura: Optional[str]) -> None:
        """Validate height format (e.g., '6-2' for 6 feet 2 inches)"""
        if altura is not None:
            if not re.match(r'^\d{1}-\d{1,2}$', altura):
                raise ValidationError("Formato de altura inválido. Use formato '6-2' (pies-pulgadas)")
    
    @staticmethod
    def validate_peso_format(peso: Optional[int]) -> None:
        """Validate weight format"""
        if peso is not None:
            if peso < 100 or peso > 400:
                raise ValidationError("El peso debe estar entre 100 y 400 libras")
    
    @staticmethod
    def validate_edad_format(edad: Optional[int]) -> None:
        """Validate age format"""
        if edad is not None:
            if edad < 18 or edad > 50:
                raise ValidationError("La edad debe estar entre 18 y 50 años")
    
    @staticmethod
    def validate_nombre_unique_in_team(nombre: str, equipo_id: UUID, exclude_id: Optional[UUID] = None) -> None:
        """Validate that player name is unique within the team"""
        
        existing_player = JugadorRepository().get_by_nombre_equipo(nombre, equipo_id, exclude_id)
        if existing_player:
            raise ConflictError("Ya existe un jugador con ese nombre en el equipo")
    
    @staticmethod
    def validate_imagen_url_format(imagen_url: Optional[str]) -> None:
        """Validate image URL format"""
        if imagen_url is not None and imagen_url.strip():
            # Basic URL validation
            url_pattern = r'^https?:\/\/.*\.(jpg|jpeg|png|gif|webp)$'
            if not re.match(url_pattern, imagen_url.strip(), re.IGNORECASE):
                raise ValidationError("URL de imagen inválida. Debe ser una URL válida con extensión de imagen")
    
    @staticmethod
    def validate_jugador_activo(jugador: JugadoresDB) -> None:
        """Validate that player is active"""
        if not jugador.activo:
            raise ValidationError("El jugador no está activo")
    
    @staticmethod
    def validate_jugador_can_be_deleted(jugador_id: UUID) -> None:
        """Validate that player can be deleted"""
        # Check if player is in any fantasy teams
        jugador = JugadorValidator.validate_exists(jugador_id)
    
    @staticmethod
    def validate_required_fields_bulk(jugador_data) -> None:
        """Validate required fields for bulk creation"""
        if not jugador_data.nombre:
            raise ValidationError("Campo 'nombre' es requerido")
        
        if not jugador_data.posicion:
            raise ValidationError("Campo 'posicion' es requerido")
        
        if not jugador_data.equipo_nfl:
            raise ValidationError("Campo 'equipo_nfl' es requerido")
        
        if not jugador_data.imagen:
            raise ValidationError("Campo 'imagen' es requerido")
    
    @staticmethod
    def validate_posicion_format_bulk(posicion: str) -> None:
        """Validate position format for bulk creation"""
        try:
            PosicionJugadorEnum(posicion)
        except ValueError:
            valid_positions = [pos.value for pos in PosicionJugadorEnum]
            raise ValidationError(f"Posición inválida. Posiciones válidas: {', '.join(valid_positions)}")
    
    @staticmethod
    def validate_equipo_exists_by_nombre(equipo_nombre: str, equipo_cache: dict) -> EquipoDB:
        """Validate NFL team exists by name with caching support"""
        # Check cache first
        if equipo_nombre in equipo_cache:
            return equipo_cache[equipo_nombre]
        
        # Query database
        equipo = EquipoDB.query.filter(EquipoDB.nombre == equipo_nombre).first()
        if not equipo:
            raise NotFoundError(f"Equipo NFL '{equipo_nombre}' no encontrado")
        
        # Store in cache
        equipo_cache[equipo_nombre] = equipo
        return equipo
    
    @staticmethod
    def validate_jugador_unique_by_nombre_equipo(nombre: str, equipo_id: UUID) -> None:
        """Validate player doesn't already exist in team"""
        existing_player = JugadorRepository().get_by_nombre_equipo(nombre, equipo_id)
        if existing_player:
            raise ConflictError(f"Ya existe un jugador con ese nombre en el equipo")
    
    @staticmethod
    def validate_imagen_url_bulk(imagen_url: str) -> None:
        """
        Validate image URL format for bulk creation.
        Accepts:
        - URLs: http:// or https://
        - Data URIs: data:image/...;base64,...
        - Raw base64: strings that look like base64 encoded data
        """
        import re
        
        # Check if it's a URL
        if imagen_url.startswith(('http://', 'https://')):
            return
        
        # Check if it's a data URI
        if imagen_url.startswith('data:'):
            return
        
        # Check if it's raw base64 (common chars in base64: A-Z, a-z, 0-9, +, /, =)
        # Must be at least 100 chars and match base64 pattern
        if len(imagen_url) >= 100:
            base64_pattern = r'^[A-Za-z0-9+/]*={0,2}$'
            if re.match(base64_pattern, imagen_url):
                return
        
        raise ValidationError("Imagen debe ser una URL (http:// o https://), datos base64 con prefijo data:, o base64 sin prefijo")
    
    @staticmethod
    def validate_for_create(nombre: str, posicion: str, equipo_id: UUID, imagen_url: str) -> None:
        """Validate all requirements for creating a player"""
        # Validate required fields
        if not nombre or not nombre.strip():
            raise ValidationError("El nombre del jugador es requerido")
        
        if not posicion:
            raise ValidationError("La posición del jugador es requerida")
        
        if not equipo_id:
            raise ValidationError("El equipo NFL es requerido")
        
        if not imagen_url or not imagen_url.strip():
            raise ValidationError("La URL de imagen es requerida")
        
        # Validate unique name in team
        JugadorValidator.validate_nombre_unique_in_team(nombre, equipo_id)
    
    @staticmethod
    def validate_for_update(jugador_id: UUID, nuevo_nombre: Optional[str] = None,
                          nuevo_equipo_id: Optional[UUID] = None) -> JugadoresDB:
        """Validate all requirements for updating a player"""
        jugador = JugadorValidator.validate_exists(jugador_id)
        
        # Validate unique name per NFL team if changing name or team
        if nuevo_nombre or nuevo_equipo_id:
            nombre_a_validar = nuevo_nombre or jugador.nombre
            equipo_a_validar = nuevo_equipo_id or jugador.equipo_id
            
            JugadorValidator.validate_nombre_unique_in_team(nombre_a_validar, equipo_a_validar, jugador_id)
        
        return jugador
    
    @staticmethod
    def validate_for_create_noticia(jugador_id: UUID, es_lesion: bool, resumen: Optional[str] = None,
                                   designacion: Optional[str] = None) -> JugadoresDB:
        """Validate all requirements for creating player news"""
        jugador = JugadorValidator.validate_exists(jugador_id)
        
        if not jugador.activo:
            raise ValidationError(f"El jugador con ID {jugador_id} no está activo")
        
        # Validate injury news requirements
        if es_lesion:
            if not resumen:
                raise ValidationError("El resumen es requerido para noticias de lesión")
            if not designacion:
                raise ValidationError("La designación es requerida para noticias de lesión")
            if len(resumen) > 30:
                raise ValidationError("El resumen no puede exceder 30 caracteres")
        
        return jugador


# Create validator instance
jugador_validator = JugadorValidator()