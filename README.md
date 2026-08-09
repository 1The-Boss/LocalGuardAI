# LocalGuardAI Connect

AI-assisted emergency report system with priority scoring.
Backend: FastAPI + SQLAlchemy (async) + PostgreSQL. Frontend: React.

## Requirements

- Python 3.11+
- PostgreSQL running locally (the app connects to the `localguard` database)
- Node.js (for the frontend)

## Database connection

The app connects to a local PostgreSQL database using the `DATABASE_URL`
environment variable (stored in `.env` at the project root):

```
DATABASE_URL=postgresql+asyncpg://postgres:7531@localhost:5432/localguard
```

| Component | Value |
|---|---|
| Host / Port | `localhost:5432` |
| Database | `localguard` |
| Username | `postgres` |
| Password | `7531` |

> Keep `.env` out of version control — it contains credentials.

Tables (`users`, `reports`) are created automatically on startup
(`Base.metadata.create_all`), and a leader user (`leader` / `admin`) plus
seeded officers are inserted if they don't already exist.

## Backend setup

```bash
# 1. Create a virtual environment and install dependencies
python -m venv myenv1
myenv1\Scripts\activate          # Windows
pip install -r requirements.txt

# 2. Create .env in the project root
#    DATABASE_URL=postgresql+asyncpg://postgres:7531@localhost:5432/localguard
#    SECRET_KEY=<your-secret-key>

# 3. Start the API
uvicorn app.main:app --reload
```

API docs are available at http://localhost:8000/docs.

## Frontend setup

```bash
cd frontend
npm install
npm start
```

The frontend proxies API calls to `http://localhost:8000`.

## Key endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/auth/login` | Login, returns a JWT |
| POST | `/reports/` | Create a report (AI priority scoring) |
| GET | `/reports/` | List all reports |
| GET | `/reports/{id}` | Get one report |
| PATCH | `/reports/{id}` | Update a report (leader role) |
| DELETE | `/reports/{id}` | Delete a report |
| GET | `/health` | Health check |
