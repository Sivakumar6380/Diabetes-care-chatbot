from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth, database

router = APIRouter(prefix="/health", tags=["health"])

@router.post("/symptoms", response_model=schemas.Symptom)
def log_symptoms(
    symptom: schemas.SymptomCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Basic prediction logic (mock)
    prediction = "General fatigue"
    if "fever" in symptom.symptoms_text.lower():
        prediction = "Possible Viral Infection"
    
    db_symptom = models.Symptom(
        user_id=current_user.id,
        symptoms_text=symptom.symptoms_text,
        prediction=prediction
    )
    db.add(db_symptom)
    db.commit()
    db.refresh(db_symptom)
    return db_symptom

@router.get("/history", response_model=List[schemas.Symptom])
def get_symptom_history(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Symptom).filter(models.Symptom.user_id == current_user.id).all()
