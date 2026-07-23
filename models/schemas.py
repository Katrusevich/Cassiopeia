"""Pydantic request/response bodies (separate from the SQLAlchemy models in database.py)."""

from pydantic import BaseModel


class TaskDoneUpdate(BaseModel):
    done: bool


class TaskTimeLog(BaseModel):
    actual_minutes: int
    task_type: str | None = None


class QuickTaskCreate(BaseModel):
    title: str
    is_top_task: bool = False
    scheduled_time: str | None = None  # "HH:MM"
    priority: str = "medium"
