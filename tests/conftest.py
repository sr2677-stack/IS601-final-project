import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User, Calculation
from app.auth import hash_password

TEST_DB = "sqlite:///./test.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, follow_redirects=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client, db):
    """Client with a logged-in session cookie."""
    db.add(User(username="testuser", email="t@test.com", hashed_password=hash_password("password123")))
    db.commit()
    client.post("/login", data={"username": "testuser", "password": "password123"})
    return client
