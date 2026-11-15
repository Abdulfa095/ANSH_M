from sqlalchemy import Column, Integer, String, DateTime
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AlertSubscription(Base):
    __tablename__ = "alert_subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String, index=True, nullable=False)
    commodity = Column(String, nullable=False)
    state = Column(String, nullable=False)
    mandi = Column(String, nullable=False)
    taluk = Column(String)
    district = Column(String)
    language = Column(String, default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
