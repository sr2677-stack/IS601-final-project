import pytest
import time
from playwright.sync_api import Page, expect


BASE = "http://localhost:8000"


def login(page: Page):
    username = f"e2euser_{int(time.time() * 1000)}"
    page.goto(f"{BASE}/register")
    page.fill("[name=username]", username)
    page.fill("[name=email]", f"{username}@test.com")
    page.fill("[name=password]", "password123")
    page.fill("[name=confirm]", "password123")
    page.click("button[type=submit]")
    page.fill("[name=username]", username)
    page.fill("[name=password]", "password123")
    page.click("button[type=submit]")


def test_full_report_flow(page: Page):
    login(page)
    # Do some calculations
    for _ in range(3):
        page.fill("[name=operand_a]", "5")
        page.select_option("[name=operation]", "add")
        page.fill("[name=operand_b]", "3")
        page.click("button[type=submit]")

    # Visit report
    page.goto(f"{BASE}/report")
    expect(page.locator(".stat-box")).to_have_count(3)
    expect(page.get_by_text("3")).to_be_visible()   # total_calculations
    expect(page.get_by_text("add")).to_be_visible()

    # Visit history
    page.goto(f"{BASE}/history")
    rows = page.locator("tbody tr")
    expect(rows).to_have_count(3)


def test_delete_from_history(page: Page):
    login(page)
    page.fill("[name=operand_a]", "2")
    page.select_option("[name=operation]", "multiply")
    page.fill("[name=operand_b]", "4")
    page.click("button[type=submit]")
    page.goto(f"{BASE}/history")
    page.click(".btn-danger")
    expect(page.locator("tbody tr")).to_have_count(0)


def test_report_redirects_unauthenticated(page: Page):
    page.goto(f"{BASE}/report")
    expect(page).to_have_url(f"{BASE}/login")
