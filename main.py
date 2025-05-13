from fastapi import FastAPI
from app.api import endpoints

# Создаём приложение FastAPI
app = FastAPI(title="Travelling Salesman Problem API")

# Подключаем маршруты (эндпоинты) из файла endpoints
app.include_router(endpoints.router)