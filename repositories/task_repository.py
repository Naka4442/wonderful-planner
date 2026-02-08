from datetime import date
from typing import List, Optional, Tuple
from sqlalchemy import func

from models.task import Task, TaskSchema, TaskCreateDto
from repositories.abstract_repository import AbstractRepository


class TaskRepository(AbstractRepository):
    def create(self, task_data: TaskCreateDto) -> TaskSchema:
        task = Task(**task_data.model_dump())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return TaskSchema.model_validate(task)
    
    def get_by_id(self, task_id: int) -> Optional[TaskSchema]:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        return TaskSchema.model_validate(task) if task else None
    
    def get_by_user_id(self, user_id: int) -> List[TaskSchema]:
        tasks = self.db.query(Task).filter(Task.user_id == user_id).all()
        return [TaskSchema.model_validate(task) for task in tasks]
    
    def get_by_user_id_and_date(self, user_id: int, day: date) -> List[TaskSchema]:
        tasks = self.db.query(Task).filter(
            Task.user_id == user_id,
            func.date(Task.start_time) == day
        ).all()
        return [TaskSchema.model_validate(task) for task in tasks]
    
    def get_tasks_for_period(self, user_id: int, start_date: date, end_date: date) -> List[TaskSchema]:
        tasks = self.db.query(Task).filter(
            Task.user_id == user_id,
            func.date(Task.start_time) >= start_date,
            func.date(Task.start_time) <= end_date
        ).all()
        return [TaskSchema.model_validate(task) for task in tasks]
    
    def get_completed_tasks(self, user_id: int, day: date) -> List[TaskSchema]:
        tasks = self.db.query(Task).filter(
            Task.user_id == user_id,
            func.date(Task.start_time) == day,
            Task.is_done == True
        ).all()
        return [TaskSchema.model_validate(task) for task in tasks]
    
    def get_pending_tasks(self, user_id: int, day: date) -> List[TaskSchema]:
        tasks = self.db.query(Task).filter(
            Task.user_id == user_id,
            func.date(Task.start_time) == day,
            Task.is_done == False
        ).all()
        return [TaskSchema.model_validate(task) for task in tasks]
    
    def mark_as_done(self, task_id: int, user_id: int, actual_time: int) -> Optional[TaskSchema]:
        task = self.db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()
        
        if not task:
            return None
            
        task.is_done = True
        task.actual_time = actual_time
        self.db.commit()
        self.db.refresh(task)
        return TaskSchema.model_validate(task)
    
    def delete(self, task_id: int) -> None:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task:
            self.db.delete(task)
            self.db.commit()
    
    def get_statistics(self, user_id: int, start_date: date, end_date: date) -> Tuple:
        """Возвращает статистику за период"""
        tasks = self.db.query(Task).filter(
            Task.user_id == user_id,
            func.date(Task.start_time) >= start_date,
            func.date(Task.start_time) <= end_date,
            Task.is_done == True
        ).all()
        
        positive_count = 0
        positive_total = 0
        negative_count = 0
        negative_total = 0
        total_difficulty = 0
        total_tasks = len(tasks)
        
        for task in tasks:
            difference = task.supposed_time - task.actual_time
            total_difficulty += task.difficulty
            
            if difference >= 0:
                positive_count += 1
                positive_total += difference
            else:
                negative_count += 1
                negative_total += abs(difference)
        
        return (
            positive_count,
            positive_total,
            negative_count,
            negative_total,
            total_difficulty,
            total_tasks
        )