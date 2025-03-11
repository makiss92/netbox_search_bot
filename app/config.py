import os
from pydantic import HttpUrl, ValidationError
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Класс для хранения настроек приложения.
    Настройки загружаются из переменных окружения или файла .env.
    """
    netbox_api_url: HttpUrl
    netbox_api_token: str
    telegram_bot_token: str
    ssl_ca_cert: str = "self-signed.crt"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

if not os.path.exists(".env"):
    print("Предупреждение: Файл .env не найден. Переменные окружения будут загружены из системы.")

try:
    settings = Settings()
except ValidationError as e:
    print(f"Ошибка загрузки настроек: {e}")
    raise