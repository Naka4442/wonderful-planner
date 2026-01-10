from sqlalchemy.orm import Session
from models import Task


class TaskServices:
    def __init__(self, db: Session):
        self.db = db
        
    def create(
        self, 
        title: str, 
        user_id: int, 
        description: str, 
        difficulty: int, 
        supposed_time: int
    ):
        task = Task(
            title=title, 
            user_id=user_id, 
            description=description, 
            difficulty=difficulty, 
            supposed_time=supposed_time
        )
        self.db.add(task)
        self.db.commit()