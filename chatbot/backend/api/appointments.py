from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth, database

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("/", response_model=schemas.Appointment)
def book_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_appointment = models.Appointment(
        user_id=current_user.id,
        doctor_name=appointment.doctor_name,
        appointment_time=appointment.appointment_time
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.get("/", response_model=List[schemas.Appointment])
def get_appointments(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Appointment).filter(models.Appointment.user_id == current_user.id).all()
