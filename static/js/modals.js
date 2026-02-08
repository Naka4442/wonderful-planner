// Управление модальными окнами
document.addEventListener('DOMContentLoaded', function() {
    // Обработка быстрого выбора времени
    document.querySelectorAll('.time-suggestion').forEach(btn => {
        btn.addEventListener('click', function() {
            const minutes = parseInt(this.getAttribute('data-minutes'));
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            
            document.getElementById('time-hours').value = hours;
            document.getElementById('time-minutes').value = mins;
            updateTotalMinutes();
        });
    });
    
    // Обновление общего времени
    function updateTotalMinutes() {
        let hours = parseInt(document.getElementById('time-hours').value);
        let minutes = parseInt(document.getElementById('time-minutes').value);
        
        if (isNaN(hours)) hours = 0;
        if (isNaN(minutes)) minutes = 0;
        
        const total = hours * 60 + minutes;
        
        const totalElement = document.getElementById('total-minutes');
        if (totalElement) {
            let text = total + ' минут';
            if (total === 1) {
                text = '1 минута';
            } else if (total > 1 && total < 5) {
                text = total + ' минуты';
            }
            totalElement.textContent = text;
        }
    }
    
    const timeHours = document.getElementById('time-hours');
    const timeMinutes = document.getElementById('time-minutes');
    if (timeHours && timeMinutes) {
        timeHours.addEventListener('input', updateTotalMinutes);
        timeMinutes.addEventListener('input', updateTotalMinutes);
    }
    
    // Закрытие модальных окон
    function closeAllModals() {
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.classList.add('hidden');
        });
    }
    
    document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
        btn.addEventListener('click', closeAllModals);
    });
    
    // Обработка завершения задачи
    const completeTaskBtn = document.getElementById('complete-task-btn');
    if (completeTaskBtn) {
        completeTaskBtn.addEventListener('click', async function() {
            const taskId = document.getElementById('complete-modal').getAttribute('data-task-id');
            let hours = parseInt(document.getElementById('time-hours').value);
            let minutes = parseInt(document.getElementById('time-minutes').value);
            
            if (isNaN(hours)) hours = 0;
            if (isNaN(minutes)) minutes = 0;
            
            const totalMinutes = hours * 60 + minutes;
            
            if (totalMinutes === 0) {
                alert('Пожалуйста, укажите время выполнения');
                return;
            }
            
            // Показываем индикатор загрузки
            const originalText = completeTaskBtn.innerHTML;
            completeTaskBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Сохранение...';
            completeTaskBtn.disabled = true;
            
            // Отправляем запрос на сервер
            try {
                const response = await fetch('/check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 
                        taskId: taskId, 
                        minutes: totalMinutes 
                    })
                });
                
                const result = await response.json();
                
                if (response.ok && result.success) {
                    // Показываем окно успеха
                    document.getElementById('complete-modal').classList.add('hidden');
                    document.getElementById('success-modal').classList.remove('hidden');
                    
                    // Через 2 секунды перезагружаем страницу
                    setTimeout(function() {
                        location.reload();
                    }, 2000);
                } else {
                    throw new Error(result.error || 'Ошибка при сохранении');
                }
            } catch (error) {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при сохранении задачи: ' + error.message);
            } finally {
                // Восстанавливаем кнопку
                completeTaskBtn.innerHTML = originalText;
                completeTaskBtn.disabled = false;
            }
        });
    }
    
    // Закрытие окна успеха
    const modalOk = document.querySelector('.modal-ok');
    if (modalOk) {
        modalOk.addEventListener('click', function() {
            location.reload();
        });
    }
    
    // Закрытие по клику на overlay
    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeAllModals();
            }
        });
    });
    
    // Функция для показа деталей задачи (глобальная)
    window.showTaskDetails = async function(taskId) {
        try {
            const response = await fetch('/api/task/' + taskId);
            const result = await response.json();
            
            if (result.success) {
                const task = result.task;
                const modalContent = document.getElementById('task-details-content');
                
                let startTime = '';
                if (task.start_time) {
                    const date = new Date(task.start_time);
                    startTime = date.toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'});
                }
                
                let description = task.description || 'Нет описания';
                
                modalContent.innerHTML = `
                    <div class="task-details">
                        <h4>${task.title}</h4>
                        <p class="task-description">${description}</p>
                        <div class="details-grid">
                            <div class="detail-item">
                                <i class="fas fa-signal"></i>
                                <span>Сложность:</span>
                                <strong>${task.difficulty}/10</strong>
                            </div>
                            <div class="detail-item">
                                <i class="far fa-clock"></i>
                                <span>Планируемое время:</span>
                                <strong>${task.supposed_time} мин</strong>
                            </div>
                            ${startTime ? `
                            <div class="detail-item">
                                <i class="far fa-calendar"></i>
                                <span>Время начала:</span>
                                <strong>${startTime}</strong>
                            </div>
                            ` : ''}
                            ${task.actual_time ? `
                            <div class="detail-item">
                                <i class="fas fa-stopwatch"></i>
                                <span>Фактическое время:</span>
                                <strong>${task.actual_time} мин</strong>
                            </div>
                            ` : ''}
                            <div class="detail-item">
                                <i class="fas fa-check-circle"></i>
                                <span>Статус:</span>
                                <strong>${task.is_done ? 'Выполнено' : 'Активна'}</strong>
                            </div>
                        </div>
                    </div>
                `;
                
                // Показываем модальное окно
                const modal = document.getElementById('task-details-modal');
                modal.classList.remove('hidden');
                
                // Прокручиваем к верху
                modal.scrollTop = 0;
            }
        } catch (error) {
            console.error('Ошибка при получении деталей задачи:', error);
            alert('Не удалось загрузить детали задачи');
        }
    };
});
// Анимация прогресса при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Анимация прогресс-бара эффективности
    const efficiencyFill = document.querySelector('.efficiency-fill');
    if (efficiencyFill) {
        // Уже установлена ширина через style, добавляем анимацию
        efficiencyFill.style.transition = 'width 1.5s ease-out';
    }
    
    // Анимация кругового прогресса
    const progressFill = document.querySelector('.progress-ring-fill');
    if (progressFill) {
        const completionRate = parseFloat('{{ statistics.completion_rate }}') || 0;
        const circumference = 283; // 2 * π * r (r = 45)
        const offset = circumference - (completionRate / 100 * circumference);
        
        // Устанавливаем начальное значение
        progressFill.style.strokeDashoffset = circumference;
        
        // Запускаем анимацию с задержкой
        setTimeout(() => {
            progressFill.style.transition = 'stroke-dashoffset 1.5s ease-out';
            progressFill.style.strokeDashoffset = offset;
        }, 300);
    }
    
    // Анимация счетчиков (опционально)
    function animateCounter(element, target) {
        const duration = 1500;
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = `${Math.round(target)} %`;
                clearInterval(timer);
            } else {
                element.textContent = `${Math.round(current)} %`;
            }
        }, 16);
    }
    
    // Анимируем основные счетчики
    setTimeout(() => {
        document.querySelectorAll('.metric-value, .time-count, .quality-value').forEach(element => {
            const text = element.textContent;
            const value = parseFloat(text.replace(/[^\d.]/g, ''));
            if (!isNaN(value) && value > 0 && value < 1000) {
                animateCounter(element, value);
            }
        });
    }, 500);
});