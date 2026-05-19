from conexion import Conexion


class IdeaCampanaDAO:

    @classmethod
    def listar(cls):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM ideas_campana ORDER BY created_at DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error listar ideas: {e}")
            return []
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener(cls, idea_id):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM ideas_campana WHERE id=%s", (idea_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error obtener idea: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar(cls, nombre, descripcion):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ideas_campana (nombre, descripcion, estado) VALUES (%s, %s, 'borrador')",
                (nombre, descripcion)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error insertar idea: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar(cls, idea_id, nombre, descripcion):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE ideas_campana SET nombre=%s, descripcion=%s WHERE id=%s",
                (nombre, descripcion, idea_id)
            )
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error actualizar idea: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def eliminar(cls, idea_id):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ideas_campana WHERE id=%s", (idea_id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error eliminar idea: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def listar_colaboraciones(cls, idea_id):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT ic.*, i.nombre AS influencer_nombre, i.handle AS influencer_handle
                FROM idea_colaboraciones ic
                LEFT JOIN influencers i ON i.id = ic.influencer_id
                WHERE ic.idea_id=%s
                ORDER BY ic.id DESC
                """,
                (idea_id,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error listar colaboraciones de idea: {e}")
            return []
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def agregar_colaboracion(cls, idea_id, influencer_id, detalle, monto, fecha_entrega):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO idea_colaboraciones (idea_id, influencer_id, detalle, monto, fecha_entrega)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (idea_id, influencer_id, detalle, monto, fecha_entrega)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error agregar colaboración idea: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def listar_hitos(cls, idea_id):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM idea_hitos WHERE idea_id=%s ORDER BY fecha_hora",
                (idea_id,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error listar hitos idea: {e}")
            return []
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def agregar_hito(cls, idea_id, titulo, descripcion, lugar, fecha_hora):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO idea_hitos (idea_id, titulo, descripcion, lugar, fecha_hora)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (idea_id, titulo, descripcion, lugar, fecha_hora)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error agregar hito idea: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def marcar_activada(cls, idea_id, campana_id):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE ideas_campana SET estado='activada', campana_id=%s WHERE id=%s",
                (campana_id, idea_id)
            )
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error marcar idea activada: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)
