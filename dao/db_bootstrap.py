from conexion import Conexion


def bootstrap_schema():
    conn = None
    cursor = None
    try:
        conn = Conexion.obtener_conexion()
        if not conn:
            return
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ideas_campana (
              id INT AUTO_INCREMENT PRIMARY KEY,
              nombre VARCHAR(180) NOT NULL,
              descripcion TEXT NULL,
              estado VARCHAR(20) NOT NULL DEFAULT 'borrador',
              campana_id INT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              INDEX idx_ideas_estado (estado)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS idea_colaboraciones (
              id INT AUTO_INCREMENT PRIMARY KEY,
              idea_id INT NOT NULL,
              influencer_id INT NOT NULL,
              detalle TEXT NULL,
              monto DECIMAL(12,2) DEFAULT 0,
              fecha_entrega DATE NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              INDEX idx_idea_colab_idea (idea_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS idea_hitos (
              id INT AUTO_INCREMENT PRIMARY KEY,
              idea_id INT NOT NULL,
              titulo VARCHAR(180) NOT NULL,
              descripcion TEXT NULL,
              lugar VARCHAR(180) NULL,
              fecha_hora DATETIME NOT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              INDEX idx_idea_hito_idea (idea_id)
            )
            """
        )

        cursor.execute("SHOW COLUMNS FROM permisos_usuario LIKE 'puede_aprobar'")
        if not cursor.fetchone():
            cursor.execute(
                "ALTER TABLE permisos_usuario ADD COLUMN puede_aprobar TINYINT(1) NOT NULL DEFAULT 0"
            )

        conn.commit()
        print("Schema bootstrap OK")
    except Exception as e:
        print(f"Schema bootstrap error: {e}")
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        Conexion.liberar_conexion(conn)
