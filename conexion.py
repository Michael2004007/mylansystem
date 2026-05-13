import os
import mysql.connector
from mysql.connector import Error


class Conexion:
    # Variables de entorno compatibles con Railway y desarrollo local
    HOST = os.environ.get('DB_HOST') or os.environ.get('MYSQLHOST') or os.environ.get('MYSQL_HOST', 'localhost')
    DATABASE = os.environ.get('DB_NAME') or os.environ.get('MYSQLDATABASE') or os.environ.get('MYSQL_DATABASE', 'mylan_marketing')
    USER = os.environ.get('DB_USER') or os.environ.get('MYSQLUSER') or os.environ.get('MYSQL_USER', 'root')
    PASSWORD = os.environ.get('DB_PASSWORD') or os.environ.get('MYSQLPASSWORD') or os.environ.get('MYSQL_PASSWORD', 'Oscar2025-')
    DB_PORT = int(os.environ.get('DB_PORT') or os.environ.get('MYSQLPORT') or os.environ.get('MYSQL_PORT', '3306'))
    POOL_SIZE = 5
    POOL_NAME = "mylan_pool"
    _pool = None

    @classmethod
    def obtener_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name=cls.POOL_NAME,
                    pool_size=cls.POOL_SIZE,
                    host=cls.HOST,
                    port=cls.DB_PORT,
                    database=cls.DATABASE,
                    user=cls.USER,
                    password=cls.PASSWORD,
                    autocommit=False,  # explícito para evitar comportamiento ambiguo
                    connect_timeout=10  # timeout de conexión para Railway
                )
                print("✅ Pool de conexiones creado correctamente.")
                print(f"📍 Conectado a: {cls.HOST}:{cls.DB_PORT}/{cls.DATABASE}")
            except Error as e:
                print(f"❌ Error al crear el pool: {e}")
                print(f"🔍 Intentando conectar a: {cls.HOST}:{cls.DB_PORT}")
                raise
        return cls._pool

    @classmethod
    def obtener_conexion(cls):
        try:
            return cls.obtener_pool().get_connection()
        except Error as e:
            print(f"❌ Error al obtener conexión del pool: {e}")
            return None

    @classmethod
    def liberar_conexion(cls, conexion):
        if conexion is not None:
            try:
                conexion.rollback()  # limpia cualquier transacción colgada antes de devolver al pool
            except Exception:
                pass
            finally:
                try:
                    conexion.close()
                except Exception:
                    pass