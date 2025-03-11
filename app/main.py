from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.bot import start_bot, bot  # Импортируем bot
import asyncio
import logging
import uvicorn

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Обработчик событий жизненного цикла приложения.
    """
    try:
        logger.info("Запуск FastAPI и бота...")
        asyncio.create_task(start_bot(bot))  # Передаем bot в start_bot
        yield
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")
        raise
    finally:
        logger.info("Приложение завершает работу.")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    """
    Корневой endpoint для проверки работы приложения.
    """
    return {"message": "NetBox Search Bot is running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)