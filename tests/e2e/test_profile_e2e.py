from uuid import uuid4
from playwright.sync_api import Page, expect

BASE = "http://localhost:8000"


def _unique_user(prefix: str = "profilee2e") -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


def register_and_login(page: Page, username: str, password: str):
    page.goto(f"{BASE}/register")
    page.fill("[name=username]", username)
    page.fill("[name=email]", f"{username}@test.com")
    page.fill("[name=password]", password)
    page.fill("[name=confirm]", password)
    page.click("button[type=submit]")
    page.wait_for_url(f"{BASE}/login", timeout=8000)
    page.fill("[name=username]", username)
    page.fill("[name=password]", password)
    page.click("button[type=submit]")
    page.wait_for_url(f"{BASE}/dashboard", timeout=8000)


def test_profile_update_and_password_change_flow(page: Page):
    username = _unique_user()
    old_password = "password123"
    new_password = "newpassword123"
    new_username = f"{username}_new"
    new_email = f"{new_username}@test.com"

    register_and_login(page, username, old_password)
    page.click("nav a:has-text('Profile')")
    page.wait_for_url(f"{BASE}/profile", timeout=5000)

    page.fill("[name=username]", new_username)
    page.fill("[name=email]", new_email)
    page.click("button:has-text('Update profile')")
    expect(page.locator("body")).to_contain_text("Profile updated successfully")

    page.fill("[name=current_password]", old_password)
    page.fill("[name=new_password]", new_password)
    page.fill("[name=confirm_password]", new_password)
    page.click("button:has-text('Change password')")
    page.wait_for_url(f"{BASE}/login", timeout=8000)

    page.fill("[name=username]", new_username)
    page.fill("[name=password]", old_password)
    page.click("button[type=submit]")
    expect(page).to_have_url(f"{BASE}/login")

    page.fill("[name=username]", new_email)
    page.fill("[name=password]", new_password)
    page.click("button[type=submit]")
    page.wait_for_url(f"{BASE}/dashboard", timeout=8000)
    expect(page.locator("h1")).to_contain_text(new_username)


def test_change_password_mismatch_shows_client_validation(page: Page):
    username = _unique_user("profilemismatch")
    register_and_login(page, username, "password123")
    page.goto(f"{BASE}/profile")
    page.fill("[name=current_password]", "password123")
    page.fill("[name=new_password]", "newpassword123")
    page.fill("[name=confirm_password]", "differentpassword")
    page.locator("[name=confirm_password]").dispatch_event("input")
    expect(page.locator("#confirm-err")).to_be_visible()
