import os
import time
from pathlib import Path
import pymysql
from dotenv import load_dotenv
load_dotenv()

def get_conn():
    return pymysql.connect(host=os.getenv("DB_HOST","127.0.0.1"),port=int(os.getenv("DB_PORT","3306")),user=os.getenv("DB_USER","root"),password=os.getenv("DB_PASSWORD",""),database=os.getenv("DB_NAME","expense_db"),cursorclass=pymysql.cursors.DictCursor,autocommit=True)

def init_database():
    schema=Path("/app/db/schema.sql")
    if not schema.exists():
        schema=Path(__file__).resolve().parent/"db"/"schema.sql"
    if not schema.exists():
        schema=Path.cwd()/"db"/"schema.sql"
    if not schema.exists():
        raise FileNotFoundError(f"Database schema not found: {schema}")
    sql=schema.read_text(encoding="utf-8")
    statements=[]
    for part in sql.split(";"):
        statement=part.strip()
        if not statement: continue
        upper=statement.upper()
        if upper.startswith("CREATE DATABASE") or upper.startswith("USE EXPENSE_DB"): continue
        statements.append(statement)
    for attempt in range(1,31):
        try:
            conn=get_conn()
            try:
                with conn.cursor() as cur:
                    cur.execute("SHOW TABLES LIKE 'employees'")
                    if cur.fetchone():
                        print("Database already initialized; skipping schema import.")
                        return
                    for statement in statements: cur.execute(statement)
                print(f"Database schema initialized successfully in {os.getenv('DB_NAME','expense_db')}.")
                return
            finally: conn.close()
        except Exception as exc:
            print(f"Database not ready (attempt {attempt}/30): {exc}")
            time.sleep(2)
    raise RuntimeError("Could not initialize database after 30 attempts.")

if __name__=="__main__":
    init_database()
