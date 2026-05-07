# FastAPI Calculator App

A full-stack calculator web application built with FastAPI, SQLAlchemy, and Jinja2.

## Features
- User registration and login with JWT authentication
- Profile update (username/email) and secure password change
- Six calculator operations: add, subtract, multiply, divide, power, modulus
- Calculation history per user
- Usage report with stats and operation breakdown
- Dockerized deployment
- CI/CD with GitHub Actions

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Auth**: JWT tokens, bcrypt password hashing
- **Frontend**: Jinja2 templates
- **Database**: SQLite
- **Testing**: pytest, Playwright
- **DevOps**: Docker, GitHub Actions

## Running locally

### 1. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up database
```bash
alembic upgrade head
```

### 4. Start the app
```bash
uvicorn app.main:app --reload
```
Visit http://localhost:8000

## Running with Docker
```bash
docker-compose up --build
```
Visit http://localhost:8000

## Running tests

### Unit and integration tests (no server needed)
```bash
pytest tests/unit tests/integration -v
```

### E2E tests (server must be running)
```bash
# Terminal 1
uvicorn app.main:app --port 8000

# Terminal 2
playwright install chromium
pytest tests/e2e -v
```

### All tests with coverage
```bash
pip install pytest-cov
pytest tests/unit tests/integration --cov=app --cov-report=term-missing
```

## Running Alembic migrations
```bash
alembic upgrade head       # apply migrations
alembic downgrade base     # rollback all
```

## Docker Hub
https://hub.docker.com/r/sr2677stack/calculator-app

## CI/CD
GitHub Actions automatically:
1. Runs all unit, integration, and E2E tests
2. Builds the Docker image
3. Pushes to Docker Hub on every push to main
