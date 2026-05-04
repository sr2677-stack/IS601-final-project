import pytest
from playwright.sync_api import Page, expect

BASE = "http://localhost:8000"


# ── Helpers ───────────────────────────────────────────────────────────────────

def register_and_login(page: Page, username: str = "e2euser", password: str = "password123"):
    page.goto(f"{BASE}/register")
    page.fill("[name=username]", username)
    page.fill("[name=email]", f"{username}@test.com")
    page.fill("[name=password]", password)
    page.fill("[name=confirm]", password)
    page.click("button[type=submit]")
    # lands on login after register
    page.fill("[name=username]", username)
    page.fill("[name=password]", password)
    page.click("button[type=submit]")
    expect(page).to_have_url(f"{BASE}/dashboard")


def do_calculation(page: Page, op: str, a: str, b: str):
    page.fill("[name=operand_a]", a)
    page.select_option("[name=operation]", op)
    page.fill("[name=operand_b]", b)
    page.click("button[type=submit]")


# ── Registration flow ─────────────────────────────────────────────────────────

def test_register_page_loads(page: Page):
    page.goto(f"{BASE}/register")
    expect(page).to_have_title("Register")
    expect(page.locator("h2")).to_contain_text("Create account")


def test_register_success(page: Page):
    page.goto(f"{BASE}/register")
    page.fill("[name=username]", "newuser")
    page.fill("[name=email]", "newuser@test.com")
    page.fill("[name=password]", "password123")
    page.fill("[name=confirm]", "password123")
    page.click("button[type=submit]")
    expect(page).to_have_url(f"{BASE}/login")


def test_register_duplicate_username(page: Page):
    register_and_login(page, "dupuser")
    page.goto(f"{BASE}/logout")
    # try to register same username again
    page.goto(f"{BASE}/register")
    page.fill("[name=username]", "dupuser")
    page.fill("[name=email]", "other@test.com")
    page.fill("[name=password]", "password123")
    page.fill("[name=confirm]", "password123")
    page.click("button[type=submit]")
    # should stay on register with an error
    expect(page).to_have_url(f"{BASE}/register")


def test_register_client_validation_short_username(page: Page):
    page.goto(f"{BASE}/register")
    page.fill("[name=username]", "ab")  # too short
    page.fill("[name=email]", "ab@test.com")
    page.fill("[name=password]", "password123")
    page.fill("[name=confirm]", "password123")
    page.click("button[type=submit]")
    expect(page.locator("#username-err")).to_be_visible()


def test_register_password_mismatch(page: Page):
    page.goto(f"{BASE}/register")
    page.fill("[name=username]", "mismatch")
    page.fill("[name=email]", "m@test.com")
    page.fill("[name=password]", "password123")
    page.fill("[name=confirm]", "different999")
    page.locator("[name=confirm]").dispatch_event("input")
    expect(page.locator("#confirm-err")).to_be_visible()


# ── Login flow ────────────────────────────────────────────────────────────────

def test_login_page_loads(page: Page):
    page.goto(f"{BASE}/login")
    expect(page).to_have_title("Login")
    expect(page.locator("h2")).to_contain_text("Welcome back")


def test_login_success(page: Page):
    register_and_login(page)
    expect(page).to_have_url(f"{BASE}/dashboard")
    expect(page.locator("nav")).to_contain_text("e2euser")


def test_login_wrong_password(page: Page):
    register_and_login(page, "wrongpwduser")
    page.goto(f"{BASE}/logout")
    page.goto(f"{BASE}/login")
    page.fill("[name=username]", "wrongpwduser")
    page.fill("[name=password]", "wrongpassword")
    page.click("button[type=submit]")
    expect(page).to_have_url(f"{BASE}/login")


def test_login_nonexistent_user(page: Page):
    page.goto(f"{BASE}/login")
    page.fill("[name=username]", "ghostuser")
    page.fill("[name=password]", "password123")
    page.click("button[type=submit]")
    expect(page).to_have_url(f"{BASE}/login")


def test_logout(page: Page):
    register_and_login(page)
    page.click("button:has-text('Sign out')")
    expect(page).to_have_url(f"{BASE}/login")


