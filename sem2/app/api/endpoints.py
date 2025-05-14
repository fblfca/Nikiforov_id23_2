from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
from app.schemas.user import UserCreate, UserMe, UserLoginResponse
from app.schemas.graph import Graph, PathResult
from app.cruds.user import create_user, get_user_by_email, authenticate_user
from app.services.aco import AntColonyOptimization
from app.db.database import get_db
from app.core.config import settings
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

@router.post("/sign-up/", response_model=UserLoginResponse)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):

    # Проверяем, не зарегистрирован ли email
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Создаём нового пользователя
    new_user = create_user(db, user)
    # Генерируем JWT-токен для нового пользователя
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    # # Отладка
    # print("Generated access_token for sign-up:", access_token)

    # Oтвет с id, email и токеном
    response = {"id": new_user.id, "email": new_user.email, "access_token": access_token}
    print("Returning sign-up response:", response)
    return response

# @router.post("/login/", response_model=UserLoginResponse)
# async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=15)
#     access_token = create_access_token(
#         data={"sub": user.email}, expires_delta=access_token_expires
#     )
#     print("Generated access_token:", access_token)
#     response = {"id": user.id, "email": user.email, "access_token": access_token}
#     print("Returning response:", response)
#     return response
@router.post("/login/", response_model=UserLoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # form_data.username(password): почта(пароль) пользователя, введённый в поле логина(пароля)

    user = authenticate_user(db, form_data.username, form_data.password)
    # Проверяем, существует ли пользователь и верен ли пароль
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Время жизни токена (15 минут)
    access_token_expires = timedelta(minutes=15)
    # Создаём JWT-токен с почтой пользователя в поле "sub"
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    # # Отладки
    # print("Generated access_token:", access_token)
    
    # Формируем ответ с id, email и токеном
    response = {"id": user.id, "email": user.email, "access_token": access_token}
    print("Returning response:", response)
    return response

@router.get("/users/me/", response_model=UserMe)
async def read_users_me(current_user: UserMe = Depends(get_current_user)):
    return current_user

@router.post("/shortest-path/", response_model=PathResult)
async def shortest_path(graph: Graph, current_user: UserMe = Depends(get_current_user)):
    print("Received input:", graph)
    aco = AntColonyOptimization(graph)
    result = aco.run()
    if result is None:
        raise HTTPException(status_code=400, detail="No Hamiltonian path found")
    return result
