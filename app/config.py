from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    netbox_api_url: str
    netbox_api_token: str
    telegram_bot_token: str

    class Config:
        env_file = ".env"

settings = Settings()