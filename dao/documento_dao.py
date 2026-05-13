import json
from conexion import Conexion
from entidades.documento import Documento


class DocumentoDAO:

    @classmethod
    def listar(cls, tipo=None):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            if tipo:
                cursor.execute("SELECT * FROM documentos WHERE tipo=%s ORDER BY created_at DESC", (tipo,))
            else:
                cursor.execute("SELECT * FROM documentos ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [Documento(**row) for row in rows]
        except Exception as e:
            print(f"❌ Error listar documentos: {e}")
            return []
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar(cls, documento):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO documentos (tipo, datos, pdf_ruta)
                              VALUES (%s, %s, %s)""",
                           (documento.tipo, json.dumps(documento.datos), documento.pdf_ruta))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error insertar documento: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener(cls, id):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM documentos WHERE id=%s", (id,))
            row = cursor.fetchone()
            return Documento(**row) if row else None
        except Exception as e:
            print(f"❌ Error obtener documento: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)