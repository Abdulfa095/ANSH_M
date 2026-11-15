import json
import os
import sys

# Define path to the project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine
from app.db import models
from datetime import datetime

# Create tables
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Migrate Users
print("Migrating Users...")
users_path = os.path.join(os.path.dirname(__file__), "app", "data", "users.json")
if os.path.exists(users_path):
    with open(users_path, "r", encoding="utf-8") as f:
        try:
            users_data = json.load(f)
            for u in users_data:
                # Check if exists
                existing = db.query(models.User).filter(models.User.phone == u.get("phone")).first()
                if not existing:
                    new_user = models.User(
                        name=u.get("name"),
                        phone=u.get("phone"),
                        hashed_password=u.get("password_hash"),
                        # role=u.get("role", "user"),
                        created_at=datetime.fromisoformat(u.get("created_at") or datetime.now().isoformat())
                    )
                    db.add(new_user)
            db.commit()
            print(f"Migrated users.")
        except Exception as e:
            print(f"Error migrating users: {e}")

# Migrate Subscriptions
print("Migrating Subscriptions...")
regs_path = os.path.join(os.path.dirname(__file__), "app", "data", "registrations.json")
if os.path.exists(regs_path):
    with open(regs_path, "r", encoding="utf-8") as f:
        try:
            regs_data = json.load(f)
            for r in regs_data:
                # Check if exists
                existing = db.query(models.AlertSubscription).filter(
                    models.AlertSubscription.phone == r.get("phone"),
                    models.AlertSubscription.commodity == r.get("commodity")
                ).first()
                
                if not existing:
                    new_sub = models.AlertSubscription(
                        name=r.get("name"),
                        phone=r.get("phone"),
                        commodity=r.get("commodity"),
                        mandi=r.get("mandi") or "Unknown",
                        taluk=r.get("taluk"),
                        district=r.get("district"),
                        state=r.get("state"),
                        language=r.get("language", "en"),
                        created_at=datetime.fromisoformat(r.get("timestamp") or datetime.now().isoformat())
                    )
                    db.add(new_sub)
            db.commit()
            print(f"Migrated subscriptions.")
        except Exception as e:
            print(f"Error migrating subscriptions: {e}")

db.close()
print("Migration complete!")
