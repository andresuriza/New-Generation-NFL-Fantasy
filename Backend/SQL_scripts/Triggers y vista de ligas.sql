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
