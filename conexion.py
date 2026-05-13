import os
import mysql.connector
from mysql.connector import Error


class Conexion:
    # Usar las variables que Railway genera automáticamente (MYSQL_*)
    HOST = os.environ.get('MYSQL_HOST', 'localhost')
    DATABASE = os.environ.get('MYSQL_DATABASE', 'railway')
    USER = os.environ.get('MYSQL_USER', 'root')
    PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    DB_PORT = int(os.environ.get('MYSQL_PORT', '3306'))
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
                    autocommit=False,
                    connect_timeout=10
                )
                print("✅ Pool de conexiones creado correctamente.")
                print(f"📍 Conectado a: {cls.HOST}:{cls.DB_PORT}/{cls.DATABASE}")
            except Error as e:
                print(f"❌ Error al crear el pool: {e}")
                print(f"🔍 Host: {cls.HOST}, Port: {cls.DB_PORT}, User: {cls.USER}, DB: {cls.DATABASE}")
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
                conexion.rollback()
            except Exception:
                pass
            finally:
                try:
                    conexion.close()
                except Exception:
                    pass