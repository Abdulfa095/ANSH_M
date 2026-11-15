from sqlalchemy.orm import Session
from . import models
from datetime import datetime

def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()

def create_user(db: Session, phone: str, name: str, hashed_password: str):
    db_user = models.User(
        phone=phone,
        name=name,
        hashed_password=hashed_password,
        created_at=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_users(db: Session):
    return db.query(models.User).all()

def create_alert_subscription(db: Session, name: str, phone: str, commodity: str, state: str, mandi: str, taluk: str = None, district: str = None, language: str = "en"):
    db_alert = models.AlertSubscription(
        name=name,
        phone=phone,
        commodity=commodity,
        state=state,
        mandi=mandi,
        taluk=taluk,
        district=district,
        language=language,
        created_at=datetime.utcnow()
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_all_alert_subscriptions(db: Session):
    return db.query(models.AlertSubscription).all()

def delete_alert_subscription(db: Session, phone: str, commodity: str):
    db_alert = db.query(models.AlertSubscription).filter(
        models.AlertSubscription.phone == phone,
        models.AlertSubscription.commodity == commodity
    ).first()
    if db_alert:
        db.delete(db_alert)
        db.commit()
        return True
    return False
