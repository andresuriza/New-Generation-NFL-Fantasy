-- ============================================================================
-- NFL Fantasy League Database Creation Script
-- Generated from SQLAlchemy models
-- ============================================================================

-- Extensions required for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- ENUMS
-- ============================================================================

-- User role enum
CREATE TYPE rol_usuario_enum AS ENUM ('manager', 'administrador');

-- User state enum  
CREATE TYPE estado_usuario_enum AS ENUM ('activa', 'bloqueado', 'eliminada');

-- League state enum
CREATE TYPE estado_liga_enum AS ENUM ('Pre_draft', 'Draft');

-- Membership role enum
CREATE TYPE rol_membresia_enum AS ENUM ('Comisionado', 'Manager');

-- ============================================================================
-- TABLES
-- ============================================================================

-- Users table
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(50) NOT NULL,
    alias VARCHAR(50) NOT NULL,
    correo VARCHAR(50) NOT NULL UNIQUE,
    contrasena_hash TEXT NOT NULL,
    rol rol_usuario_enum NOT NULL DEFAULT 'manager',
    estado estado_usuario_enum NOT NULL DEFAULT 'activa',
    idioma VARCHAR(10) NOT NULL DEFAULT 'Ingles',
    imagen_perfil_url TEXT NOT NULL DEFAULT '/img/perfil/default.png',
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    creado_en TIMESTAMPTZ DEFAULT NOW()
);

-- Seasons table
CREATE TABLE temporadas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(100) NOT NULL UNIQUE,
    semanas INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    es_actual BOOLEAN NOT NULL DEFAULT FALSE,
    creado_en TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT check_semanas CHECK (semanas >= 1 AND semanas <= 17),
    CONSTRAINT ck_temp_rango CHECK (fecha_fin > fecha_inicio)
);

-- Season weeks table
CREATE TABLE temporadas_semanas (
    temporada_id UUID NOT NULL,
    numero INTEGER NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    
    PRIMARY KEY (temporada_id, numero),
    FOREIGN KEY (temporada_id) REFERENCES temporadas(id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT ck_sem_rango CHECK (fecha_fin > fecha_inicio)
);

-- Leagues table
CREATE TABLE ligas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    contrasena_hash TEXT NOT NULL,
    equipos_max SMALLINT NOT NULL,
    estado estado_liga_enum NOT NULL DEFAULT 'Pre_draft',
    temporada_id UUID NOT NULL,
    comisionado_id UUID NOT NULL,
    
    -- Configuration defaults
    playoffs_equipos SMALLINT NOT NULL DEFAULT 4,
    puntajes_decimales BOOLEAN NOT NULL DEFAULT TRUE,
    trade_deadline_activa BOOLEAN NOT NULL DEFAULT FALSE,
    limite_cambios_temp INTEGER,
    limite_agentes_temp INTEGER,
    
    -- JSONB configuration fields with defaults
    formato_posiciones JSONB NOT NULL DEFAULT '{"QB":1, "RB":2, "K":1, "DEF":1, "WR":2, "FLEX_RB_WR":1, "TE":1, "BANCA":6, "IR":3}'::jsonb,
    puntos_config JSONB NOT NULL DEFAULT '{"passing_yards_points_per_25_yards": 1, "passing_touchdown_points": 4, "interception_thrown_points": -2, "rushing_yards_points_per_10_yards": 1, "reception_points": 1, "receiving_yards_points_per_10_yards": 1, "rushing_or_receiving_touchdown_points": 6, "defense_sack_points": 1, "defense_interception_points": 2, "defense_fumble_recovered_points": 2, "defense_safety_points": 2, "defense_touchdown_points": 6, "team_defense_two_point_return_points": 2, "kicking_pat_made_points": 1, "field_goal_made_0_to_50_yards_points": 3, "field_goal_made_50_plus_yards_points": 5, "points_allowed_less_equal_10_points": 5, "points_allowed_less_equal_20_points": 2, "points_allowed_less_equal_30_points": 0, "points_allowed_greater_30_points": -2}'::jsonb,
    
    creado_en TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NOW(),
    
    -- Foreign Keys
    FOREIGN KEY (temporada_id) REFERENCES temporadas(id) ON DELETE RESTRICT,
    FOREIGN KEY (comisionado_id) REFERENCES usuarios(id) ON DELETE RESTRICT,
    
    -- Constraints
    CONSTRAINT ck_equipos_max CHECK (equipos_max IN (4,6,8,10,12,14,16,18,20)),
    CONSTRAINT ck_playoffs_equipos CHECK (playoffs_equipos IN (4,6)),
    CONSTRAINT ck_nombre_liga_len CHECK (length(nombre) BETWEEN 1 AND 100)
);

