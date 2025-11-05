CREATE EXTENSION IF NOT EXISTS pgcrypto;

--Posiciones(basado en el json)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'posicion_jugador') THEN
    CREATE TYPE posicion_jugador AS ENUM ('QB','RB','WR','TE','K','DEF','IR');
  END IF;
END$$;

CREATE TABLE IF NOT EXISTS jugadores (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),   
  nombre         VARCHAR(100) NOT NULL,                        
  posicion       posicion_jugador NOT NULL,                    -- QB/RB/WR/TE/K/DEF/IR
  equipo_id      UUID NOT NULL REFERENCES equipos(id)          -- equipo NFL (tabla equipos)
                 ON DELETE RESTRICT,
  imagen_url     TEXT NOT NULL,                                
  thumbnail_url  TEXT,                                        
  activo         BOOLEAN NOT NULL DEFAULT true,                
  creado_en      TIMESTAMPTZ NOT NULL DEFAULT now(),           

  --Nombre único por equipo NFL
  CONSTRAINT uq_jugador_por_equipo UNIQUE (equipo_id, nombre),


  CONSTRAINT ck_nombre_jugador_len CHECK (length(nombre) BETWEEN 1 AND 100)
);


CREATE TABLE IF NOT EXISTS jugadores_por_equipo (
  liga_id    UUID NOT NULL,
  equipo_id  UUID NOT NULL,
  jugador_id UUID NOT NULL REFERENCES jugadores(id) ON DELETE RESTRICT,

  --es_titular BOOLEAN NOT NULL DEFAULT true,
  creado_en  TIMESTAMPTZ NOT NULL DEFAULT now(),

  --Jugador único dentro de ese equipo fantasy en esa liga
  CONSTRAINT pk_jugadores_por_equipo PRIMARY KEY (liga_id, equipo_id, jugador_id),

  --Relación con el equipo fantasy en esa liga
  CONSTRAINT fk_jpe_ligas_equipos
    FOREIGN KEY (liga_id, equipo_id)
    REFERENCES ligas_equipos (liga_id, equipo_id)
    ON DELETE CASCADE,

  --Evitar que un jugador esté en dos equipos de la misma liga
  CONSTRAINT uq_jugador_por_liga UNIQUE (liga_id, jugador_id)
);
