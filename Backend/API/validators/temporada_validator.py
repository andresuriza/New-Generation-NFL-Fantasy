"""
Temporada validation service
"""
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from repositories.temporada_repository import TemporadaRepository
from models.database_models import TemporadaDB
from exceptions.business_exceptions import NotFoundError, ValidationError, ConflictError


class TemporadaValidator:
    """Validation service for Temporada model"""
    
    @staticmethod
    def validate_exists(temporada_id: UUID) -> TemporadaDB:
        """Validate that a season exists"""
        temporada = TemporadaRepository().get(temporada_id)
        if not temporada:
            raise NotFoundError("Temporada no encontrada")
        return temporada
    
    @staticmethod
    def validate_nombre_format(nombre: str) -> None:
        """Validate season name format"""
        if not nombre or not nombre.strip():
            raise ValidationError("El nombre de la temporada es requerido")
        
        if len(nombre.strip()) < 3:
            raise ValidationError("El nombre de la temporada debe tener al menos 3 caracteres")
        
        if len(nombre.strip()) > 100:
            raise ValidationError("El nombre de la temporada no puede tener más de 100 caracteres")
    
    @staticmethod
    def validate_nombre_unique(nombre: str, exclude_id: Optional[UUID] = None) -> None:
        """Validate that season name is unique"""
        existing_temporada = TemporadaRepository().get_by_nombre(nombre, exclude_id)
        if existing_temporada:
            raise ConflictError("Ya existe una temporada con ese nombre")
    
    @staticmethod
    def validate_date_range(fecha_inicio: date, fecha_fin: date) -> None:
        """Validate season date range"""
        if fecha_inicio >= fecha_fin:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        # Validate that the season is not too short
        duration_days = (fecha_fin - fecha_inicio).days
        if duration_days < 30:
            raise ValidationError("La temporada debe durar al menos 30 días")
        
        # Validate that the season is not too long (e.g., max 1 year)
        if duration_days > 365:
            raise ValidationError("La temporada no puede durar más de 1 año")
    
    @staticmethod
    def validate_weeks_count(semanas: int) -> None:
        """Validate number of weeks in season"""
        if semanas < 1:
            raise ValidationError("La temporada debe tener al menos 1 semana")
        
        if semanas > 18:
            raise ValidationError(
                f"La temporada no puede tener más de 18 semanas. Valor proporcionado: {semanas}. "
                "La NFL regular season tiene 18 semanas (semanas 1-18), que es el máximo permitido."
            )
    
    @staticmethod
    def validate_weeks_count_range(semanas: int) -> None:
        """Validate number of weeks in season (1-18 range for NFL)"""
        if semanas < 1 or semanas > 18:
            raise ValidationError(
                f"El número de semanas debe estar entre 1 y 18 (temporada regular NFL). "
                f"Valor proporcionado: {semanas}"
            )
    
    @staticmethod
    def validate_fecha_fin_posterior_inicio(fecha_inicio: date, fecha_fin: date) -> None:
        """Validate that end date is after start date"""
        if fecha_fin <= fecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio")
    
    @staticmethod
    def validate_weeks_within_season(temporada_id: UUID, semanas_data: list) -> None:
        """Validate that week dates are within season range and don't overlap"""
        
        # Get season to check date range
        temporada = TemporadaValidator.validate_exists(temporada_id)
        if not temporada:
            raise NotFoundError("Temporada no encontrada")
        
        # Validate each week
        for semana_data in semanas_data:
            numero = semana_data.get('numero')
            fecha_inicio = semana_data.get('fecha_inicio')
            fecha_fin = semana_data.get('fecha_fin')
            
            # Validate week number
            if numero < 1 or numero > temporada.semanas:
                raise ValidationError(f"El número de semana {numero} está fuera del rango válido (1-{temporada.semanas})")
            
            # Validate week dates are within season
            if fecha_inicio < temporada.fecha_inicio or fecha_inicio > temporada.fecha_fin:
                raise ValidationError(f"La fecha de inicio de la semana {numero} debe estar dentro del rango de la temporada")
            
            if fecha_fin < temporada.fecha_inicio or fecha_fin > temporada.fecha_fin:
                raise ValidationError(f"La fecha de fin de la semana {numero} debe estar dentro del rango de la temporada")
            
            # Validate week date range
            if fecha_inicio >= fecha_fin:
                raise ValidationError(f"La fecha de inicio de la semana {numero} debe ser anterior a la fecha de fin")
        
        # Check for overlapping weeks
        sorted_weeks = sorted(semanas_data, key=lambda x: x.get('fecha_inicio'))
        for i in range(len(sorted_weeks) - 1):
            current_week = sorted_weeks[i]
            next_week = sorted_weeks[i + 1]
            
            if current_week.get('fecha_fin') >= next_week.get('fecha_inicio'):
                raise ValidationError(f"Las fechas de las semanas {current_week.get('numero')} y {next_week.get('numero')} se traslapan")
    
    @staticmethod
    def validate_only_one_current_season(exclude_id: Optional[UUID] = None) -> None:
        """Validate that only one season can be marked as current"""
        query = db.query(TemporadaDB).filter(TemporadaDB.es_actual == True)
        if exclude_id:
            query = query.filter(TemporadaDB.id != exclude_id)
        
        existing_current = query.first()
        if existing_current:
            raise ConflictError(f"Ya existe una temporada marcada como actual: '{existing_current.nombre}'")
    
    @staticmethod
    def validate_season_weeks_consistency(semanas_count: int, fecha_inicio: date, fecha_fin: date) -> None:
        """Validate that the number of weeks is consistent with the date range"""
        duration_days = (fecha_fin - fecha_inicio).days
        expected_duration = semanas_count * 7  # Approximately 7 days per week
        
        # Allow some flexibility (±7 days per week)
        min_duration = semanas_count * 6
        max_duration = semanas_count * 8
        
        if duration_days < min_duration:
            raise ValidationError(f"El rango de fechas ({duration_days} días) es muy corto para {semanas_count} semanas")
        
        if duration_days > max_duration:
            raise ValidationError(f"El rango de fechas ({duration_days} días) es muy largo para {semanas_count} semanas")
    
    @staticmethod
    def validate_season_dates_not_overlap(fecha_inicio: date, fecha_fin: date, exclude_id: Optional[UUID] = None) -> None:
        """Validate that season dates don't overlap with existing seasons"""
        
        overlapping_season = TemporadaRepository().get_overlapping_season(fecha_inicio, fecha_fin, exclude_id)
        if overlapping_season:
            raise ConflictError(f"Las fechas se superponen con la temporada '{overlapping_season.nombre}'")
    
    @staticmethod
    def validate_season_in_future_or_current(fecha_inicio: date) -> None:
        """Validate that season start date is not in the past"""
        today = date.today()
        if fecha_inicio < today:
            raise ValidationError("La fecha de inicio no puede ser en el pasado")
    
    @staticmethod
    def validate_complete_season_creation(nombre: str, semanas: int, 
                                        fecha_inicio: date, fecha_fin: date, 
                                        es_actual: bool = False) -> None:
        """Comprehensive validation for season creation"""
        # Validate name
        TemporadaValidator.validate_nombre_format(nombre)
        TemporadaValidator.validate_nombre_unique(nombre)
        
        # Validate weeks count
        TemporadaValidator.validate_weeks_count(semanas)
        
        # Validate dates
        TemporadaValidator.validate_date_range(fecha_inicio, fecha_fin)
        TemporadaValidator.validate_season_in_future_or_current(fecha_inicio)
        TemporadaValidator.validate_season_dates_not_overlap(fecha_inicio, fecha_fin)
        
        # Validate weeks consistency with date range
        TemporadaValidator.validate_season_weeks_consistency(semanas, fecha_inicio, fecha_fin)
        
        # Validate current season uniqueness
        if es_actual:
            TemporadaValidator.validate_only_one_current_season()
    
    @staticmethod
    def validate_week_creation(temporada_id: UUID, numero: int, 
                          fecha_inicio: date, fecha_fin: date) -> None:
        """Validate individual week creation"""
        
        # Get season
        temporada = TemporadaValidator.validate_exists(temporada_id)
        
        # Validate week number
        if numero < 1 or numero > temporada.semanas:
            raise ValidationError(f"El número de semana debe estar entre 1 y {temporada.semanas}")
        
        # Check if week already exists
        existing_week = TemporadaRepository().get_week_by_numero(temporada_id, numero)
        
        if existing_week:
            raise ConflictError(f"La semana {numero} ya existe para esta temporada")
        
        # Validate week dates
        if fecha_inicio >= fecha_fin:
            raise ValidationError("La fecha de inicio de la semana debe ser anterior a la fecha de fin")
        
        # Validate week is within season range
        if fecha_inicio < temporada.fecha_inicio or fecha_fin > temporada.fecha_fin:
            raise ValidationError("Las fechas de la semana deben estar dentro del rango de la temporada")
        
        # Check for overlaps with existing weeks
        overlapping_week = TemporadaRepository().get_overlapping_week(temporada_id, fecha_inicio, fecha_fin)
        
        if overlapping_week:
            raise ConflictError(f"Las fechas se traslapan con la semana {overlapping_week.numero}")
    
    @staticmethod
    def validate_season_update(temporada_id: UUID, nombre: Optional[str] = None,
                          es_actual: Optional[bool] = None) -> None:
        """Validate season update operations"""
        temporada = TemporadaValidator.validate_exists(temporada_id)
        
        # Check if season can be modified
        TemporadaValidator.validate_season_can_be_modified(temporada)
        
        # Validate name if being updated
        if nombre is not None:
            TemporadaValidator.validate_nombre_format(nombre)
            TemporadaValidator.validate_nombre_unique(nombre, temporada_id)
        
        # Validate current season status if being updated
        if es_actual is True:
            TemporadaValidator.validate_only_one_current_season(temporada_id)
    
    @staticmethod
    def validate_season_can_be_modified(temporada: TemporadaDB) -> None:
        """Validate that season can be modified"""
        today = date.today()
        
        # If season has already started, some modifications might be restricted
        if temporada.fecha_inicio <= today:
            raise ValidationError("No se puede modificar una temporada que ya ha comenzado")
    
    @staticmethod
    def validate_season_can_be_deleted(temporada_id: UUID) -> None:
        """Validate that season can be deleted"""
        temporada = TemporadaValidator.validate_exists(temporada_id)
        
        # Check if any leagues are using this season
        liga_count = TemporadaRepository().count_ligas_by_temporada(temporada_id)
        
        if liga_count > 0:
            raise ValidationError(f"No se puede eliminar la temporada porque está siendo utilizada por {liga_count} liga(s)")
    
    @staticmethod
    def validate_current_week(semana_actual: int, total_semanas: int) -> None:
        """Validate current week number"""
        if semana_actual < 0:
            raise ValidationError("La semana actual no puede ser negativa")
        
        if semana_actual > total_semanas:
            raise ValidationError("La semana actual no puede ser mayor al total de semanas")


# Create validator instance
temporada_validator = TemporadaValidator()