-- League members table
CREATE TABLE ligas_miembros (
    liga_id UUID NOT NULL,
    usuario_id UUID NOT NULL,
    alias VARCHAR(50) NOT NULL,
    rol rol_membresia_enum NOT NULL DEFAULT 'Manager',
    creado_en TIMESTAMPTZ DEFAULT NOW(),
    equipo_fantasy_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (liga_id, usuario_id),
    FOREIGN KEY (liga_id) REFERENCES ligas(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT uq_alias_por_liga UNIQUE (liga_id, alias),
    CONSTRAINT ck_alias_len CHECK (length(alias) BETWEEN 1 AND 50)
);

-- League members audit table
CREATE TABLE ligas_miembros_aud (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    liga_id UUID NOT NULL,
    usuario_id UUID NOT NULL,
    accion VARCHAR NOT NULL,
    creado_en TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (liga_id) REFERENCES ligas(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT ck_accion CHECK (accion IN ('unirse','salir'))
);

-- League quotas table
CREATE TABLE ligas_cupos (
    liga_id UUID PRIMARY KEY,
    miembros_actuales INTEGER NOT NULL DEFAULT 0,
    actualizado_en TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (liga_id) REFERENCES ligas(id) ON DELETE CASCADE,
    
    -- Constraints
    CONSTRAINT ck_miembros_no_negativos CHECK (miembros_actuales >= 0)
);

-- Teams table
CREATE TABLE equipos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    liga_id UUID NOT NULL,
    usuario_id UUID NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    thumbnail TEXT,
    creado_en TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (liga_id) REFERENCES ligas(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT
);


-- Media table
CREATE TABLE media (
    equipo_id UUID PRIMARY KEY,
    url TEXT NOT NULL,
    generado_en TIMESTAMPTZ DEFAULT NOW(),
    creado_en TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE
);

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
-- ============================================================================
-- INDEXES
-- ============================================================================

-- Unique index to ensure only one current season
CREATE UNIQUE INDEX uq_temporada_actual ON temporadas (es_actual) 
WHERE es_actual = TRUE;

-- Unique index to ensure only one comisionado per league
CREATE UNIQUE INDEX uq_unico_comisionado_por_liga ON ligas_miembros (liga_id) 
WHERE rol = 'Comisionado';

-- Performance indexes
CREATE INDEX idx_usuarios_correo ON usuarios(correo);
CREATE INDEX idx_usuarios_estado ON usuarios(estado);
CREATE INDEX idx_ligas_temporada ON ligas(temporada_id);
CREATE INDEX idx_ligas_comisionado ON ligas(comisionado_id);
CREATE INDEX idx_ligas_estado ON ligas(estado);
CREATE INDEX idx_equipos_liga ON equipos(liga_id);
CREATE INDEX idx_equipos_usuario ON equipos(usuario_id);
CREATE INDEX idx_miembros_liga ON ligas_miembros(liga_id);
CREATE INDEX idx_miembros_usuario ON ligas_miembros(usuario_id);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for tables with actualizado_en field
CREATE TRIGGER update_ligas_updated_at BEFORE UPDATE ON ligas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_equipos_updated_at BEFORE UPDATE ON equipos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SAMPLE DATA (Optional)
-- ============================================================================

-- Insert a default admin user
INSERT INTO usuarios (nombre, alias, correo, contrasena_hash, rol, idioma) VALUES
('Administrador', 'admin', 'admin@nflfantasy.com', '$2b$12$hashed_password_placeholder', 'administrador', 'en');

-- Insert a current season
INSERT INTO temporadas (nombre, semanas, fecha_inicio, fecha_fin, es_actual) VALUES
('NFL Season 2024', 17, '2024-09-01', '2024-12-31', TRUE);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE usuarios IS 'Users table containing all registered users';
COMMENT ON TABLE temporadas IS 'NFL seasons with their configuration';
COMMENT ON TABLE temporadas_semanas IS 'Individual weeks within each season';
COMMENT ON TABLE ligas IS 'Fantasy football leagues';
COMMENT ON TABLE ligas_miembros IS 'League membership table (users joined to leagues)';
COMMENT ON TABLE ligas_miembros_aud IS 'Audit trail for league membership changes';
COMMENT ON TABLE ligas_cupos IS 'League quotas tracking current members count';
COMMENT ON TABLE equipos IS 'Teams within leagues';
COMMENT ON TABLE ligas_equipos IS 'Relationship between leagues and teams';
COMMENT ON TABLE media IS 'Media files associated with teams';

COMMENT ON COLUMN ligas.equipos_max IS 'Maximum number of regular members (excludes comisionado)';
COMMENT ON COLUMN ligas.formato_posiciones IS 'JSONB configuration for team positions';
COMMENT ON COLUMN ligas.puntos_config IS 'JSONB configuration for scoring rules';
COMMENT ON INDEX uq_unico_comisionado_por_liga IS 'Ensures only one comisionado per league';

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

SELECT 'Database schema created successfully!' as result;

CREATE OR REPLACE FUNCTION agregar_comisionado_auto()
RETURNS TRIGGER AS $$
DECLARE
  v_alias TEXT;
BEGIN
  -- Tomamos el alias del usuario (o “Comisionado” si no hay)
  SELECT u.alias INTO v_alias
  FROM usuarios u
  WHERE u.id = NEW.comisionado_id;

  v_alias := COALESCE(NULLIF(v_alias, ''), 'Comisionado');

  -- Inserta membresía del comisionado (rol fijo)
  INSERT INTO ligas_miembros (liga_id, usuario_id, alias, rol)
  VALUES (NEW.id, NEW.comisionado_id, v_alias, 'Comisionado')
  ON CONFLICT DO NOTHING;

  -- Auditoría de incorporación
  INSERT INTO ligas_miembros_aud (liga_id, usuario_id, accion)
  VALUES (NEW.id, NEW.comisionado_id, 'unirse');

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Then create the trigger:
CREATE TRIGGER agregar_comisionado_auto_trigger
AFTER INSERT ON ligas
FOR EACH ROW
EXECUTE FUNCTION agregar_comisionado_auto();

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================