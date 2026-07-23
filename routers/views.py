"""
Ендпоінти для рендерингу HTML-шаблонів (Jinja2) + невеликий JSON API,
яким користується app.js, щоб оновлювати праву панель (задачі) і
Колесо Балансу одразу після відповіді чат-агента, без перезавантаження
сторінки.
"""

from datetime import date, datetime

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from models.database import Task, get_db

router = APIRouter()

templates = Jinja2Templates(directory="templates")


def _serialize_task(t: Task) -> dict:
    return {
        "id": t.id,
        "title": t.title,
        "priority": t.priority.value,
        "estimated_time": t.estimated_time,
        "is_top_task": t.is_top_task,
        "reschedule_reason": t.reschedule_reason,
        "completed": t.completed,
        "deadline": t.deadline.isoformat() if t.deadline else None,
        "scheduled_time": t.scheduled_time.isoformat() if t.scheduled_time else None,
    }


def _auto_forward_overdue(db: Session) -> None:
    """Missed-deadline tasks are pulled back into today so they aren't lost."""
    today = date.today()
    overdue = db.query(Task).filter(
        Task.is_today.is_(True),
        Task.completed.is_(False),
        Task.deadline.isnot(None),
        Task.deadline < today,
    ).all()
    for t in overdue:
        t.deadline = today
        t.reschedule_reason = "Auto-forwarded: missed deadline"
    if overdue:
        db.commit()


def _collect_today(db: Session) -> dict:
    _auto_forward_overdue(db)
    today_tasks = db.query(Task).filter(Task.is_today.is_(True)).all()

    top_tasks = [
        t for t in today_tasks if t.is_top_task and not t.completed]
    minor_tasks = [
        t for t in today_tasks if not t.is_top_task and not t.completed]
    completed_tasks = [t for t in today_tasks if t.completed]

    now = datetime.now()
    upcoming = [
        t for t in today_tasks
        if t.scheduled_time and not t.completed and t.scheduled_time >= now
    ]
    next_notification = min(upcoming, key=lambda t: t.scheduled_time) if upcoming else None

    return {
        "top_tasks": top_tasks,
        "minor_tasks": minor_tasks,
        "completed_tasks": completed_tasks,
        "next_notification": next_notification,
    }


@router.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    """Головна (і єдина) сторінка нашого застосунку."""
    ctx = _collect_today(db)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "page_title": "TODAY",
            "is_today": True,
            **ctx,
        }
    )


@router.get("/api/today")
def api_today(db: Session = Depends(get_db)):
    """
    JSON-версія тих самих даних, що й на / — використовується app.js,
    щоб перемалювати список задач після того, як агент у чаті
    щось створив/переніс, без перезавантаження всієї сторінки.
    """
    ctx = _collect_today(db)
    return {
        "top_tasks": [_serialize_task(t) for t in ctx["top_tasks"]],
        "minor_tasks": [_serialize_task(t) for t in ctx["minor_tasks"]],
        "completed_tasks": [_serialize_task(t) for t in ctx["completed_tasks"]],
    }
