import pytest
from app.models import Calculation


# ── Auth protection ───────────────────────────────────────────────────────────

def test_dashboard_requires_auth(client):
    r = client.get("/dashboard")
    assert r.status_code == 401 or "/login" in str(r.url)


def test_calculate_requires_auth(client):
    r = client.post("/calculate", data={"operation": "add", "operand_a": 2, "operand_b": 3})
    assert r.status_code == 401 or "/login" in str(r.url)


# ── Dashboard ─────────────────────────────────────────────────────────────────

def test_dashboard_loads(auth_client):
    r = auth_client.get("/dashboard")
    assert r.status_code == 200
    assert "Calculate" in r.text


def test_dashboard_shows_recent_calculations(auth_client):
    auth_client.post("/calculate", data={"operation": "add", "operand_a": 1, "operand_b": 2})
    r = auth_client.get("/dashboard")
    assert r.status_code == 200
    assert "add" in r.text


# ── Calculations: positive cases ──────────────────────────────────────────────

@pytest.mark.parametrize("op,a,b,expected", [
    ("add",      10,  5, 15.0),
    ("subtract", 10,  5,  5.0),
    ("multiply",  4,  3, 12.0),
    ("divide",   10,  2,  5.0),
    ("power",     2, 10, 1024.0),
    ("modulus",  10,  3,  1.0),
])
def test_calculate_operations(auth_client, db, op, a, b, expected):
    r = auth_client.post("/calculate", data={"operation": op, "operand_a": a, "operand_b": b})
    assert r.status_code == 200  # after redirect
    calc = db.query(Calculation).order_by(Calculation.id.desc()).first()
    assert calc is not None
    assert calc.operation == op
    assert calc.result == expected


def test_calculate_persists_to_db(auth_client, db):
    auth_client.post("/calculate", data={"operation": "add", "operand_a": 7, "operand_b": 3})
    calcs = db.query(Calculation).all()
    assert len(calcs) == 1
    assert calcs[0].operand_a == 7.0
    assert calcs[0].operand_b == 3.0
    assert calcs[0].result == 10.0


def test_multiple_calculations_accumulate(auth_client, db):
    for i in range(5):
        auth_client.post("/calculate", data={"operation": "add", "operand_a": i, "operand_b": 1})
    assert db.query(Calculation).count() == 5


def test_calculate_float_operands(auth_client, db):
    auth_client.post("/calculate", data={"operation": "multiply", "operand_a": 1.5, "operand_b": 4.0})
    calc = db.query(Calculation).first()
    assert calc.result == 6.0


# ── Calculations: negative / validation cases ─────────────────────────────────

def test_invalid_operation_rejected(auth_client, db):
    r = auth_client.post("/calculate", data={"operation": "sqrt", "operand_a": 9, "operand_b": 0})
    assert r.status_code == 422 or r.status_code == 400
    assert db.query(Calculation).count() == 0


def test_divide_by_zero_rejected(auth_client, db):
    r = auth_client.post("/calculate", data={"operation": "divide", "operand_a": 5, "operand_b": 0})
    assert r.status_code in (400, 422, 500)
    assert db.query(Calculation).count() == 0


def test_modulus_by_zero_rejected(auth_client, db):
    r = auth_client.post("/calculate", data={"operation": "modulus", "operand_a": 5, "operand_b": 0})
    assert r.status_code in (400, 422, 500)
    assert db.query(Calculation).count() == 0


def test_missing_operand_rejected(auth_client):
    r = auth_client.post("/calculate", data={"operation": "add", "operand_a": 5})
    assert r.status_code == 422


def test_non_numeric_operand_rejected(auth_client):
    r = auth_client.post("/calculate", data={"operation": "add", "operand_a": "abc", "operand_b": 3})
    assert r.status_code == 422


# ── Delete ────────────────────────────────────────────────────────────────────

def test_delete_own_calculation(auth_client, db):
    auth_client.post("/calculate", data={"operation": "add", "operand_a": 1, "operand_b": 1})
    calc = db.query(Calculation).first()
    r = auth_client.get(f"/calculations/{calc.id}/delete")
    assert r.status_code == 200
    db.expire_all()
    assert db.query(Calculation).count() == 0


def test_cannot_delete_other_users_calculation(client, db):
    from app.models import User
    from app.auth import hash_password

    # Create two users
    u1 = User(username="user1", email="u1@test.com", hashed_password=hash_password("password123"))
    u2 = User(username="user2", email="u2@test.com", hashed_password=hash_password("password123"))
    db.add_all([u1, u2])
    db.commit()

    # user1 creates a calculation
    client.post("/login", data={"username": "user1", "password": "password123"})
    client.post("/calculate", data={"operation": "add", "operand_a": 5, "operand_b": 5})
    calc = db.query(Calculation).first()

    # user2 tries to delete it
    client.post("/login", data={"username": "user2", "password": "password123"})
    client.get(f"/calculations/{calc.id}/delete")

    db.expire_all()
    assert db.query(Calculation).count() == 1  # still there


def test_delete_nonexistent_calculation(auth_client):
    r = auth_client.get("/calculations/99999/delete")
    # should redirect gracefully, not 500
    assert r.status_code in (200, 404)