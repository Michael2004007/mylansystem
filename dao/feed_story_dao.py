import mimetypes
from conexion import Conexion


class FeedStoryDAO:

    @classmethod
    def listar(cls, anio=None, mes=None, semana=None, dia_semana=None, tipo=None):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT fs.*, u.nombre AS responsable_nombre
                FROM feed_stories fs
                LEFT JOIN usuarios u ON u.id = fs.responsable_id
                WHERE 1=1
            """
            params = []
            if anio:
                sql += " AND YEAR(fs.fecha_publicacion) = %s"
                params.append(anio)
            if mes:
                sql += " AND MONTH(fs.fecha_publicacion) = %s"
                params.append(mes)
            if semana:
                sql += " AND WEEK(fs.fecha_publicacion, 1) = %s"
                params.append(semana)
            if dia_semana is not None:
                sql += " AND WEEKDAY(fs.fecha_publicacion) = %s"
                params.append(dia_semana)
            if tipo:
                sql += " AND fs.tipo = %s"
                params.append(tipo)
            sql += " ORDER BY fs.fecha_publicacion DESC, fs.hora_publicacion DESC, fs.id DESC"
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            for r in rows:
                nombre = (r.get('archivo_nombre') or '').lower()
                r['is_video'] = nombre.endswith(('.mp4', '.mov', '.avi', '.m4v', '.webm'))
                r['mime_type'] = mimetypes.guess_type(r.get('archivo_nombre') or '')[0] or ''
            return rows
        except Exception as e:
            print(f"Error listar feed/stories: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def listar_hoy(cls):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT fs.*, u.nombre AS responsable_nombre
                FROM feed_stories fs
                LEFT JOIN usuarios u ON u.id = fs.responsable_id
                WHERE fs.fecha_publicacion = CURDATE()
                ORDER BY fs.hora_publicacion, fs.id
                """
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error listar contenidos de hoy: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener(cls, contenido_id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM feed_stories WHERE id=%s", (contenido_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error obtener contenido: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar(cls, tipo, fecha_publicacion, hora_publicacion, copy_texto, archivo_nombre, archivo_ruta, responsable_id, observacion=None):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO feed_stories
                (tipo, fecha_publicacion, hora_publicacion, copy_texto, archivo_nombre, archivo_ruta, responsable_id, observacion, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pendiente')
                """,
                (tipo, fecha_publicacion, hora_publicacion, copy_texto, archivo_nombre, archivo_ruta, responsable_id, observacion)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error insertar contenido: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def marcar_publicado(cls, contenido_id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE feed_stories SET estado='publicado' WHERE id=%s", (contenido_id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error marcar publicado: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar_observacion(cls, contenido_id, observacion):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE feed_stories SET observacion=%s WHERE id=%s", (observacion, contenido_id))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error actualizar observación: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar_detalle(cls, contenido_id, hora_publicacion, copy_texto, responsable_id, observacion):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE feed_stories
                SET hora_publicacion=%s,
                    copy_texto=%s,
                    responsable_id=%s,
                    observacion=%s
                WHERE id=%s
                """,
                (hora_publicacion, copy_texto, responsable_id, observacion, contenido_id)
            )
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error actualizar detalle de contenido: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)
