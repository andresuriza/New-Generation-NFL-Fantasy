CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE ligas (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),   -- identificador único
  nombre      VARCHAR(100) NOT NULL,                        -- nombre visible de la liga
  creado_en   TIMESTAMPTZ  NOT NULL DEFAULT now(),          -- fecha de creación
  actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now(),        -- fecha de actualización

  CONSTRAINT ck_nombre_liga_len CHECK (length(nombre) BETWEEN 1 AND 100)
);