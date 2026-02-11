from datetime import date, datetime, timedelta
from flask import session, redirect, render_template, request, jsonify, url_for
from typing import Tuple, Optional
import logging

from pydantic import ValidationError

from models.event import EventCreateDto, EventUpdateDto
from models.task import TaskCreateDto, TaskUpdateDto
from services.task_services import TaskServices
from presenters.schedule_presenter import SchedulePresenter

# Настройка логирования
logger = logging.getLogger(__name__)


class TaskController:
    def __init__(self, task_service: TaskServices):
        self.task_service = task_service
        self.presenter = SchedulePresenter()

    def _get_user_id(self) -> Optional[int]:
        """Получить ID пользователя из сессии"""
        return session.get("user_id")

    def _get_user_name(self) -> Optional[str]:
        """Получить имя пользователя из сессии"""
        return session.get("user_name")

    def _check_auth(self) -> Tuple[int, str]:
        """Проверить аутентификацию и вернуть user_id и user_name"""
        user_id = self._get_user_id()
        if user_id is None:
            return None, None  # Перенаправление на логин

        user_name = self._get_user_name() or "Пользователь"
        return user_id, user_name

    def _parse_date_param(self, date_str: Optional[str]) -> Optional[date]:
        """Парсинг строки даты из параметров запроса"""
        if not date_str:
            return None

        try:
            parts = date_str.split("-")
            if len(parts) != 3:
                return None
            year, month, day = map(int, parts)
            return date(year, month, day)
        except (ValueError, TypeError) as e:
            logger.warning(f"Ошибка парсинга даты {date_str}: {e}")
            return None

    def day_index(self):
        user_id, user_name = self._check_auth()
        if user_id is None:
            return redirect(url_for("users.signin"))

        selected_date = self._parse_date_param(request.args.get("date")) or date.today()

        try:
            schedule = self.task_service.get_daily_schedule(user_id, selected_date)
            statistics = self.task_service.get_daily_statistics(user_id, selected_date)

            context = self.presenter.prepare_daily_view(
                schedule, statistics, user_name, selected_date
            )

            return render_template("day_index.html", **context)
        except Exception as e:
            logger.error(f"Ошибка в day_index: {e}")
            return render_template(
                "error.html", error="Произошла ошибка при загрузке расписания"
            )

    def week_index(self):
        """Главная страница недельного расписания"""
        try:
            user_id, user_name = self._check_auth()
        except redirect as e:
            return e

        try:
            selected_date_str = request.args.get("week_start")
            if selected_date_str:
                week_start = date.fromisoformat(selected_date_str)
            else:
                today = date.today()
                week_start = today - timedelta(days=today.weekday())

            if week_start.weekday() != 0:
                week_start = week_start - timedelta(days=week_start.weekday())

            week_schedule = self.task_service.get_weekly_schedule(
                user_id, week_start=week_start
            )
            week_statistics = self.task_service.get_weekly_statistics(
                user_id, week_start=week_start
            )

            context = self.presenter.prepare_weekly_view(
                week_schedule, week_statistics, user_name, week_start
            )

            return render_template("week_index.html", **context)

        except Exception as e:
            logger.error(f"Ошибка в week_index: {e}")
            # В случае ошибки лучше вернуть шаблон с сообщением об ошибке
            return render_template("week_index.html", error=str(e), user_name=user_name)

    
    def create_task(self):
        """Обработка создания задачи"""
        try:
            user_id, user_name = self._check_auth()
        except redirect as e:
            return e

        if request.is_json:
            try:
                data = request.get_json()
                task_data = TaskCreateDto(**data, user_id=user_id)
                new_task = self.task_service.create_task(task_data)
                return jsonify({'success': True, 'task': new_task.model_dump()}), 201
            except Exception as e:
                logger.error(f"Ошибка при создании задачи через API: {e}")
                return jsonify({'error': str(e)}), 400

        if request.method == "POST":
            try:
                form_data = request.form.to_dict()
                if 'difficulty' in form_data:
                    form_data['difficulty'] = int(form_data['difficulty'])
                if 'supposed_time' in form_data:
                    form_data['supposed_time'] = int(form_data['supposed_time'])
                
                task_data = TaskCreateDto(**form_data, user_id=user_id)
                self.task_service.create_task(task_data)
                
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
    
    def create_event(self):
        """Обработка создания события"""
        try:
            user_id, user_name = self._check_auth()
        except redirect as e:
            return e

        if request.is_json:
            try:
                data = request.get_json()
                data['is_repeated'] = data.get('is_repeated', False)
                event_data = EventCreateDto(**data, user_id=user_id)
                new_event = self.task_service.create_event(event_data)
                return jsonify({'success': True, 'event': new_event.model_dump()}), 201
            except Exception as e:
                logger.error(f"Ошибка при создании события через API: {e}")
                if isinstance(e, ValidationError):
                    return jsonify({'error': e.errors()}), 400
                return jsonify({'error': repr(e)}), 400

        if request.method == "POST":
            try:
                form_data = request.form.to_dict()
                form_data['is_repeated'] = 'is_repeated' in form_data
                if 'difficulty' in form_data:
                    form_data['difficulty'] = int(form_data['difficulty'])
                if 'repeat_weekday' in form_data and form_data['repeat_weekday']:
                    form_data['repeat_weekday'] = int(form_data['repeat_weekday'])
                else:
                    form_data['repeat_weekday'] = None
                
                if 'start_time' in form_data:
                    form_data['start_time'] = datetime.fromisoformat(form_data['start_time'])
                if 'end_time' in form_data and form_data['end_time']:
                    form_data['end_time'] = datetime.fromisoformat(form_data['end_time'])
                
                event_data = EventCreateDto(**form_data, user_id=user_id)
                self.task_service.create_event(event_data)
                
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

    def update_task_api(self, task_id: int):
        """API: Обновить задачу"""
        try:
            user_id, _ = self._check_auth()
        except redirect:
            return jsonify({'error': 'Требуется аутентификация'}), 401

        try:
            task = self.task_service.get_task_by_id(task_id)
            if not task or task.user_id != user_id:
                return jsonify({'error': 'Задача не найдена или нет доступа'}), 404

            update_data = TaskUpdateDto(**request.get_json())
            updated_task = self.task_service.update_task(task_id, update_data)

            return jsonify({'success': True, 'task': updated_task.model_dump()})
        except Exception as e:
            logger.error(f"Ошибка при обновлении задачи: {e}")
            return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500

    def delete_task_api(self, task_id: int):
        """API: Удалить задачу"""
        try:
            user_id, _ = self._check_auth()
        except redirect:
            return jsonify({'error': 'Требуется аутентификация'}), 401

        try:
            task = self.task_service.get_task_by_id(task_id)
            if not task or task.user_id != user_id:
                return jsonify({'error': 'Задача не найдена или нет доступа'}), 404

            self.task_service.delete_task(task_id)
            return jsonify({'success': True, 'message': 'Задача успешно удалена'})
        except Exception as e:
            logger.error(f"Ошибка при удалении задачи: {e}")
            return jsonify({'error': f'Ошибка при удалении: {str(e)}'}), 500

    def get_event_details(self, event_id: int):
        """API: Получить детали события"""
        try:
            user_id, _ = self._check_auth()
        except redirect:
            return jsonify({'error': 'Требуется аутентификация'}), 401
        
        try:
            event = self.task_service.get_event_by_id(event_id)
            if not event or event.user_id != user_id:
                return jsonify({'error': 'Событие не найдено или нет доступа'}), 404
            
            return jsonify({'success': True, 'event': event.model_dump()})
        except Exception as e:
            logger.error(f"Ошибка при получении деталей события: {e}")
            return jsonify({'error': f'Ошибка: {str(e)}'}), 500

    def update_event_api(self, event_id: int):
        """API: Обновить событие"""
        try:
            user_id, _ = self._check_auth()
        except redirect:
            return jsonify({'error': 'Требуется аутентификация'}), 401

        try:
            event = self.task_service.get_event_by_id(event_id)
            if not event or event.user_id != user_id:
                return jsonify({'error': 'Событие не найдено или нет доступа'}), 404

            update_data = EventUpdateDto(**request.get_json())
            updated_event = self.task_service.update_event(event_id, update_data)

            return jsonify({'success': True, 'event': updated_event.model_dump()})
        except Exception as e:
            logger.error(f"Ошибка при обновлении события: {e}")
            return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500

    def delete_event_api(self, event_id: int):
        """API: Удалить событие"""
        try:
            user_id, _ = self._check_auth()
        except redirect:
            return jsonify({'error': 'Требуется аутентификация'}), 401

        try:
            event = self.task_service.get_event_by_id(event_id)
            if not event or event.user_id != user_id:
                return jsonify({'error': 'Событие не найдено или нет доступа'}), 404

            self.task_service.delete_event(event_id)
            return jsonify({'success': True, 'message': 'Событие успешно удалено'})
        except Exception as e:
            logger.error(f"Ошибка при удалении события: {e}")
            return jsonify({'error': f'Ошибка при удалении: {str(e)}'}), 500
    
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