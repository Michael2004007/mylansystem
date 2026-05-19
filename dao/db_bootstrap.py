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
            CREATE TABLE IF NOT EXISTS carpetas (
              id INT AUTO_INCREMENT PRIMARY KEY,
              nombre VARCHAR(120) NOT NULL,
              tipo VARCHAR(40) NOT NULL,
              parent_id INT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              INDEX idx_carpetas_tipo (tipo),
              INDEX idx_carpetas_parent (parent_id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS archivos (
              id INT AUTO_INCREMENT PRIMARY KEY,
              carpeta_id INT NOT NULL,
              nombre VARCHAR(255) NOT NULL,
              tipo VARCHAR(30) NOT NULL,
              ruta VARCHAR(500) NOT NULL,
              tamano_kb INT DEFAULT 0,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              INDEX idx_archivos_carpeta (carpeta_id)
            )
            """
        )

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

        cursor.execute(
            """
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
            )
            """
        )

        cursor.execute(
            """
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
