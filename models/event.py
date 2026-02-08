from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from models.base import Base


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(String(255))
    difficulty = Column(Integer, nullable=False, default=1)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    is_repeated = Column(Boolean, default=False)
    repeat_weekday = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created = Column(DateTime, default=datetime.now)


class EventSchema(BaseModel):
    id: int
    title: str
    description: str | None = None
    difficulty: int = Field(ge=1, le=10)
    start_time: datetime
    end_time: datetime | None = None
    is_repeated: bool = False
    repeat_weekday: int | None = None
    user_id: int
    created: datetime
    
    class Config:
        from_attributes = True


class EventCreateDto(BaseModel):
    title: str
    description: str | None = None
    difficulty: int = Field(ge=1, le=10, default=1)
    start_time: datetime
    end_time: datetime | None = None
    is_repeated: bool = False
    repeat_weekday: int | None = Field(None, ge=0, le=6)
    user_id: int
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, v, info):
        if v and 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('End time must be after start time')
        return v