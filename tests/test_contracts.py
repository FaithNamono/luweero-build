VALID = {
    "engineer_name": "John Doe",
    "client_name": "Luweero Property Developers Ltd",
    "project_location": "Luweero Town",
    "milestone_title": "Foundation Concrete Pour",
    "milestone_budget_ugx": 3500000,
}


def test_create_contract_sets_pending_payment(client):
    r = client.post("/api/v1/contracts/create", json=VALID)
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1
    assert body["status"] == "PENDING_PAYMENT"
    assert body["milestone_budget_ugx"] == 3500000


def test_location_check_is_case_insensitive(client):
    r = client.post("/api/v1/contracts/create", json={**VALID, "project_location": "wobulenzi, LUWEERO district"})
    assert r.status_code == 201


def test_location_without_luweero_is_rejected(client):
    r = client.post("/api/v1/contracts/create", json={**VALID, "project_location": "Kampala"})
    assert r.status_code == 422
    assert "Luweero" in r.text


def test_budget_must_be_positive(client):
    r = client.post("/api/v1/contracts/create", json={**VALID, "milestone_budget_ugx": 0})
    assert r.status_code == 422
