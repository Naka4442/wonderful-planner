// Календарь и отображение событий
document.addEventListener('DOMContentLoaded', function() {
    // Обработка выбора даты
    const datePicker = document.getElementById('select-day');
    if (datePicker) {
        datePicker.addEventListener('change', function() {
            const selectedDate = this.value;
            window.location.href = '/?date=' + selectedDate;
        });
    }
    
    // Подсветка текущего времени в календаре
    function highlightCurrentTime() {
        const now = new Date();
        const currentHour = now.getHours();
        const currentMinute = now.getMinutes();
        
        // Убираем предыдущую подсветку
        document.querySelectorAll('.current-time-indicator').forEach(el => {
            el.remove();
        });
        
        // Добавляем индикатор текущего времени
        const currentHourElement = document.querySelector(`.time-slot-hour[data-hour="${currentHour}"]`);
        if (currentHourElement) {
            const hourContent = currentHourElement.querySelector('.hour-content');
            if (hourContent) {
                const indicator = document.createElement('div');
                indicator.className = 'current-time-indicator';
                indicator.style.position = 'absolute';
                indicator.style.left = '0';
                indicator.style.right = '0';
                indicator.style.top = currentMinute + 'px';
                indicator.style.height = '2px';
                indicator.style.backgroundColor = '#e74c3c';
                indicator.style.zIndex = '10';
                hourContent.appendChild(indicator);
            }
        }
    }
    
    // Если сегодняшняя дата, показываем текущее время
    if (document.getElementById('select-day').value === new Date().toISOString().split('T')[0]) {
        highlightCurrentTime();
        // Обновляем каждую минуту
        setInterval(highlightCurrentTime, 60000);
    }
    
    // Прокрутка к текущему времени
    function scrollToCurrentTime() {
        const now = new Date();
        const currentHour = now.getHours();
        const currentHourElement = document.querySelector(`.time-slot-hour[data-hour="${currentHour}"]`);
        if (currentHourElement) {
            currentHourElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    // Прокручиваем к текущему времени при загрузке
    if (document.getElementById('select-day').value === new Date().toISOString().split('T')[0]) {
        setTimeout(scrollToCurrentTime, 500);
    }
    
    // Обработка кликов на элементах календаря
    document.querySelectorAll('.calendar-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.stopPropagation();
            const taskId = this.getAttribute('data-task-id');
            const eventId = this.getAttribute('data-event-id');
            
            if (taskId) {
                showTaskDetails(taskId);
            } else if (eventId) {
                // Можно добавить показ деталей события
                console.log('Событие:', eventId);
            }
        });
    });
});