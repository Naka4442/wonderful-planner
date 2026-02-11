from datetime import date
from pydantic import BaseModel
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base


class UserInfoQuestion(Base):
    __tablename__ = "user_info_questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String(255))


class UserInfo(Base):
    __tablename__ = "user_info"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    question_id = Column(Integer, ForeignKey("user_info_questions.id"), primary_key=True)
    points = Column(Integer, nullable=False)

    created = Column(Date, default=date.today)

    question = relationship("UserInfoQuestion", backref="user_infos")


class UserInfoQuestionSchema(BaseModel):
    id: int
    question: str


class UserInfoSchema(BaseModel):
    user_id: int
    question_id: int
    points: int
    created: date

    question: UserInfoQuestionSchema | None = None


class UserInfoCreateDto(BaseModel):
    user_id: int | None = None
    question_id: int
    points: int
