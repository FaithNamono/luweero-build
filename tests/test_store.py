ORDER = {
    "contractor_id": 12,
    "delivery_site_location": "Wobulenzi, Luweero",
    "items": [
        {"product_id": 101, "product_name": "Tororo Cement Bag", "quantity": 50, "unit_price_ugx": 32000},
        {"product_id": 204, "product_name": "Electrical Conduit Pipe", "quantity": 15, "unit_price_ugx": 8500},
    ],
}


def test_order_total_and_lines(client):
    r = client.post("/api/v1/store/order", json=ORDER)
    assert r.status_code == 201
    body = r.json()
    # 50 * 32,000 + 15 * 8,500 = 1,600,000 + 127,500
    assert body["total_ugx"] == 1_727_500
    assert body["status"] == "AWAITING_FULFILLMENT"
    assert [i["line_total_ugx"] for i in body["items"]] == [1_600_000, 127_500]


def test_empty_items_rejected(client):
    r = client.post("/api/v1/store/order", json={**ORDER, "items": []})
    assert r.status_code == 422


def test_zero_quantity_rejected(client):
    bad = {**ORDER, "items": [{**ORDER["items"][0], "quantity": 0}]}
    assert client.post("/api/v1/store/order", json=bad).status_code == 422
