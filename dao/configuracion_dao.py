from conexion import Conexion


class ConfiguracionDAO:

    @classmethod
    def obtener(cls, clave):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT valor FROM configuracion WHERE clave = %s", (clave,))
            row = cursor.fetchone()
            return row['valor'] if row else None
        except Exception as e:
            print(f"❌ Error obtener config: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar(cls, clave, valor):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            if Conexion.es_postgres():
                cursor.execute("""INSERT INTO configuracion (clave, valor)
                                  VALUES (%s, %s)
                                  ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor""",
                               (clave, valor))
            else:
                cursor.execute("""INSERT INTO configuracion (clave, valor)
                                  VALUES (%s, %s)
                                  ON DUPLICATE KEY UPDATE valor = %s""",
                               (clave, valor, valor))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error actualizar config: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener_logo(cls):
        """Obtiene la ruta del logo desde la configuración"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("SELECT valor FROM configuracion WHERE clave = 'logo_ruta' LIMIT 1")
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(f"❌ Error obtener logo: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)
