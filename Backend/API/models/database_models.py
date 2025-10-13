from sqlalchemy import Column, String, DateTime, Text, UUID, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
import uuid

# Enums for user roles and states
class RolUsuarioEnum(enum.Enum):
    manager = "manager"
    administrador = "administrador"

class EstadoUsuarioEnum(enum.Enum):
    activa = "activa"
    bloqueado = "bloqueado"
    eliminada = "eliminada"

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
    equipos = relationship("EquipoDB", back_populates="usuario")

class LigaDB(Base):
    __tablename__ = "ligas"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    equipos = relationship("EquipoDB", back_populates="liga", cascade="all, delete-orphan")

class EquipoDB(Base):
    __tablename__ = "equipos"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    liga_id = Column(PG_UUID(as_uuid=True), ForeignKey("ligas.id", ondelete="CASCADE"), nullable=False)
    usuario_id = Column(PG_UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    nombre = Column(String(100), nullable=False)
    thumbnail = Column(Text, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    liga = relationship("LigaDB", back_populates="equipos")
    usuario = relationship("UsuarioDB", back_populates="equipos")
    media = relationship("MediaDB", back_populates="equipo", uselist=False, cascade="all, delete-orphan")

class MediaDB(Base):
    __tablename__ = "media"
    
    equipo_id = Column(PG_UUID(as_uuid=True), ForeignKey("equipos.id", ondelete="CASCADE"), primary_key=True)
    url = Column(Text, nullable=False)
    generado_en = Column(DateTime(timezone=True), default=func.now())
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    equipo = relationship("EquipoDB", back_populates="media")