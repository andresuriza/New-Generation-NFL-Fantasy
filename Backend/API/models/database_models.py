from sqlalchemy import Column, String, DateTime, Text, UUID, Enum, ForeignKey, Integer, CheckConstraint, SmallInteger, Boolean, Date, UniqueConstraint, Index, text, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
import uuid
#TODO  -- include campo de equipo fantasy en ligas_miembros
# Enums for user roles and states
class RolUsuarioEnum(enum.Enum):
    manager = "manager"
    administrador = "administrador"

class EstadoUsuarioEnum(enum.Enum):
    activa = "activa"
    bloqueado = "bloqueado"
    eliminada = "eliminada"

class EstadoLigaEnum(enum.Enum):
    Pre_draft = "Pre_draft"
    Draft = "Draft"

class RolMembresiaEnum(enum.Enum):
    Comisionado = "Comisionado"
    Manager = "Manager"
class PosicionJugadorEnum(enum.Enum):
    QB = "QB"
    RB = "RB"
    WR = "WR"
    TE = "TE"
    K = "K"
    DEF = "DEF"
    IR = "IR"
class UsuarioDB(Base):
    __tablename__ = "usuarios"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(50), nullable=False)
    alias = Column(String(50), nullable=False)
    correo = Column(String(50), nullable=False, unique=True)
    contrasena_hash = Column(Text, nullable=False)
    rol = Column(Enum(RolUsuarioEnum), nullable=False, default=RolUsuarioEnum.manager)
    estado = Column(Enum(EstadoUsuarioEnum), nullable=False, default=EstadoUsuarioEnum.activa)
    idioma = Column(String(10), nullable=False, default="Ingles")
    imagen_perfil_url = Column(Text, nullable=False, default="/img/perfil/default.png")
    failed_attempts = Column(Integer, nullable=False, default=0)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    equipos_fantasy = relationship("EquipoFantasyDB", back_populates="usuario")
    ligas_miembros = relationship("LigaMiembroDB", back_populates="usuario")
    ligas_miembros_aud = relationship("LigaMiembroAudDB", back_populates="usuario")

