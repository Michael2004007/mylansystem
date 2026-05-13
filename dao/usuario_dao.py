from conexion import Conexion
from entidades.usuario import Usuario
from werkzeug.security import generate_password_hash, check_password_hash


class UsuarioDAO:

    @classmethod
    def listar(cls):
        """Obtiene todos los usuarios"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios ORDER BY nombre")
            rows = cursor.fetchall()
            return [Usuario(**row) for row in rows]
        except Exception as e:
            print(f"❌ Error listar usuarios: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener(cls, id):
        """Obtiene un usuario por ID"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
            row = cursor.fetchone()
            return Usuario(**row) if row else None
        except Exception as e:
            print(f"❌ Error obtener usuario: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener_por_email(cls, email):
        """Obtiene un usuario por email"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            row = cursor.fetchone()
            return Usuario(**row) if row else None
        except Exception as e:
            print(f"❌ Error obtener usuario por email: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar(cls, usuario, password_plano):
        """Inserta un nuevo usuario con contraseña hasheada"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()

            password_hash = generate_password_hash(password_plano)

            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password_hash, rol, activo)
                VALUES (%s, %s, %s, %s, %s)
            """, (usuario.nombre, usuario.email, password_hash, usuario.rol, usuario.activo))

            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error insertar usuario: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar(cls, usuario, password_plano=None):
        """Actualiza un usuario (con o sin cambio de contraseña)"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()

            if password_plano:
                password_hash = generate_password_hash(password_plano)
                cursor.execute("""
                    UPDATE usuarios 
                    SET nombre=%s, email=%s, password_hash=%s, rol=%s, activo=%s
                    WHERE id=%s
                """, (usuario.nombre, usuario.email, password_hash, usuario.rol, usuario.activo, usuario.id))
            else:
                cursor.execute("""
                    UPDATE usuarios 
                    SET nombre=%s, email=%s, rol=%s, activo=%s
                    WHERE id=%s
                """, (usuario.nombre, usuario.email, usuario.rol, usuario.activo, usuario.id))

            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error actualizar usuario: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def eliminar(cls, id):
        """Elimina un usuario"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error eliminar usuario: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def verificar_password(cls, usuario, password_plano):
        """Verifica si la contraseña es correcta"""
        try:
            return check_password_hash(usuario.password_hash, password_plano)
        except Exception as e:
            print(f"❌ Error verificar password: {e}")
            return False

    @classmethod
    def existe_email(cls, email, excluir_id=None):
        """Verifica si un email ya existe (útil para validación)"""
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()

            if excluir_id:
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s AND id != %s",
                               (email, excluir_id))
            else:
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s", (email,))

            count = cursor.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"❌ Error verificar email: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            Conexion.liberar_conexion(conn)