"""
Головний файл застосунку "Old Money Planner".
Збирає всі компоненти, ініціалізує базу даних та запускає сервер.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from models.database import init_db
from routers import chat, pages, tasks, views, wheel


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Логіка, що виконується при запуску сервера
    print("Ініціалізація бази даних...")
    init_db()
    print("База даних готова.")
    yield
    # Логіка, що виконується при зупинці сервера (якщо потрібно)


app = FastAPI(
    title="Cassiopeia",
    description="Елегантний планувальник завдань з ШІ-агентом",
    version="1.0.0",
    lifespan=lifespan
)

# 1. Підключаємо роутери API та веб-сторінок
app.include_router(views.router)  # Головна сторінка (GET /)
# Чат-агент (POST /chat, GET /chat/history)
app.include_router(chat.router)
app.include_router(wheel.router)  # Колесо Балансу (GET /wheel)
app.include_router(tasks.router)  # PATCH/POST /api/tasks/{id}/...
app.include_router(pages.router)  # /vision, /week, /month, /year, /tracker

# 2. Монтуємо папку зі статикою (CSS, JS, зображення)
# Важливо: це має йти після роутерів, щоб уникнути конфліктів шляхів
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    # Запуск локального сервера для розробки
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
