// Управление задачами
document.addEventListener('DOMContentLoaded', function() {
    // Переключение вкладок задач
    const tabBtns = document.querySelectorAll('.tab-btn');
    const taskLists = document.querySelectorAll('.tasks-list');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Обновляем активные кнопки
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Показываем нужную вкладку
            taskLists.forEach(list => list.classList.remove('active'));
            document.getElementById(tabId + '-tasks').classList.add('active');
        });
    });
    
    // Обработка завершения задачи
    document.querySelectorAll('.task-complete-toggle').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                const taskCard = this.closest('.task-card');
                const taskId = taskCard.getAttribute('data-task-id');
                const taskTitle = taskCard.querySelector('h4').textContent;
                const taskDescriptionElement = taskCard.querySelector('.task-description');
                let taskDescription = '';
                if (taskDescriptionElement) {
                    taskDescription = taskDescriptionElement.textContent;
                }
                
                const taskBadge = taskCard.querySelector('.task-badge');
                let taskDifficulty = '1';
                if (taskBadge) {
                    const match = taskBadge.textContent.match(/\d+/);
                    if (match) {
                        taskDifficulty = match[0];
                    }
                }
                
                const taskTimeElement = taskCard.querySelector('.task-time-info span');
                let taskPlanned = '30';
                if (taskTimeElement) {
                    const match = taskTimeElement.textContent.match(/\d+/);
                    if (match) {
                        taskPlanned = match[0];
                    }
                }
                
                // Заполняем модальное окно
                document.getElementById('modal-task-title').textContent = taskTitle;
                document.getElementById('modal-task-description').textContent = taskDescription;
                document.getElementById('modal-task-difficulty').textContent = taskDifficulty;
                document.getElementById('modal-task-planned').textContent = taskPlanned;
                
                // Сохраняем ID задачи
                document.getElementById('complete-modal').setAttribute('data-task-id', taskId);
                
                // Показываем модальное окно
                document.getElementById('complete-modal').classList.remove('hidden');
                
                // Сбрасываем checkbox
                this.checked = false;
            }
        });
    });
});