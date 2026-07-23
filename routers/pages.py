"""
Standalone pages outside the "/" SPA: Vision & Mission, Week/Month/Year
calendars (+ per-day detail view), Task Tracker.
"""

import calendar
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from models.database import Task, VisionMission, get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _top_tasks_for_day(db: Session, day: date, limit: int = 3) -> list[Task]:
    tasks = db.query(Task).filter(Task.deadline == day).all()
    tasks.sort(key=lambda t: (not t.is_top_task, _PRIORITY_ORDER.get(t.priority.value, 3)))
    return tasks[:limit]


# --- Vision & Mission -----------------------------------------------------

@router.get("/vision")
def vision_page(request: Request, db: Session = Depends(get_db)):
    row = db.query(VisionMission).first()
    return templates.TemplateResponse("pages/vision.html", {
        "request": request,
        "content": row.content if row else "",
        "active_page": "vision",
    })


@router.post("/vision")
def save_vision(content: str = Form(...), db: Session = Depends(get_db)):
    row = db.query(VisionMission).first()
    if row:
        row.content = content
    else:
        db.add(VisionMission(content=content))
    db.commit()
    return RedirectResponse(url="/vision", status_code=303)


# --- Day detail (shares the Today layout) ----------------------------------

@router.get("/day/{date_str}")
def day_page(date_str: str, request: Request, db: Session = Depends(get_db)):
    try:
        day = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid date")

    tasks = db.query(Task).filter(Task.deadline == day).all()
    top_tasks = [t for t in tasks if t.is_top_task and not t.completed]
    minor_tasks = [t for t in tasks if not t.is_top_task and not t.completed]
    is_today = day == date.today()

    next_notification = None
    if is_today:
        now = datetime.now()
        upcoming = [t for t in tasks if t.scheduled_time and not t.completed and t.scheduled_time >= now]
        next_notification = min(upcoming, key=lambda t: t.scheduled_time) if upcoming else None

    return templates.TemplateResponse("pages/day.html", {
        "request": request,
        "page_title": day.strftime("%A, %B %d").upper(),
        "top_tasks": top_tasks,
        "minor_tasks": minor_tasks,
        "is_today": is_today,
        "next_notification": next_notification,
        "active_page": "today" if is_today else None,
    })


# --- Week -------------------------------------------------------------------

@router.get("/week")
def week_page(request: Request, d: str | None = None, db: Session = Depends(get_db)):
    anchor = datetime.strptime(d, "%Y-%m-%d").date() if d else date.today()
    monday = anchor - timedelta(days=anchor.weekday())

    days = []
    for i in range(7):
        day = monday + timedelta(days=i)
        days.append({
            "date": day.isoformat(),
            "label": day.strftime("%a"),
            "day_num": day.day,
            "tasks": _top_tasks_for_day(db, day),
            "is_today": day == date.today(),
        })

    return templates.TemplateResponse("pages/week.html", {
        "request": request,
        "days": days,
        "range_label": f"{monday.strftime('%b %d')} – {(monday + timedelta(days=6)).strftime('%b %d, %Y')}",
        "prev_week": (monday - timedelta(days=7)).isoformat(),
        "next_week": (monday + timedelta(days=7)).isoformat(),
        "active_page": "week",
    })


# --- Month --------------------------------------------------------------

@router.get("/month")
def month_page(request: Request, y: int | None = None, m: int | None = None, db: Session = Depends(get_db)):
    today = date.today()
    year, month = y or today.year, m or today.month

    cal = calendar.Calendar(firstweekday=0)  # Monday
    weeks = []
    for week in cal.monthdayscalendar(year, month):
        week_cells = []
        for day_num in week:
            if day_num == 0:
                week_cells.append(None)
                continue
            day = date(year, month, day_num)
            week_cells.append({
                "date": day.isoformat(),
                "day_num": day_num,
                "tasks": _top_tasks_for_day(db, day, limit=2),
                "is_today": day == today,
            })
        weeks.append(week_cells)

    prev_month = (date(year, month, 1) - timedelta(days=1))
    next_month = (date(year, month, calendar.monthrange(year, month)[1]) + timedelta(days=1))

    return templates.TemplateResponse("pages/month.html", {
        "request": request,
        "weeks": weeks,
        "month_label": date(year, month, 1).strftime("%B %Y"),
        "prev_month": {"y": prev_month.year, "m": prev_month.month},
        "next_month": {"y": next_month.year, "m": next_month.month},
        "active_page": "month",
    })


# --- Year -----------------------------------------------------------------

@router.get("/year")
def year_page(request: Request, y: int | None = None, db: Session = Depends(get_db)):
    today = date.today()
    year = y or today.year

    months = []
    for m in range(1, 13):
        start = date(year, m, 1)
        end = date(year, m, calendar.monthrange(year, m)[1])
        count = db.query(Task).filter(Task.deadline >= start, Task.deadline <= end).count()
        months.append({
            "num": m,
            "name": start.strftime("%B"),
            "count": count,
            "is_current": (year, m) == (today.year, today.month),
        })

    return templates.TemplateResponse("pages/year.html", {
        "request": request,
        "year": year,
        "months": months,
        "prev_year": year - 1,
        "next_year": year + 1,
        "active_page": "year",
    })


# --- Task Tracker -----------------------------------------------------------

@router.get("/tracker")
def tracker_page(request: Request, db: Session = Depends(get_db)):
    loggable = (
        db.query(Task)
        .filter(Task.is_today.is_(True), Task.actual_minutes.is_(None))
        .all()
    )
    logged = (
        db.query(Task)
        .filter(Task.actual_minutes.isnot(None))
        .order_by(Task.id.desc())
        .limit(20)
        .all()
    )
    return templates.TemplateResponse("pages/tracker.html", {
        "request": request,
        "loggable": loggable,
        "logged": logged,
        "active_page": "tracker",
    })
