import json
import os
from decimal import Decimal
from datetime import date, datetime

import mysql.connector
import psycopg2
from psycopg2.extras import execute_values


TABLES_ORDER = [
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


def norm(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime, date)):
        return v
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False)
    return v


def get_mysql_conn():
    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
    )


def get_pg_conn():
    dsn = os.environ["SUPABASE_DATABASE_URL"]
    if dsn.startswith("postgres://"):
        dsn = "postgresql://" + dsn[len("postgres://"):]
    return psycopg2.connect(dsn)


def fetch_all(mysql_conn, table):
    cur = mysql_conn.cursor(dictionary=True)
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    cur.close()
    return rows


def reset_table(pg_conn, table):
    with pg_conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")


def insert_rows(pg_conn, table, rows):
    if not rows:
        return 0
    cols = list(rows[0].keys())
    values = []
    for r in rows:
        values.append(tuple(norm(r[c]) for c in cols))
    sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES %s"
    with pg_conn.cursor() as cur:
        execute_values(cur, sql, values, page_size=1000)
    return len(rows)


def sync_sequence(pg_conn, table):
    with pg_conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT pg_get_serial_sequence(%s, 'id')
            """,
            (table,),
        )
        seq = cur.fetchone()[0]
        if seq:
            cur.execute(f"SELECT COALESCE(MAX(id), 1) FROM {table}")
            max_id = cur.fetchone()[0]
            cur.execute("SELECT setval(%s, %s, true)", (seq, max_id))


def main():
    mysql_conn = get_mysql_conn()
    pg_conn = get_pg_conn()
    pg_conn.autocommit = False

    copied = {}
    try:
        for table in TABLES_ORDER:
            rows = fetch_all(mysql_conn, table)
            reset_table(pg_conn, table)
            count = insert_rows(pg_conn, table, rows)
            sync_sequence(pg_conn, table)
            copied[table] = count
            print(f"{table}: {count} filas")

        pg_conn.commit()
        print("Migracion completada OK.")
    except Exception as e:
        pg_conn.rollback()
        print(f"Error migrando: {e}")
        raise
    finally:
        mysql_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    main()
