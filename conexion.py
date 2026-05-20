import os
from urllib.parse import urlparse

import mysql.connector
from mysql.connector import Error as MySQLError


class Conexion:
    POOL_SIZE = 5
    POOL_NAME = "mylan_pool"
    _pool = None
    _driver = None

    @classmethod
    def _detect_driver(cls):
        if cls._driver:
            return cls._driver
        db_url = os.environ.get("DATABASE_URL", "").strip()
        if db_url.startswith("postgres://") or db_url.startswith("postgresql://"):
            cls._driver = "postgres"
        else:
            cls._driver = "mysql"
        return cls._driver

    @classmethod
    def es_postgres(cls):
        return cls._detect_driver() == "postgres"

    @classmethod
    def obtener_pool(cls):
        driver = cls._detect_driver()
        if cls._pool is not None:
            return cls._pool

        if driver == "postgres":
            from psycopg2.pool import SimpleConnectionPool

            db_url = os.environ.get("DATABASE_URL", "").strip()
            if db_url.startswith("postgres://"):
                db_url = "postgresql://" + db_url[len("postgres://"):]
            cls._pool = SimpleConnectionPool(1, cls.POOL_SIZE, dsn=db_url)
            host = urlparse(db_url).hostname or "postgres"
            print(f"Pool Postgres creado. Host: {host}")
            return cls._pool

        host = os.environ.get("MYSQL_HOST") or os.environ.get("MYSQLHOST") or "localhost"
        database = os.environ.get("MYSQL_DATABASE") or os.environ.get("MYSQLDATABASE") or "railway"
        user = os.environ.get("MYSQL_USER") or os.environ.get("MYSQLUSER") or "root"
        password = os.environ.get("MYSQL_PASSWORD") or os.environ.get("MYSQLPASSWORD") or ""
        db_port = int(os.environ.get("MYSQL_PORT") or os.environ.get("MYSQLPORT") or "3306")

        cls._pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name=cls.POOL_NAME,
            pool_size=cls.POOL_SIZE,
            host=host,
            port=db_port,
            database=database,
            user=user,
            password=password,
            autocommit=False,
            connect_timeout=10,
        )
        print(f"Pool MySQL creado. Host: {host}:{db_port}/{database}")
        return cls._pool

    @classmethod
    def obtener_conexion(cls):
        try:
            pool = cls.obtener_pool()
            if cls.es_postgres():
                conn = pool.getconn()
                conn.autocommit = False
                return _PostgresConnectionWrapper(conn)
            return pool.get_connection()
        except MySQLError as e:
            print(f"Error MySQL al obtener conexion: {e}")
            return None
        except Exception as e:
            print(f"Error al obtener conexion: {e}")
            return None

    @classmethod
    def liberar_conexion(cls, conexion):
        if conexion is None:
            return
        raw_conn = conexion._conn if isinstance(conexion, _PostgresConnectionWrapper) else conexion
        try:
            raw_conn.rollback()
        except Exception:
            pass
        try:
            if cls.es_postgres() and cls._pool is not None:
                cls._pool.putconn(raw_conn)
            else:
                raw_conn.close()
        except Exception:
            pass


class _PostgresConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self, dictionary=False):
        import psycopg2.extras

        if dictionary:
            return _PostgresCursorWrapper(
                self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            )
        return _PostgresCursorWrapper(self._conn.cursor())

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()


class _PostgresCursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor
        self.lastrowid = None

    def execute(self, query, params=None):
        self.lastrowid = None
        q = (query or "").strip()
        up = q.upper()
        is_insert = up.startswith("INSERT INTO")
        has_returning = "RETURNING" in up

        if is_insert and not has_returning:
            patched = q.rstrip(";") + " RETURNING id"
            self._cursor.execute(patched, params)
            row = self._cursor.fetchone()
            if row is not None:
                self.lastrowid = row.get("id") if isinstance(row, dict) else row[0]
            return

        self._cursor.execute(query, params)
        if is_insert and has_returning:
            row = self._cursor.fetchone()
            if row is not None:
                self.lastrowid = row.get("id") if isinstance(row, dict) else row[0]

    def __getattr__(self, item):
        return getattr(self._cursor, item)
