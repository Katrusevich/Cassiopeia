"""
GET /wheel — поточні оцінки Колеса Балансу.
Запис відбувається ВИКЛЮЧНО через чат-агента (tool update_wheel_score
у services/gemini_agent.py) — прямого PATCH/POST тут навмисне немає,
щоб дотриматись принципу "редагувати тільки через чат" з макета.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.config import settings
from models.database import WheelScore, get_db

router = APIRouter()


@router.get("/wheel")
def get_wheel(db: Session = Depends(get_db)):
    scores = {s.category: s.score for s in db.query(WheelScore).all()}
    # гарантуємо, що в відповіді завжди всі 9 категорій, навіть якщо
    # користувач ще не заповнив частину з них через чат
    return {
        "categories": [
            {"category": cat, "score": scores.get(cat, 5)}
            for cat in settings.wheel_categories
        ]
    }