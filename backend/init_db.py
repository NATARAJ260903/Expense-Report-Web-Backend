"""
Database initialization script.
Run this once after deploying to Railway to set up the schema.
"""
import pymysql
import os
from app.db import get_connection

def init_database():
    """Initialize the expense_db schema with tables and sample data."""
    
    schema_sql = """
CREATE DATABASE IF NOT EXISTS expense_db;
USE expense_db;

DROP TABLE IF EXISTS approvals;
DROP TABLE IF EXISTS expenses;
DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(200) NOT NULL UNIQUE,
  role ENUM('employee','manager','finance_admin') NOT NULL,
  manager_id INT NULL,
  department VARCHAR(80) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_employee_manager FOREIGN KEY (manager_id)
    REFERENCES employees(id) ON DELETE SET NULL
);

CREATE TABLE expenses (
  id INT PRIMARY KEY AUTO_INCREMENT,
  employee_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  category ENUM('Travel','Meals','Accommodation','Office Supplies','Client Entertainment','Other') NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  expense_date DATE NOT NULL,
  receipt_filename VARCHAR(300) NULL,
  description TEXT NULL,
  status ENUM('draft','submitted','approved','rejected','paid') NOT NULL DEFAULT 'draft',
  submitted_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_expense_employee FOREIGN KEY (employee_id)
    REFERENCES employees(id) ON DELETE CASCADE
);

CREATE TABLE approvals (
  id INT PRIMARY KEY AUTO_INCREMENT,
  expense_id INT NOT NULL,
  actioned_by INT NOT NULL,
  action ENUM('approved','rejected','paid') NOT NULL,
  comment TEXT NULL,
  actioned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_approval_expense FOREIGN KEY (expense_id)
    REFERENCES expenses(id) ON DELETE CASCADE,
  CONSTRAINT fk_approval_employee FOREIGN KEY (actioned_by)
    REFERENCES employees(id) ON DELETE CASCADE
);

INSERT INTO employees (id,name,email,role,manager_id,department) VALUES
(1,'Amit Employee','amit@beeja.com','employee',4,'Sales'),
(2,'Neha Employee','neha@beeja.com','employee',4,'Operations'),
(3,'Rahul Employee','rahul@beeja.com','employee',4,'Tech'),
(4,'Priya Manager','priya@beeja.com','manager',NULL,'Operations'),
(5,'Karan Finance','karan@beeja.com','finance_admin',NULL,'Finance');

INSERT INTO expenses
(employee_id,title,category,amount,expense_date,receipt_filename,description,status,submitted_at)
VALUES
(1,'Client visit taxi','Travel',850.00,'2026-08-01','taxi.jpg','Taxi for client meeting','draft',NULL),
(2,'Team lunch','Meals',2200.00,'2026-08-02','lunch.jpg','Operations team lunch','draft',NULL),
(3,'Cloud conference','Travel',4500.00,'2026-08-03','conference.pdf','Travel to cloud conference','submitted','2026-08-03 10:00:00'),
(1,'Hotel stay','Accommodation',6200.00,'2026-08-04','hotel.pdf','Client project hotel','submitted','2026-08-04 11:00:00'),
(2,'Office stationery','Office Supplies',1250.00,'2026-08-05','stationery.jpg','Printer and stationery supplies','approved','2026-08-05 09:00:00'),
(3,'Customer dinner','Client Entertainment',3800.00,'2026-08-05','dinner.jpg','Dinner with customer','approved','2026-08-05 19:00:00'),
(1,'Parking','Travel',500.00,'2026-08-06','parking.jpg','Client parking','rejected','2026-08-06 09:00:00'),
(2,'Software book','Other',900.00,'2026-08-07','book.jpg','Technical reference','rejected','2026-08-07 09:00:00'),
(3,'Flight ticket','Travel',8000.00,'2026-08-08','flight.pdf','Business travel','paid','2026-08-08 08:00:00'),
(1,'Airport transfer','Travel',1400.00,'2026-08-09','transfer.jpg','Airport transfer','paid','2026-08-09 07:00:00');

INSERT INTO approvals (expense_id,actioned_by,action,comment) VALUES
(5,4,'approved','Looks good'),
(6,4,'approved','Approved for client work'),
(7,4,'rejected','Please attach a clearer receipt'),
(8,4,'rejected','Please provide business purpose'),
(9,4,'approved','Approved'),
(9,5,'paid','Payment processed'),
(10,4,'approved','Approved'),
(10,5,'paid','Payment processed');
"""
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Execute multi-statement SQL
            for statement in schema_sql.split(';'):
                statement = statement.strip()
                if statement:
                    cur.execute(statement)
        print("✓ Database initialized successfully!")
        print("✓ Created tables: employees, expenses, approvals")
        print("✓ Loaded sample data with 5 employees and 10 expenses")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    init_database()
