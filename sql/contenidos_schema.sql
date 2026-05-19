CREATE TABLE IF NOT EXISTS carpetas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(120) NOT NULL,
  tipo VARCHAR(40) NOT NULL,
  parent_id INT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_carpetas_tipo (tipo),
  INDEX idx_carpetas_parent (parent_id),
  CONSTRAINT fk_carpetas_parent
    FOREIGN KEY (parent_id) REFERENCES carpetas(id)
    ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS archivos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  carpeta_id INT NOT NULL,
  nombre VARCHAR(255) NOT NULL,
  tipo VARCHAR(30) NOT NULL,
  ruta VARCHAR(500) NOT NULL,
  tamano_kb INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_archivos_carpeta (carpeta_id),
  CONSTRAINT fk_archivos_carpeta
    FOREIGN KEY (carpeta_id) REFERENCES carpetas(id)
    ON DELETE CASCADE
);
