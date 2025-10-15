-- Active: 1760290916467@@127.0.0.1@5432@postgres
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- UUID y bcrypt
CREATE EXTENSION IF NOT EXISTS citext;    -- para correo case-insensitive

CREATE DATABASE "XNFL-Fantasy"
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;


CREATE TYPE rol_usuario AS ENUM ('manager','administrador');
CREATE TYPE estado_usuario AS ENUM ('activa','bloqueado','eliminada');

CREATE TABLE usuarios (
  id                UUID         PRIMARY KEY DEFAULT gen_random_uuid(),         -- ID único autogenerado
  nombre            VARCHAR(50)  NOT NULL,                                       -- 1–50
  alias             VARCHAR(50)  NOT NULL,                                       -- 1–50
  correo  			CITEXT       NOT NULL UNIQUE,
  contrasena_hash   TEXT         NOT NULL,                                       -- almacenamos hash, no la contraseña
  rol               rol_usuario  NOT NULL DEFAULT 'manager',
  estado            estado_usuario  NOT NULL DEFAULT 'activa',
  idioma            VARCHAR(10)  NOT NULL DEFAULT 'Ingles',                      
  imagen_perfil_url TEXT         NOT NULL DEFAULT '/img/perfil/default.png',     -- imagen por defecto
  creado_en         TIMESTAMPTZ  NOT NULL DEFAULT now(),                         -- fecha de creación
  failed_attempts INT DEFAULT 0,
  -- Validaciones de longitudes y formato de correo
  CONSTRAINT ck_nombre_len  CHECK (length(nombre) BETWEEN 1 AND 50),
  CONSTRAINT ck_alias_len   CHECK (length(alias)  BETWEEN 1 AND 50),
  CONSTRAINT ck_correo_len  CHECK (length(correo) <= 50),
  CONSTRAINT ck_correo_fmt  CHECK (correo ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$')
);



CREATE TABLE ligas (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),   -- identificador único
  nombre      VARCHAR(100) NOT NULL,                        -- nombre visible de la liga
  creado_en   TIMESTAMPTZ  NOT NULL DEFAULT now(),          -- fecha de creación
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now(),        -- fecha de actualización

  CONSTRAINT ck_nombre_liga_len CHECK (length(nombre) BETWEEN 1 AND 100)
);

CREATE TABLE equipos (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  liga_id    UUID NOT NULL REFERENCES ligas(id) ON DELETE CASCADE,
  usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
  nombre     VARCHAR(100) NOT NULL,
  creado_en  TIMESTAMPTZ NOT NULL DEFAULT now(),
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_equipo_nombre_por_liga UNIQUE (liga_id, nombre),
  CONSTRAINT uq_usuario_por_liga       UNIQUE (liga_id, usuario_id),
  CONSTRAINT ck_nombre_len             CHECK (length(nombre) BETWEEN 1 AND 100)
);

CREATE TABLE media (
  equipo_id    UUID PRIMARY KEY REFERENCES equipos(id) ON DELETE CASCADE,     
  url          TEXT NOT NULL,                               -- URL de la imagen
  generado_en  TIMESTAMPTZ DEFAULT now(),
  creado_en    TIMESTAMPTZ NOT NULL DEFAULT now()
);



