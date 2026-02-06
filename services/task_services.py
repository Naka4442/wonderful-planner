from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Task
from datetime import date, timedelta
from sqlalchemy import func, or_

from models.event import EventSchema
from models.task import TaskCreateDto, TaskSchema
from repositories.event_repository import EventRepository
from repositories.task_repository import TaskRepository


class ScheduleDaySchema(BaseModel):
    day: date
    tasks: List[TaskSchema]
    events: List[EventSchema]


class ScheduleWeekSchema(BaseModel):
    days: List[ScheduleDaySchema]


class TaskServices:
    def __init__(
        self,
        task_repository: TaskRepository,
        event_repository: EventRepository
    ):
        self.task_repo = task_repository
        self.event_repo = event_repository
        
    def create_task(self, task_data: TaskCreateDto) -> None:
        self.task_repo.create(task_data)
        
    def get_shedule_by_day(self, user_id: int, day: date) -> ScheduleDaySchema:
        tasks = self.task_repo.get_by_user_id_and_date(user_id, day)
        events = self.event_repo.get_by_user_id_and_date(user_id, day)
        return ScheduleDaySchema(day=day, tasks=tasks, events=events)
    
    def get_schedule_by_week(self, user_id: int, monday_date: date) -> ScheduleWeekSchema:
        days = []
        for i in range(7):
            day = monday_date + timedelta(days=i)
            tasks = self.task_repo.get_by_user_id_and_date(user_id, day)
            events = self.event_repo.get_by_user_id_and_date(user_id, day)
            days.append(ScheduleDaySchema(day=day, tasks=tasks, events=events))
        return ScheduleWeekSchema(days=days)

    # def get_positive_difference_by_day(self, user_id: int, day: date):
    #     count = 0
    #     day_difference = 0
    #     tasks = self.db.query(Task).filter(Task.user_id == user_id, func.date(Task.start_time) == day, Task.is_done == 1).all()
    #     for task in tasks:
    #         if task.supposed_time - task.actual_time >= 0:
    #             count += 1
    #             day_difference += task.supposed_time - task.actual_time
    #     return count, day_difference
    # def get_negative_difference_by_day(self, user_id: int, day: date):
    #     count = 0
    #     day_difference = 0
    #     tasks = self.db.query(Task).filter(Task.user_id == user_id, func.date(Task.start_time) == day, Task.is_done == 1).all()
    #     for task in tasks:
    #         if task.supposed_time - task.actual_time <= 0:
    #             count += 1
    #             day_difference += task.supposed_time - task.actual_time
    #     return count, day_difference
    
    # def get_positive_difference_by_week(self, user_id: int, day:date):
    #     count = 0
    #     week_difference = 0
    #     tasks = self.db.query(Task).filter(
    #         Task.user_id == user_id,Task.start_time >= day,
    #         Task.start_time < day + timedelta(days=8), 
    #         Task.is_done == 1
    #     ).all()
    #     for task in tasks:
    #         if task.supposed_time - task.actual_time >= 0:
    #             count += 1
    #             week_difference += task.supposed_time - task.actual_time
    #     return count,week_difference
    # def get_negative_difference_by_week(self, user_id: int, day:date):
    #     count = 0
    #     week_difference = 0
    #     tasks = self.db.query(Task).filter(
    #         Task.user_id == user_id,Task.start_time >= day,
    #         Task.start_time < day + timedelta(days=8),
    #         Task.is_done == 1
    #     ).all()
    #     for task in tasks:
    #         if task.supposed_time - task.actual_time <= 0:
    #             count += 1
    #             week_difference += task.supposed_time - task.actual_time

    #     return count,week_difference
    
    # def get_difficulty_by_week(self, user_id: int, day:date):
    #     week_difficulty = 0
    #     tasks = self.db.query(Task).filter(
    #         Task.user_id == user_id,
    #         Task.start_time >= day,
    #         Task.start_time < day + timedelta(days=8), 
    #         Task.is_done == 1
    #     ).all()
    #     for task in tasks:
    #         week_difficulty += task.difficulty
    #     return week_difficulty
    
    # def get_difficulty_by_day(self, user_id: int, day:date):
    #     day_difficulty = 0
    #     tasks = self.db.query(Task).filter(Task.user_id == user_id, func.date(Task.start_time) == day, Task.is_done == 1).all()
    #     for task in tasks:
    #         day_difficulty += task.difficulty
    #     return day_difficulty
    
    # def check_task(self, task_id: int, minutes: int, user_id: int):
    #     task = self.db.query(Task).filter(Task.id == task_id).first()
    #     if task.user_id != user_id:
    #         raise ValueError("Вы не можете завершить не вашу задачу")
    #     task.actual_time = minutes
    #     task.is_done = True
    #     self.db.commit()
        
    # def get_schedule(self, user_id: int, day: date):
    #     weekday = day.weekday() + 1
        
    #     repeated_tasks = self.db.query(Task).filter(
    #             Task.user_id == user_id, 
    #             Task.is_event == True,
    #             or_(Task.repeat_weekday == weekday,
    #             func.date(Task.start_time) == day)
    #         ).order_by(Task.repeat_time_start).all()
        
    #     return repeated_tasks
    
    # def get_week_schedule(self, user_id: int):
    #     repeated_tasks = self.db.query(Task).filter(
    #             Task.user_id == user_id, 
    #             Task.is_repeated == True
    #         ).order_by(Task.repeat_time_start).all()
        
    #     return repeated_tasks
    
    # def get_not_event_tasks_by_day(self, user_id: int, day:date):
    #     not_event_tasks = self.db.query(Task).filter(
    #         Task.user_id == user_id,
    #         Task.is_event == False,
    #         func.date(Task.start_time) == day
    #     ).all()
    #     return not_event_tasks
        