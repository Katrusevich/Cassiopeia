"""
Схема БД (одна таблиця `tasks`, як описано в PRD, розділ 5)
+ engine/сесія для SQLite.
"""

import enum
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
    create_engine,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from core.config import settings


class Base(DeclarativeBase):
    pass


class Priority(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Status(str, enum.Enum):
    inbox = "inbox"
    today = "today"
    done = "done"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority), default=Priority.medium, index=True
    )
    estimated_time: Mapped[int] = mapped_column(Integer, default=30)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_today: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_top_task: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True)
    status: Mapped[Status] = mapped_column(
        Enum(Status), default=Status.inbox, index=True
    )
    # НОВЕ: явний прапорець "виконано" для чекбоксів Today-панелі
    # (окремо від status, який ще й керує inbox/today workflow)
    completed: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True)
    # НОВЕ: точний час (не тільки дата) для сповіщень "час завдання настав"
    scheduled_time: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True)
    # НОВЕ: для Task Tracker — фактичний час виконання + тип задачі
    actual_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True)
    task_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now())

    # НОВЕ: прив'язка до категорії Колеса Балансу (впливає на пріоритизацію
    # агентом — задачі з "провислих" категорій підважуються при плануванні)
    wheel_category: Mapped[str | None] = mapped_column(
        String(50), nullable=True)

    # НОВЕ: якщо задачу зсунув агент через форс-мажор — тут коротке
    # пояснення "чому", яке показується у Today ("перенесено, бо...")
    reschedule_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Task id={self.id} title={self.title!r} status={self.status}>"


class WheelScore(Base):
    """
    Колесо Балансу: одна оцінка (1-9) на категорію.
    Немає user_id — MVP однокористувацький, як і решта таблиць.
    Оновлюється виключно через чат-агента (tool update_wheel_score).
    """

    __tablename__ = "wheel_scores"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=5)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class VisionMission(Base):
    """Singleton row: the user's personal "why" — shown on the Vision & Mission page."""

    __tablename__ = "vision_mission"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class ChatMessage(Base):
    """
    Історія чату — потрібна, щоб агент бачив контекст попередніх
    повідомлень (наприклад, "мій фокус — Кар'єра" з макета) при кожному
    новому виклику Gemini.
    """

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(20))  # "user" | "model"
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now())


# --- engine / session ---------------------------------------------------

engine = create_engine(
    settings.database_url,
    # потрібно лише для SQLite
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _ensure_task_columns() -> None:
    """
    create_all() only creates missing TABLES, not missing COLUMNS on a
    table that already exists on disk. `completed`/`scheduled_time` were
    added after planner.db already had rows, so add them by hand and
    backfill `completed` from the pre-existing status field.
    """
    with engine.begin() as conn:
        existing_cols = {
            row[1] for row in conn.execute(text("PRAGMA table_info(tasks)"))
        }
        if "completed" not in existing_cols:
            conn.execute(
                text("ALTER TABLE tasks ADD COLUMN completed BOOLEAN DEFAULT 0"))
            conn.execute(
                text("UPDATE tasks SET completed = 1 WHERE status = 'done'"))
        if "scheduled_time" not in existing_cols:
            conn.execute(
                text("ALTER TABLE tasks ADD COLUMN scheduled_time DATETIME"))
        if "actual_minutes" not in existing_cols:
            conn.execute(
                text("ALTER TABLE tasks ADD COLUMN actual_minutes INTEGER"))
        if "task_type" not in existing_cols:
            conn.execute(
                text("ALTER TABLE tasks ADD COLUMN task_type VARCHAR(50)"))


_WHEEL_CATEGORY_TRANSLATIONS = {
    "Здоров'я": "Health",
    "Стосунки": "Relationships",
    "Оточення": "Environment",
    "Покликання": "Career & Purpose",
    "Забезпеченість": "Finances",
    "Самовдосконалення": "Personal Growth",
    "Яскравість життя": "Fun & Recreation",
    "Духовність": "Spirituality",
}


def _ensure_wheel_categories_translated() -> None:
    """wheel_categories moved from Ukrainian to English labels — rename any
    existing rows so previously-entered scores aren't orphaned."""
    with engine.begin() as conn:
        for old, new in _WHEEL_CATEGORY_TRANSLATIONS.items():
            conn.execute(
                text("UPDATE wheel_scores SET category = :new WHERE category = :old"),
                {"new": new, "old": old},
            )


def init_db() -> None:
    """Створює таблиці, якщо їх ще немає. Викликається при старті main.py."""
    Base.metadata.create_all(bind=engine)
    _ensure_task_columns()
    _ensure_wheel_categories_translated()


def get_db():
    """FastAPI dependency: видає сесію і гарантовано закриває її."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
