CREATE OR REPLACE FUNCTION registrar_usuario(
  p_nombre        TEXT,
  p_alias         TEXT,
  p_correo        TEXT,
  p_contrasena    TEXT,
  p_idioma        TEXT DEFAULT 'Ingles',
  p_imagen_url    TEXT DEFAULT '/img/perfil/default.png',
  p_rol           rol_usuario DEFAULT 'manager'
) RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
  v_id UUID;
BEGIN
  -- Inserta; si el correo ya existe (UNIQUE), no lanza excepción: retorna NULL
  WITH ins AS (
    INSERT INTO usuarios (
      nombre, alias, correo, contrasena_hash, rol, estado, idioma, imagen_perfil_url
    ) VALUES (
      p_nombre,
      p_alias,
      p_correo,
      crypt(p_contrasena, gen_salt('bf')),  -- bcrypt (Blowfish)
      COALESCE(p_rol, 'manager'),
      'activa',
      COALESCE(p_idioma, 'Ingles'),
      COALESCE(p_imagen_url, '/img/perfil/default.png')
    )
    ON CONFLICT (correo) DO NOTHING
    RETURNING id
  )
  SELECT id INTO v_id FROM ins;

  RETURN v_id;  -- NULL si ya existía el correo
END;
$$;


CREATE OR REPLACE FUNCTION verificar_login_simple(
  p_correo      TEXT,
  p_contrasena  TEXT
) RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
  v_id     UUID;
  v_hash   TEXT;
  v_estado estado_usuario;
BEGIN
  SELECT id, contrasena_hash, estado
    INTO v_id, v_hash, v_estado
  FROM usuarios
  WHERE correo = p_correo;

  IF NOT FOUND THEN
    RETURN NULL; -- no existe el correo
  END IF;

  -- compara usando el hash como "salt"
  IF v_hash <> crypt(p_contrasena, v_hash) THEN
    RETURN NULL; -- contraseña incorrecta
  END IF;

  -- opcional mínimo: exigir cuenta activa
  IF v_estado <> 'activa' THEN
    RETURN NULL;
  END IF;

  RETURN v_id; -- éxito
END;
$$;

CREATE OR REPLACE FUNCTION bloquear_usuario(
  p_usuario_id UUID
) RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
  v_actual TEXT;
BEGIN
  -- obtener el estado actual (por claridad, aunque se puede omitir)
  SELECT estado INTO v_actual FROM usuarios WHERE id = p_usuario_id;

  IF NOT FOUND THEN
    RETURN FALSE; -- usuario no existe
  END IF;

  -- solo cambia si está activa
  UPDATE usuarios
     SET estado = 'bloqueado'
   WHERE id = p_usuario_id AND estado = 'activa';

  IF FOUND THEN
    RETURN TRUE;  -- éxito: estado cambiado
  ELSE
    RETURN FALSE; -- ya estaba suspendida/eliminada
  END IF;
END;
$$;

