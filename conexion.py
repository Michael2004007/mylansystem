import os
import mysql.connector
from mysql.connector import Error


class Conexion:
    HOST = os.environ.get("MYSQL_HOST", "localhost")
    DATABASE = os.environ.get("MYSQL_DATABASE", "railway")
    USER = os.environ.get("MYSQL_USER", "root")
    PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    DB_PORT = os.environ.get("MYSQL_PORT", "3306")
    POOL_SIZE = 5
    POOL_NAME = "mylan_pool"
    _pool = None

    @classmethod
    def obtener_pool(cls):
        if cls._pool is None:
            try:
                host = os.environ.get("MYSQL_HOST") or os.environ.get("MYSQLHOST") or cls.HOST
                database = os.environ.get("MYSQL_DATABASE") or os.environ.get("MYSQLDATABASE") or cls.DATABASE
                user = os.environ.get("MYSQL_USER") or os.environ.get("MYSQLUSER") or cls.USER
                password = os.environ.get("MYSQL_PASSWORD") or os.environ.get("MYSQLPASSWORD") or cls.PASSWORD
                raw_port = os.environ.get("MYSQL_PORT") or os.environ.get("MYSQLPORT") or cls.DB_PORT
                port = int(raw_port)

                cls._pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name=cls.POOL_NAME,
                    pool_size=cls.POOL_SIZE,
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password,
                    autocommit=False,
                    connect_timeout=10,
                )
                print("Pool de conexiones creado correctamente.")
                print(f"Conectado a: {host}:{port}/{database}")
            except Error as e:
                print(f"Error al crear el pool: {e}")
                print(
                    "Variables MySQL detectadas: "
                    f"host={os.environ.get('MYSQL_HOST') or os.environ.get('MYSQLHOST')}, "
                    f"port={os.environ.get('MYSQL_PORT') or os.environ.get('MYSQLPORT')}, "
                    f"user={os.environ.get('MYSQL_USER') or os.environ.get('MYSQLUSER')}, "
                    f"db={os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQLDATABASE')}"
                )
        return cls._pool

    @classmethod
    def obtener_conexion(cls):
        try:
            return cls.obtener_pool().get_connection()
        except Error as e:
            print(f"Error al obtener conexion del pool: {e}")
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
