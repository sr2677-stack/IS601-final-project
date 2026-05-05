from uuid import uuid4
from playwright.sync_api import Page, expect

BASE = "http://localhost:8000"


# ── Helper ────────────────────────────────────────────────────────────────────

def register_and_login(page: Page) -> str:
    username = f"report_{uuid4().hex[:8]}"
    page.goto(f"{BASE}/register")
    page.fill("[name=username]", username)
    page.fill("[name=email]", f"{username}@test.com")
    page.fill("[name=password]", "password123")
    page.fill("[name=confirm]", "password123")
    page.click("button[type=submit]")
    page.wait_for_url(f"{BASE}/login", timeout=8000)
    page.fill("[name=username]", username)
    page.fill("[name=password]", "password123")
    page.click("button[type=submit]")
    page.wait_for_url(f"{BASE}/dashboard", timeout=8000)
    return username


def do_calculation(page: Page, op: str, a: str, b: str):
    page.fill("[name=operand_a]", a)
    page.select_option("[name=operation]", op)
    page.fill("[name=operand_b]", b)
    page.click("button[type=submit]")
    page.wait_for_url(f"{BASE}/dashboard", timeout=5000)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_full_report_flow(page: Page):
    register_and_login(page)

    # Do 3 calculations
    for _ in range(3):
        do_calculation(page, "add", "5", "3")

    # Visit report page
    page.goto(f"{BASE}/report")
    expect(page.locator(".stat-box")).to_have_count(3)

    # Check total calculations — use .value inside first stat-box specifically
    first_stat = page.locator(".stat-box").nth(0)
    expect(first_stat.locator(".value")).to_have_text("3")

    # Check most used operation — last stat box
    last_stat = page.locator(".stat-box").nth(2)
    expect(last_stat.locator(".value")).to_have_text("add")

    # Visit history and confirm 3 rows
    page.goto(f"{BASE}/history")
    expect(page.locator("tbody tr")).to_have_count(3)


def test_delete_from_history(page: Page):
    register_and_login(page)
    do_calculation(page, "multiply", "2", "4")
    page.goto(f"{BASE}/history")
    expect(page.locator("tbody tr")).to_have_count(1)
    page.click(".btn-danger")
    expect(page.locator("tbody tr")).to_have_count(0)
    expect(page.locator("p")).to_contain_text("No calculations yet")


def test_report_redirects_unauthenticated(page: Page):
    page.goto(f"{BASE}/report")
    # Should redirect to login or show not authenticated
    assert "/login" in page.url or "Not authenticated" in page.locator("body").inner_text()