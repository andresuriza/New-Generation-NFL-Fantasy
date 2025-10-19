CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Temporadas
CREATE TABLE IF NOT EXISTS temporadas (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre        VARCHAR(100) NOT NULL,
  semanas       INT NOT NULL CHECK (semanas BETWEEN 1 AND 17),
  fecha_inicio  DATE NOT NULL,
  fecha_fin     DATE NOT NULL,
  es_actual     BOOLEAN NOT NULL DEFAULT false,  
  creado_en     TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT ck_temp_rango CHECK (fecha_fin > fecha_inicio), --Que no sea igual inicio y fin
  CONSTRAINT uq_temporadas_nombre UNIQUE (nombre)          --Nombre Unico
);

--Temporada puede ser "actual"
CREATE UNIQUE INDEX IF NOT EXISTS uq_temporada_actual
  ON temporadas ((es_actual))
  WHERE es_actual = true;

--Tabla dependiente para semanas
CREATE TABLE IF NOT EXISTS temporadas_semanas (
  temporada_id  UUID NOT NULL REFERENCES temporadas(id) ON DELETE CASCADE,
  numero        INT  NOT NULL,      -- semana 1..N dentro de la temporada
  fecha_inicio  DATE NOT NULL,
  fecha_fin     DATE NOT NULL,
  CONSTRAINT pk_temp_sem PRIMARY KEY (temporada_id, numero),
  CONSTRAINT ck_sem_rango CHECK (fecha_fin > fecha_inicio)
);

