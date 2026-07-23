"""
POST /chat          — надіслати повідомлення агенту, отримати відповідь
GET  /chat/history   — вся історія (для рендеру сторінки чату при завантаженні)
"""

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from models.database import ChatMessage, get_db
from services import gemini_agent

router = APIRouter()


@router.post("/chat")
def send_message(message: str = Form(...), db: Session = Depends(get_db)):
    message = message.strip()
    if not message:
        raise HTTPException(
            status_code=400, detail="Порожнє повідомлення")

    if message.lower() in {"done", "i'm done", "im done", "finished"}:
        reply = gemini_agent.forward_remaining_tasks(db)
        return {"ok": True, "reply": reply, "quick_replies": []}

    result = gemini_agent.chat(db, message)
    return {"ok": True, "reply": result["reply"], "quick_replies": result["quick_replies"]}


@router.get("/chat/history")
def get_history(db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).order_by(
        ChatMessage.created_at.asc()).all()
    return {
        "messages": [
            {"role": m.role, "content": m.content} for m in messages
        ]
    }
