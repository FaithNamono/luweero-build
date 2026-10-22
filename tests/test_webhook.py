from app.config import get_settings
from tests.test_contracts import VALID
from tests.test_store import ORDER

URL = "/api/v1/mock-payment/webhook"


def _hook(ref="TXN-YO-112233", ptype="ESCROW_LOCK", rid=1, status="SUCCESS"):
    return {
        "transaction_reference": ref,
        "payment_type": ptype,
        "reference_id": rid,
        "transaction_status": status,
    }


def _contract(client):
    return client.post("/api/v1/contracts/create", json=VALID).json()["id"]


def _order(client):
    return client.post("/api/v1/store/order", json=ORDER).json()["id"]


def test_escrow_lock_flips_contract(client, db):
    cid = _contract(client)
    r = client.post(URL, json=_hook(rid=cid))
    assert r.status_code == 200
    assert r.json()["new_status"] == "ESCROW_LOCKED"

    from app.models import Contract

    assert db.get(Contract, cid).status == "ESCROW_LOCKED"


def test_store_purchase_flips_order(client):
    oid = _order(client)
    r = client.post(URL, json=_hook(ref="TXN-2", ptype="STORE_PURCHASE", rid=oid))
    assert r.status_code == 200
    assert r.json()["new_status"] == "PAID_PROCESSING"


def test_duplicate_reference_is_idempotent(client):
    cid = _contract(client)
    assert client.post(URL, json=_hook(rid=cid)).status_code == 200
    again = client.post(URL, json=_hook(rid=cid))
    assert again.status_code == 200
    assert "Duplicate" in again.json()["detail"]


def test_failed_transaction_does_not_change_state(client):
    cid = _contract(client)
    r = client.post(URL, json=_hook(rid=cid, status="FAILED"))
    assert r.status_code == 200
    assert r.json()["new_status"] == "PENDING_PAYMENT"


def test_unknown_reference_id_returns_404(client):
    assert client.post(URL, json=_hook(rid=999)).status_code == 404


def test_second_payment_for_locked_contract_conflicts(client):
    cid = _contract(client)
    client.post(URL, json=_hook(ref="A", rid=cid))
    assert client.post(URL, json=_hook(ref="B", rid=cid)).status_code == 409


def test_invalid_payment_type_rejected(client):
    assert client.post(URL, json=_hook(ptype="REFUND")).status_code == 422


def test_shared_secret_enforced_when_configured(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "webhook_shared_secret", "topsecret")
    cid = _contract(client)
    assert client.post(URL, json=_hook(rid=cid)).status_code == 401
    ok = client.post(URL, json=_hook(rid=cid), headers={"X-Webhook-Secret": "topsecret"})
    assert ok.status_code == 200
