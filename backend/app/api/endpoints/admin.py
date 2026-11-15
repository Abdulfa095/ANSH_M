from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import crud

router = APIRouter()

@router.get("/registrations")
async def get_all_registrations(db: Session = Depends(get_db)):
    # In a real app, this would be protected by an admin role check
    return crud.get_all_alert_subscriptions(db)

@router.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    users = crud.get_all_users(db)
    # Remove hashed passwords before returning
    users_data = []
    for user in users:
        u_dict = {
            "id": user.id,
            "name": user.name,
            "phone": user.phone,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        users_data.append(u_dict)
    return users_data

@router.delete("/registrations/{phone}")
async def delete_registration(phone: str, commodity: str, db: Session = Depends(get_db)):
    if crud.delete_alert_subscription(db, phone, commodity):
        return {"message": "Registration deleted"}
    else:
        raise HTTPException(status_code=404, detail="Registration not found")
