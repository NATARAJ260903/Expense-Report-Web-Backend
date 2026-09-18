import os
import time
from pathlib import Path
import pymysql
from dotenv import load_dotenv
load_dotenv()

def get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST","127.0.0.1"),
        port=int(os.getenv("DB_PORT","3306")),
        user=os.getenv("DB_USER","root"),
        password=os.getenv("DB_PASSWORD",""),
        database=os.getenv("DB_NAME","expense_db"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

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
        if not statement:
            continue
        upper=statement.upper()
        if upper.startswith("CREATE DATABASE") or upper.startswith("USE EXPENSE_DB"):
            continue
        statements.append(statement)

    for attempt in range(1,31):
        try:
            conn=get_conn()
            try:
                with conn.cursor() as cur:
                    cur.execute("SHOW TABLES LIKE 'employees'")
                    if not cur.fetchone():
                        for statement in statements:
                            cur.execute(statement)
                        print(f"Database schema initialized successfully in {os.getenv('DB_NAME','expense_db')}.")

                    # Keep an existing database compatible with the current login code.
                    cur.execute("SHOW COLUMNS FROM employees LIKE 'password'")
                    if not cur.fetchone():
                        cur.execute("ALTER TABLE employees ADD COLUMN password VARCHAR(128) NOT NULL DEFAULT ''")
                        print("Added missing employees.password column.")

                    demo_passwords = {
                        "amit@beeja.com": "employee123",
                        "neha@beeja.com": "employee456",
                        "rahul@beeja.com": "rahul123",
                        "priya@beeja.com": "manager123",
                        "karan@beeja.com": "finance123",
                    }
                    for email, password in demo_passwords.items():
                        cur.execute("UPDATE employees SET password=%s WHERE email=%s", (password, email))

                    # Ensure demo accounts exist even when the database was initialized earlier.
                    cur.execute("SELECT id FROM employees WHERE email=%s", ("priya@beeja.com",))
                    priya=cur.fetchone()
                    if not priya:
                        cur.execute(
                            "INSERT INTO employees (id,name,email,password,role,manager_id,department) VALUES (4,%s,%s,%s,%s,NULL,%s)",
                            ("Priya Manager","priya@beeja.com","manager123","manager","Operations"),
                        )
                        priya_id=4
                    else:
                        priya_id=priya["id"]

                    demo_users=[
                        (1,"Amit Employee","amit@beeja.com","employee123","employee",priya_id,"Sales"),
                        (2,"Neha Employee","neha@beeja.com","employee456","employee",priya_id,"Operations"),
                        (3,"Rahul Employee","rahul@beeja.com","rahul123","employee",priya_id,"Tech"),
                        (5,"Karan Finance","karan@beeja.com","finance123","finance_admin",None,"Finance"),
                    ]
                    for uid,name,email,password,role,manager_id,department in demo_users:
                        cur.execute("SELECT id FROM employees WHERE email=%s",(email,))
                        if not cur.fetchone():
                            cur.execute(
                                "INSERT INTO employees (id,name,email,password,role,manager_id,department) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                                (uid,name,email,password,role,manager_id,department),
                            )
                    print("Demo accounts verified.")
                return
            finally:
                conn.close()
        except Exception as exc:
            print(f"Database not ready (attempt {attempt}/30): {exc}")
            time.sleep(2)
    raise RuntimeError("Could not initialize database after 30 attempts.")

if __name__=="__main__":
    init_database()
