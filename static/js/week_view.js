/**
 * Функционал недельного представления
 */

class WeekView {
    constructor() {
        this.selectedDate = null;
        this.currentTaskId = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupWeekNavigation();
        this.setupDaySelection();
        this.setupDragAndDrop();
        this.updateCurrentTime();
        
        // Обновление текущего времени каждую минуту
        setInterval(() => this.updateCurrentTime(), 60000);
    }

    setupEventListeners() {
        // Выбор недели через datepicker
        const weekPicker = document.getElementById('select-week');
        if (weekPicker) {
            weekPicker.addEventListener('change', (e) => {
                const selectedDate = new Date(e.target.value);
                const monday = this.getMonday(selectedDate);
                window.location.href = `/week?week_start=${monday.toISOString().split('T')[0]}`;
            });
        }

        // Закрытие деталей дня
        const closeDetailsBtn = document.getElementById('close-details');
        if (closeDetailsBtn) {
            closeDetailsBtn.addEventListener('click', () => {
                this.hideDayDetails();
            });
        }

        // Переключение табов в деталях дня
        const tabButtons = document.querySelectorAll('.details-tab-btn');
        tabButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.dataset.tab;
                this.switchDayDetailsTab(tab);
            });
        });

        // Клик по элементу в расписании
        document.addEventListener('click', (e) => {
            const taskElement = e.target.closest('.week-item.task-item');
            if (taskElement) {
                const taskId = taskElement.dataset.taskId;
                const date = taskElement.dataset.date;
                this.showTaskDetails(taskId, date);
            }

            const eventElement = e.target.closest('.week-item.event-item');
            if (eventElement) {
                const eventId = eventElement.dataset.eventId;
                const date = eventElement.dataset.date;
                this.showEventDetails(eventId, date);
            }
        });
    }

    setupWeekNavigation() {
        // Навигация стрелками клавиатуры
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            switch(e.key) {
                case 'ArrowLeft':
                    this.navigateWeek('prev');
                    break;
                case 'ArrowRight':
                    this.navigateWeek('next');
                    break;
                case 'Escape':
                    this.hideDayDetails();
                    break;
            }
        });
    }

    setupDaySelection() {
        // Клик по заголовку дня
        const dayHeaders = document.querySelectorAll('.day-header:not(.time-column)');
        dayHeaders.forEach(header => {
            header.addEventListener('click', (e) => {
                const date = header.dataset.date;
                const dayData = this.getDayData(date);
                if (dayData) {
                    this.showDayDetails(dayData);
                }
            });
        });
    }

    setupDragAndDrop() {
        // Перетаскивание несрочных задач
        const unscheduledTasks = document.querySelectorAll('.unscheduled-task');
        const daySlots = document.querySelectorAll('.day-time-slot');

        unscheduledTasks.forEach(task => {
            task.setAttribute('draggable', 'true');
            
            task.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', task.dataset.taskId);
                task.classList.add('dragging');
            });

            task.addEventListener('dragend', () => {
                task.classList.remove('dragging');
                daySlots.forEach(slot => slot.classList.remove('drag-over'));
            });
        });

        daySlots.forEach(slot => {
            slot.addEventListener('dragover', (e) => {
                e.preventDefault();
                slot.classList.add('drag-over');
            });

            slot.addEventListener('dragleave', () => {
                slot.classList.remove('drag-over');
            });

            slot.addEventListener('drop', async (e) => {
                e.preventDefault();
                slot.classList.remove('drag-over');
                
                const taskId = e.dataTransfer.getData('text/plain');
                const date = slot.dataset.date;
                const hour = parseInt(slot.dataset.hour);
                const minutes = Math.floor((e.offsetY / slot.offsetHeight) * 60);
                
                if (taskId) {
                    await this.scheduleTask(taskId, date, hour, minutes);
                }
            });
        });
    }

    async scheduleTask(taskId, date, hour, minutes) {
        try {
            const startTime = new Date(date);
            startTime.setHours(hour, minutes, 0, 0);
            
            const response = await fetch('/api/tasks/schedule', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    task_id: parseInt(taskId),
                    start_time: startTime.toISOString()
                })
            });

            if (response.ok) {
                location.reload();
            } else {
                alert('Ошибка при планировании задачи');
            }
        } catch (error) {
            console.error('Error scheduling task:', error);
            alert('Ошибка при планировании задачи');
        }
    }

    showDayDetails(dayData) {
        const detailsContainer = document.getElementById('day-details');
        const titleElement = document.getElementById('selected-day-title');
        const contentElement = document.getElementById('day-details-content');
        
        // Обновляем заголовок
        titleElement.textContent = `${dayData.day_name}, ${dayData.full_date_str}`;
        
        // Обновляем счетчики
        document.getElementById('day-tasks-count').textContent = dayData.undone_tasks.length;
        document.getElementById('day-events-count').textContent = dayData.events.length;
        document.getElementById('day-completed-count').textContent = dayData.done_tasks.length;
        
        // Заполняем контент
        contentElement.innerHTML = this.generateDayDetailsContent(dayData);
        
        // Показываем панель
        detailsContainer.classList.remove('hidden');
        
        // Скроллим к панели
        detailsContainer.scrollIntoView({ behavior: 'smooth' });
        
        this.selectedDate = dayData.date;
    }

    generateDayDetailsContent(dayData) {
        return `
            <div class="day-tasks-list">
                ${this.generateTasksList(dayData.undone_tasks, 'active')}
                ${this.generateEventsList(dayData.events)}
                ${this.generateTasksList(dayData.done_tasks, 'completed')}
            </div>
        `;
    }

    generateTasksList(tasks, status) {
        if (tasks.length === 0) {
            return `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>Нет ${status === 'active' ? 'активных' : 'выполненных'} задач</p>
                </div>
            `;
        }

        return tasks.map(task => `
            <div class="day-task-card" data-task-id="${task.id}">
                <div class="day-task-header">
                    <div class="day-task-title">${task.title}</div>
                    <div class="day-task-time">
                        ${task.start_time ? `<i class="far fa-clock"></i>${task.start_time}` : ''}
                    </div>
                </div>
                ${task.description ? `<p class="task-description">${task.description}</p>` : ''}
                <div class="day-task-meta">
                    <span class="day-task-meta-item">
                        <i class="fas fa-signal"></i>
                        Сложность: ${task.difficulty}
                    </span>
                    <span class="day-task-meta-item">
                        <i class="far fa-clock"></i>
                        Время: ${task.supposed_time || 30} мин
                    </span>
                    ${status === 'completed' && task.actual_time ? `
                        <span class="day-task-meta-item">
                            <i class="fas fa-stopwatch"></i>
                            Факт: ${task.actual_time} мин
                        </span>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    generateEventsList(events) {
        if (events.length === 0) {
            return `
                <div class="empty-state">
                    <i class="fas fa-calendar"></i>
                    <p>Нет событий</p>
                </div>
            `;
        }

        return events.map(event => `
            <div class="day-task-card event-card" data-event-id="${event.id}">
                <div class="day-task-header">
                    <div class="day-task-title">${event.title}</div>
                    <div class="day-task-time">
                        <i class="far fa-clock"></i>
                        ${event.start_time ? event.start_time : ''}
                        ${event.end_time ? ` - ${event.end_time}` : ''}
                    </div>
                </div>
                ${event.description ? `<p class="task-description">${event.description}</p>` : ''}
                <div class="day-task-meta">
                    ${event.is_repeated ? `
                        <span class="day-task-meta-item">
                            <i class="fas fa-redo"></i>
                            Повторяющееся
                        </span>
                    ` : ''}
                    ${event.difficulty > 1 ? `
                        <span class="day-task-meta-item">
                            <i class="fas fa-star"></i>
                            Важность: ${event.difficulty}
                        </span>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    hideDayDetails() {
        const detailsContainer = document.getElementById('day-details');
        detailsContainer.classList.add('hidden');
        this.selectedDate = null;
    }

    switchDayDetailsTab(tabName) {
        // Обновляем активный таб
        const tabButtons = document.querySelectorAll('.details-tab-btn');
        tabButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Показываем соответствующий контент
        // (в реальной реализации здесь будет загрузка данных для выбранного таба)
    }

    async showTaskDetails(taskId, date) {
        try {
            const response = await fetch(`/api/tasks/${taskId}?date=${date}`);
            if (response.ok) {
                const task = await response.json();
                this.openTaskDetailsModal(task);
            }
        } catch (error) {
            console.error('Error fetching task details:', error);
        }
    }

    async showEventDetails(eventId, date) {
        try {
            const response = await fetch(`/api/events/${eventId}?date=${date}`);
            if (response.ok) {
                const event = await response.json();
                this.openEventDetailsModal(event);
            }
        } catch (error) {
            console.error('Error fetching event details:', error);
        }
    }

    openTaskDetailsModal(task) {
        // Используем существующее модальное окно деталей задачи
        const modal = document.getElementById('task-details-modal');
        const content = document.getElementById('task-details-content');
        
        content.innerHTML = `
            <div class="task-preview">
                <h4>${task.title}</h4>
                ${task.description ? `<p class="task-description">${task.description}</p>` : ''}
                <div class="details-grid">
                    <div class="detail-item">
                        <i class="fas fa-signal"></i>
                        <span>Сложность:</span>
                        <strong>${task.difficulty}</strong>
                    </div>
                    <div class="detail-item">
                        <i class="far fa-clock"></i>
                        <span>Планируемое время:</span>
                        <strong>${task.supposed_time || 30} мин</strong>
                    </div>
                    ${task.start_time ? `
                        <div class="detail-item">
                            <i class="fas fa-calendar"></i>
                            <span>Время начала:</span>
                            <strong>${new Date(task.start_time).toLocaleTimeString()}</strong>
                        </div>
                    ` : ''}
                    ${task.actual_time ? `
                        <div class="detail-item">
                            <i class="fas fa-stopwatch"></i>
                            <span>Фактическое время:</span>
                            <strong>${task.actual_time} мин</strong>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        modal.classList.remove('hidden');
    }

    openEventDetailsModal(event) {
        // Аналогично для событий
        const modal = document.getElementById('task-details-modal');
        const content = document.getElementById('task-details-content');
        
        content.innerHTML = `
            <div class="task-preview">
                <h4>${event.title}</h4>
                ${event.description ? `<p class="task-description">${event.description}</p>` : ''}
                <div class="details-grid">
                    <div class="detail-item">
                        <i class="far fa-calendar"></i>
                        <span>Дата:</span>
                        <strong>${new Date(event.start_time).toLocaleDateString()}</strong>
                    </div>
                    <div class="detail-item">
                        <i class="far fa-clock"></i>
                        <span>Время:</span>
                        <strong>
                            ${new Date(event.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            ${event.end_time ? ` - ${new Date(event.end_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}` : ''}
                        </strong>
                    </div>
                    ${event.is_repeated ? `
                        <div class="detail-item">
                            <i class="fas fa-redo"></i>
                            <span>Повтор:</span>
                            <strong>Есть</strong>
                        </div>
                    ` : ''}
                    ${event.difficulty > 1 ? `
                        <div class="detail-item">
                            <i class="fas fa-star"></i>
                            <span>Важность:</span>
                            <strong>${event.difficulty}</strong>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        modal.classList.remove('hidden');
    }

    navigateWeek(direction) {
        const currentWeekStart = new Date(document.querySelector('.week-range').dataset.start);
        let newWeekStart;
        
        if (direction === 'prev') {
            newWeekStart = new Date(currentWeekStart);
            newWeekStart.setDate(currentWeekStart.getDate() - 7);
        } else {
            newWeekStart = new Date(currentWeekStart);
            newWeekStart.setDate(currentWeekStart.getDate() + 7);
        }
        
        window.location.href = `/week?week_start=${newWeekStart.toISOString().split('T')[0]}`;
    }

    updateCurrentTime() {
        // Удаляем старую линию текущего времени
        document.querySelectorAll('.current-time-line-week').forEach(el => el.remove());
        
        const now = new Date();
        const currentDay = now.toISOString().split('T')[0];
        const currentHour = now.getHours();
        const currentMinute = now.getMinutes();
        
        // Находим колонку текущего дня
        const currentDayColumn = document.querySelector(`.day-column[data-date="${currentDay}"]`);
        if (!currentDayColumn) return;
        
        // Находим слот текущего часа
        const currentHourSlot = currentDayColumn.querySelector(`.day-time-slot[data-hour="${currentHour}"]`);
        if (!currentHourSlot) return;
        
        // Рассчитываем позицию
        const minutePercentage = (currentMinute / 60) * 100;
        const topPosition = (currentHourSlot.offsetHeight * minutePercentage) / 100;
        
        // Создаем линию текущего времени
        const timeLine = document.createElement('div');
        timeLine.className = 'current-time-line-week';
        timeLine.style.top = `${topPosition}px`;
        
        currentHourSlot.style.position = 'relative';
        currentHourSlot.appendChild(timeLine);
    }

    getMonday(date) {
        const d = new Date(date);
        const day = d.getDay();
        const diff = d.getDate() - day + (day === 0 ? -6 : 1); // adjust when day is sunday
        return new Date(d.setDate(diff));
    }

    getDayData(dateString) {
        // Находим данные дня из week_data
        const dayElement = document.querySelector(`.day-header[data-date="${dateString}"]`);
        if (!dayElement) return null;
        
        // В реальной реализации здесь будет запрос к серверу или поиск в данных страницы
        // Для примера возвращаем null
        return null;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    const weekView = new WeekView();
    
    // Экспортируем для глобального доступа (если нужно)
    window.weekView = weekView;
});