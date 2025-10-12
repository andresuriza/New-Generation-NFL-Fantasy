CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- UUID y bcrypt
CREATE EXTENSION IF NOT EXISTS citext;    -- para correo case-insensitive

CREATE TYPE rol_usuario AS ENUM ('manager','administrador');
CREATE TYPE estado_usuario AS ENUM ('activa','bloqueada','eliminada');

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

  -- Validaciones de longitudes y formato de correo
  CONSTRAINT ck_nombre_len  CHECK (length(nombre) BETWEEN 1 AND 50),
  CONSTRAINT ck_alias_len   CHECK (length(alias)  BETWEEN 1 AND 50),
  CONSTRAINT ck_correo_len  CHECK (length(correo) <= 50),
  CONSTRAINT ck_correo_fmt  CHECK (correo ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$')
);

