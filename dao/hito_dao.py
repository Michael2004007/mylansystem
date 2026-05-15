from conexion import Conexion
from entidades.hito import Hito
import json
from datetime import datetime


class HitoDAO:

    @classmethod
    def listar_por_campana(cls, campana_id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM hitos_campana WHERE campana_id = %s ORDER BY fecha_hora",
                (campana_id,)
            )
            rows = cursor.fetchall()
            hitos = []
            for row in rows:
                # Parsear el historial JSON si existe
                if row.get('historial_postergaciones'):
                    try:
                        row['historial_postergaciones'] = json.loads(row['historial_postergaciones'])
                    except:
                        row['historial_postergaciones'] = []
                else:
                    row['historial_postergaciones'] = []
                hitos.append(Hito(**row))
            return hitos
        except Exception as e:
            print(f"❌ Error listar hitos: {e}")
            return []
        finally:
            if cursor: cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener(cls, id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM hitos_campana WHERE id = %s", (id,))
            row = cursor.fetchone()
            if row:
                # Parsear el historial JSON si existe
                if row.get('historial_postergaciones'):
                    try:
                        row['historial_postergaciones'] = json.loads(row['historial_postergaciones'])
                    except:
                        row['historial_postergaciones'] = []
                else:
                    row['historial_postergaciones'] = []
                return Hito(**row)
            return None
        except Exception as e:
            print(f"❌ Error obtener hito: {e}")
            return None
        finally:
            if cursor: cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar(cls, hito):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            sql = """INSERT INTO hitos_campana
                     (campana_id, titulo, descripcion, lugar, fecha_hora, estado)
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (
                hito.campana_id, hito.titulo, hito.descripcion,
                hito.lugar, hito.fecha_hora, hito.estado
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error insertar hito: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def marcar_hecho(cls, id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("UPDATE hitos_campana SET estado='hecho' WHERE id=%s", (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error marcar hito hecho: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def postergar(cls, id, nueva_fecha, motivo):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)

            # 1. Obtener el hito actual con su fecha e historial
            cursor.execute(
                "SELECT fecha_hora, historial_postergaciones FROM hitos_campana WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            fecha_anterior = row['fecha_hora']
            historial_json = row['historial_postergaciones']

            # 2. Parsear el historial existente
            if historial_json:
                try:
                    historial = json.loads(historial_json)
                except:
                    historial = []
            else:
                historial = []

            # 3. Agregar la nueva postergación al historial
            historial.append({
                'fecha_anterior': str(fecha_anterior),
                'fecha_nueva': nueva_fecha,
                'motivo': motivo,
                'fecha_postergacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            # 4. Actualizar el hito con la nueva fecha, estado postergado y el historial
            sql = """UPDATE hitos_campana
                     SET fecha_hora = %s,
                         estado = 'postergado',
                         historial_postergaciones = %s
                     WHERE id = %s"""
            cursor.execute(sql, (nueva_fecha, json.dumps(historial), id))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error postergar hito: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            Conexion.liberar_conexion(conn)

    @classmethod
    def eliminar(cls, id):
        conn = None
        cursor = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM hitos_campana WHERE id=%s", (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error eliminar hito: {e}")
            if conn: conn.rollback()
            return None
        finally:
            if cursor: cursor.close()
            Conexion.liberar_conexion(conn)