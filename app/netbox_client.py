import requests
import logging
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

class NetBoxClient:
    def __init__(self):
        self.base_url = settings.netbox_api_url
        self.headers = {
            "Authorization": f"Token {settings.netbox_api_token}",
            "Content-Type": "application/json",
        }

    def check_connection(self):
        """
        Проверяет подключение к API NetBox.
        Возвращает True, если подключение успешно, иначе False.
        """
        try:
            url = f"{self.base_url}status/"
            response = requests.get(url, headers=self.headers, verify=False)  # Отключение проверки SSL
            if response.status_code == 200:
                logger.info("Подключение к NetBox API успешно.")
                return True
            else:
                logger.error(f"Ошибка подключения к NetBox API. Код ответа: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Ошибка при подключении к NetBox API: {e}")
            return False

    def search_devices(self, query: str):
        """
        Поиск устройств в NetBox по запросу.
        """
        url = f"{self.base_url}dcim/devices/?q={query}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def search_ips(self, query: str):
        """
        Поиск IP-адресов в NetBox по запросу.
        """
        url = f"{self.base_url}ipam/ip-addresses/?q={query}"
        response = requests.get(url, headers=self.headers)
        return response.json()