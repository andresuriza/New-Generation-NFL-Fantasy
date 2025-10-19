CREATE EXTENSION IF NOT EXISTS pgcrypto;

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


