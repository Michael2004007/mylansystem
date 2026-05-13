import os
import mysql.connector
from mysql.connector import Error
from urllib.parse import urlparse


class Conexion:
    # Intentar usar MYSQL_URL primero (Railway lo genera automáticamente)
    MYSQL_URL = os.environ.get('MYSQL_URL') or os.environ.get('DATABASE_URL')

    if MYSQL_URL and MYSQL_URL.startswith('mysql://'):
        # Parsear la URL
        parsed = urlparse(MYSQL_URL)
        HOST = parsed.hostname
        DATABASE = parsed.path[1:] if parsed.path else 'railway'
        USER = parsed.username
        PASSWORD = parsed.password
        DB_PORT = parsed.port or 3306
        print(f"🔗 Usando MYSQL_URL para conectar a: {HOST}:{DB_PORT}/{DATABASE}")
    else:
        # Variables individuales (fallback)
        HOST = os.environ.get('DB_HOST') or os.environ.get('MYSQLHOST') or os.environ.get('MYSQL_HOST', 'localhost')
        DATABASE = os.environ.get('DB_NAME') or os.environ.get('MYSQLDATABASE') or os.environ.get('MYSQL_DATABASE',
                                                                                                  'mylan_marketing')
        USER = os.environ.get('DB_USER') or os.environ.get('MYSQLUSER') or os.environ.get('MYSQL_USER', 'root')
        PASSWORD = os.environ.get('DB_PASSWORD') or os.environ.get('MYSQLPASSWORD') or os.environ.get('MYSQL_PASSWORD',
                                                                                                      '')
        DB_PORT = int(os.environ.get('DB_PORT') or os.environ.get('MYSQLPORT') or os.environ.get('MYSQL_PORT', '3306'))
        print(f"🔗 Usando variables individuales para conectar a: {HOST}:{DB_PORT}/{DATABASE}")

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
                print(f"🔍 Intentando conectar a: {cls.HOST}:{cls.DB_PORT}")
                print(f"🔍 Usuario: {cls.USER}, Database: {cls.DATABASE}")
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
                conexion.rollback()
            except Exception:
                pass
            finally:
                try:
                    conexion.close()
                except Exception:
                    pass