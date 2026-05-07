import pytest
from app.auth import hash_password, verify_password
from app.models import User
from app.routes.auth_routes import validate_and_hash_new_password


def _user_with_password(password: str = "password123") -> User:
    return User(username="logicuser", email="logic@test.com", hashed_password=hash_password(password))


def test_validate_and_hash_new_password_success():
    user = _user_with_password()
    new_hash = validate_and_hash_new_password(user, "password123", "newpassword123", "newpassword123")
    assert new_hash != user.hashed_password
    assert verify_password("newpassword123", new_hash)


def test_validate_and_hash_new_password_wrong_current():
    user = _user_with_password()
    with pytest.raises(ValueError, match="Current password is incorrect"):
        validate_and_hash_new_password(user, "wrong123", "newpassword123", "newpassword123")


def test_validate_and_hash_new_password_mismatch():
    user = _user_with_password()
    with pytest.raises(ValueError, match="do not match"):
        validate_and_hash_new_password(user, "password123", "newpassword123", "newpassword999")


def test_validate_and_hash_new_password_reuse_disallowed():
    user = _user_with_password()
    with pytest.raises(ValueError, match="must be different"):
        validate_and_hash_new_password(user, "password123", "password123", "password123")
