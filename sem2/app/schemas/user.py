# from pydantic import BaseModel, EmailStr
#
# # Схема для запроса регистрации и входа
# class UserCreate(BaseModel):
#     email: EmailStr  # Валидирует, что это корректный email
#     password: str
#
# # Схема для ответа с данными пользователя
# class UserLoginResponse(BaseModel):
#     id: int
#     email: str
#     token: str
#
#     class Config:
#         from_attributes = True  # Позволяет преобразовывать объекты SQLAlchemy в Pydantic
#
# # Схема для получения текущего пользователя
# class UserMe(BaseModel):
#     id: int
#     email: str
#
#     class Config:
#         from_attributes = True
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserMe(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class UserLoginResponse(BaseModel):
    id: int
    email: str
    access_token: str
