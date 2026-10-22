"""Seed demo users so GET /api/v1/users/profile/{id} works out of the box.

Run from the project root:  python -m scripts.seed
Optionally upload a real blueprint:  python -m scripts.seed --blueprint path/to/plan.pdf
"""
import argparse
from pathlib import Path

from app.database import SessionLocal
from app.models import User
from app.services import storage

DEMO_USERS = [
    {"id": 4, "name": "Alex Mukasa", "role": "Civil Engineer", "key": "user-4/foundation-plan.pdf"},
    {"id": 12, "name": "Luweero Property Developers Ltd", "role": "Contractor", "key": None},
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blueprint", type=Path, help="PDF to upload to the configured bucket for user 4")
    args = parser.parse_args()

    if args.blueprint:
        with args.blueprint.open("rb") as fh:
            storage.upload_blueprint(DEMO_USERS[0]["key"], fh)
        print(f"Uploaded blueprint as {DEMO_USERS[0]['key']}")

    with SessionLocal() as db:
        for u in DEMO_USERS:
            if db.get(User, u["id"]) is None:
                db.add(User(id=u["id"], name=u["name"], role=u["role"], blueprint_object_key=u["key"]))
        db.commit()
    print("Seeded demo users (4, 12).")


if __name__ == "__main__":
    main()
