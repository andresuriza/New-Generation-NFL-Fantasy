CREATE OR REPLACE FUNCTION crear_equipo_y_media_simple(
  p_liga_id    UUID,
  p_usuario_id UUID,
  p_nombre     TEXT,
  p_url        TEXT DEFAULT NULL
) RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
  v_equipo_id UUID;
BEGIN
  -- 1) Crear equipo; si hay conflicto de unicidad, retorna NULL sin excepción
  WITH ins AS (
    INSERT INTO equipos (liga_id, usuario_id, nombre)
    VALUES (p_liga_id, p_usuario_id, p_nombre)
    ON CONFLICT ON CONSTRAINT uq_equipo_nombre_por_liga DO NOTHING
    RETURNING id
  ), ins2 AS (
    -- si no chocó por nombre, intentamos también evitar choque por usuario/liga
    SELECT id FROM ins
    UNION ALL
    SELECT id FROM (
      INSERT INTO equipos (liga_id, usuario_id, nombre)
      VALUES (p_liga_id, p_usuario_id, p_nombre)
      ON CONFLICT ON CONSTRAINT uq_usuario_por_liga DO NOTHING
      RETURNING id
    ) z
  )
  SELECT id INTO v_equipo_id FROM ins2 LIMIT 1;

  -- Si no se pudo insertar por algún UNIQUE, devolvemos NULL
  IF v_equipo_id IS NULL THEN
    RETURN NULL;
  END IF;

  -- 2) (Opcional) Crear/actualizar imagen 1:1 si se envía URL
  IF p_url IS NOT NULL THEN
    INSERT INTO media (equipo_id, url, generado_en)
    VALUES (v_equipo_id, p_url, now())
    ON CONFLICT (equipo_id) DO UPDATE
      SET url = EXCLUDED.url,
          generado_en = now();
  END IF;

  RETURN v_equipo_id;
END;
$$;
