from datetime import date
from typing import List

from sqlalchemy import func
from models.task import Task, TaskCreateDto, TaskSchema
from repositories.abstract_repository import AbstractRepository


class TaskRepository(AbstractRepository):
    def create(self, task_data: TaskCreateDto) -> TaskSchema:
        task = Task(**task_data.model_dump())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return TaskSchema.model_validate(task, from_attributes=True)
    
    def get_by_user_id(self, user_id: int) -> List[TaskSchema]:
        return [
            TaskSchema.model_validate(task, from_attributes=True)
            for task in self.db.query(Task).filter(
                Task.user_id == user_id
            ).all()
        ]

    def get_by_user_id_and_date(self, user_id: int, day: date) -> List[TaskSchema]:
        return [
            TaskSchema.model_validate(task, from_attributes=True)
            for task in self.db.query(Task).filter(
                Task.user_id == user_id,
                func.date(Task.start_time) == day
            ).all()
        ]

    def get_by_id(self, task_id: int) -> TaskSchema | None:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            return None
        return TaskSchema.model_validate(task, from_attributes=True)

    def done_task(self, task_id: int, actual_time: int) -> None:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        task.is_done = True
        task.actual_time = actual_time
        self.db.commit()

    def delete_task(self, task_id: int) -> None:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        self.db.delete(task)
        self.db.commit()
    