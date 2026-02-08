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
    
    # ========== РЕНДЕРИНГ СТРАНИЦ ==========
    
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
            
            # Подготавливаем задачи для календаря
            processed_tasks = []
            for task in schedule.tasks:
                if task.start_time:
                    start_dt = task.start_time
                    duration_minutes = task.supposed_time
                    
                    processed_tasks.append({
                        'task': task,
                        'start_hour': start_dt.hour,
                        'start_minute': start_dt.minute,
                        'duration_minutes': duration_minutes,
                        'end_minute': (start_dt.minute + duration_minutes) % 60,
                        'end_hour': start_dt.hour + (start_dt.minute + duration_minutes) // 60,
                        'start_datetime': start_dt
                    })
            
            # Подготавливаем события для календаря
            processed_events = []
            for event in schedule.events:
                if event.start_time:
                    try:
                        # Конвертируем время из строки в datetime
                        from datetime import datetime
                        if isinstance(event.start_time, str):
                            start_dt = datetime.fromisoformat(event.start_time.replace('Z', '+00:00'))
                        else:
                            start_dt = event.start_time
                        
                        end_dt = None
                        if event.end_time:
                            if isinstance(event.end_time, str):
                                end_dt = datetime.fromisoformat(event.end_time.replace('Z', '+00:00'))
                            else:
                                end_dt = event.end_time
                        
                        if not end_dt:
                            end_dt = start_dt + timedelta(hours=1)
                        
                        duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
                        
                        processed_events.append({
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
            
            # Получаем статистику
            statistics = self.task_service.get_daily_statistics(user_id, selected_date)
            
            # Разделяем задачи на выполненные и невыполненные
            pending_tasks = [task for task in schedule.tasks if not task.is_done]
            completed_tasks = [task for task in schedule.tasks if task.is_done]
            
            # Рассчитываем дополнительные метрики
            pos_count = statistics.positive_differences
            pos_difference = statistics.total_positive_time
            neg_count = statistics.negative_differences
            neg_difference = statistics.total_negative_time
            difficulty_sum = sum(task.difficulty for task in completed_tasks)
            
            return render_template(
                "day_index.html",
                user_name=user_name,
                selected_date=selected_date.strftime("%Y-%m-%d"),
                
                # Для статистики
                pos_count=pos_count,
                pos_difference=pos_difference,
                neg_count=neg_count,
                neg_difference=neg_difference,
                difficulty=difficulty_sum,
                
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
            logger.error(f"Ошибка при получении дневного расписания: {e}")
            return render_template(
                "day_index.html",
                user_name=user_name,
                error="Ошибка при загрузке расписания",
                processed_tasks=[],
                processed_events=[],
                undone=[],
                done=[],
                events=[],
                selected_date=selected_date.strftime("%Y-%m-%d"),
                pos_count=0,
                pos_difference=0,
                neg_count=0,
                neg_difference=0,
                difficulty=0
            )
    
    def week_index(self):
        """Недельное представление"""
        try:
            user_id, user_name = self._check_auth()
        except redirect as e:
            return e
        
        # Определяем дату
        selected_date = self._parse_date_param(request.args.get("date"))
        if not selected_date:
            selected_date = date.today()
        
        # Находим понедельник текущей недели
        week_start = selected_date - timedelta(days=selected_date.weekday())
        
        try:
            # Получаем расписание на неделю
            schedule = self.task_service.get_weekly_schedule(user_id, week_start)
            
            # Получаем статистику за неделю
            statistics = self.task_service.get_weekly_statistics(user_id, week_start)
            
            # Подготавливаем данные для шаблона
            week_days = []
            for day_schedule in schedule.days:
                pending_tasks = [task for task in day_schedule.tasks if not task.is_done]
                completed_tasks = [task for task in day_schedule.tasks if task.is_done]
                
                week_days.append({
                    'date': day_schedule.day,
                    'date_str': day_schedule.day.strftime("%Y-%m-%d"),
                    'day_name': day_schedule.day.strftime("%A"),
                    'tasks': day_schedule.tasks,
                    'events': day_schedule.events,
                    'pending': pending_tasks,
                    'completed': completed_tasks,
                    'total_tasks': len(day_schedule.tasks),
                    'completed_count': len(completed_tasks)
                })
            
            return render_template(
                "week_index.html",
                user_name=user_name,
                week_days=week_days,
                statistics=statistics,
                week_start=week_start.strftime("%Y-%m-%d"),
                selected_date=selected_date.strftime("%Y-%m-%d"),
                today=date.today().strftime("%Y-%m-%d")
            )
            
        except Exception as e:
            logger.error(f"Ошибка при получении недельного расписания: {e}")
            return render_template(
                "week_index.html",
                user_name=user_name,
                error="Ошибка при загрузке недельного расписания",
                week_days=[],
                week_start=week_start.strftime("%Y-%m-%d")
            )
    
    # ========== СОЗДАНИЕ ЗАДАЧ И СОБЫТИЙ ==========
    
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
    
    # ========== API ЭНДПОИНТЫ ==========
    
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