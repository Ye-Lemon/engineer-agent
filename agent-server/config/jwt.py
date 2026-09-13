from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


# 后端项目根路径
BASE_DIR = Path(__file__).resolve().parent.parent



class Settings(BaseSettings):
    DataBase_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_DAYS: int

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra="ignore"
    )

settings = Settings()