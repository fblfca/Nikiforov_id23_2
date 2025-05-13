from pydantic_settings import BaseSettings

# Класс для хранения настроек
class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    DATABASE_URL: str = "sqlite:///app.db"  # Путь к базе данных SQLite

    class Config:
        env_file = ".env"  # Загружаем переменные из .env
        env_file_encoding = "utf-8"

# Создаём объект настроек
settings = Settings()