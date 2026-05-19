from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, auth, database
from ..services.ai_service import ai_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=dict)
async def chat_with_ai(
    message: str, 
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. Store user message
    user_msg = models.ChatMessage(user_id=current_user.id, role="user", content=message)
    db.add(user_msg)
    
    # 2. Fetch recent history for memory (last 10 messages)
    history = db.query(models.ChatMessage)\
        .filter(models.ChatMessage.user_id == current_user.id)\
        .order_by(models.ChatMessage.timestamp.desc())\
        .limit(10)\
        .all()
    history.reverse() # Back to chronological order
    
    # 3. Fetch latest health context
    latest_readings = db.query(models.GlucoseReading)\
        .filter(models.GlucoseReading.user_id == current_user.id)\
        .order_by(models.GlucoseReading.timestamp.desc())\
        .limit(5)\
        .all()
    
    # 4. Get AI response with memory and personalization
    response_text = await ai_service.get_response(
        message, 
        history=history, 
        latest_readings=latest_readings
    )
    
    # 5. Store AI response
    ai_msg = models.ChatMessage(user_id=current_user.id, role="assistant", content=response_text)
    db.add(ai_msg)
    db.commit()
    
    return {"response": response_text}