def test_protected_redirect_when_not_logged_in(page: Page):
    page.goto(f"{BASE}/dashboard")
    expect(page).to_have_url(f"{BASE}/login")


# ── Calculation flow ──────────────────────────────────────────────────────────

def test_dashboard_calculator_visible(page: Page):
    register_and_login(page)
    expect(page.locator("[name=operand_a]")).to_be_visible()
    expect(page.locator("[name=operation]")).to_be_visible()
    expect(page.locator("[name=operand_b]")).to_be_visible()


def test_add_calculation_appears_in_recent(page: Page):
    register_and_login(page)
    do_calculation(page, "add", "10", "5")
    expect(page.locator("table")).to_be_visible()
    expect(page.locator("tbody")).to_contain_text("add")
    expect(page.locator("tbody")).to_contain_text("15")


def test_subtract_calculation(page: Page):
    register_and_login(page)
    do_calculation(page, "subtract", "20", "8")
    expect(page.locator("tbody")).to_contain_text("12")


def test_multiply_calculation(page: Page):
    register_and_login(page)
    do_calculation(page, "multiply", "6", "7")
    expect(page.locator("tbody")).to_contain_text("42")


def test_divide_calculation(page: Page):
    register_and_login(page)
    do_calculation(page, "divide", "15", "3")
    expect(page.locator("tbody")).to_contain_text("5")


def test_power_calculation(page: Page):
    register_and_login(page)
    do_calculation(page, "power", "2", "8")
    expect(page.locator("tbody")).to_contain_text("256")


def test_modulus_calculation(page: Page):
    register_and_login(page)
    do_calculation(page, "modulus", "17", "5")
    expect(page.locator("tbody")).to_contain_text("2")


def test_multiple_calculations_show_in_recent(page: Page):
    register_and_login(page)
    do_calculation(page, "add", "1", "1")
    do_calculation(page, "multiply", "3", "3")
    do_calculation(page, "subtract", "10", "4")
    rows = page.locator("tbody tr")
    expect(rows).to_have_count(3)


def test_recent_shows_max_five(page: Page):
    register_and_login(page)
    for i in range(7):
        do_calculation(page, "add", str(i), "1")
    rows = page.locator("tbody tr")
    expect(rows).to_have_count(5)


# ── History flow ──────────────────────────────────────────────────────────────

def test_history_page_loads(page: Page):
    register_and_login(page)
    page.goto(f"{BASE}/history")
    expect(page).to_have_title("History")


def test_history_empty_state(page: Page):
    register_and_login(page)
    page.goto(f"{BASE}/history")
    expect(page.locator("p")).to_contain_text("No calculations yet")


def test_history_shows_all_calculations(page: Page):
    register_and_login(page)
    do_calculation(page, "add", "1", "2")
    do_calculation(page, "divide", "8", "4")
    do_calculation(page, "power", "3", "3")
    page.goto(f"{BASE}/history")
    rows = page.locator("tbody tr")
    expect(rows).to_have_count(3)


def test_delete_calculation_from_history(page: Page):
    register_and_login(page)
    do_calculation(page, "add", "5", "5")
    page.goto(f"{BASE}/history")
    expect(page.locator("tbody tr")).to_have_count(1)
    page.click(".btn-danger")
    expect(page.locator("tbody tr")).to_have_count(0)
    expect(page.locator("p")).to_contain_text("No calculations yet")


def test_history_link_from_dashboard(page: Page):
    register_and_login(page)
    do_calculation(page, "add", "1", "1")
    page.click("a:has-text('Open full history')")
    expect(page).to_have_url(f"{BASE}/history")


# ── Navigation ────────────────────────────────────────────────────────────────

def test_nav_links_present(page: Page):
    register_and_login(page)
    expect(page.locator("nav a:has-text('Dashboard')")).to_be_visible()
    expect(page.locator("nav a:has-text('History')")).to_be_visible()
    expect(page.locator("nav a:has-text('Report')")).to_be_visible()


def test_nav_history_link(page: Page):
    register_and_login(page)
    page.click("nav a:has-text('History')")
    expect(page).to_have_url(f"{BASE}/history")


def test_nav_report_link(page: Page):
    register_and_login(page)
    page.click("nav a:has-text('Report')")
    expect(page).to_have_url(f"{BASE}/report")
