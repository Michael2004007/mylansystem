from conexion import Conexion
from entidades.archivo import Archivo


class ArchivoDAO:

    @classmethod
    def listar_por_carpeta(cls, carpeta_id):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM archivos WHERE carpeta_id=%s ORDER BY created_at DESC", (carpeta_id,))
            rows = cursor.fetchall()
            return [Archivo(**row) for row in rows]
        except Exception as e:
            print(f"❌ Error listar archivos: {e}")
            return []
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar(cls, archivo):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO archivos (carpeta_id, nombre, tipo, ruta, tamano_kb)
                              VALUES (%s, %s, %s, %s, %s)""",
                           (archivo.carpeta_id, archivo.nombre, archivo.tipo,
                            archivo.ruta, archivo.tamano_kb))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error insertar archivo: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def eliminar(cls, id):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM archivos WHERE id = %s", (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error eliminar archivo: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener(cls, id):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM archivos WHERE id=%s", (id,))
            row = cursor.fetchone()
            return Archivo(**row) if row else None
        except Exception as e:
            print(f"❌ Error obtener archivo: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar_ruta(cls, id, ruta):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE archivos SET ruta=%s WHERE id=%s", (ruta, id))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error actualizar ruta archivo: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def crear_carpeta(cls, nombre, tipo, parent_id=None):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO carpetas (nombre, tipo, parent_id) VALUES (%s, %s, %s)",
                (nombre, tipo, parent_id)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error crear carpeta: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def listar_carpetas(cls, tipo=None):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            if tipo:
                cursor.execute("SELECT * FROM carpetas WHERE tipo=%s AND parent_id IS NULL", (tipo,))
            else:
                cursor.execute("SELECT * FROM carpetas WHERE parent_id IS NULL")
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error listar carpetas: {e}")
            return []
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def listar_subcarpetas(cls, parent_id):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM carpetas WHERE parent_id=%s ORDER BY nombre",
                (parent_id,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error listar subcarpetas: {e}")
            return []
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener_carpeta(cls, carpeta_id):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM carpetas WHERE id=%s", (carpeta_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"❌ Error obtener carpeta: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)
