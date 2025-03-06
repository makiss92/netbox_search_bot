from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from app.netbox_client import NetBoxClient
from app.config import settings
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

bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()
netbox_client = NetBoxClient()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для поиска информации в NetBox. Используй /search <запрос> для поиска.")

@dp.message(Command("search"))
async def search(message: types.Message):
    query = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else ""
    if not query:
        await message.reply("Пожалуйста, укажите запрос для поиска.")
        return

    devices = netbox_client.search_devices(query)
    if devices['results']:
        response = "\n".join([f"{device['name']} - {device['id']}" for device in devices['results']])
    else:
        response = "Ничего не найдено."

    await message.reply(response)

async def start_bot():
    # Проверка подключения к NetBox перед запуском бота
    if netbox_client.check_connection():
        logger.info("Бот запущен.")
        await dp.start_polling(bot, skip_updates=True)  # Игнорировать старые сообщения
    else:
        logger.error("Не удалось подключиться к NetBox API. Бот не запущен.")