import os
import time
from pathlib import Path

import pymysql
from dotenv import load_dotenv

load_dotenv()


def get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "expense_db"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def init_database():
    schema = Path(__file__).resolve().parents[1] / "db" / "schema.sql"
    sql = schema.read_text(encoding="utf-8")

    # The application connects directly to DB_NAME (for Railway this is
    # usually "railway"), while schema.sql is also used locally with
    # "expense_db". Skip the database-selection statements from schema.sql
    # and create the tables inside the database already selected above.
    statements = []
    for part in sql.split(";"):
        statement = part.strip()
        if not statement:
            continue
        upper = statement.upper()
        if upper.startswith("CREATE DATABASE"):
            continue
        if upper.startswith("USE EXPENSE_DB"):
            continue
        statements.append(statement)

    for attempt in range(1, 31):
        try:
            conn = get_conn()
            try:
                with conn.cursor() as cur:
                    cur.execute("SHOW TABLES LIKE 'employees'")
                    if cur.fetchone():
                        print("Database already initialized; skipping schema import.")
                        return

                    for statement in statements:
                        cur.execute(statement)

                print(
                    f"Database schema initialized successfully in "
                    f"{os.getenv('DB_NAME', 'expense_db')}."
                )
                return
            finally:
                conn.close()
        except Exception as exc:
            print(f"Database not ready (attempt {attempt}/30): {exc}")
            time.sleep(2)

    raise RuntimeError("Could not initialize database after 30 attempts.")


if __name__ == "__main__":
    init_database()
