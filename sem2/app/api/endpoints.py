from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from app.schemas.user import UserCreate, UserMe
from app.schemas.graph import Graph, PathResult
from app.cruds.user import create_user, get_user_by_email, authenticate_user
from app.services.aco import AntColonyOptimization
from app.db.database import get_db
from app.core.config import settings
from passlib.context import CryptContext

# Создаём роутер для API-эндпоинтов
router = APIRouter()
# Контекст для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Схема OAuth2 для аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Функция для создания JWT-токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # Устанавливаем время истечения токена (по умолчанию 15 минут)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # Кодируем токен с использованием секретного ключа и алгоритма
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Получение текущего пользователя по токену
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Ошибка для невалидных учетных данных
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем токен
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Ищем пользователя в базе данных по email
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# Эндпоинт для регистрации нового пользователя
@router.post("/sign-up/", response_model=UserMe)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, не зарегистрирован ли email
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Создаём нового пользователя
    new_user = create_user(db, user)
    return {"id": new_user.id, "email": new_user.email}

# Эндпоинт для входа (логина) пользователя
@router.post("/login/", response_model=UserMe)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Проверяем email и пароль
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Создаём токен (не возвращается в ответе)
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    # Возвращаем только id и email
    return {"id": user.id, "email": user.email}

# Эндпоинт для получения данных текущего пользователя
@router.get("/users/me/", response_model=UserMe)
async def read_users_me(current_user: UserMe = Depends(get_current_user)):
    return current_user

# Эндпоинт для поиска кратчайшего пути
@router.post("/shortest-path/", response_model=PathResult)
async def shortest_path(graph: Graph):
    # Выводим полученные данные для отладки
    print("Received input:", graph)
    # Создаём объект алгоритма ACO
    aco = AntColonyOptimization(graph)
    # Запускаем алгоритм
    result = aco.run()
    # Если путь не найден, возвращаем ошибку
    if result is None:
        raise HTTPException(status_code=400, detail="No Hamiltonian path found")
    return result