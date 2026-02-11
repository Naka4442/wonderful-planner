from typing import List
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String, Integer, Text, DateTime
from datetime import datetime
from models.base import Base
from models.user_info import UserInfoCreateDto


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True)
    password = Column(Text)
    name = Column(String(255))
    created = Column(DateTime, default=datetime.now)


class UserSchema(BaseModel):
    id: int
    email: str
    password: str
    name: str
    created: datetime


class UserCreateDto(BaseModel):
    email: str
    password: str
    name: str


class UserSignupDto(BaseModel):
    email: str
    name: str
    password: str
    password2: str

    info: List[UserInfoCreateDto] | None = None


class UserSigninDto(BaseModel):
    email: str
    password: str
