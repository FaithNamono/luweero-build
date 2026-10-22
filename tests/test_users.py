from app.models import User


def test_profile_has_trust_badges_and_blueprint_url(client, db):
    db.add(User(id=4, name="Alex Mukasa", role="Civil Engineer", blueprint_object_key="user-4/foundation-plan.pdf"))
    db.commit()

    r = client.get("/api/v1/users/profile/4")
    assert r.status_code == 200
    assert r.json() == {
        "user_id": 4,
        "name": "Alex Mukasa",
        "role": "Civil Engineer",
        "is_identity_verified_by_laboremus": True,
        "is_credentials_verified_by_verify_ug": True,
        "cloud_storage_blueprint_url": "https://storage.example.test/blueprints/user-4/foundation-plan.pdf",
    }


def test_profile_without_blueprint_returns_null_url(client, db):
    db.add(User(id=5, name="No Plans", role="Civil Engineer"))
    db.commit()
    assert client.get("/api/v1/users/profile/5").json()["cloud_storage_blueprint_url"] is None


def test_unknown_user_404(client):
    assert client.get("/api/v1/users/profile/404").status_code == 404
