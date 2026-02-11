from datetime import date, datetime, timedelta
import logging
from typing import List, Dict, Any

from models.schedule import ScheduleDaySchema, ScheduleWeekSchema, StatisticsSchema

# Настройка логирования
logger = logging.getLogger(__name__)


class SchedulePresenter:
    """
    Отвечает за подготовку данных расписания для отображения в шаблонах.
    """

    def prepare_daily_view(
        self,
        schedule: ScheduleDaySchema,
        statistics: StatisticsSchema,
        user_name: str,
        selected_date: date,
    ) -> Dict[str, Any]:
        """Подготавливает контекст для шаблона дневного вида."""
        processed_tasks = self._process_tasks_for_calendar(schedule.tasks)
        processed_events = self._process_events_for_calendar(schedule.events)

        pending_tasks = [task for task in schedule.tasks if not task.is_done]
        completed_tasks = [task for task in schedule.tasks if task.is_done]

        return {
            "user_name": user_name,
            "selected_date": selected_date.strftime("%Y-%m-%d"),
            "statistics": statistics,
            "processed_tasks": processed_tasks,
            "processed_events": processed_events,
            "undone": pending_tasks,
            "done": completed_tasks,
            "events": schedule.events,
            "current_hour": datetime.now().hour
            if selected_date == date.today()
            else None,
            "today": date.today().strftime("%Y-%m-%d"),
        }

    def prepare_weekly_view(
        self,
        week_schedule: ScheduleWeekSchema,
        week_statistics: StatisticsSchema,
        user_name: str,
        week_start: date,
    ) -> Dict[str, Any]:
        """Подготавливает контекст для шаблона недельного вида."""
        week_data = []
        for day_schedule in week_schedule.days:
            processed_tasks = self._process_tasks_for_calendar(day_schedule.tasks)
            processed_events = self._process_events_for_calendar(day_schedule.events)

            undone_tasks = [t for t in day_schedule.tasks if not t.is_done]
            done_tasks = [t for t in day_schedule.tasks if t.is_done]

            week_data.append(
                {
                    "date": day_schedule.day,
                    "day_name": self._get_day_name(day_schedule.day),
                    "date_str": day_schedule.day.strftime("%d.%m"),
                    "full_date_str": day_schedule.day.strftime("%d %B %Y"),
                    "tasks": day_schedule.tasks,
                    "events": day_schedule.events,
                    "undone_tasks": undone_tasks,
                    "done_tasks": done_tasks,
                    "processed_tasks": processed_tasks,
                    "processed_events": processed_events,
                    "is_today": day_schedule.day == date.today(),
                }
            )

        week_end = week_start + timedelta(days=6)
        return {
            "user_name": user_name,
            "week_data": week_data,
            "week_start": week_start,
            "week_end": week_end,
            "week_range": f"{week_start.strftime('%d %b')} - {week_end.strftime('%d %b %Y')}",
            "statistics": week_statistics,
            "prev_week": week_start - timedelta(days=7),
            "next_week": week_start + timedelta(days=7),
            "today": date.today(),
        }

    def _process_tasks_for_calendar(self, tasks: List) -> List[Dict[str, Any]]:
        """Обработка задач для календаря."""
        processed = []
        for task in tasks:
            if task.start_time:
                try:
                    start_dt = task.start_time
                    duration_minutes = task.supposed_time or 30

                    end_minute = (start_dt.minute + duration_minutes) % 60
                    end_hour = start_dt.hour + (
                        start_dt.minute + duration_minutes
                    ) // 60

                    processed.append(
                        {
                            "task": task,
                            "start_hour": start_dt.hour,
                            "start_minute": start_dt.minute,
                            "duration_minutes": duration_minutes,
                            "end_minute": end_minute,
                            "end_hour": end_hour,
                            "start_datetime": start_dt,
                        }
                    )
                except Exception as e:
                    logger.error(f"Ошибка обработки задачи {task.id}: {e}")
                    continue
        return processed

    def _process_events_for_calendar(self, events: List) -> List[Dict[str, Any]]:
        """Обработка событий для календаря."""
        processed = []
        for event in events:
            if event.start_time:
                try:
                    start_dt = self._parse_datetime(event.start_time)
                    end_dt = (
                        self._parse_datetime(event.end_time) if event.end_time else None
                    )

                    if not end_dt:
                        end_dt = start_dt + timedelta(hours=1)

                    duration_minutes = int((end_dt - start_dt).total_seconds() / 60)

                    processed.append(
                        {
                            "event": event,
                            "start_hour": start_dt.hour,
                            "start_minute": start_dt.minute,
                            "end_hour": end_dt.hour,
                            "end_minute": end_dt.minute,
                            "duration_minutes": duration_minutes,
                            "start_datetime": start_dt,
                            "end_datetime": end_dt,
                        }
                    )
                except Exception as e:
                    logger.error(f"Ошибка обработки события {event.id}: {e}")
                    continue
        return processed

    def _parse_datetime(self, dt_value: Any) -> datetime:
        """Парсинг datetime из разных форматов."""
        if isinstance(dt_value, str):
            if "Z" in dt_value:
                dt_value = dt_value.replace("Z", "+00:00")
            return datetime.fromisoformat(dt_value)
        return dt_value

    def _get_day_name(self, date_obj: date) -> str:
        """Получить название дня недели на русском."""
        days = {
            0: "Понедельник",
            1: "Вторник",
            2: "Среда",
            3: "Четверг",
            4: "Пятница",
            5: "Суббота",
            6: "Воскресенье",
        }
        return days[date_obj.weekday()]