class TemporadaDB(Base):
    __tablename__ = "temporadas"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False, unique=True)
    semanas = Column(Integer, nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    es_actual = Column(Boolean, nullable=False, default=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ligas = relationship("LigaDB", back_populates="temporada")
    temporadas_semanas = relationship("TemporadaSemanaDB", back_populates="temporada", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('semanas >= 1 AND semanas <= 18', name='check_semanas'),
        CheckConstraint('fecha_fin > fecha_inicio', name='ck_temp_rango'),
        Index('uq_temporada_actual', 'es_actual', unique=True, postgresql_where=text('es_actual = true'))
    )

class TemporadaSemanaDB(Base):
    __tablename__ = "temporadas_semanas"
    
    temporada_id = Column(PG_UUID(as_uuid=True), ForeignKey("temporadas.id", ondelete="CASCADE"), primary_key=True)
    numero = Column(Integer, primary_key=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    
    # Relationships
    temporada = relationship("TemporadaDB", back_populates="temporadas_semanas")
    
    __table_args__ = (
        CheckConstraint('fecha_fin > fecha_inicio', name='ck_sem_rango'),
    )

class LigaDB(Base):
    __tablename__ = "ligas"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    contrasena_hash = Column(Text, nullable=False)
    equipos_max = Column(SmallInteger, nullable=False)
    estado = Column(Enum(EstadoLigaEnum), nullable=False, default=EstadoLigaEnum.Pre_draft)
    temporada_id = Column(PG_UUID(as_uuid=True), ForeignKey("temporadas.id", ondelete="RESTRICT"), nullable=False)
    comisionado_id = Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)

    # Configuraciones por defecto
    playoffs_equipos = Column(SmallInteger, nullable=False, default=4)
    puntajes_decimales = Column(Boolean, nullable=False, default=True)
    trade_deadline_activa = Column(Boolean, nullable=False, default=False)
    limite_cambios_temp = Column(Integer, nullable=True)
    limite_agentes_temp = Column(Integer, nullable=True)

    # Formato de posiciones por defecto (JSONB)
    formato_posiciones = Column(JSONB, nullable=False, server_default=func.cast(
        '{"QB":1, "RB":2, "K":1, "DEF":1, "WR":2, "FLEX_RB_WR":1, "TE":1, "BANCA":6, "IR":3}',
        JSONB
    ))

    # Esquema de puntos por defecto (JSONB)
    puntos_config = Column(JSONB, nullable=False, server_default=func.cast(
        '{"passing_yards_points_per_25_yards": 1, "passing_touchdown_points": 4, "interception_thrown_points": -2, "rushing_yards_points_per_10_yards": 1, "reception_points": 1, "receiving_yards_points_per_10_yards": 1, "rushing_or_receiving_touchdown_points": 6, "defense_sack_points": 1, "defense_interception_points": 2, "defense_fumble_recovered_points": 2, "defense_safety_points": 2, "defense_touchdown_points": 6, "team_defense_two_point_return_points": 2, "kicking_pat_made_points": 1, "field_goal_made_0_to_50_yards_points": 3, "field_goal_made_50_plus_yards_points": 5, "points_allowed_less_equal_10_points": 5, "points_allowed_less_equal_20_points": 2, "points_allowed_less_equal_30_points": 0, "points_allowed_greater_30_points": -2}',
        JSONB
    ))

    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    temporada = relationship("TemporadaDB", back_populates="ligas")
    equipos_fantasy = relationship("EquipoFantasyDB", back_populates="liga", cascade="all, delete-orphan")
    miembros = relationship("LigaMiembroDB", back_populates="liga", cascade="all, delete-orphan")
    miembros_aud = relationship("LigaMiembroAudDB", back_populates="liga", cascade="all, delete-orphan")
    cupos = relationship("LigaCupoDB", back_populates="liga", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('equipos_max IN (4,6,8,10,12,14,16,18,20)', name='ck_equipos_max'),
        CheckConstraint('playoffs_equipos IN (4,6)', name='ck_playoffs_equipos'),
        CheckConstraint('length(nombre) BETWEEN 1 AND 100', name='ck_nombre_liga_len')
    )

class LigaMiembroDB(Base):
    __tablename__ = "ligas_miembros"
    
    liga_id = Column(PG_UUID(as_uuid=True), ForeignKey("ligas.id", ondelete="CASCADE"), primary_key=True)
    usuario_id = Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    alias = Column(String(50), nullable=False)
    rol = Column(Enum(RolMembresiaEnum), nullable=False, default=RolMembresiaEnum.Manager)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    liga = relationship("LigaDB", back_populates="miembros")
    usuario = relationship("UsuarioDB", back_populates="ligas_miembros")
    
    __table_args__ = (
        UniqueConstraint('liga_id', 'alias', name='uq_alias_por_liga'),
        CheckConstraint('length(alias) BETWEEN 1 AND 50', name='ck_alias_len'),
        Index('uq_unico_comisionado_por_liga', 'liga_id', unique=True, 
              postgresql_where=text("rol = 'Comisionado'"))
    )

class LigaMiembroAudDB(Base):
    __tablename__ = "ligas_miembros_aud"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    liga_id = Column(PG_UUID(as_uuid=True), ForeignKey("ligas.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    accion = Column(String, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    liga = relationship("LigaDB", back_populates="miembros_aud")
    usuario = relationship("UsuarioDB", back_populates="ligas_miembros_aud")
    
    __table_args__ = (
        CheckConstraint("accion IN ('unirse','salir')", name='ck_accion'),
    )

class LigaCupoDB(Base):
    __tablename__ = "ligas_cupos"
    
    liga_id = Column(PG_UUID(as_uuid=True), ForeignKey("ligas.id", ondelete="CASCADE"), primary_key=True)
    miembros_actuales = Column(Integer, nullable=False, default=0)
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    liga = relationship("LigaDB", back_populates="cupos")
    
    __table_args__ = (
        CheckConstraint('miembros_actuales >= 0', name='ck_miembros_no_negativos'),
    )

class EquipoDB(Base):
    """Modelo de datos para equipos NFL (equipos reales de la NFL)"""
    __tablename__ = "equipos"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    nombre = Column(String(100), nullable=False)
    ciudad = Column(String(100), nullable=True)
    thumbnail = Column(Text, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=text("NOW()"))
    actualizado_en = Column(DateTime(timezone=True), server_default=text("NOW()"))
    
    # Relationships
    media = relationship("MediaDB", back_populates="equipo", uselist=False, cascade="all, delete-orphan")
    jugadores = relationship("JugadoresDB", back_populates="equipo_nfl")

class MediaDB(Base):
    __tablename__ = "media"
    
    equipo_id = Column(PG_UUID(as_uuid=True), ForeignKey("equipos.id", ondelete="CASCADE"), primary_key=True)
    url = Column(Text, nullable=False)
    generado_en = Column(DateTime(timezone=True), default=func.now())
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    equipo = relationship("EquipoDB", back_populates="media")

class JugadoresDB(Base):
    __tablename__ = "jugadores"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    nombre = Column(String(100), nullable=False)
    posicion = Column(Enum(PosicionJugadorEnum), nullable=False)
    equipo_id = Column(PG_UUID(as_uuid=True), ForeignKey("equipos.id", ondelete="RESTRICT"), nullable=False)
    imagen_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=text("now()"))
    
    # Relationships
    equipo_nfl = relationship("EquipoDB", back_populates="jugadores")

    __table_args__ = (
        UniqueConstraint('equipo_id', 'nombre', name='uq_jugador_por_equipo'),
        CheckConstraint('length(nombre) BETWEEN 1 AND 100', name='ck_nombre_jugador_len')
    )

class EquipoFantasyDB(Base):
    __tablename__ = "equipos_fantasy"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    liga_id = Column(PG_UUID(as_uuid=True), ForeignKey("ligas.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    nombre = Column(String(100), nullable=False)
    imagen_url = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=text("NOW()"))
    actualizado_en = Column(DateTime(timezone=True), server_default=text("NOW()"))
    
    # Relationships
    liga = relationship("LigaDB", back_populates="equipos_fantasy")
    usuario = relationship("UsuarioDB", back_populates="equipos_fantasy")
    audit_logs = relationship("EquipoFantasyAuditDB", back_populates="equipo_fantasy", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('liga_id', 'nombre', name='uq_nombre_equipo_fantasy_por_liga'),
        CheckConstraint('length(nombre) BETWEEN 1 AND 100', name='ck_nombre_equipo_fantasy_len'),
        CheckConstraint(
            "imagen_url IS NULL OR imagen_url ~ '\\.(jpg|jpeg|png)(\\?.*)?$'",
            name='ck_imagen_url_format'
        )
    )

class EquipoFantasyAuditDB(Base):
    __tablename__ = "equipos_fantasy_audit"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    equipo_fantasy_id = Column(PG_UUID(as_uuid=True), ForeignKey("equipos_fantasy.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    accion = Column(String(50), nullable=False)  # 'CREATE', 'UPDATE_NOMBRE', 'UPDATE_IMAGEN', 'DELETE'
    campo_modificado = Column(String(50), nullable=True)  # 'nombre', 'imagen_url', NULL for CREATE/DELETE
    valor_anterior = Column(Text, nullable=True)
    valor_nuevo = Column(Text, nullable=True)
    timestamp_accion = Column(DateTime(timezone=True), server_default=text("NOW()"))
    
    # Relationships
    equipo_fantasy = relationship("EquipoFantasyDB", back_populates="audit_logs")
    usuario = relationship("UsuarioDB")
