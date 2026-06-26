#!/usr/bin/env python
"""
Reset database schema and load mock data from CSV files.
Usage: python data/load_mock_data.py
"""

import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
DATA_DIR = Path(__file__).parent

from app.database import SessionLocal, engine, Base
from app.models.user import Agent, Admin, UserRole
from app.models.listing import Listing
from app.models.lead import Lead, LeadStatus


def reset_database():
    """Drop and recreate all tables so seeding starts from a clean state."""
    print("Resetting database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✓ Database schema reset complete")


def load_agents():
    """Load agents from agents.csv"""
    db = SessionLocal()
    try:
        agents_file = DATA_DIR / "agents.csv"
        with open(agents_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                agent = Agent(
                    email=row["email"],
                    full_name=row["full_name"],
                    hashed_password=row["hashed_password"],
                    role=UserRole.AGENT,
                    is_active=int(row["is_active"]),
                )
                db.add(agent)

        db.commit()
        print(f"✓ Loaded {db.query(Agent).count()} agents")
    finally:
        db.close()


def load_admins():
    """Load admins from admins.csv"""
    db = SessionLocal()
    try:
        admins_file = DATA_DIR / "admins.csv"
        with open(admins_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                admin = Admin(
                    email=row["email"],
                    full_name=row["full_name"],
                    hashed_password=row["hashed_password"],
                    role=UserRole.ADMIN,
                    is_active=int(row["is_active"]),
                )
                db.add(admin)

        db.commit()
        print(f"✓ Loaded {db.query(Admin).count()} admins")
    finally:
        db.close()


def load_listings():
    """Load listings from listings.csv"""
    db = SessionLocal()
    try:
        listings_file = DATA_DIR / "listings.csv"
        with open(listings_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                listing = Listing(
                    title=row["title"],
                    description=row["description"],
                    address=row["address"],
                    price=float(row["price"]),
                    bedrooms=int(row["bedrooms"]),
                    bathrooms=int(row["bathrooms"]),
                    square_feet=float(row["square_feet"])
                    if row["square_feet"]
                    else None,
                    listing_type=row["listing_type"],
                    is_active=int(row["is_active"]),
                )
                db.add(listing)

        db.commit()
        print(f"✓ Loaded {db.query(Listing).count()} listings")
    finally:
        db.close()


def load_leads():
    """Load leads from leads.csv"""
    db = SessionLocal()
    try:
        leads_file = DATA_DIR / "leads.csv"
        with open(leads_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lead = Lead(
                    client_name=row["client_name"],
                    client_email=row["client_email"],
                    client_phone=row["client_phone"],
                    listing_id=int(row["listing_id"]),
                    message=row["message"],
                    status=LeadStatus(row["status"]),
                    assigned_agent_id=int(row["assigned_agent_id"])
                    if row["assigned_agent_id"]
                    else None,
                    notes=row["notes"],
                )
                db.add(lead)

        db.commit()
        print(f"✓ Loaded {db.query(Lead).count()} leads")
    finally:
        db.close()


def main():
    print("Resetting and loading mock data into database...")
    print()

    try:
        reset_database()
        load_agents()
        load_admins()
        load_listings()
        load_leads()
        print()
        print("✓ All mock data loaded successfully!")
    except Exception as e:
        print(f"✗ Error loading mock data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
