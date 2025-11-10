"""
Jugador validation service
"""
import re
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from models.database_models import JugadoresDB, EquipoDB, PosicionJugadorEnum
from exceptions.business_exceptions import NotFoundError, ValidationError, ConflictError


class JugadorValidator:
    """Validation service for Jugador model"""
    
    @staticmethod
    def validate_exists(db: Session, jugador_id: UUID) -> JugadoresDB:
        """Validate that a player exists"""
        jugador = db.query(JugadoresDB).filter(JugadoresDB.id == jugador_id).first()
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
    def validate_email_unique(db: Session, email: str, exclude_id: Optional[UUID] = None) -> None:
        """Validate that email is unique"""
        query = db.query(JugadoresDB).filter(JugadoresDB.email == email)
        if exclude_id:
            query = query.filter(JugadoresDB.id != exclude_id)
        
        if query.first():
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
    def validate_dorsal_unique_in_team(db: Session, equipo_id: UUID, dorsal: int, exclude_id: Optional[UUID] = None) -> None:
        """Validate that jersey number is unique within the team"""
        query = db.query(JugadoresDB).filter(
            JugadoresDB.equipo_id == equipo_id,
            JugadoresDB.dorsal == dorsal
        )
        
        if exclude_id:
            query = query.filter(JugadoresDB.id != exclude_id)
        
        existing_player = query.first()
        if existing_player:
            raise ConflictError(f"El dorsal {dorsal} ya existe en este equipo")
    
    @staticmethod
    def validate_equipo_nfl_exists(db: Session, equipo_id: UUID) -> EquipoDB:
        """Validate that NFL team exists"""
        equipo = db.query(EquipoDB).filter(EquipoDB.id == equipo_id).first()
        if not equipo:
            raise NotFoundError("Equipo NFL no encontrado")
        return equipo
    
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
    def validate_nombre_unique_in_team(db: Session, nombre: str, equipo_id: UUID, exclude_id: Optional[UUID] = None) -> None:
        """Validate that player name is unique within the team"""
        query = db.query(JugadoresDB).filter(
            JugadoresDB.nombre == nombre,
            JugadoresDB.equipo_id == equipo_id
        )
        
        if exclude_id:
            query = query.filter(JugadoresDB.id != exclude_id)
        
        existing_player = query.first()
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
    def validate_jugador_can_be_deleted(db: Session, jugador_id: UUID) -> None:
        """Validate that player can be deleted"""
        # Check if player is in any fantasy teams
        from models.database_models import EquipoFantasyDB
        
        # This would need to be implemented based on your fantasy team-player relationship
        # For now, we'll just check if player exists
        jugador = JugadorValidator.validate_exists(db, jugador_id)
        # Add more business rules as needed
    
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
    def validate_equipo_exists_by_nombre(db: Session, equipo_nombre: str, equipo_cache: dict) -> EquipoDB:
        """Validate NFL team exists by name with caching support"""
        # Check cache first
        if equipo_nombre in equipo_cache:
            return equipo_cache[equipo_nombre]
        
        # Query database
        equipo = db.query(EquipoDB).filter(EquipoDB.nombre.ilike(equipo_nombre)).first()
        if not equipo:
            raise NotFoundError(f"Equipo NFL '{equipo_nombre}' no encontrado")
        
        # Store in cache
        equipo_cache[equipo_nombre] = equipo
        return equipo
    
    @staticmethod
    def validate_jugador_unique_by_nombre_equipo(db: Session, nombre: str, equipo_id: UUID) -> None:
        """Validate player doesn't already exist in team"""
        existing_player = db.query(JugadoresDB).filter(
            JugadoresDB.nombre == nombre,
            JugadoresDB.equipo_id == equipo_id
        ).first()
        
        if existing_player:
            raise ConflictError(f"Ya existe un jugador con ese nombre en el equipo")
    
    @staticmethod
    def validate_imagen_url_bulk(imagen_url: str) -> None:
        """Validate image URL format for bulk creation"""
        if not imagen_url.startswith(('http://', 'https://')):
            raise ValidationError("URL de imagen debe comenzar con http:// o https://")


# Create validator instance
jugador_validator = JugadorValidator()