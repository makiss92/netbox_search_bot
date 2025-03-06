from fastapi import FastAPI
from app.bot import start_bot
import asyncio
import logging

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

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    logger.info("Запуск FastAPI и бота...")
    asyncio.create_task(start_bot())

@app.get("/")
async def read_root():
    return {"message": "NetBox Search Bot is running!"}