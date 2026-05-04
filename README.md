## Running locally
```bash
pip install -r requirements.txt
alembic upgrade head
python -m app.main
```

## Running with Docker
```bash
docker-compose up --build
```

## Running tests
```bash
pytest tests/unit tests/integration -v          # fast tests
playwright install chromium                      # first time only
python -m app.main                               # start server
pytest tests/e2e -v                             # E2E
```

## Docker Hub
https://hub.docker.com/r/YOUR_USERNAME/calculator-app
