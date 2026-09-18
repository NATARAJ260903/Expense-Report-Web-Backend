# Expense Report Web + Backend

This project contains:
- FastAPI backend
- MySQL 8 database with schema and seed data
- React/Vite frontend with Employee, Manager, and Finance dashboards

## MySQL configuration
The project is configured consistently to use:
- Host: `127.0.0.1`
- Port: `3306`
- User: `root`
- Password: `password`
- Database: `expense_db`

`docker-compose.yml`, `backend/.env`, `backend/app/db.py`, and `db/schema.sql` all target the same database. The backend has a fallback to `password` if `DB_PASSWORD` is not set.

## Run

### 1. Start MySQL

From the project root:
```bash
docker compose up -d db
```

If you already have a MySQL server running on port 3306, make sure the `root` password is `password` and the `expense_db` database exists. Otherwise use the Docker database above.

### 2. Load/reset schema

For a fresh Docker database, the schema can be imported with:
```bash
docker exec -i expense-db mysql -uroot -ppassword < db/schema.sql
```

### 3. Start backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend: http://localhost:8000

### 4. Start frontend

In another terminal:
```bash
cd web
npm install
npm run dev
```

Frontend: http://localhost:5173

The frontend reads `VITE_API_BASE` when provided and otherwise uses `http://localhost:8000`.
