from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from models.base import Base


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    description = Column(String(255), nullable=True, default=None)
    difficulty = Column(Integer, nullable=False, default=1)

    start_time = Column(String(255), nullable=False)
    end_time = Column(String(255), nullable=False)
    
    is_repeated = Column(Boolean, nullable=False, default=False)
    repeat_weekday = Column(Integer, nullable=True, default=None)

    user_id = Column(Integer, ForeignKey("users.id"))
    created = Column(DateTime, default=datetime.now)


class EventSchema(BaseModel):
    id: int
    title: str
    description: str | None = None
    difficulty: int
    start_time: str | None = None
    end_time: str | None = None
    is_repeated: bool
    repeat_weekday: int | None = None

    user_id: int
    created: datetime


class EventCreateDto(BaseModel):
    title: str
    description: str | None = None
    difficulty: int

    start_time: datetime
    end_time: datetime | None = None

    user_id: int
