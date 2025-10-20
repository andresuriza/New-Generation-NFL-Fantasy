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


