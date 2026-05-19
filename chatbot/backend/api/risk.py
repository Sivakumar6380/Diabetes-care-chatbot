from fastapi import APIRouter, Depends
from .. import models, schemas, auth
from ..services.ai_service import ai_service

router = APIRouter(prefix="/risk", tags=["risk"])

@router.post("/predict")
async def predict_risk(
    data: schemas.RiskData,
    current_user: models.User = Depends(auth.get_current_user)
):
    result = ai_service.predict_readmission_risk(data.dict())
    return result
