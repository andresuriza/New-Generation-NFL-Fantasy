-- Estados de liga
DROP TABLE IF EXISTS ligas CASCADE;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_liga') THEN
    CREATE TYPE estado_liga AS ENUM ('Pre_draft','Draft');
  END IF;
END$$;

CREATE TABLE IF NOT EXISTS ligas (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre               VARCHAR(100) NOT NULL UNIQUE,
  descripcion          TEXT,
  contrasena_hash      TEXT NOT NULL,                         -- misma política que usuarios (bcrypt)
  equipos_max          SMALLINT NOT NULL
                         CHECK (equipos_max IN (4,6,8,10,12,14,16,18,20)),
  estado               estado_liga NOT NULL DEFAULT 'Pre_draft',
  temporada_id         UUID NOT NULL REFERENCES temporadas(id) ON DELETE RESTRICT, 
  comisionado_id       UUID NOT NULL REFERENCES usuarios(id)   ON DELETE RESTRICT,  

  -- Configuraciones por defecto
  playoffs_equipos     SMALLINT NOT NULL DEFAULT 4 CHECK (playoffs_equipos IN (4,6)),
  puntajes_decimales   BOOLEAN  NOT NULL DEFAULT true,
  trade_deadline_activa BOOLEAN NOT NULL DEFAULT false,        -- inactiva por defecto
  limite_cambios_temp  INT,                                    -- NULL = sin límite
  limite_agentes_temp  INT,                                    -- NULL = sin límite

  -- Formato de posiciones por defecto (JSONB)
  formato_posiciones   JSONB NOT NULL DEFAULT
   '{
      "QB":1, "RB":2, "K":1, "DEF":1, "WR":2,
      "FLEX_RB_WR":1, "TE":1, "BANCA":6, "IR":3
    }'::jsonb,

  -- Esquema de puntos por defecto (JSONB)
  puntos_config JSONB NOT NULL DEFAULT
	'{
	  "passing_yards_points_per_25_yards": 1,
	  "passing_touchdown_points": 4,
	  "interception_thrown_points": -2,
	  "rushing_yards_points_per_10_yards": 1,
	  "reception_points": 1,
	  "receiving_yards_points_per_10_yards": 1,
	  "rushing_or_receiving_touchdown_points": 6,
	  "defense_sack_points": 1,
	  "defense_interception_points": 2,
	  "defense_fumble_recovered_points": 2,
	  "defense_safety_points": 2,
	  "defense_touchdown_points": 6,
	  "team_defense_two_point_return_points": 2,
	  "kicking_pat_made_points": 1,
	  "field_goal_made_0_to_50_yards_points": 3,
	  "field_goal_made_50_plus_yards_points": 5,
	  "points_allowed_less_equal_10_points": 5,
	  "points_allowed_less_equal_20_points": 2,
	  "points_allowed_less_equal_30_points": 0,
	  "points_allowed_greater_30_points": -2
	}'::jsonb,


  creado_en            TIMESTAMPTZ NOT NULL DEFAULT now(),
  actualizado_en       TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- coherencias ligeras
  CONSTRAINT ck_nombre_liga_len CHECK (length(nombre) BETWEEN 1 AND 100)
);

-- helper para updated_at
CREATE OR REPLACE FUNCTION trg_set_actualizado_liga()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  NEW.actualizado_en := now();
  RETURN NEW;
END$$;

DROP TRIGGER IF EXISTS trg_ligas_actualizado ON ligas;
CREATE TRIGGER trg_ligas_actualizado
BEFORE UPDATE ON ligas
FOR EACH ROW EXECUTE FUNCTION trg_set_actualizado_liga();
