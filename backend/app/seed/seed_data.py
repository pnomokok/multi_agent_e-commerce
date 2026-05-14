"""Run once to populate the database with demo data."""
import json
import sys
from pathlib import Path

# Allow running as: python -m app.seed.seed_data
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from app.database import SessionLocal, create_tables
from app.models.product import Product
from app.models.seller import Seller
from app.models.customer import Customer

SEED_DIR = Path(__file__).parent


def load_json(filename: str) -> list[dict]:
    return json.loads((SEED_DIR / filename).read_text(encoding="utf-8"))


def seed():
    create_tables()
    db = SessionLocal()
    try:
        if db.query(Seller).count() > 0:
            print("Database already seeded. Skipping.")
            return

        for s in load_json("sellers.json"):
            db.add(Seller(**s))

        for c in load_json("customers.json"):
            db.add(Customer(**c))

        for p in load_json("products.json"):
            db.add(Product(**p))

        db.commit()
        print(f"Seeded {db.query(Seller).count()} seller(s), "
              f"{db.query(Customer).count()} customer(s), "
              f"{db.query(Product).count()} product(s).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
