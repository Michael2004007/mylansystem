from conexion import Conexion
from entidades.campana import Campana


class CampanaDAO:

    @classmethod
    def listar(cls):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM campanas ORDER BY anio, mes")
            rows = cursor.fetchall()
            return [Campana(**row) for row in rows]
        except Exception as e:
            print(f"❌ Error listar campañas: {e}")
            return []
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener(cls, id):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM campanas WHERE id = %s", (id,))
            row = cursor.fetchone()
            return Campana(**row) if row else None
        except Exception as e:
            print(f"❌ Error obtener campaña: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar(cls, campana):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            sql = """INSERT INTO campanas
                     (nombre, mes, anio, presupuesto, gastado, descripcion, fecha_inicio, fecha_fin, status)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                campana.nombre, campana.mes, campana.anio,
                campana.presupuesto, campana.gastado, campana.descripcion,
                campana.fecha_inicio, campana.fecha_fin, campana.status
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error insertar campaña: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar(cls, campana):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            sql = """UPDATE campanas SET nombre=%s, mes=%s, anio=%s,
                     presupuesto=%s, descripcion=%s,
                     fecha_inicio=%s, fecha_fin=%s, status=%s
                     WHERE id=%s"""
            cursor.execute(sql, (
                campana.nombre, campana.mes, campana.anio,
                campana.presupuesto, campana.descripcion,
                campana.fecha_inicio, campana.fecha_fin,
                campana.status, campana.id
            ))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error actualizar campaña: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def completar(cls, id):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE campanas SET status='completada' WHERE id=%s", (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error completar campaña: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar_gasto(cls, id, monto):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE campanas SET gastado = gastado + %s WHERE id = %s", (monto, id))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error actualizar gasto campaña: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def eliminar(cls, id):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM campanas WHERE id = %s", (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error eliminar campaña: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)