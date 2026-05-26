from conexion import Conexion


class CalendarioDAO:

    @classmethod
    def listar_por_mes(cls, mes, anio):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            if Conexion.es_postgres():
                cursor.execute("""SELECT * FROM cal_eventos
                                  WHERE EXTRACT(MONTH FROM fecha)=%s
                                    AND EXTRACT(YEAR FROM fecha)=%s
                                  ORDER BY fecha""", (mes, anio))
            else:
                cursor.execute("""SELECT * FROM cal_eventos
                                  WHERE MONTH(fecha)=%s AND YEAR(fecha)=%s
                                  ORDER BY fecha""", (mes, anio))
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error listar eventos: {e}")
            return []
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def listar_anio(cls, anio):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            if Conexion.es_postgres():
                cursor.execute("""SELECT * FROM cal_eventos
                                  WHERE EXTRACT(YEAR FROM fecha)=%s
                                  ORDER BY fecha""", (anio,))
            else:
                cursor.execute("""SELECT * FROM cal_eventos
                                  WHERE YEAR(fecha)=%s
                                  ORDER BY fecha""", (anio,))
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error listar eventos año: {e}")
            return []
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def listar_destacados(cls, anio):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            if Conexion.es_postgres():
                cursor.execute("""SELECT * FROM cal_eventos
                                  WHERE destacado IS TRUE
                                    AND EXTRACT(YEAR FROM fecha)=%s
                                  ORDER BY fecha""", (anio,))
            else:
                cursor.execute("""SELECT * FROM cal_eventos
                                  WHERE destacado=1 AND YEAR(fecha)=%s
                                  ORDER BY fecha""", (anio,))
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error listar destacados: {e}")
            return []
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar(cls, nombre, fecha, tipo, accion_sugerida=None, campana_id=None, destacado=0, color=None):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            if Conexion.es_postgres():
                destacado = bool(destacado)
            cursor.execute("""INSERT INTO cal_eventos (nombre, fecha, tipo, accion_sugerida, campana_id, destacado, color)
                              VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                           (nombre, fecha, tipo, accion_sugerida, campana_id, destacado, color))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ Error insertar evento: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar(cls, id, nombre, fecha, tipo, accion_sugerida=None, campana_id=None):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("""UPDATE cal_eventos
                              SET nombre=%s, fecha=%s, tipo=%s, accion_sugerida=%s, campana_id=%s
                              WHERE id=%s""",
                           (nombre, fecha, tipo, accion_sugerida, campana_id, id))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error actualizar evento: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def eliminar(cls, id):
        conn = None
        try:
            conn   = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cal_eventos WHERE id = %s", (id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ Error eliminar evento: {e}")
            return None
        finally:
            Conexion.liberar_conexion(conn)
