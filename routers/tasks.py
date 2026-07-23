"""
PATCH /api/tasks/{id}/done    — toggle the "completed" checkbox on Today panel
POST  /api/tasks/{id}/forward — push an overdue task to the next day
"""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.database import Priority, Status, Task, get_db
from models.schemas import QuickTaskCreate, TaskDoneUpdate, TaskTimeLog

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/quick-add")
def quick_add_task(payload: QuickTaskCreate, db: Session = Depends(get_db)):
    """Bypasses chat for fast, no-friction task entry (Today panel "+ Add Task")."""
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title is required")

    today = date.today()
    scheduled_dt = None
    if payload.scheduled_time:
        try:
            hh, mm = (int(p) for p in payload.scheduled_time.split(":"))
            scheduled_dt = datetime.combine(today, datetime.min.time()).replace(hour=hh, minute=mm)
        except (ValueError, TypeError):
            scheduled_dt = None

    priority = payload.priority if payload.priority in Priority._value2member_map_ else "medium"

    task = Task(
        raw_input=title,
        title=title,
        priority=Priority(priority),
        estimated_time=30,
        deadline=today,
        scheduled_time=scheduled_dt,
        is_today=True,
        is_top_task=payload.is_top_task,
        status=Status.today,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"ok": True, "id": task.id, "title": task.title}


@router.patch("/{task_id}/done")
def set_task_done(task_id: int, payload: TaskDoneUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = payload.done
    task.status = Status.done if payload.done else Status.today
    db.commit()
    return {"ok": True, "id": task.id, "completed": task.completed}


@router.post("/{task_id}/forward")
def forward_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    today = date.today()
    base_date = task.deadline if task.deadline and task.deadline >= today else today
    new_deadline = base_date + timedelta(days=1)

    if task.scheduled_time:
        task.scheduled_time = datetime.combine(new_deadline, task.scheduled_time.time())
    task.deadline = new_deadline
    task.is_today = False
    task.reschedule_reason = "Auto-forwarded: missed deadline"
    db.commit()
    return {"ok": True, "id": task.id, "new_deadline": task.deadline.isoformat()}


@router.patch("/{task_id}/log-time")
def log_task_time(task_id: int, payload: TaskTimeLog, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.actual_minutes = payload.actual_minutes
    if payload.task_type:
        task.task_type = payload.task_type
    db.commit()
    return {"ok": True, "id": task.id, "actual_minutes": task.actual_minutes, "task_type": task.task_type}


@router.get("/tracker-stats")
def tracker_stats(db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.actual_minutes.isnot(None)).all()
    items = [
        {
            "id": t.id,
            "title": t.title,
            "task_type": t.task_type,
            "estimated_minutes": t.estimated_time,
            "actual_minutes": t.actual_minutes,
            "efficiency_pct": round(t.estimated_time / t.actual_minutes * 100)
            if t.actual_minutes else None,
        }
        for t in tasks
    ]
    return {"tasks": items}
