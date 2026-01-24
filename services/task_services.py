from sqlalchemy.orm import Session
from models import Task
from datetime import date, timedelta
from sqlalchemy import func



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
        is_repeated: bool = False,
        repeat_time_start: str = None,
        repeat_time_end: str = None,
        repeat_weekday: int = None,
        start_time: str = None,
        end_time: str = None
    ):
        if is_repeated:
            task = Task(
                title=title, 
                user_id=user_id, 
                description=description, 
                difficulty=difficulty, 
                supposed_time=supposed_time,
                is_repeated=is_repeated,
                repeat_time_start=repeat_time_start,
                repeat_time_end=repeat_time_end,
                repeat_weekday=repeat_weekday,
            )
        else:
            task = Task(
                title=title, 
                user_id=user_id, 
                description=description, 
                difficulty=difficulty,
                is_repeated=is_repeated,
                supposed_time=supposed_time,
                start_time=start_time,
                end_time=end_time
            )
        self.db.add(task)
        self.db.commit()
        
    def get_all(self, user_id: int):
        tasks = self.db.query(Task).filter(Task.user_id == user_id).all()
        return tasks

    def get_time_difference_by_day(self, user_id: int, day:date):
        day_difference = 0
        tasks = self.db.query(Task).filter(Task.user_id == user_id, func.date(Task.start_time) == day, Task.is_done == 1).all()
        for task in tasks:
            day_difference += abs(task.supposed_time - task.actual_time)
        return day_difference
    def get_time_difference_by_week(self, user_id: int, day:date):
        week_difference = 0
        tasks = self.db.query(Task).filter(Task.user_id == user_id,Task.start_time >= day,Task.start_time < day + timedelta(days=8), Task.is_done == 1).all()
        for task in tasks:
            week_difference += abs(task.supposed_time - task.actual_time)
        return week_difference
    def get_difficulty_by_week(self, user_id: int, day:date):
        week_difficulty = 0
        tasks = self.db.query(Task).filter(Task.user_id == user_id,Task.start_time >= day,Task.start_time < day + timedelta(days=8), Task.is_done == 1).all()
        for task in tasks:
            week_difficulty += task.difficulty
        return week_difficulty
    def get_difficulty_by_day(self, user_id: int, day:date):
        day_difficulty = 0
        tasks = self.db.query(Task).filter(Task.user_id == user_id, func.date(Task.start_time) == day, Task.is_done == 1).all()
        for task in tasks:
            day_difficulty += task.difficulty
        return day_difficulty

    
    def check_task(self, task_id: int, minutes: int, user_id: int):
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task.user_id != user_id:
            raise ValueError("Вы не можете завершить не вашу задачу")
        task.actual_time = minutes
        task.is_done = True
        self.db.commit()
        
    def get_schedule(self, user_id: int, day: date):
        weekday = day.weekday() + 1
        
        repeated_tasks = self.db.query(Task).filter(
                Task.user_id == user_id, 
                Task.is_repeated == True,
                Task.repeat_weekday == weekday
            ).order_by(Task.repeat_time_start).all()
        
        return repeated_tasks
    
    def get_week_schedule(self, user_id: int):
        repeated_tasks = self.db.query(Task).filter(
                Task.user_id == user_id, 
                Task.is_repeated == True
            ).order_by(Task.repeat_time_start).all()
        
        return repeated_tasks
    
    def get_not_repeated_tasks(self, user_id: int):
        not_repeated_tasks = self.db.query(Task).filter(
            Task.user_id == user_id,
            Task.is_repeated == False
        )
        return not_repeated_tasks
        