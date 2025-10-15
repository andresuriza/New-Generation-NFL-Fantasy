CREATE TABLE media (
  equipo_id    UUID PRIMARY KEY REFERENCES equipos(id) ON DELETE CASCADE,     
  url          TEXT NOT NULL,                               -- URL de la imagen
  generado_en  TIMESTAMPTZ DEFAULT now(),
  creado_en    TIMESTAMPTZ NOT NULL DEFAULT now()
);

