CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- para gen_random_uuid()

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
