from sqlalchemy import Column, Integer, String
from app.db.database import Base

# Модель пользователя для базы данных
class User(Base):
    __tablename__ = "users"  # Имя таблицы в базе данных

    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор
    email = Column(String, unique=True, index=True)  # Email, должен быть уникальным
    hashed_password = Column(String)  # Хэшированный пароль