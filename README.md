# Tic Tac Toe Backend (FastAPI)

This container implements the backend service for the persistent Tic Tac Toe app – managing users, authentication, games, real-time board logic, and APIs.

---

## Quick Start

1. **Install dependencies** (use a clean Python 3.9+/3.10+ venv):

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r tic_tac_toe_backend/requirements.txt
   ```

2. **Set up Database Connection:**

   - By default, the backend connects to a PostgreSQL database (see below for details).
   - You can connect to the database container or set up your own DB (see `.env` settings).

3. **Configure Environment:**

   See [Environment Variables](#environment-variables) below. You may create a `.env` file in the project root:

   ```
   # .env SAMPLE for backend
   POSTGRES_URL=postgresql://appuser:dbuser123@localhost:5000/myapp
   POSTGRES_USER=appuser
   POSTGRES_PASSWORD=dbuser123
   POSTGRES_DB=myapp
   POSTGRES_PORT=5000

   SECRET_KEY=changeme-super-secret
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ENV=development
   ```

   The default values match the example database container in this repository.

4. **Run Development Server:**

   ```bash
   # from the backend root:
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 3001
   ```

   FastAPI docs: Browse at [http://localhost:3001/docs](http://localhost:3001/docs)

---

## Service Ports & Connections

- **Backend REST API**: `http://localhost:3001`
- **Database (Postgres)**: `localhost:5000` (default dev port, see [Database Container](../tictactoe-persistor-62001-62ff234f/README.md))
- **Frontend**: Typically runs at `http://localhost:3000`, expects backend at port `3001`.

---

## Backend/DB Interaction

- All ORM/SQL traffic uses the `POSTGRES_*` variables (see config.py).
- If running both containers as provided, the backend `.env` should point to:
  ```
  POSTGRES_URL=postgresql://appuser:dbuser123@localhost:5000/myapp
  ```

---

## Environment Variables

| Name                    | Default                                   | Purpose                             |
|-------------------------|-------------------------------------------|-------------------------------------|
| POSTGRES_URL            | postgresql://...                          | Full SQLAlchemy-style DB URI        |
| POSTGRES_USER           | postgres (or appuser in dev)              | DB Username                         |
| POSTGRES_PASSWORD       | postgres (or dbuser123 in dev)            | DB Password                         |
| POSTGRES_DB             | tic_tac_toe (or myapp in dev)             | DB Name                             |
| POSTGRES_PORT           | 5432 (or 5000 in dev container)           | DB Port                             |
| SECRET_KEY              | changeme-super-secret                     | JWT signing secret                  |
| JWT_ALGORITHM           | HS256                                     | JWT crypto alg                      |
| ACCESS_TOKEN_EXPIRE_MINUTES | 60                                    | How long tokens are valid           |
| ENV                     | development                               | Deployment environment              |

---

## Bootstrap and Development Tips

- If running locally with the provided DB container, ensure the database is started first (see `/tic_tac_toe_database/startup.sh`).
- API endpoints are fully described in FastAPI docs at `/docs`.
- This backend container is stateless and connects to the DB per your configuration.
- For local iteration, use `uvicorn --reload`.

---

## API Endpoints

- Register user: `POST /users/register`
- Log in: `POST /users/login`
- Start game: `POST /games`
- Make move: `POST /games/{game_id}/move`
- Get game state: `GET /games/{game_id}`
- User history: `GET /users/{user_id}/games`

All endpoints (except registration/login) require JWT Bearer authentication.

---

## Cross-Container Usage

- The backend requires the database to be running and accessible per `.env` above.
- When used with the provided frontend, set the backend URL in the frontend to `http://localhost:3001`.

---

## Troubleshooting

- For database connection issues, check your `.env` and ensure the DB container is running and accessible.
- Example psql command if connecting manually:
  ```
  psql -h localhost -U appuser -d myapp -p 5000
  ```
- For password/secret security, update `SECRET_KEY` in production.

---
