from conexion import Conexion
from entidades.permiso import Permiso


class PermisoDAO:

    @classmethod
    def obtener_permisos_usuario(cls, usuario_id):
        """Obtiene todos los permisos de un usuario"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM permisos_usuario 
                WHERE usuario_id = %s
            """, (usuario_id,))
            rows = cursor.fetchall()
            return [Permiso(**row) for row in rows]
        except Exception as e:
            print(f"❌ Error obtener permisos: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def tiene_permiso(cls, usuario_id, modulo, requiere_editar=False, requiere_aprobar=False):
        """Verifica si un usuario tiene permiso en un módulo"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)

            if requiere_aprobar:
                cursor.execute("""
                    SELECT puede_aprobar FROM permisos_usuario 
                    WHERE usuario_id = %s AND modulo = %s
                """, (usuario_id, modulo))
            elif requiere_editar:
                cursor.execute("""
                    SELECT puede_editar FROM permisos_usuario 
                    WHERE usuario_id = %s AND modulo = %s
                """, (usuario_id, modulo))
            else:
                cursor.execute("""
                    SELECT puede_ver FROM permisos_usuario 
                    WHERE usuario_id = %s AND modulo = %s
                """, (usuario_id, modulo))

            row = cursor.fetchone()
            if not row:
                return False

            if requiere_aprobar:
                return row.get('puede_aprobar', False)
            return row.get('puede_editar' if requiere_editar else 'puede_ver', False)
        except Exception as e:
            print(f"❌ Error verificar permiso: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def asignar_permiso(cls, usuario_id, modulo, puede_ver=True, puede_editar=False, puede_aprobar=False):
        """Asigna o actualiza un permiso"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            if Conexion.es_postgres():
                cursor.execute("""
                    INSERT INTO permisos_usuario (usuario_id, modulo, puede_ver, puede_editar, puede_aprobar)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (usuario_id, modulo) DO UPDATE SET
                        puede_ver = EXCLUDED.puede_ver,
                        puede_editar = EXCLUDED.puede_editar,
                        puede_aprobar = EXCLUDED.puede_aprobar
                """, (usuario_id, modulo, puede_ver, puede_editar, puede_aprobar))
            else:
                cursor.execute("""
                    INSERT INTO permisos_usuario (usuario_id, modulo, puede_ver, puede_editar, puede_aprobar)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        puede_ver = VALUES(puede_ver),
                        puede_editar = VALUES(puede_editar),
                        puede_aprobar = VALUES(puede_aprobar)
                """, (usuario_id, modulo, puede_ver, puede_editar, puede_aprobar))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error asignar permiso: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def eliminar_permisos_usuario(cls, usuario_id):
        """Elimina todos los permisos de un usuario"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM permisos_usuario WHERE usuario_id = %s", (usuario_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error eliminar permisos: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def asignar_todos_permisos(cls, usuario_id):
        """Asigna todos los permisos (admin completo)"""
        modulos = ['inicio', 'tareas', 'campanas', 'ideas_campanas', 'calendario', 'influencers',
                   'ecommerce', 'contenidos', 'feed_stories', 'ideas_feed_stories', 'reportes', 'usuarios']

        for modulo in modulos:
            cls.asignar_permiso(usuario_id, modulo, puede_ver=True, puede_editar=True, puede_aprobar=True)

        return True
