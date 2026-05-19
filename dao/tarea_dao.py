from conexion import Conexion
from entidades.tarea import Tarea


class TareaDAO:

    @classmethod
    def listar(cls, estado=None, usuario_id=None, busqueda=None):
        """Lista tareas con filtros opcionales"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)

            sql = """
                SELECT t.*, c.nombre as campana_nombre, u.nombre as usuario_nombre
                FROM tareas t
                LEFT JOIN campanas c ON t.campana_id = c.id
                LEFT JOIN usuarios u ON t.usuario_id = u.id
                WHERE 1=1
            """
            params = []

            if estado:
                sql += " AND t.estado = %s"
                params.append(estado)

            if usuario_id:
                sql += " AND t.usuario_id = %s"
                params.append(usuario_id)

            if busqueda:
                sql += " AND (t.titulo LIKE %s OR t.descripcion LIKE %s)"
                busqueda_param = f"%{busqueda}%"
                params.append(busqueda_param)
                params.append(busqueda_param)

            sql += " ORDER BY t.fecha_entrega ASC"

            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            return [Tarea(**row) for row in rows]
        except Exception as e:
            print(f"❌ Error listar tareas: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener(cls, id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.*, c.nombre as campana_nombre, u.nombre as usuario_nombre
                FROM tareas t
                LEFT JOIN campanas c ON t.campana_id = c.id
                LEFT JOIN usuarios u ON t.usuario_id = u.id
                WHERE t.id = %s
            """, (id,))
            row = cursor.fetchone()
            return Tarea(**row) if row else None
        except Exception as e:
            print(f"❌ Error obtener tarea: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar(cls, tarea):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            sql = """INSERT INTO tareas (titulo, descripcion, estado, prioridad, 
                     fecha_entrega, campana_id, usuario_id)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (tarea.titulo, tarea.descripcion, tarea.estado,
                                 tarea.prioridad, tarea.fecha_entrega,
                                 tarea.campana_id, tarea.usuario_id))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error insertar tarea: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar(cls, tarea):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            sql = """UPDATE tareas SET titulo=%s, descripcion=%s, estado=%s,
                     prioridad=%s, fecha_entrega=%s, campana_id=%s, usuario_id=%s
                     WHERE id=%s"""
            cursor.execute(sql, (tarea.titulo, tarea.descripcion, tarea.estado,
                                 tarea.prioridad, tarea.fecha_entrega,
                                 tarea.campana_id, tarea.usuario_id, tarea.id))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error actualizar tarea: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def postergar(cls, id, motivo, nueva_fecha):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            if Conexion.es_postgres():
                sql = """UPDATE tareas
                         SET estado = 'postergada',
                             fecha_entrega = %s,
                             postergaciones = COALESCE(postergaciones, '[]'::jsonb) ||
                                jsonb_build_array(
                                    jsonb_build_object('motivo', %s, 'fecha', NOW())
                                )
                         WHERE id = %s"""
                cursor.execute(sql, (nueva_fecha, motivo, id))
            else:
                sql = """UPDATE tareas
                         SET estado = 'postergada',
                             fecha_entrega = %s,
                             postergaciones = JSON_ARRAY_APPEND(
                                 COALESCE(postergaciones, JSON_ARRAY()),
                                 '$',
                                 JSON_OBJECT('motivo', %s, 'fecha', NOW())
                             )
                         WHERE id = %s"""
                cursor.execute(sql, (nueva_fecha, motivo, id))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error postergar tarea: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def eliminar(cls, id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tareas WHERE id = %s", (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error eliminar tarea: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def cambiar_estado(cls, id, estado):
        """Cambia el estado de una tarea"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE tareas SET estado = %s WHERE id = %s", (estado, id))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error cambiar estado: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)
