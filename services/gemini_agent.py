"""
Чат-агент на Gemini 3.6 Flash з function calling.

Ключова відмінність від старого ai_langchain.py: тут модель не просто
парсить один текст у структуру, а веде діалог і сама вирішує, який
"інструмент" викликати — створити задачу, оновити Колесо Балансу чи
перебудувати день при форс-мажорі.

Кожен виклик chat() відкриває власну DB-сесію і прив'язує до неї tools
через closure — так функції-інструменти мають прямий доступ до БД без
глобального стану.
"""

from datetime import date, datetime, timedelta

from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from core.config import settings
from models.database import ChatMessage, Priority, Status, Task, VisionMission, WheelScore

SYSTEM_INSTRUCTION = """\
Ти — асистент-планувальник "Cassiopeia". Спілкуєшся стримано,
по суті, у стилі персонального асистента "old money" (елегантно,
без зайвої фамільярності).

ТВОЇ ІНСТРУМЕНТИ:
- offer_quick_replies — коли природно запропонувати 2-4 короткі готові
  варіанти відповіді замість вільного тексту (напр. вибір фокуса
  планування, підтвердження так/ні, вибір категорії). Виклич цей
  інструмент І ТАКОЖ напиши звичайну текстову відповідь з тим самим
  питанням — кнопки лише доповнюють текст, не замінюють його.
- create_task — коли користувач називає нову задачу.
- update_wheel_score — коли користувач оцінює категорію Колеса Балансу
  (від 1 до 9) або коли ви разом проходите опитування по всіх 8
  категоріях (використовуй ТОЧНО ці англійські назви як значення
  category, навіть коли спілкуєшся українською): Health, Relationships,
  Environment, "Career & Purpose", Finances, "Personal Growth",
  "Fun & Recreation", Spirituality.
- postpone_tasks — коли користувач повідомляє про форс-мажор
  ("зустріч затягнулась", "не встигаю", "перенеси день"). Проаналізуй
  контекст задач нижче, вибери, ЩО саме реалістично прибрати з
  сьогодні (найнижчий пріоритет і задачі без жорсткого дедлайну
  переносяться першими), і виклич інструмент з коротким поясненням
  причини для кожної.

ПРАВИЛО 3: на день не може бути більше 3 головних задач одночасно.
Якщо після форс-мажору лишається вільне вікно — НЕ пропонуй заповнити
його новою головною задачею без явного прохання користувача; це
навмисне обмеження когнітивного навантаження, а не помилка.

Сьогоднішня дата: {today}.

ПОТОЧНИЙ СТАН ДНЯ (для контексту, не виводь як є, використовуй для рішень):
{today_context}

ПОТОЧНЕ КОЛЕСО БАЛАНСУ:
{wheel_context}

VISION & MISSION користувача (головна причина, чому він взагалі планує;
враховуй це, коли даєш рекомендації чи пропонуєш пріоритети):
{vision_context}

Відповідай користувачу короткими повідомленнями українською.
Якщо викликаєш інструмент — обов'язково після цього поясни користувачу
звичайною мовою, що саме змінилось.
"""


def _build_today_context(db: Session) -> str:
    tasks = (
        db.query(Task)
        .filter(Task.is_today.is_(True), Task.status != Status.done)
        .all()
    )
    if not tasks:
        return "На сьогодні задач не заплановано."
    lines = [
        f"- id={t.id} | {'[TOP]' if t.is_top_task else '[MINOR]'} {t.title} | priority={t.priority.value} | "
        f"{t.estimated_time}хв | deadline={t.deadline or '-'}"
        for t in tasks
    ]
    return "\n".join(lines)


def _build_wheel_context(db: Session) -> str:
    scores = db.query(WheelScore).all()
    if not scores:
        return "Колесо Балансу ще не заповнене."
    return ", ".join(f"{s.category}: {s.score}/9" for s in scores)


def _build_vision_context(db: Session) -> str:
    row = db.query(VisionMission).first()
    if not row or not row.content.strip():
        return "Ще не заповнено (сторінка /vision)."
    return row.content.strip()


