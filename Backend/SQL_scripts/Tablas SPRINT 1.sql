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
  cupo_equipos         INT NOT NULL,

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
  cupo_equipos         INT NOT NULL,

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

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'rol_membresia') THEN
    CREATE TYPE rol_membresia AS ENUM ('Comisionado','Manager');
  END IF;
END$$;

CREATE TABLE IF NOT EXISTS ligas_miembros (
  liga_id     UUID NOT NULL REFERENCES ligas(id)    ON DELETE CASCADE,
  usuario_id  UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  alias       VARCHAR(50) NOT NULL,
  rol         rol_membresia NOT NULL DEFAULT 'Manager',
  creado_en   TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT pk_liga_miembro PRIMARY KEY (liga_id, usuario_id),
  CONSTRAINT uq_alias_por_liga UNIQUE (liga_id, alias),
  CONSTRAINT ck_alias_len CHECK (length(alias) BETWEEN 1 AND 50)
);

CREATE UNIQUE INDEX uq_unico_comisionado_por_liga
  ON ligas_miembros (liga_id)
  WHERE rol = 'Comisionado';

CREATE TABLE IF NOT EXISTS ligas_miembros_aud (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  liga_id    UUID NOT NULL REFERENCES ligas(id)    ON DELETE CASCADE,
  usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  accion     TEXT NOT NULL CHECK (accion IN ('unirse','salir')),
  creado_en  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Contador para ligas
CREATE TABLE IF NOT EXISTS ligas_cupos(
  liga_id            UUID PRIMARY KEY REFERENCES ligas(id) ON DELETE CASCADE,
  miembros_actuales  INT  NOT NULL DEFAULT 0,
  actualizado_en     TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT ck_miembros_no_negativos CHECK (miembros_actuales >= 0)
);



-- Trigger: al crear la liga, agrega comisionado a membresías y auditoría
CREATE OR REPLACE FUNCTION trg_liga_insert_add_commissioner()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  v_alias TEXT;
BEGIN
  -- Tomamos el alias del usuario (o “Comisionado” si no hay)
  SELECT u.alias INTO v_alias
  FROM usuarios u
  WHERE u.id = NEW.comisionado_id;

  v_alias := COALESCE(NULLIF(v_alias, ''), 'Comisionado');

  -- Inserta membresía del comisionado (rol fijo) 
  -- Nota: no debería haber conflicto al crear la liga; ON CONFLICT por seguridad
  INSERT INTO ligas_miembros (liga_id, usuario_id, alias, rol)
  VALUES (NEW.id, NEW.comisionado_id, v_alias, 'Comisionado')
  ON CONFLICT DO NOTHING;

  -- Auditoría de incorporación
  INSERT INTO ligas_miembros_aud (liga_id, usuario_id, accion)
  VALUES (NEW.id, NEW.comisionado_id, 'unirse');

  RETURN NEW;
END;
$$;




CREATE TABLE IF NOT EXISTS ligas_equipos (
  liga_id        UUID NOT NULL REFERENCES ligas(id)   ON DELETE CASCADE,
  equipo_id      UUID NOT NULL REFERENCES equipos(id) ON DELETE CASCADE,
  usuario_id     UUID NOT NULL,  -- manager del equipo, debe ser miembro de la liga

  -- un usuario (manager) solo puede tener un equipo en una misma liga
  CONSTRAINT uq_usuario_un_equipo_por_liga UNIQUE (liga_id, usuario_id),

  -- el manager debe ser miembro registrado de la liga
  CONSTRAINT fk_le_miembro
    FOREIGN KEY (liga_id, usuario_id)
    REFERENCES ligas_miembros (liga_id, usuario_id)
    ON DELETE CASCADE
);


-- Inicializar el contador cuando se crea una liga
CREATE OR REPLACE FUNCTION trg_liga_init()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  INSERT INTO ligas_cupos(liga_id, miembros_actuales)
  VALUES (NEW.id, 0)
  ON CONFLICT (liga_id) DO NOTHING;
  RETURN NEW;
END$$;

DROP TRIGGER IF EXISTS trg_ligas_init ON ligas;
CREATE TRIGGER trg_ligas_init
AFTER INSERT ON ligas
FOR EACH ROW
EXECUTE FUNCTION trg_liga_init();


-- Incrementar al unirse un miembro
CREATE OR REPLACE FUNCTION trg_miembro_inc()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  UPDATE ligas_cupos
     SET miembros_actuales = miembros_actuales + 1,
         actualizado_en    = now()
   WHERE liga_id = NEW.liga_id;
  RETURN NEW;
END$$;

DROP TRIGGER IF EXISTS trg_lm_inc ON ligas_miembros;
CREATE TRIGGER trg_lm_inc
AFTER INSERT ON ligas_miembros
FOR EACH ROW
EXECUTE FUNCTION trg_miembro_inc();


-- Decrementar al eliminar un miembro
CREATE OR REPLACE FUNCTION trg_miembro_dec()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  UPDATE ligas_cupos
     SET miembros_actuales = GREATEST(miembros_actuales - 1, 0),
         actualizado_en    = now()
   WHERE liga_id = OLD.liga_id;
  RETURN OLD;
END$$;

DROP TRIGGER IF EXISTS trg_lm_dec ON ligas_miembros;
CREATE TRIGGER trg_lm_dec
AFTER DELETE ON ligas_miembros
FOR EACH ROW
EXECUTE FUNCTION trg_miembro_dec();


--VISTA
CREATE OR REPLACE VIEW ligas_cupos_vista AS
SELECT
  l.id,
  l.nombre,
  l.temporada_id,
  l.estado,
  l.cupo_equipos,
  c.miembros_actuales,
  (l.cupo_equipos - c.miembros_actuales) AS cupos_disponibles,
  c.actualizado_en
FROM ligas l
JOIN ligas_cupos c ON c.liga_id = l.id;



