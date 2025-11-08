"""
Service for handling database constraint errors and converting them to business exceptions
"""
import re
from typing import Dict, Optional
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2.errors import (
    UniqueViolation, 
    CheckViolation,
    ForeignKeyViolation,
    NotNullViolation,
    StringDataRightTruncation
)
from exceptions.business_exceptions import (
    ValidationError, 
    ConflictError, 
    ForeignKeyError, 
    ConstraintViolationError
)

class ConstraintErrorService:
    """Service for mapping database constraints to user-friendly error messages"""
    
    # Constraint name to error message mapping
    CONSTRAINT_MESSAGES = {
        # Users table constraints
        "usuarios_correo_key": "El correo electrónico ya está registrado",
        "usuarios_pkey": "Error interno: ID de usuario duplicado",
        
        # Seasons table constraints
        "temporadas_nombre_key": "Ya existe una temporada con ese nombre",
        "check_semanas": "El número de semanas debe estar entre 1 y 17",
        "ck_temp_rango": "La fecha de fin debe ser posterior a la fecha de inicio",
        
        # Season weeks table constraints
        "ck_sem_rango": "La fecha de fin de la semana debe ser posterior a la fecha de inicio",
        
        # Leagues table constraints
        "ligas_nombre_key": "Ya existe una liga con ese nombre",
        "ck_equipos_max": "El número máximo de equipos debe ser 4, 6, 8, 10, 12, 14, 16, 18 o 20",
        "ck_playoffs_equipos": "El número de equipos en playoffs debe ser 4 o 6",
        "ck_nombre_liga_len": "El nombre de la liga debe tener entre 1 y 100 caracteres",
        
        # League members table constraints
        "ligas_miembros_pkey": "El usuario ya es miembro de esta liga",
        "uq_alias_por_liga": "Ya existe un usuario con ese alias en esta liga",
        "ck_alias_len": "El alias debe tener entre 1 y 50 caracteres",
        
        # League quotas table constraints
        "ck_miembros_no_negativos": "El número de miembros no puede ser negativo",
        
        # Fantasy teams table constraints
        "uq_nombre_equipo_fantasy_por_liga": "Ya existe un equipo con ese nombre en esta liga",
        "ck_nombre_equipo_fantasy_len": "El nombre del equipo debe tener entre 1 y 100 caracteres",
        "ck_imagen_url_format": "La URL de la imagen debe ser un archivo JPG o PNG válido",
        
        # Players table constraints
        "uq_jugador_por_equipo": "Ya existe un jugador con ese nombre en este equipo",
        "ck_nombre_jugador_len": "El nombre del jugador debe tener entre 1 y 100 caracteres",
        
        # Foreign key constraints
        "ligas_temporada_id_fkey": "La temporada especificada no existe",
        "ligas_comisionado_id_fkey": "El usuario comisionado no existe",
        "ligas_miembros_liga_id_fkey": "La liga especificada no existe",
        "ligas_miembros_usuario_id_fkey": "El usuario especificado no existe",
        "equipos_fantasy_liga_id_fkey": "La liga especificada no existe",
        "equipos_fantasy_usuario_id_fkey": "El usuario especificado no existe",
        "jugadores_equipo_id_fkey": "El equipo NFL especificado no existe",
        
        # Not null constraints
        "usuarios_nombre_not_null": "El nombre del usuario es obligatorio",
        "usuarios_alias_not_null": "El alias del usuario es obligatorio",
        "usuarios_correo_not_null": "El correo electrónico es obligatorio",
        "usuarios_contrasena_hash_not_null": "La contraseña es obligatoria",
        "ligas_nombre_not_null": "El nombre de la liga es obligatorio",
        "ligas_contrasena_hash_not_null": "La contraseña de la liga es obligatoria",
        "ligas_equipos_max_not_null": "El número máximo de equipos es obligatorio",
        "jugadores_nombre_not_null": "El nombre del jugador es obligatorio",
        "jugadores_posicion_not_null": "La posición del jugador es obligatoria",
    }
    
    # Column length constraints
    COLUMN_LENGTH_LIMITS = {
        "usuarios": {
            "nombre": 50,
            "alias": 50,
            "correo": 50,
            "idioma": 10
        },
        "ligas": {
            "nombre": 100,
            "descripcion": None  # TEXT field, no specific limit
        },
        "equipos_fantasy": {
            "nombre": 100
        },
        "jugadores": {
            "nombre": 100
        },
        "ligas_miembros": {
            "alias": 50,
            "equipo_fantasy_name": 50
        }
    }
    
    @classmethod
    def handle_integrity_error(cls, error: IntegrityError):
        """
        Convert SQLAlchemy IntegrityError to business exception
        """
        orig_error = error.orig
        error_message = str(orig_error)
        
        # Handle unique constraint violations
        if isinstance(orig_error, UniqueViolation):
            return cls._handle_unique_violation(error_message)
        
        # Handle check constraint violations
        elif isinstance(orig_error, CheckViolation):
            return cls._handle_check_violation(error_message)
        
        # Handle foreign key violations
        elif isinstance(orig_error, ForeignKeyViolation):
            return cls._handle_foreign_key_violation(error_message)
        
        # Handle not null violations
        elif isinstance(orig_error, NotNullViolation):
            return cls._handle_not_null_violation(error_message)
        
        # Handle string data truncation
        elif isinstance(orig_error, StringDataRightTruncation):
            return cls._handle_truncation_violation(error_message)
        
        # Fallback for other integrity errors
        raise ValidationError("Error de validación en la base de datos")
    
    @classmethod
    def _handle_unique_violation(cls, error_message: str):
        """Handle unique constraint violations"""
        # Extract constraint name from error message
        constraint_match = re.search(r'constraint "([^"]+)"', error_message)
        if constraint_match:
            constraint_name = constraint_match.group(1)
            if constraint_name in cls.CONSTRAINT_MESSAGES:
                raise ConflictError(
                    cls.CONSTRAINT_MESSAGES[constraint_name],
                    constraint_name
                )
        
        # Check for specific patterns in the error message
        if "usuarios_correo" in error_message:
            raise ConflictError("El correo electrónico ya está registrado")
        elif "ligas_nombre" in error_message:
            raise ConflictError("Ya existe una liga con ese nombre")
        elif "uq_alias_por_liga" in error_message:
            raise ConflictError("Ya existe un usuario con ese alias en esta liga")
        elif "uq_nombre_equipo_fantasy_por_liga" in error_message:
            raise ConflictError("Ya existe un equipo con ese nombre en esta liga")
        
        raise ConflictError("El valor ingresado ya existe en el sistema")
    
    @classmethod
    def _handle_check_violation(cls, error_message: str):
        """Handle check constraint violations"""
        constraint_match = re.search(r'constraint "([^"]+)"', error_message)
        if constraint_match:
            constraint_name = constraint_match.group(1)
            if constraint_name in cls.CONSTRAINT_MESSAGES:
                raise ConstraintViolationError(
                    cls.CONSTRAINT_MESSAGES[constraint_name],
                    "check",
                    constraint_name
                )
        
        # Check for specific patterns
        if "check_semanas" in error_message:
            raise ValidationError("El número de semanas debe estar entre 1 y 17")
        elif "ck_equipos_max" in error_message:
            raise ValidationError("El número máximo de equipos debe ser 4, 6, 8, 10, 12, 14, 16, 18 o 20")
        elif "ck_playoffs_equipos" in error_message:
            raise ValidationError("El número de equipos en playoffs debe ser 4 o 6")
        elif "ck_temp_rango" in error_message or "ck_sem_rango" in error_message:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio")
        
        raise ValidationError("Los datos ingresados no cumplen con las reglas de validación")
    
    @classmethod
    def _handle_foreign_key_violation(cls, error_message: str):
        """Handle foreign key constraint violations"""
        constraint_match = re.search(r'constraint "([^"]+)"', error_message)
        if constraint_match:
            constraint_name = constraint_match.group(1)
            if constraint_name in cls.CONSTRAINT_MESSAGES:
                raise ForeignKeyError(cls.CONSTRAINT_MESSAGES[constraint_name])
        
        # Check for specific patterns
        if "temporada_id" in error_message:
            raise ForeignKeyError("La temporada especificada no existe")
        elif "comisionado_id" in error_message or "usuario_id" in error_message:
            raise ForeignKeyError("El usuario especificado no existe")
        elif "liga_id" in error_message:
            raise ForeignKeyError("La liga especificada no existe")
        elif "equipo_id" in error_message:
            raise ForeignKeyError("El equipo especificado no existe")
        
        raise ForeignKeyError("La referencia especificada no existe en el sistema")
    
    @classmethod
    def _handle_not_null_violation(cls, error_message: str):
        """Handle not null constraint violations"""
        # Extract column name from error message
        column_match = re.search(r'column "([^"]+)"', error_message)
        if column_match:
            column_name = column_match.group(1)
            
            # Try to find specific constraint message
            for constraint in cls.CONSTRAINT_MESSAGES:
                if constraint.endswith(f"_{column_name}_not_null"):
                    raise ValidationError(cls.CONSTRAINT_MESSAGES[constraint])
            
            # Generic message based on column name
            field_names = {
                "nombre": "nombre",
                "alias": "alias",
                "correo": "correo electrónico",
                "contrasena_hash": "contraseña",
                "equipos_max": "número máximo de equipos",
                "posicion": "posición del jugador"
            }
            
            field_name = field_names.get(column_name, column_name)
            raise ValidationError(f"El campo {field_name} es obligatorio")
        
        raise ValidationError("Faltan campos obligatorios")
    
    @classmethod
    def _handle_truncation_violation(cls, error_message: str):
        """Handle string data truncation violations"""
        # Try to extract table and column information
        table_match = re.search(r'relation "([^"]+)"', error_message)
        
        if table_match:
            table_name = table_match.group(1)
            
            # Get column limits for the table
            if table_name in cls.COLUMN_LENGTH_LIMITS:
                table_limits = cls.COLUMN_LENGTH_LIMITS[table_name]
                # Find the most likely violated column (this is heuristic)
                if "nombre" in table_limits and table_limits["nombre"]:
                    raise ValidationError(f"El nombre no puede exceder {table_limits['nombre']} caracteres")
                elif "alias" in table_limits and table_limits["alias"]:
                    raise ValidationError(f"El alias no puede exceder {table_limits['alias']} caracteres")
                elif "correo" in table_limits and table_limits["correo"]:
                    raise ValidationError(f"El correo electrónico no puede exceder {table_limits['correo']} caracteres")
        
        raise ValidationError("Uno o más campos exceden la longitud máxima permitida")
    
    @classmethod
    def handle_data_error(cls, error: DataError):
        """Handle SQLAlchemy DataError (e.g., invalid UUID, invalid enum values)"""
        error_message = str(error.orig).lower()
        
        if "invalid input syntax for type uuid" in error_message:
            raise ValidationError("El formato del ID proporcionado no es válido")
        elif "invalid input value for enum" in error_message:
            if "rol_usuario_enum" in error_message:
                raise ValidationError("El rol de usuario especificado no es válido. Debe ser 'manager' o 'administrador'")
            elif "estado_usuario_enum" in error_message:
                raise ValidationError("El estado de usuario especificado no es válido. Debe ser 'activa', 'bloqueado' o 'eliminada'")
            elif "estado_liga_enum" in error_message:
                raise ValidationError("El estado de liga especificado no es válido. Debe ser 'Pre_draft' o 'Draft'")
            elif "rol_membresia_enum" in error_message:
                raise ValidationError("El rol de membresía especificado no es válido. Debe ser 'Comisionado' o 'Manager'")
            elif "posicion_jugador" in error_message:
                raise ValidationError("La posición del jugador no es válida. Debe ser QB, RB, WR, TE, K, DEF o IR")
            else:
                raise ValidationError("El valor proporcionado para el campo no es válido")
        
        raise ValidationError("Los datos proporcionados tienen un formato incorrecto")

# Create singleton instance
constraint_error_service = ConstraintErrorService()