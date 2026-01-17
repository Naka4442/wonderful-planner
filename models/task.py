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
    
    start_time = Column(DateTime, default=None, nullable=True)
    end_time = Column(DateTime, default=None, nullable=True)
    
    is_repeated = Column(Boolean, default=False)
    repeat_time_start = Column(Time, nullable=True, default=None)
    repeat_time_end = Column(Time, nullable=True, default=None)
    repeat_weekday = Column(Integer, nullable=True, default=None)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    
    created = Column(DateTime, default=datetime.now)
    
    