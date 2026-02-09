from datetime import date, datetime, timedelta
from flask import session, redirect, render_template, request, jsonify, url_for
from typing import Tuple, Optional
import logging

from models.event import EventCreateDto
from models.task import TaskCreateDto
from services.task_services import TaskServices

# Настройка логирования
logger = logging.getLogger(__name__)


class TaskController:
    def __init__(self, task_service: TaskServices):
        self.task_service = task_service
    
    def _get_user_id(self) -> Optional[int]:
        """Получить ID пользователя из сессии"""
        return session.get('user_id')
    
    def _get_user_name(self) -> Optional[str]:
        """Получить имя пользователя из сессии"""
        return session.get('user_name')
    
    def _check_auth(self) -> Tuple[int, str]:
        """Проверить аутентификацию и вернуть user_id и user_name"""
        user_id = self._get_user_id()
        if user_id is None:
            raise redirect(url_for('users.signin'))  # Перенаправление на логин
        
        user_name = self._get_user_name() or "Пользователь"
        return user_id, user_name
    
    def _parse_date_param(self, date_str: Optional[str]) -> Optional[date]:
        """Парсинг строки даты из параметров запроса"""
        if not date_str:
            return None
        
        try:
            parts = date_str.split('-')
            if len(parts) != 3:
                return None
            year, month, day = map(int, parts)
            return date(year, month, day)
        except (ValueError, TypeError) as e:
            logger.warning(f"Ошибка парсинга даты {date_str}: {e}")
            return None
    
    def day_index(self):
        try:
            user_id, user_name = self._check_auth()
        except redirect as e:
            return e
        
        # Определяем дату
        selected_date = self._parse_date_param(request.args.get("date"))
        if not selected_date:
            selected_date = date.today()
        
        try:
            # Получаем расписание на день
            schedule = self.task_service.get_daily_schedule(user_id, selected_date)
            
            # Подготавливаем данные для представления
            processed_tasks = self._process_tasks_for_calendar(schedule.tasks)
            processed_events = self._process_events_for_calendar(schedule.events)
            
            # Получаем статистику
            statistics = self.task_service.get_daily_statistics(user_id, selected_date)
            
            # Разделяем задачи
            pending_tasks = [task for task in schedule.tasks if not task.is_done]
            completed_tasks = [task for task in schedule.tasks if task.is_done]
            
            return render_template(
                "day_index.html",
                user_name=user_name,
                selected_date=selected_date.strftime("%Y-%m-%d"),
                
                # Для статистики
                statistics=statistics,
                
                # Для календаря
                processed_tasks=processed_tasks,
                processed_events=processed_events,
                
                # Для списков
                undone=pending_tasks,
                done=completed_tasks,
                events=schedule.events,
                
                # Для текущего времени
                current_hour=datetime.now().hour if selected_date == date.today() else None,
                today=date.today().strftime("%Y-%m-%d")
            )
        except Exception as e:
            logger.error(f"Ошибка в day_index: {e}")
            return render_template("error.html", error="Произошла ошибка при загрузке расписания")

    def _process_tasks_for_calendar(self, tasks):
        """Обработка задач для календаря"""
        processed = []
        for task in tasks:
            if task.start_time:
                try:
                    start_dt = task.start_time
                    duration_minutes = task.supposed_time or 30
                    
                    end_minute = (start_dt.minute + duration_minutes) % 60
                    end_hour = start_dt.hour + (start_dt.minute + duration_minutes) // 60
                    
                    processed.append({
                        'task': task,
                        'start_hour': start_dt.hour,
                        'start_minute': start_dt.minute,
                        'duration_minutes': duration_minutes,
                        'end_minute': end_minute,
                        'end_hour': end_hour,
                        'start_datetime': start_dt
                    })
                except Exception as e:
                    logger.error(f"Ошибка обработки задачи {task.id}: {e}")
                    continue
        return processed

    def _process_events_for_calendar(self, events):
        """Обработка событий для календаря"""
        processed = []
        for event in events:
            if event.start_time:
                try:
                    # Конвертируем время
                    start_dt = self._parse_datetime(event.start_time)
                    end_dt = self._parse_datetime(event.end_time) if event.end_time else None
                    
                    if not end_dt:
                        end_dt = start_dt + timedelta(hours=1)
                    
                    duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
                    
                    processed.append({
                        'event': event,
                        'start_hour': start_dt.hour,
                        'start_minute': start_dt.minute,
                        'end_hour': end_dt.hour,
                        'end_minute': end_dt.minute,
                        'duration_minutes': duration_minutes,
                        'start_datetime': start_dt,
                        'end_datetime': end_dt
                    })
                except Exception as e:
                    logger.error(f"Ошибка обработки события {event.id}: {e}")
                    continue
        return processed

    def _parse_datetime(self, dt_value):
        """Парсинг datetime из разных форматов"""
        if isinstance(dt_value, str):
            # Убираем Z и преобразуем
            if 'Z' in dt_value:
                dt_value = dt_value.replace('Z', '+00:00')
            return datetime.fromisoformat(dt_value)
        return dt_value
    
    def week_index(self):
        """Главная страница недельного расписания"""
        try:
            user_id, user_name = self._check_auth()
            # Определяем дату начала недели
            selected_date_str = request.args.get('week_start')
            if selected_date_str:
                selected_date = date.fromisoformat(selected_date_str)
            else:
                # Если не указана, используем понедельник текущей недели
                today = date.today()
                selected_date = today - timedelta(days=today.weekday())  # Приводим к понедельнику
            
            # Проверяем, что дата действительно понедельник
            if selected_date.weekday() != 0:  # 0 = понедельник
                selected_date = selected_date - timedelta(days=selected_date.weekday())
            
            # Получаем расписание на неделю
            week_schedule = self.task_service.get_weekly_schedule(
                user_id,  # Здесь должен быть реальный user_id из сессии
                week_start=selected_date
            )
            
            # Получаем статистику за неделю
            week_statistics = self.task_service.get_weekly_statistics(
                user_id,
                week_start=selected_date
            )
            
            # Формируем данные для календаря
            week_data = []
            for day_schedule in week_schedule.days:
                # Обрабатываем задачи для дня
                processed_tasks = []
                for task in day_schedule.tasks:
                    if task.start_time:
                        start_dt = task.start_time
                        start_hour = start_dt.hour
                        start_minute = start_dt.minute
                        
                        # Рассчитываем продолжительность
                        duration_minutes = task.supposed_time if task.supposed_time else 30
                        
                        processed_tasks.append({
                            'task': task,
                            'start_datetime': start_dt,
                            'start_hour': start_hour,
                            'start_minute': start_minute,
                            'duration_minutes': duration_minutes
                        })
                
                # Обрабатываем события для дня
                processed_events = []
                for event in day_schedule.events:
                    if event.start_time:
                        start_dt = event.start_time
                        start_hour = start_dt.hour
                        start_minute = start_dt.minute
                        
                        # Рассчитываем продолжительность события
                        duration_minutes = 60  # По умолчанию 1 час
                        if event.end_time and event.start_time:
                            duration_minutes = int((event.end_time - event.start_time).total_seconds() / 60)
                        
                        processed_events.append({
                            'event': event,
                            'start_datetime': start_dt,
                            'start_hour': start_hour,
                            'start_minute': start_minute,
                            'duration_minutes': duration_minutes,
                            'end_datetime': event.end_time if hasattr(event, 'end_time') else None
                        })
                
                # Разделяем задачи на выполненные и активные
                undone_tasks = [t for t in day_schedule.tasks if not t.is_done]
                done_tasks = [t for t in day_schedule.tasks if t.is_done]
                
                week_data.append({
                    'date': day_schedule.day,
                    'day_name': self._get_day_name(day_schedule.day),
                    'date_str': day_schedule.day.strftime('%d.%m'),
                    'full_date_str': day_schedule.day.strftime('%d %B %Y'),
                    'tasks': day_schedule.tasks,
                    'events': day_schedule.events,
                    'undone_tasks': undone_tasks,
                    'done_tasks': done_tasks,
                    'processed_tasks': processed_tasks,
                    'processed_events': processed_events,
                    'is_today': day_schedule.day == date.today()
                })
            
            # Формируем диапазон недели
            week_end = selected_date + timedelta(days=6)
            week_range = f"{selected_date.strftime('%d %b')} - {week_end.strftime('%d %b %Y')}"
            
            # Определяем предыдущую и следующую недели
            prev_week = selected_date - timedelta(days=7)
            next_week = selected_date + timedelta(days=7)
            
            return render_template(
                'week_index.html',
                week_data=week_data,
                week_start=selected_date,
                week_end=week_end,
                week_range=week_range,
                statistics=week_statistics,
                prev_week=prev_week,
                next_week=next_week,
                today=date.today()
            )
            
        except Exception as e:
            print(f"Error in week_index: {e}")
            return render_template(
                'week_index.html',
                error=str(e),
                week_data=[],
                week_start=date.today(),
                week_end=date.today(),
                week_range="Ошибка",
                statistics=None,
                prev_week=date.today(),
                next_week=date.today(),
                today=date.today()
            )
    
    def _get_day_name(self, date_obj: date) -> str:
        """Получить название дня недели на русском"""
        days = {
            0: 'Понедельник',
            1: 'Вторник',
            2: 'Среда',
            3: 'Четверг',
            4: 'Пятница',
            5: 'Суббота',
            6: 'Воскресенье'
        }
        return days[date_obj.weekday()]
    
    def create_task_page(self):
        """Страница создания задачи"""
        try:
            user_id, user_name = self._check_auth()
        except redirect as e:
            return e
        
        return render_template("create.html", user_name=user_name)
    
    def create_task(self):
        """Обработка создания задачи"""
        try:
            user_id, user_name = self._check_auth()
        except redirect as e:
            return e
        
        if request.method == "POST":
            try:
                # Получаем данные из формы
                form_data = request.form.to_dict()
                
                # Конвертируем строковые значения
                if 'difficulty' in form_data:
                    form_data['difficulty'] = int(form_data['difficulty'])
                if 'supposed_time' in form_data:
                    form_data['supposed_time'] = int(form_data['supposed_time'])
                
                # Создаем DTO
                task_data = TaskCreateDto(**form_data, user_id=user_id)
                
                # Сохраняем задачу
                self.task_service.create_task(task_data)
                
                # Перенаправляем на главную страницу
                return redirect(url_for('day_index'))
                
            except Exception as e:
                logger.error(f"Ошибка при создании задачи: {e}")
                return render_template(
                    "create.html", 
                    error=f"Ошибка при создании задачи: {str(e)}", 
                    user_name=user_name,
                    form_data=request.form.to_dict()
                )
        
        return render_template("create.html", user_name=user_name)
    
    def create_event_page(self):
        """Страница создания события"""
        try:
            user_id, user_name = self._check_auth()
        except redirect as e:
            return e
        
        return render_template("create_event.html", user_name=user_name)
    
    def create_event(self):
        """Обработка создания события"""
        try:
            user_id, user_name = self._check_auth()
        except redirect as e:
            return e
        
        if request.method == "POST":
            try:
                # Получаем данные из формы
                form_data = request.form.to_dict()
                
                # Обработка checkbox
                form_data['is_repeated'] = 'is_repeated' in form_data
                
                # Конвертируем значения
                if 'difficulty' in form_data:
                    form_data['difficulty'] = int(form_data['difficulty'])
                if 'repeat_weekday' in form_data and form_data['repeat_weekday']:
                    form_data['repeat_weekday'] = int(form_data['repeat_weekday'])
                else:
                    form_data['repeat_weekday'] = None
                
                # Конвертируем строки времени в datetime
                from datetime import datetime
                if 'start_time' in form_data:
                    form_data['start_time'] = datetime.fromisoformat(form_data['start_time'])
                if 'end_time' in form_data and form_data['end_time']:
                    form_data['end_time'] = datetime.fromisoformat(form_data['end_time'])
                
                # Создаем DTO
                event_data = EventCreateDto(**form_data, user_id=user_id)
                
                # Сохраняем событие
                self.task_service.create_event(event_data)
                
                # Перенаправляем на главную страницу
                return redirect(url_for('day_index'))
                
            except Exception as e:
                logger.error(f"Ошибка при создании события: {e}")
                return render_template(
                    "create_event.html", 
                    error=f"Ошибка при создании события: {str(e)}", 
                    user_name=user_name,
                    form_data=request.form.to_dict()
                )
        
        return render_template("create_event.html", user_name=user_name)
    
    def check_task(self):
        """API: Отметить задачу как выполненную"""
        try:
            user_id, user_name = self._check_auth()
        except redirect as e:
            return jsonify({'error': 'Требуется аутентификация'}), 401
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Отсутствуют данные'}), 400
            
            task_id = int(data.get('taskId'))
            minutes = int(data.get('minutes'))
            
            # Отмечаем задачу как выполненную
            result = self.task_service.mark_task_as_done(task_id, user_id, minutes)
            
            if not result:
                return jsonify({'error': 'Задача не найдена или нет доступа'}), 404
            
            return jsonify({
                'success': True,
                'message': 'Задача успешно завершена',
                'task': {
                    'id': result.id,
                    'title': result.title,
                    'actual_time': result.actual_time
                }
            })
            
        except ValueError as e:
            logger.error(f"Ошибка валидации: {e}")
            return jsonify({'error': 'Неверные данные'}), 400
        except Exception as e:
            logger.error(f"Ошибка при завершении задачи: {e}")
            return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500
    
    def delete_task_api(self):
        """API: Удалить задачу"""
        try:
            user_id, user_name = self._check_auth()
        except redirect as e:
            return jsonify({'error': 'Требуется аутентификация'}), 401
        
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Отсутствуют данные'}), 400
            
            task_id = int(data.get('taskId'))
            
            # Удаляем задачу
            self.task_service.delete_task(task_id)
            
            return jsonify({
                'success': True,
                'message': 'Задача успешно удалена'
            })
            
        except Exception as e:
            logger.error(f"Ошибка при удалении задачи: {e}")
            return jsonify({'error': f'Ошибка при удалении: {str(e)}'}), 500
    
    def get_task_details(self, task_id: int):
        """Получить детали задачи"""
        try:
            user_id, user_name = self._check_auth()
        except redirect as e:
            return jsonify({'error': 'Требуется аутентификация'}), 401
        
        try:
            task = self.task_service.get_task_by_id(task_id)
            
            if not task:
                return jsonify({'error': 'Задача не найдена'}), 404
            
            # Проверяем, что задача принадлежит пользователю
            if task.user_id != user_id:
                return jsonify({'error': 'Нет доступа к задаче'}), 403
            
            return jsonify({
                'success': True,
                'task': task.model_dump()
            })
            
        except Exception as e:
            logger.error(f"Ошибка при получении деталей задачи: {e}")
            return jsonify({'error': f'Ошибка: {str(e)}'}), 500
    
    def get_statistics_api(self):
        """API: Получить статистику"""
        try:
            user_id, user_name = self._check_auth()
        except redirect as e:
            return jsonify({'error': 'Требуется аутентификация'}), 401
        
        try:
            period = request.args.get('period', 'day')
            date_str = request.args.get('date')
            
            selected_date = self._parse_date_param(date_str) or date.today()
            
            if period == 'week':
                week_start = selected_date - timedelta(days=selected_date.weekday())
                statistics = self.task_service.get_weekly_statistics(user_id, week_start)
            else:
                statistics = self.task_service.get_daily_statistics(user_id, selected_date)
            
            return jsonify({
                'success': True,
                'statistics': statistics.model_dump(),
                'period': period,
                'date': selected_date.strftime("%Y-%m-%d")
            })
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            return jsonify({'error': f'Ошибка: {str(e)}'}), 500