CREATE TABLE IF NOT EXISTS ideas_campana (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(180) NOT NULL,
  descripcion TEXT NULL,
  estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
  campana_id INT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_ideas_estado (estado)
);

CREATE TABLE IF NOT EXISTS idea_colaboraciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  idea_id INT NOT NULL,
  influencer_id INT NOT NULL,
  detalle TEXT NULL,
  monto DECIMAL(12,2) DEFAULT 0,
  fecha_entrega DATE NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_idea_colab_idea (idea_id),
  CONSTRAINT fk_idea_colab_idea
    FOREIGN KEY (idea_id) REFERENCES ideas_campana(id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS idea_hitos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  idea_id INT NOT NULL,
  titulo VARCHAR(180) NOT NULL,
  descripcion TEXT NULL,
  lugar VARCHAR(180) NULL,
  fecha_hora DATETIME NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_idea_hito_idea (idea_id),
  CONSTRAINT fk_idea_hito_idea
    FOREIGN KEY (idea_id) REFERENCES ideas_campana(id)
    ON DELETE CASCADE
);
