// This file contains logic for populating and interacting with modals.
document.addEventListener('DOMContentLoaded', () => {
    console.log("modals.js loaded");

    // Ensure wonderPlanner and wonderPlanner.modals objects exist
    window.wonderPlanner = window.wonderPlanner || {};
    window.wonderPlanner.modals = window.wonderPlanner.modals || {}; // Initialize if not existing
    
    const completeModal = document.getElementById('complete-modal');
    const timeHoursInput = completeModal.querySelector('#time-hours');
    const timeMinutesInput = completeModal.querySelector('#time-minutes');
    const totalMinutesSpan = completeModal.querySelector('#total-minutes');
    const completeTaskBtn = completeModal.querySelector('#complete-task-btn');
    const timeSuggestionButtons = completeModal.querySelectorAll('.time-suggestion');
    const successModal = document.getElementById('success-modal');

    // Helper to update total minutes display
    const updateTotals = () => {
        const hours = parseInt(timeHoursInput.value) || 0;
        const minutes = parseInt(timeMinutesInput.value) || 0;
        totalMinutesSpan.textContent = `${(hours * 60) + minutes} минут`;
    };

    // Setup event listeners for the complete modal once
    const setupCompleteModalListeners = () => {
        // Event listeners for time inputs
        timeHoursInput.oninput = updateTotals;
        timeMinutesInput.oninput = updateTotals;

        // Event listeners for time suggestion buttons
        timeSuggestionButtons.forEach(btn => {
            btn.onclick = (e) => {
                e.preventDefault();
                const minutesToAdd = parseInt(btn.dataset.minutes);
                timeHoursInput.value = Math.floor(minutesToAdd / 60);
                timeMinutesInput.value = minutesToAdd % 60;
                updateTotals();
            };
        });

        // Handle task completion
        completeTaskBtn.onclick = async () => {
            const taskIdToComplete = completeModal.getAttribute('data-task-id');
            const hours = parseInt(timeHoursInput.value) || 0;
            const minutes = parseInt(timeMinutesInput.value) || 0;
            const actualMinutes = (hours * 60) + minutes;

            try {
                await window.wonderPlanner.api.checkTask(taskIdToComplete, actualMinutes);
                window.wonderPlanner.modals.hideAllModals(); // Hide current modal
                successModal.classList.remove('hidden'); // Show success modal
                // Reload page after a short delay or user acknowledges success
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } catch (error) {
                alert(`Не удалось завершить задачу: ${error.message}`);
            }
        };

        // Handle closing the success modal
        successModal.querySelector('.modal-ok').onclick = () => {
            window.location.reload();
        };

        // Handle closing the complete modal (including reverting checkbox)
        completeModal.addEventListener('click', (e) => {
            if (e.target.closest('[data-action="close-modal"]')) {
                completeModal.classList.add('hidden'); // Hide modal
                if(completeModal.currentCheckbox) {
                    completeModal.currentCheckbox.checked = false; // Revert checkbox state
                    completeModal.currentCheckbox = null; // Clear reference
                }
            }
        });
    };



    // Call setup function once on DOMContentLoaded
    setupCompleteModalListeners();
        
    // Merge new modal functions into existing wonderPlanner.modals
    Object.assign(window.wonderPlanner.modals, {
        // Helper to hide all modals
        hideAllModals: () => {
            document.querySelectorAll('.modal-overlay').forEach(modal => {
                modal.classList.add('hidden');
            });
        },
        showTaskDetails: async (taskId) => {
            window.wonderPlanner.modals.hideAllModals(); // Hide all other modals first
            console.log('showTaskDetails called for taskId:', taskId);
            try {
                const { task } = await window.wonderPlanner.api.getTask(taskId);
                const modal = document.getElementById('task-details-modal');
                const footer = document.getElementById('task-details-footer');
                
                if (!modal || !footer) {
                    console.error('Task details modal or footer element not found.');
                    alert('Не удалось загрузить детали задачи: Не найдены элементы модального окна.');
                    return;
                }
                
                document.getElementById('task-details-content').innerHTML = `
                    <div class="task-details">
                        <h4>${task.title}</h4>
                        <p class="task-description">${task.description || 'Нет описания'}</p>
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
                            ${task.start_time ? `
                            <div class="detail-item">
                                <i class="far fa-calendar"></i>
                                <span>Время начала:</span>
                                <strong>${new Date(task.start_time).toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'})}</strong>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                `;
                
                footer.innerHTML = `
                    <button class="btn-secondary modal-cancel" data-action="close-modal">Закрыть</button>
                    <button class="btn-danger" data-action="delete-task" data-task-id="${task.id}"><i class="fas fa-trash"></i> Удалить</button>
                    ${!task.is_done ? `<button class="btn-primary" data-action="complete-task-button" data-task-id="${task.id}"><i class="fas fa-check"></i> Завершить</button>` : ''}
                    <button class="btn-info" data-action="edit-task" data-task-id="${task.id}"><i class="fas fa-edit"></i> Редактировать</button>
                `;
                
                modal.classList.remove('hidden');
                // Force a reflow
                void modal.offsetWidth;
            } catch (error) {
                console.error('Error in showTaskDetails:', error);
                alert(`Не удалось загрузить детали задачи: ${error.message}`);
            }
        },
    
        showEventDetails: async (eventId) => {
            window.wonderPlanner.modals.hideAllModals(); // Hide all other modals first
            console.log('showEventDetails called for eventId:', eventId);
            try {
                const { event } = await window.wonderPlanner.api.getEvent(eventId);
                const modal = document.getElementById('event-details-modal');
                const footer = document.getElementById('event-details-footer'); // Get footer here
    
                if (!modal || !footer) {
                    console.error('Event details modal or footer element not found.');
                    alert('Не удалось загрузить детали события: Не найдены элементы модального окна.');
                    return;
                }
    
                document.getElementById('event-details-content').innerHTML = `
                    <div class="event-details">
                        <h4>${event.title}</h4>
                        <p class="event-description">${event.description || 'Нет описания'}</p>
                        <div class="details-grid">
                            <div class="detail-item">
                                <i class="fas fa-star"></i>
                                <span>Важность:</span>
                                <strong>${event.difficulty}/10</strong>
                            </div>
                            ${event.start_time ? `
                            <div class="detail-item">
                                <i class="far fa-calendar"></i>
                                <span>Начало:</span>
                                <strong>${new Date(event.start_time).toLocaleDateString('ru-RU', {day: '2-digit', month: '2-digit', year: 'numeric'})} ${new Date(event.start_time).toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'})}</strong>
                            </div>
                            ` : ''}
                            ${event.end_time ? `
                            <div class="detail-item">
                                <i class="far fa-calendar"></i>
                                <span>Окончание:</span>
                                <strong>${new Date(event.end_time).toLocaleDateString('ru-RU', {day: '2-digit', month: '2-digit', year: 'numeric'})} ${new Date(event.end_time).toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'})}</strong>
                            </div>
                            ` : ''}
                            ${event.is_repeated ? `
                            <div class="detail-item">
                                <i class="fas fa-redo"></i>
                                <span>Повторяется</span>
                            </div>
                            ` : ''}
                        </div>
                    </div>
                `;
    
                footer.innerHTML = `
                    <button class="btn-secondary modal-cancel" data-action="close-modal">Закрыть</button>
                    <button class="btn-danger btn-small" data-action="delete-event" data-event-id="${event.id}"><i class="fas fa-trash"></i></button>
                    <button class="btn-primary" data-action="edit-event" data-event-id="${event.id}"><i class="fas fa-edit"></i> Редактировать</button>
                `;
    
                modal.classList.remove('hidden');
                // Force a reflow
                void modal.offsetWidth;
            } catch (error) {
                console.error('Error in showEventDetails:', error);
                alert(`Не удалось загрузить детали события: ${error.message}`);
            }
        },
        
        showCompleteModal: (task, checkbox) => {
            window.wonderPlanner.modals.hideAllModals(); // Hide all other modals first
            
            // Store checkbox reference
            completeModal.currentCheckbox = checkbox;

            // Initialize inputs with planned time if available
            const plannedMinutes = task.supposed_time || 0;
            timeHoursInput.value = Math.floor(plannedMinutes / 60);
            timeMinutesInput.value = plannedMinutes % 60;
            updateTotals();

            document.getElementById('modal-task-title').textContent = task.title;
            document.getElementById('modal-task-description').textContent = task.description || '';
            document.getElementById('modal-task-difficulty').textContent = task.difficulty;
            document.getElementById('modal-task-planned').textContent = task.supposed_time;
            
            completeModal.setAttribute('data-task-id', task.id);
            
            completeModal.classList.remove('hidden');
            void completeModal.offsetWidth; // Force reflow
            
            // This listener is now attached once in setupCompleteModalListeners
            // We only need to handle the checkbox state on modal close if needed
        }
    });
});