CREATE TABLE IF NOT EXISTS feed_stories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tipo VARCHAR(20) NOT NULL,
  fecha_publicacion DATE NOT NULL,
  hora_publicacion TIME NOT NULL,
  copy_texto TEXT NULL,
  archivo_nombre VARCHAR(255) NOT NULL,
  archivo_ruta VARCHAR(500) NOT NULL,
  responsable_id INT NULL,
  observacion TEXT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_feed_fecha (fecha_publicacion),
  INDEX idx_feed_tipo (tipo)
);

CREATE TABLE IF NOT EXISTS ideas_feed_stories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tipo VARCHAR(20) NOT NULL,
  titulo VARCHAR(180) NOT NULL,
  detalle TEXT NULL,
  copy_texto TEXT NULL,
  mes INT NOT NULL,
  anio INT NOT NULL,
  agrupador VARCHAR(180) NULL,
  responsable_id INT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'idea',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_ideas_feed_mes (anio, mes)
);
