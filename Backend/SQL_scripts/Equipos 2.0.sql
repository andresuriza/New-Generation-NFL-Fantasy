CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- para gen_random_uuid()

DROP TABLE IF EXISTS equipos CASCADE;

CREATE TABLE IF NOT EXISTS equipos (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre     VARCHAR(100) NOT NULL,
  creado_en  TIMESTAMPTZ NOT NULL DEFAULT now(),
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
  ciudad     VARCHAR(30) NOT NULL,
  CONSTRAINT ck_nombre_len             CHECK (length(nombre) BETWEEN 1 AND 100),
  CONSTRAINT uq_nombre_equipo         UNIQUE (nombre)
);


