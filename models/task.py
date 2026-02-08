from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Boolean, Time
from datetime import datetime
from models.base import Base


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    description = Column(Text)
    difficulty = Column(Integer)
    is_done = Column(Boolean, default=False)

    supposed_time = Column(Integer)
    actual_time = Column(Integer, default=0)
    
    start_time = Column(DateTime, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    created = Column(DateTime, default=datetime.now)
    
    
class TaskSchema(BaseModel):
    id: int
    title: str
    description: str | None = None
    difficulty: int
    is_done: bool

    supposed_time: int
    actual_time: int | None = None

    start_time: datetime | None = None

    user_id: int
    created: datetime

    class Config:
        from_attributes = True


class TaskCreateDto(BaseModel):
    title: str
    description: str | None = None
    difficulty: int
    supposed_time: int
    user_id: int
