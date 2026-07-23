import httpx
import time
import logging

# Імпортуємо ваш ключ безпосередньо з налаштувань проєкту
from core.config import settings

# Налаштовуємо простий вивід логів у консоль
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - LOG: %(message)s")

# Беремо ключ з вашого .env файлу через Pydantic
API_KEY = settings.gemini_api_key


def fetch_google_models():
    if not API_KEY:
        logging.error(
            "Ключ API не знайдено! Перевірте ваш файл .env.")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

    logging.info(
        "Формуємо запит до серверів Google (API v1beta)...")

    # Фіксуємо час перед відправкою
    start_time = time.time()
    logging.info(
        ">>> Запит пішов у мережу! Чекаємо на відповідь...")

    with httpx.Client() as client:
        response = client.get(url)

    # Фіксуємо час після отримання відповіді
    end_time = time.time()
    duration = end_time - start_time
    logging.info(
        f"<<< Відповідь отримано! Це зайняло {duration:.2f} секунд.\n")

    # Обробляємо та виводимо результати
    if response.status_code == 200:
        data = response.json()
        print(
            "=== ДОСТУПНІ МОДЕЛІ ДЛЯ ГЕНЕРАЦІЇ ТЕКСТУ ===")
        for model in data.get("models", []):
            if "generateContent" in model.get("supportedGenerationMethods", []):
                clean_name = model['name'].replace('models/', '')
                print(f"🔹 {clean_name}")
        print("============================================")
    else:
        logging.error(
            f"Сталася помилка (Код {response.status_code}): {response.text}")


if __name__ == "__main__":
    fetch_google_models()
