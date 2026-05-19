from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth, database

router = APIRouter(prefix="/glucose", tags=["glucose"])

@router.post("/", response_model=schemas.GlucoseReading)
def create_glucose_reading(
    reading: schemas.GlucoseReadingCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_reading = models.GlucoseReading(**reading.dict(), user_id=current_user.id)
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

@router.get("/", response_model=List[schemas.GlucoseReading])
def read_glucose_readings(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.GlucoseReading).filter(models.GlucoseReading.user_id == current_user.id).order_by(models.GlucoseReading.timestamp.desc()).all()

@router.get("/latest", response_model=schemas.GlucoseReading)
def read_latest_glucose_reading(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    reading = db.query(models.GlucoseReading).filter(models.GlucoseReading.user_id == current_user.id).order_by(models.GlucoseReading.timestamp.desc()).first()
    if not reading:
        raise HTTPException(status_code=404, detail="No readings found")
    return reading

@router.delete("/", status_code=204)
def clear_glucose_readings(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db.query(models.GlucoseReading).filter(models.GlucoseReading.user_id == current_user.id).delete()
    db.commit()
    return None