def _make_tools(db: Session, quick_replies_box: dict) -> list:
    """
    Повертає список Python-функцій, які Gemini SDK автоматично
    перетворить на function-declarations (automatic function calling).
    Кожна функція — це фактична мутація в БД, тобто виклик tool'а
    моделлю одразу застосовується, без проміжного підтвердження.

    quick_replies_box — мутабельний "контейнер" (closure), куди
    offer_quick_replies складає варіанти відповіді, щоб chat() потім міг
    віддати їх окремо від тексту в JSON-відповіді /chat.
    """

    def offer_quick_replies(options: list[str]) -> dict:
        """Показує користувачу 2-4 кнопки швидкого вибору замість вільного тексту.

        Args:
            options: Короткі варіанти відповіді (напр. ["Career", "Health", "Personal Growth"]).
        """
        quick_replies_box["options"] = options[:4]
        return {"ok": True, "shown": True}

    def create_task(
        title: str,
        priority: str,
        estimated_time_minutes: int,
        deadline: str | None = None,
        scheduled_time: str | None = None,
        wheel_category: str | None = None,
        is_today: bool = False,
        is_top_task: bool = False,  # <-- ДОДАЛИ
    ) -> dict:
        """Створює нову задачу в Inbox (або одразу в Today, якщо is_today=True).

        Args:
            title: Коротка назва задачі, макс 8 слів.
            priority: Один з "high", "medium", "low".
            estimated_time_minutes: Орієнтовний час виконання у хвилинах.
            deadline: Дата дедлайну у форматі YYYY-MM-DD, або None.
            scheduled_time: Точний час у форматі HH:MM (24-год), якщо
                користувач його назвав (напр. "байдарки о 14:00"), інакше None.
                Потрібен для сповіщень "час завдання настав".
            wheel_category: Одна з 8 категорій Колеса Балансу, або None.
            is_today: True, якщо задачу треба одразу поставити на сьогодні.
            is_top_task: True, якщо це одна з 3 головних задач на день.
        """
        deadline_date = None
        if deadline:
            try:
                deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
            except ValueError:
                deadline_date = None

        scheduled_dt = None
        if scheduled_time and deadline_date:
            try:
                hh, mm = (int(p) for p in scheduled_time.split(":"))
                scheduled_dt = datetime.combine(deadline_date, datetime.min.time()).replace(hour=hh, minute=mm)
            except (ValueError, TypeError):
                scheduled_dt = None

        task = Task(
            raw_input=title,
            title=title,
            priority=Priority(priority) if priority in Priority._value2member_map_ else Priority.medium,
            estimated_time=estimated_time_minutes,
            deadline=deadline_date,
            scheduled_time=scheduled_dt,
            is_today=is_today,
            is_top_task=is_top_task,  # <-- ДОДАЛИ
            status=Status.today if is_today else Status.inbox,
            wheel_category=wheel_category,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return {"ok": True, "task_id": task.id, "title": task.title}

    def update_wheel_score(category: str, score: int) -> dict:
        """Оновлює оцінку однієї категорії Колеса Балансу.

        Args:
            category: Точна англійська назва категорії (напр. "Health",
                "Career & Purpose").
            score: Оцінка від 1 до 9.
        """
        score = max(1, min(9, score))
        row = db.query(WheelScore).filter(WheelScore.category == category).first()
        if row:
            row.score = score
        else:
            row = WheelScore(category=category, score=score)
            db.add(row)
        db.commit()
        return {"ok": True, "category": category, "score": score}

    def postpone_tasks(task_ids: list[int], reason: str) -> dict:
        """Переносить перелічені задачі назад в Inbox через форс-мажор.

        Args:
            task_ids: ID задач, які знімаються з сьогоднішнього плану.
            reason: Коротке пояснення причини (буде показане користувачу).
        """
        moved = []
        for tid in task_ids:
            task = db.get(Task, tid)
            if not task:
                continue
            task.is_today = False
            task.status = Status.inbox
            task.reschedule_reason = reason
            moved.append(task.id)
        db.commit()
        return {"ok": True, "moved_task_ids": moved, "reason": reason}

    return [offer_quick_replies, create_task, update_wheel_score, postpone_tasks]


def forward_remaining_tasks(db: Session) -> str:
    """User typed "done" (finished for the day) — push unfinished today-tasks to tomorrow."""
    tomorrow = date.today() + timedelta(days=1)
    tasks = (
        db.query(Task)
        .filter(Task.is_today.is_(True), Task.completed.is_(False))
        .all()
    )
    for t in tasks:
        t.is_today = False
        t.deadline = tomorrow
        t.reschedule_reason = "Auto-forwarded: day marked done"
    db.commit()

    reply = (
        f"Noted — {len(tasks)} remaining task(s) moved to tomorrow."
        if tasks else "Noted — nothing left to forward, well done."
    )
    db.add(ChatMessage(role="user", content="done"))
    db.add(ChatMessage(role="model", content=reply))
    db.commit()
    return reply


_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def chat(db: Session, user_message: str) -> dict:
    """
    Головна точка входу для POST /chat.
    1. Зберігає повідомлення користувача.
    2. Формує system-контекст з поточного стану дня та Колеса Балансу.
    3. Викликає Gemini з automatic function calling.
    4. Зберігає й повертає відповідь моделі (+ quick_replies, якщо агент
       викликав offer_quick_replies).
    """
    db.add(ChatMessage(role="user", content=user_message))
    db.commit()

    history = db.query(ChatMessage).order_by(ChatMessage.created_at.asc()).all()
    contents = [
        types.Content(
            role="user" if m.role == "user" else "model",
            parts=[types.Part(text=m.content)],
        )
        for m in history
    ]

    system_instruction = SYSTEM_INSTRUCTION.format(
        today=date.today().isoformat(),
        today_context=_build_today_context(db),
        wheel_context=_build_wheel_context(db),
        vision_context=_build_vision_context(db),
    )

    quick_replies_box: dict = {}
    client = _get_client()
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=_make_tools(db, quick_replies_box),  # automatic function calling
            temperature=0.4,
        ),
    )

    reply_text = response.text or "Готово."
    db.add(ChatMessage(role="model", content=reply_text))
    db.commit()
    return {"reply": reply_text, "quick_replies": quick_replies_box.get("options", [])}