from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
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

async def handle_search_command(message: types.Message, endpoint: str, entity_name: str):
    """
    Универсальный обработчик команд поиска.
    """
    query = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else ""
    if not query:
        await message.reply(f"Пожалуйста, укажите запрос для поиска {entity_name}.")
        return

    try:
        results = await netbox_client.search(endpoint, query)
        logger.info(f"Данные от NetBox API: {results}")  # Логируем данные

        if results is None:
            await message.reply("Ошибка при получении данных от NetBox API.")
            return

        if results:
            response = f"Найденные {entity_name}:\n\n"
            for result in results:
                if endpoint == "dcim/devices":
                    response += netbox_client._format_device_details(result) + "\n\n"
                else:
                    response += f"🔹 *{escape_markdown(result.get('name', 'N/A'))}*\n"
                    response += f"  - *Описание*: {escape_markdown(result.get('description', 'N/A'))}\n\n"
        else:
            response = "Ничего не найдено."

        await message.reply(response, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка при поиске {entity_name}: {e}")
        await message.reply(f"Произошла ошибка при поиске {entity_name}.")

@dp.message(Command("search_racks"))
async def search_racks(message: types.Message):
    """
    Обработчик команды /search_racks.
    """
    await handle_search_command(message, "dcim/racks", "стойки")

@dp.message(Command("search_devices"))
async def search_devices(message: types.Message):
    query = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else ""
    if not query:
        await message.reply("Пожалуйста, укажите запрос для поиска устройств.")
        return

    try:
        devices = await netbox_client.search("dcim/devices", query)
        logger.info(f"Данные от NetBox API: {devices}")  # Логируем данные

        if devices is None:
            await message.reply("Ошибка при получении данных от NetBox API.")
            return

        if devices:
            response = "Найденные устройства:\n\n"
            for device in devices:
                response += netbox_client._format_device_details(device) + "\n\n"
        else:
            response = "Ничего не найдено."

        await message.reply(response, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка при поиске устройств: {e}")
        await message.reply("Произошла ошибка при поиске устройств.")

@dp.message(Command("search_connections"))
async def search_connections(message: types.Message):
    """
    Обработчик команды /search_connections.
    """
    await handle_search_command(message, "dcim/cables", "соединения")

@dp.message(Command("search_wireless"))
async def search_wireless(message: types.Message):
    """
    Обработчик команды /search_wireless.
    """
    await handle_search_command(message, "wireless/wireless-links", "беспроводные устройства")

@dp.message(Command("search_ipam"))
async def search_ipam(message: types.Message):
    """
    Обработчик команды /search_ipam.
    """
    await handle_search_command(message, "ipam/ip-addresses", "IP-адреса")

@dp.message(Command("search_vpn"))
async def search_vpn(message: types.Message):
    """
    Обработчик команды /search_vpn.
    """
    await handle_search_command(message, "vpn/tunnels", "VPN")

@dp.message(Command("search_virtualization"))
async def search_virtualization(message: types.Message):
    """
    Обработчик команды /search_virtualization.
    """
    await handle_search_command(message, "virtualization/virtual-machines", "виртуальные машины")

@dp.message(Command("search_communication_channels"))
async def search_communication_channels(message: types.Message):
    """
    Обработчик команды /search_communication_channels.
    """
    await handle_search_command(message, "circuits/circuits", "каналы связи")

@dp.message(Command("search_power_supply"))
async def search_power_supply(message: types.Message):
    """
    Обработчик команды /search_power_supply.
    """
    await handle_search_command(message, "dcim/power-feeds", "источники питания")

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