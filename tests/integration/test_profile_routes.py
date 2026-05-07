from app.auth import verify_password
from app.models import User


def test_profile_page_requires_auth(client):
    r = client.get("/profile")
    assert r.status_code == 401 or "/login" in str(r.url)


def test_profile_page_loads(auth_client):
    r = auth_client.get("/profile")
    assert r.status_code == 200
    assert "Profile settings" in r.text


def test_profile_update_success(auth_client, db):
    r = auth_client.post("/profile/update", data={"username": "updateduser", "email": "updated@test.com"})
    assert r.status_code == 200
    db.expire_all()
    user = db.query(User).first()
    assert user.username == "updateduser"
    assert user.email == "updated@test.com"
    assert "Profile updated successfully" in r.text


def test_profile_update_duplicate_username_rejected(client, db):
    from app.auth import hash_password

    db.add_all([
        User(username="alpha", email="alpha@test.com", hashed_password=hash_password("password123")),
        User(username="beta", email="beta@test.com", hashed_password=hash_password("password123")),
    ])
    db.commit()
    client.post("/login", data={"username": "alpha", "password": "password123"})
    r = client.post("/profile/update", data={"username": "beta", "email": "alpha_new@test.com"})
    assert r.status_code == 400
    assert "Username already taken" in r.text


def test_profile_update_duplicate_email_rejected(client, db):
    from app.auth import hash_password

    db.add_all([
        User(username="alpha2", email="alpha2@test.com", hashed_password=hash_password("password123")),
        User(username="beta2", email="beta2@test.com", hashed_password=hash_password("password123")),
    ])
    db.commit()
    client.post("/login", data={"username": "alpha2", "password": "password123"})
    r = client.post("/profile/update", data={"username": "alpha2_new", "email": "beta2@test.com"})
    assert r.status_code == 400
    assert "Email already in use" in r.text


def test_change_password_success_requires_relogin(auth_client, db):
    r = auth_client.post(
        "/profile/password",
        data={
            "current_password": "password123",
            "new_password": "newpass12345",
            "confirm_password": "newpass12345",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers["location"] == "/login"

    db.expire_all()
    user = db.query(User).first()
    assert verify_password("newpass12345", user.hashed_password)
    assert not verify_password("password123", user.hashed_password)


def test_change_password_wrong_current(auth_client, db):
    r = auth_client.post(
        "/profile/password",
        data={
            "current_password": "wrongpass",
            "new_password": "newpass12345",
            "confirm_password": "newpass12345",
        },
    )
    assert r.status_code == 400
    assert "Current password is incorrect" in r.text
    user = db.query(User).first()
    assert verify_password("password123", user.hashed_password)


def test_change_password_mismatch(auth_client, db):
    r = auth_client.post(
        "/profile/password",
        data={
            "current_password": "password123",
            "new_password": "newpass12345",
            "confirm_password": "newpass99999",
        },
    )
    assert r.status_code == 400
    assert "do not match" in r.text
    user = db.query(User).first()
    assert verify_password("password123", user.hashed_password)
