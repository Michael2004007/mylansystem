import json
import os
from datetime import date, datetime
from decimal import Decimal

import mysql.connector
import psycopg2
from psycopg2.extras import execute_values


TABLES = [
    "usuarios",
    "campanas",
    "influencers",
    "permisos_usuario",
    "configuracion",
    "tareas",
    "colaboraciones",
    "hitos_campana",
    "cal_eventos",
    "ecom_ventas",
    "metas",
    "ideas_campana",
    "idea_colaboraciones",
    "idea_hitos",
    "documentos",
]

BOOL_COLUMNS = {
    ("usuarios", "activo"),
    ("permisos_usuario", "puede_ver"),
    ("permisos_usuario", "puede_editar"),
    ("permisos_usuario", "puede_aprobar"),
    ("cal_eventos", "destacado"),
}

JSON_COLUMNS = {
    ("tareas", "postergaciones"),
    ("hitos_campana", "historial_postergaciones"),
    ("documentos", "datos"),
}


def norm(table, col, val):
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, (datetime, date)):
        return val
    if (table, col) in BOOL_COLUMNS and val is not None:
        return bool(int(val)) if not isinstance(val, bool) else val
    if (table, col) in JSON_COLUMNS:
        if val is None or val == "":
            return "{}" if (table, col) == ("documentos", "datos") else "[]"
        if isinstance(val, (dict, list)):
            return json.dumps(val, ensure_ascii=False)
        return str(val)
    return val


def mysql_conn():
    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
    )


def pg_conn():
    dsn = os.environ["DATABASE_URL"]
    if dsn.startswith("postgres://"):
        dsn = "postgresql://" + dsn[len("postgres://"):]
    return psycopg2.connect(dsn)


def pg_columns(conn, table):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name=%s
            ORDER BY ordinal_position
            """,
            (table,),
        )
        return [r[0] for r in cur.fetchall()]


def copy_table(src, dst, table):
    mcur = src.cursor(dictionary=True)
    mcur.execute(f"SELECT * FROM {table}")
    rows = mcur.fetchall()
    mcur.close()

    with dst.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")

    if not rows:
        return 0

    cols_dst = set(pg_columns(dst, table))
    cols = [c for c in rows[0].keys() if c in cols_dst]
    values = [tuple(norm(table, c, r[c]) for c in cols) for r in rows]

    sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES %s"
    with dst.cursor() as cur:
        execute_values(cur, sql, values, page_size=1000)
    return len(rows)


def main():
    src = mysql_conn()
    dst = pg_conn()
    try:
        for t in TABLES:
            n = copy_table(src, dst, t)
            print(f"{t}: {n}")
        dst.commit()
        print("OK migracion completa")
    except Exception as e:
        dst.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        src.close()
        dst.close()


if __name__ == "__main__":
    main()
