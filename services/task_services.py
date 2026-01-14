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
        supposed_time: int,
        start_time: str = None,
        end_time: str = None
    ):
        task = Task(
            title=title, 
            user_id=user_id, 
            description=description, 
            difficulty=difficulty, 
            supposed_time=supposed_time,
            start_time=start_time,
            end_time=end_time
        )
        self.db.add(task)
        self.db.commit()
        
    def get_all(self, user_id: int):
        tasks = self.db.query(Task).filter(Task.user_id == user_id).all()
        return tasks
    
    def check_task(self, task_id: int, minutes: int, user_id: int):
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task.user_id != user_id:
            raise ValueError("Вы не можете завершить не вашу задачу")
        task.actual_time = minutes
        task.is_done = True
        self.db.commit()