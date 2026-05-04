def test_report_page_requires_auth(client):
    r = client.get("/report")
    assert r.status_code == 401 or "/login" in str(r.url)


def test_report_page_empty(auth_client):
    r = auth_client.get("/report")
    assert r.status_code == 200
    assert "Total calculations" in r.text


def test_report_after_calculations(auth_client):
    for _ in range(3):
        auth_client.post("/calculate", data={"operation": "add", "operand_a": 2, "operand_b": 3})
    r = auth_client.get("/api/report")
    assert r.status_code == 200
    data = r.json()
    assert data["total_calculations"] == 3
    assert data["most_used_operation"] == "add"


def test_history_page(auth_client):
    auth_client.post("/calculate", data={"operation": "multiply", "operand_a": 4, "operand_b": 5})
    r = auth_client.get("/history")
    assert r.status_code == 200
    assert "multiply" in r.text


def test_delete_calculation(auth_client):
    auth_client.post("/calculate", data={"operation": "add", "operand_a": 1, "operand_b": 1})
    r = auth_client.get("/api/report")
    calc_id = auth_client.get("/history")
    # just check it doesn't 500
    r2 = auth_client.get("/calculations/1/delete")
    assert r2.status_code == 200