from datetime import date, timedelta
from typing import Optional

from models.schedule import ScheduleDaySchema, ScheduleWeekSchema, StatisticsSchema
from models.event import EventCreateDto, EventSchema
from models.task import TaskCreateDto, TaskSchema
from repositories.event_repository import EventRepository
from repositories.task_repository import TaskRepository


class TaskServices:
    def __init__(
        self,
        task_repository: TaskRepository,
        event_repository: EventRepository
    ):
        self.task_repo = task_repository
        self.event_repo = event_repository
    
    # Task operations
    def create_task(self, task_data: TaskCreateDto) -> TaskSchema:
        """Создать новую задачу"""
        return self.task_repo.create(task_data)
    
    def mark_task_as_done(self, task_id: int, user_id: int, actual_time: int) -> Optional[TaskSchema]:
        """Отметить задачу как выполненную"""
        return self.task_repo.mark_as_done(task_id, user_id, actual_time)
    
    def get_task_by_id(self, task_id: int) -> Optional[TaskSchema]:
        """Получить задачу по ID"""
        return self.task_repo.get_by_id(task_id)
    
    def delete_task(self, task_id: int) -> None:
        """Удалить задачу"""
        self.task_repo.delete(task_id)
    
    # Event operations
    def create_event(self, event_data: EventCreateDto) -> EventSchema:
        """Создать новое событие"""
        return self.event_repo.create(event_data)
    
    def delete_event(self, event_id: int) -> None:
        """Удалить событие"""
        self.event_repo.delete(event_id)
    
    # Schedule operations
    def get_daily_schedule(self, user_id: int, day: date) -> ScheduleDaySchema:
        """Получить расписание на день"""
        tasks = self.task_repo.get_by_user_id_and_date(user_id, day)
        events = self.event_repo.get_by_user_id_and_date(user_id, day)
        return ScheduleDaySchema(day=day, tasks=tasks, events=events)
    
    def get_weekly_schedule(self, user_id: int, week_start: date) -> ScheduleWeekSchema:
        """Получить расписание на неделю"""
        days = []
        for i in range(7):
            current_day = week_start + timedelta(days=i)
            tasks = self.task_repo.get_by_user_id_and_date(user_id, current_day)
            events = self.event_repo.get_by_user_id_and_date(user_id, current_day)
            days.append(ScheduleDaySchema(day=current_day, tasks=tasks, events=events))
        return ScheduleWeekSchema(days=days)
    
    def get_completed_tasks(self, user_id: int, day: date) -> list[TaskSchema]:
        """Получить выполненные задачи за день"""
        return self.task_repo.get_completed_tasks(user_id, day)
    
    def get_pending_tasks(self, user_id: int, day: date) -> list[TaskSchema]:
        """Получить незавершенные задачи за день"""
        return self.task_repo.get_pending_tasks(user_id, day)
    
    # Statistics operations
    def get_daily_statistics(self, user_id: int, day: date) -> StatisticsSchema:
        """Получить статистику за день"""
        return self._get_statistics_for_period(user_id, day, day)
    
    def get_weekly_statistics(self, user_id: int, week_start: date) -> StatisticsSchema:
        """Получить статистику за неделю"""
        week_end = week_start + timedelta(days=6)
        return self._get_statistics_for_period(user_id, week_start, week_end)
    
    def _get_statistics_for_period(self, user_id: int, start_date: date, end_date: date) -> StatisticsSchema:
        """Вспомогательный метод для получения статистики за период"""
        # Получаем статистику из репозитория
        pos_count, pos_total, neg_count, neg_total, total_difficulty, completed_tasks = \
            self.task_repo.get_statistics(user_id, start_date, end_date)
        
        # Получаем общее количество задач за период
        all_tasks = self.task_repo.get_tasks_for_period(user_id, start_date, end_date)
        total_tasks = len(all_tasks)
        
        # Рассчитываем дополнительные метрики
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        average_difficulty = (total_difficulty / completed_tasks) if completed_tasks > 0 else 0
        
        return StatisticsSchema(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            completion_rate=round(completion_rate, 1),
            average_difficulty=round(average_difficulty, 1),
            positive_differences=pos_count,
            negative_differences=neg_count,
            total_positive_time=pos_total,
            total_negative_time=neg_total,
        )