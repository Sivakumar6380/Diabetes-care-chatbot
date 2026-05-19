from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth, database

router = APIRouter(prefix="/reminders", tags=["reminders"])

@router.post("/", response_model=schemas.Reminder)
def add_reminder(
    reminder: schemas.ReminderCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_reminder = models.Reminder(
        user_id=current_user.id,
        reminder_type=reminder.reminder_type,
        title=reminder.title,
        dosage=reminder.dosage,
        reminder_time=reminder.reminder_time,
        frequency=reminder.frequency,
        meal_timing=reminder.meal_timing,
        status=reminder.status
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@router.get("/", response_model=List[schemas.Reminder])
def get_reminders(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Reminder).filter(models.Reminder.user_id == current_user.id).all()

@router.patch("/{reminder_id}", response_model=schemas.Reminder)
def update_reminder_status(
    reminder_id: int,
    update: schemas.ReminderUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_reminder = db.query(models.Reminder).filter(
        models.Reminder.id == reminder_id, 
        models.Reminder.user_id == current_user.id
    ).first()
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    db_reminder.status = update.status
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@router.delete("/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_reminder = db.query(models.Reminder).filter(
        models.Reminder.id == reminder_id, 
        models.Reminder.user_id == current_user.id
    ).first()
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(db_reminder)
    db.commit()
    return {"message": "Reminder deleted"}
