from datetime import date
from typing import List
from pydantic import BaseModel

from models.event import EventSchema
from models.task import TaskSchema


class ScheduleDaySchema(BaseModel):
    day: date
    tasks: List[TaskSchema]
    events: List[EventSchema]


class ScheduleWeekSchema(BaseModel):
    days: List[ScheduleDaySchema]


class StatisticsSchema(BaseModel):
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    average_difficulty: float
    positive_differences: int
    negative_differences: int
    total_positive_time: int
    total_negative_time: int
