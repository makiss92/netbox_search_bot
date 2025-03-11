import aiohttp
import ssl
import logging
import os
from app.config import settings

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

def escape_markdown(text: str) -> str:
    """
    Экранирует специальные символы Markdown.
    """
    escape_chars = "_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)

class NetBoxClient:
    def __init__(self):
        """
        Инициализация клиента для работы с NetBox API.
        """
        self.base_url = settings.netbox_api_url
        self.headers = {
            "Authorization": f"Token {settings.netbox_api_token}",
            "Content-Type": "application/json",
        }
        self.ssl_ca_cert = settings.ssl_ca_cert

        # Проверка наличия файла сертификата
        if not os.path.exists(self.ssl_ca_cert):
            logger.error(f"Файл сертификата не найден: {self.ssl_ca_cert}")
            raise FileNotFoundError(f"Файл сертификата не найден: {self.ssl_ca_cert}")

    async def _fetch_data(self, endpoint: str, query: str = ""):
        try:
            url = f"{self.base_url}{endpoint}/?q={query}" if query else f"{self.base_url}{endpoint}/"
            ssl_context = ssl.create_default_context(cafile=self.ssl_ca_cert)

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, ssl=ssl_context) as response:
                    response.raise_for_status()  # Проверка на ошибки HTTP

                    if not response.content:
                        logger.error("Пустой ответ от NetBox API.")
                        return []  # Возвращаем пустой список вместо None

                    data = await response.json()
                    if not data or not isinstance(data, dict):
                        logger.error(f"Некорректный ответ от NetBox API: {data}")
                        return []  # Возвращаем пустой список вместо None

                    return data.get('results', [])
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка при запросе к NetBox API: {e}")
            return []  # Возвращаем пустой список вместо None
        except Exception as e:
            logger.error(f"Неизвестная ошибка при запросе к NetBox API: {e}")
            return []  # Возвращаем пустой список вместо None

    async def search(self, endpoint: str, query: str):
        """
        Универсальный метод для поиска данных в NetBox API.
        """
        return await self._fetch_data(endpoint, query)

    async def check_connection(self):
        """
        Проверка подключения к NetBox API.
        """
        try:
            await self._fetch_data("status")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к NetBox API: {e}")
            return False

    def _format_device_details(self, device) -> str:
        """
        Форматирует информацию об устройстве для вывода.
        """
        if not isinstance(device, dict):
            return "Некорректные данные об устройстве."

        details = []

        # Добавляем основные поля
        details.append(f"🔹 *{escape_markdown(device.get('name', 'N/A'))}*")
        details.append(f"  - *ID*: {escape_markdown(str(device.get('id', 'N/A')))}")
        details.append(f"  - *Статус*: {escape_markdown(device.get('status', {}).get('label', 'N/A'))}")
        details.append(f"  - *Серийный номер*: {escape_markdown(device.get('serial', 'N/A'))}")
        details.append(f"  - *Asset Tag*: {escape_markdown(device.get('asset_tag', 'N/A'))}")

        # Обрабатываем вложенные поля
        device_type = device.get("device_type")
        if device_type and isinstance(device_type, dict):
            details.append(f"  - *Тип устройства*: {escape_markdown(device_type.get('model', 'N/A'))}")
            manufacturer = device_type.get("manufacturer")
            if manufacturer and isinstance(manufacturer, dict):
                details.append(f"  - *Производитель*: {escape_markdown(manufacturer.get('name', 'N/A'))}")

        site = device.get("site")
        if site and isinstance(site, dict):
            details.append(f"  - *Сайт*: {escape_markdown(site.get('name', 'N/A'))}")

        rack = device.get("rack")
        if rack and isinstance(rack, dict):
            details.append(f"  - *Стойка*: {escape_markdown(rack.get('name', 'N/A'))}")

        location = device.get("location")
        if location and isinstance(location, dict):
            details.append(f"  - *Локация*: {escape_markdown(location.get('name', 'N/A'))}")

        primary_ip = device.get("primary_ip")
        if primary_ip and isinstance(primary_ip, dict):
            details.append(f"  - *Основной IP*: {escape_markdown(primary_ip.get('address', 'N/A'))}")

        # Добавляем дополнительные поля
        for key, value in device.items():
            if key not in ["name", "id", "status", "serial", "asset_tag", "device_type", "site", "rack", "location", "primary_ip"]:
                details.append(f"  - *{escape_markdown(key.capitalize())}*: {escape_markdown(str(value))}")

        return "\n".join(details)