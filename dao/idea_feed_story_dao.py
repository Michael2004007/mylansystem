from conexion import Conexion


class IdeaFeedStoryDAO:

    @classmethod
    def listar(cls, anio=None, mes=None):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT i.*, u.nombre AS responsable_nombre
                FROM ideas_feed_stories i
                LEFT JOIN usuarios u ON u.id = i.responsable_id
                WHERE 1=1
            """
            params = []
            if anio:
                sql += " AND i.anio = %s"
                params.append(anio)
            if mes:
                sql += " AND i.mes = %s"
                params.append(mes)
            sql += " ORDER BY i.anio DESC, i.mes DESC, i.id DESC"
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error listar ideas feed/stories: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar(cls, tipo, titulo, detalle, copy_texto, mes, anio, agrupador, responsable_id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO ideas_feed_stories
                (tipo, titulo, detalle, copy_texto, mes, anio, agrupador, responsable_id, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'idea')
                """,
                (tipo, titulo, detalle, copy_texto, mes, anio, agrupador, responsable_id)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error insertar idea feed/story: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def marcar_pasada(cls, idea_id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE ideas_feed_stories SET estado='pasada' WHERE id=%s", (idea_id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error marcar idea pasada: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)
