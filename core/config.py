"""
Централізовані налаштування проєкту.
Значення підтягуються з .env (див. .env.example).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    database_url: str = "sqlite:///./planner.db"

    # Gemini — рушій чат-агента (створення/перепланування задач)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"

    # захист від перепланування — ядро продукту, тому винесено в конфіг,
    # а не захардкожено в роутері
    daily_main_tasks_limit: int = 3
    daily_minor_tasks_limit: int = 10

    # 8 категорій Колеса Балансу — англійською (UI має бути англомовним)
    wheel_categories: list[str] = [
        "Health",
        "Relationships",
        "Environment",
        "Career & Purpose",
        "Finances",
        "Personal Growth",
        "Fun & Recreation",
        "Spirituality",
    ]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8")


settings = Settings()
