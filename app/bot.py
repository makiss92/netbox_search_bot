from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from app.netbox_client import NetBoxClient, escape_markdown
from app.config import settings
import asyncio
import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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

# Инициализация бота и диспетчера
bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()
netbox_client = NetBoxClient()

# Список доступных команд
COMMANDS = {
    "/search_racks": "Поиск стоек",
    "/search_devices": "Поиск устройств",
    "/search_connections": "Поиск соединений",
    "/search_wireless": "Поиск беспроводных устройств",
    "/search_ipam": "Поиск IP-адресов",
    "/search_vpn": "Поиск VPN",
    "/search_virtualization": "Поиск виртуальных машин",
    "/search_communication_channels": "Поиск каналов связи",
    "/search_power_supply": "Поиск источников питания",
}

async def send_help_message(message: types.Message):
    """
    Отправляет сообщение с подсказкой по командам.
    """
    help_text = "Доступные команды:\n\n"
    for command, description in COMMANDS.items():
        help_text += f"{command} - {description}\n"
    await message.reply(help_text)

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    """
    Обработчик команды /start.
    """
    await message.reply(
        "Привет! Я бот для поиска информации в NetBox.\n"
        "Используй команды:\n"
        "/search_racks <запрос> - поиск стоек\n"
        "/search_devices <запрос> - поиск устройств\n"
        "/search_connections <запрос> - поиск соединений\n"
        "/search_wireless <запрос> - поиск беспроводных устройств\n"
        "/search_ipam <запрос> - поиск IP-адресов\n"
        "/search_vpn <запрос> - поиск VPN\n"
        "/search_virtualization <запрос> - поиск виртуальных машин\n"
        "/search_communication_channels <запрос> - поиск каналов связи\n"
        "/search_power_supply <запрос> - поиск источников питания"
    )

@dp.message(F.text.startswith("/search_"))
async def handle_search_command(message: types.Message):
    """
    Универсальный обработчик команд поиска.
    """
    command = message.text.split(" ", 1)[0]
    if command not in COMMANDS:
        await message.reply("Неизвестная команда. Вот список доступных команд:")
        await send_help_message(message)
        return

    query = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else ""
    if not query:
        await message.reply(f"Пожалуйста, укажите запрос для поиска {COMMANDS[command]}.")
        return

    try:
        endpoint = command.replace("/search_", "").replace("_", "-")
        results = await netbox_client.search(endpoint, query)
        logger.info(f"Данные от NetBox API: {results}")  # Логируем данные

        if results is None:
            await message.reply("Ошибка при получении данных от NetBox API.")
            return

        if results:
            response = f"Найденные {COMMANDS[command]}:\n\n"
            for result in results:
                if endpoint == "devices":
                    response += netbox_client._format_device_details(result) + "\n\n"
                else:
                    response += f"🔹 *{escape_markdown(result.get('name', 'N/A'))}*\n"
                    response += f"  - *Описание*: {escape_markdown(result.get('description', 'N/A'))}\n\n"
        else:
            response = "Ничего не найдено."

        await message.reply(response, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка при поиске {COMMANDS[command]}: {e}")
        await message.reply(f"Произошла ошибка при поиске {COMMANDS[command]}.")

@dp.message()
async def handle_unknown_command(message: types.Message):
    """
    Обработчик неизвестных команд.
    """
    await message.reply("Неизвестная команда. Вот список доступных команд:")
    await send_help_message(message)

async def start_bot(bot: Bot):
    """
    Запуск бота.
    """
    try:
        if await netbox_client.check_connection():
            logger.info("Бот запущен.")
            await dp.start_polling(bot)
        else:
            logger.error("Не удалось подключиться к NetBox API. Бот не запущен.")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")