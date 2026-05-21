from conexion import Conexion
import logging


class EcommerceDAO:

    @classmethod
    def listar_ventas(cls, mes=None, anio=None):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            if mes and anio:
                cursor.execute("""SELECT v.*,
                                         COALESCE(i.nombre, 'Orgánico') as influencer_nombre
                                  FROM ecom_ventas v
                                  LEFT JOIN influencers i ON v.influencer_id = i.id
                                  WHERE v.mes=%s AND v.anio=%s
                                  ORDER BY v.fecha DESC, v.monto DESC""", (mes, anio))
            else:
                cursor.execute("""SELECT v.*,
                                         COALESCE(i.nombre, 'Orgánico') as influencer_nombre
                                  FROM ecom_ventas v
                                  LEFT JOIN influencers i ON v.influencer_id = i.id
                                  ORDER BY v.anio DESC, v.mes DESC, v.fecha DESC""")
            rows = cursor.fetchall()
            for row in rows:
                if row.get('fecha'):
                    row['fecha'] = str(row['fecha'])
            return rows
        except Exception as e:
            logging.error(f"❌ Error listar ventas: {e}", exc_info=True)
            return []
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener_venta(cls, venta_id):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM ecom_ventas WHERE id=%s", (venta_id,))
            return cursor.fetchone()
        except Exception as e:
            logging.error(f"❌ Error obtener venta: {e}", exc_info=True)
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def insertar_venta(cls, influencer_id, mes, anio, monto, nota, *, fecha=None):
        conn = None
        try:
            if not (1 <= mes <= 12):
                raise ValueError(f"Mes inválido: {mes}")
            if not (2000 <= anio <= 2100):
                raise ValueError(f"Año inválido: {anio}")
            if monto < 0:
                raise ValueError("El monto no puede ser negativo")

            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO ecom_ventas (influencer_id, mes, anio, monto, nota, fecha)
                              VALUES (%s, %s, %s, %s, %s, %s)""",
                           (influencer_id or None, mes, anio, monto, nota, fecha))
            conn.commit()
            return cursor.lastrowid
        except ValueError as ve:
            logging.error(f"❌ Error de validación al insertar venta: {ve}")
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            logging.error(f"❌ Error insertar venta: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar_venta(cls, venta_id, influencer_id, mes, anio, monto, nota, *, fecha=None):
        conn = None
        try:
            if not (1 <= mes <= 12):
                raise ValueError(f"Mes inválido: {mes}")
            if not (2000 <= anio <= 2100):
                raise ValueError(f"Año inválido: {anio}")
            if monto < 0:
                raise ValueError("El monto no puede ser negativo")

            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("""UPDATE ecom_ventas
                              SET influencer_id=%s, mes=%s, anio=%s, monto=%s, nota=%s, fecha=%s
                              WHERE id=%s""",
                           (influencer_id or None, mes, anio, monto, nota, fecha, venta_id))
            conn.commit()
            return cursor.rowcount
        except ValueError as ve:
            logging.error(f"❌ Error de validación al actualizar venta: {ve}")
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            logging.error(f"❌ Error actualizar venta: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def eliminar_venta(cls, venta_id):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ecom_ventas WHERE id=%s", (venta_id,))
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            logging.error(f"❌ Error eliminar venta: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def listar_metas(cls, anio=2025):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM metas WHERE anio=%s ORDER BY mes", (anio,))
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"❌ Error listar metas: {e}", exc_info=True)
            return []
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def actualizar_meta(cls, mes, anio, meta, real=0):
        conn = None
        try:
            if not (1 <= mes <= 12):
                raise ValueError(f"Mes inválido: {mes}")
            if not (2000 <= anio <= 2100):
                raise ValueError(f"Año inválido: {anio}")
            if meta < 0:
                raise ValueError("El valor de meta no puede ser negativo")

            conn = Conexion.obtener_conexion()
            cursor = conn.cursor()
            if Conexion.es_postgres():
                cursor.execute("""INSERT INTO metas (mes, anio, meta)
                                  VALUES (%s, %s, %s)
                                  ON CONFLICT (mes, anio) DO UPDATE SET meta = EXCLUDED.meta""",
                               (mes, anio, meta))
            else:
                cursor.execute("""INSERT INTO metas (mes, anio, meta)
                                  VALUES (%s, %s, %s)
                                  ON DUPLICATE KEY UPDATE meta=%s""",
                               (mes, anio, meta, meta))
            conn.commit()
            return cursor.rowcount
        except ValueError as ve:
            logging.error(f"❌ Error de validación al actualizar meta: {ve}")
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            logging.error(f"❌ Error actualizar meta: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def obtener_resumen_mes(cls, mes, anio):
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_ventas,
                    COALESCE(SUM(monto), 0) as monto_total,
                    COALESCE(AVG(monto), 0) as promedio,
                    COUNT(DISTINCT influencer_id) as influencers_activos
                FROM ecom_ventas
                WHERE mes=%s AND anio=%s
            """, (mes, anio))
            return cursor.fetchone()
        except Exception as e:
            logging.error(f"❌ Error obtener resumen: {e}", exc_info=True)
            return None
        finally:
            Conexion.liberar_conexion(conn)

    @classmethod
    def listar_metas_con_real(cls, anio):
        """Retorna metas del año con el real calculado desde las ventas reales."""
        conn = None
        try:
            conn = Conexion.obtener_conexion()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    m.mes,
                    m.anio,
                    m.meta,
                    COALESCE(SUM(v.monto), 0) AS real_total
                FROM metas m
                LEFT JOIN ecom_ventas v 
                    ON v.mes = m.mes AND v.anio = m.anio
                WHERE m.anio = %s
                GROUP BY m.mes, m.anio, m.meta
                ORDER BY m.mes
            """, (anio,))
            rows = cursor.fetchall()
            for row in rows:
                row['real'] = row.get('real_total', 0)
            return rows
        except Exception as e:
            logging.error(f"❌ Error listar metas con real: {e}", exc_info=True)
            return []
        finally:
            Conexion.liberar_conexion(conn)
