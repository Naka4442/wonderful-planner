from sqlalchemy import Column, String, Integer, Text, DateTime
from datetime import datetime
from models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True)
    password = Column(Text)
    name = Column(String(255))
    created = Column(DateTime, default=datetime.now)
    
