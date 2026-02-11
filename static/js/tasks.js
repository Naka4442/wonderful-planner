document.addEventListener('DOMContentLoaded', () => {

    const api = window.wonderPlanner.api; // Moved inside DOMContentLoaded

    // --- Main Event Delegation for Task/Event Actions ---
    document.body.addEventListener('click', async (e) => {
        console.log('Click event detected on body');
        const actionTarget = e.target.closest('[data-action]');
        if (!actionTarget) {
            console.log('No actionTarget found, returning.');
            return;
        }

        const action = actionTarget.dataset.action;
        const id = actionTarget.closest('[data-task-id], [data-event-id]')?.dataset.taskId || actionTarget.closest('[data-task-id], [data-event-id]')?.dataset.eventId;
                console.log('Action:', action, 'ID:', id);
                
                const isCrudAction = ['delete-task', 'delete-event', 'edit-task', 'edit-event', 'create-task', 'create-event', 'show-details', 'show-event-details', 'close-modal', 'complete-task-button', 'show-complete-modal-button'].includes(action);
                
                if (!isCrudAction) {
                    console.log('Action is not a CRUD action, returning:', action);
                    return;
                }
        
                console.log('Entering switch with action:', action, ' (Type:', typeof action, ')');
                switch (action) {
                    case 'delete-task':
                        console.log('Case: delete-task');
                        handleDelete(id, 'task');
                        break;
                    case 'delete-event':
                        console.log('Case: delete-event');
                        handleDelete(id, 'event');
                        break;
                    case 'edit-task':
                        console.log('Case: edit-task');
                        handleEdit(id, 'task');
                        break;
                    case 'edit-event':
                        console.log('Case: edit-event');
                        handleEdit(id, 'event');
                        break;
                    case 'create-task':
                        console.log('Case: create-task');
                        handleEdit(null, 'task');
                        break;
                    case 'create-event':
                        console.log('Case: create-event');
                        handleEdit(null, 'event');
                        break;
                    case 'show-details':
                        console.log('Case: show-details');
                        window.wonderPlanner.modals.showTaskDetails(id);
                        break;
                    case 'show-event-details':
                        console.log('Case: show-event-details');
                        window.wonderPlanner.modals.showEventDetails(id);
                        break;
                    case 'complete-task-button':
                        console.log('Case: complete-task-button');
                        try {
                            const { task } = await api.getTask(id);
                            window.wonderPlanner.modals.showCompleteModal(task, null); // Pass null as checkbox since it's a button
                        } catch (error) {
                            alert(`Ошибка: ${error.message}`);
                        }
                        break;
                    case 'close-modal':
                        console.log('Case: close-modal');
                        const modalToClose = actionTarget.closest('.modal-overlay');
                        if (modalToClose) {
                            modalToClose.classList.add('hidden');
                        }
                        break;
                    case 'show-complete-modal-button':
                        console.log('Case: show-complete-modal-button triggered.');
                        const completeButton = actionTarget.closest('button[data-action="show-complete-modal-button"]');
                        const completeTaskId = completeButton.dataset.taskId;
                        console.log('Extracted Task ID for completion:', completeTaskId);
                        
                        try {
                            console.log('Calling api.getTask for ID:', completeTaskId);
                            const { task } = await api.getTask(completeTaskId);
                            console.log('Task data fetched for completion:', task);
                            console.log('Calling window.wonderPlanner.modals.showCompleteModal with task:', task);
                            window.wonderPlanner.modals.showCompleteModal(task, null); // No checkbox to pass
                            console.log('window.wonderPlanner.modals.showCompleteModal called.');
                        } catch (error) {
                            console.error('Error in show-complete-modal-button handler:', error);
                            alert(`Ошибка загрузки задачи для завершения: ${error.message}`);
                        }
                        break;
                    default:
                        console.log('Default case hit for action:', action);
                        break;
                }




    // --- CRUD Handlers ---

    async function handleDelete(id, type) {
        if (!confirm(`Вы уверены, что хотите удалить ${type === 'task' ? 'задачу' : 'событие'}?`)) {
            return;
        }

        try {
            if (type === 'task') {
                await api.deleteTask(id);
            } else {
                await api.deleteEvent(id);
            }
            
            window.location.reload(); // Simple solution for now
        } catch (error) {
            alert(`Не удалось удалить: ${error.message}`);
        }
    }

    async function handleEdit(id, type) {
        console.log(`[handleEdit] called for id: ${id}, type: ${type}`);
        window.wonderPlanner.modals.hideAllModals(); // Hide all other modals first
        const modal = document.getElementById('edit-modal');
        const modalTitle = document.getElementById('edit-modal-title');
        const modalBody = document.getElementById('edit-modal-body');
        const saveButton = document.getElementById('save-edit-btn');

        if (!modal) {
            console.error("[handleEdit] edit-modal not found");
            alert("Ошибка: Не найдено модальное окно редактирования.");
            return;
        }
        if (!modalTitle) {
            console.error("[handleEdit] edit-modal-title not found");
            alert("Ошибка: Не найден заголовок модального окна редактирования.");
            return;
        }
        if (!modalBody) {
            console.error("[handleEdit] edit-modal-body not found");
            alert("Ошибка: Не найдено тело модального окна редактирования.");
            return;
        }
        if (!saveButton) {
            console.error("[handleEdit] save-edit-btn not found");
            alert("Ошибка: Не найдена кнопка сохранения в модальном окне редактирования.");
            return;
        }

        let data = {};
        const isEdit = id !== null;

        try {
            if (isEdit) {
                console.log(`[handleEdit] Fetching data for ${type} with id: ${id}`);
                const response = type === 'task' ? await api.getTask(id) : await api.getEvent(id);
                data = type === 'task' ? response.task : response.event;
                console.log('[handleEdit] Fetched data:', data);
                if (!data) {
                    throw new Error(`Данные для ${type} с ID ${id} не найдены.`);
                }
            }

            modalTitle.textContent = `${isEdit ? 'Редактировать' : 'Создать'} ${type === 'task' ? 'задачу' : 'событие'}`;
            modalBody.innerHTML = generateForm(type, data);
            modal.classList.remove('hidden');
            // Force a reflow
            void modal.offsetWidth;

            saveButton.onclick = async () => {
                const form = modalBody.querySelector('form');
                if (!form) {
                    console.error("[handleEdit] Form not found inside modalBody during save.");
                    alert("Ошибка: Не удалось найти форму для сохранения.");
                    return;
                }
                const formData = new FormData(form);
                const submitData = Object.fromEntries(formData.entries());
                console.log('[handleEdit] Submit data before conversion:', submitData);

                // Convert types from form
                if (submitData.difficulty) submitData.difficulty = parseInt(submitData.difficulty);
                if (submitData.supposed_time) submitData.supposed_time = parseInt(submitData.supposed_time);
                
                // Handle checkbox for is_repeated in event form
                if (type === 'event' && form.querySelector('#is_repeated')) {
                     submitData.is_repeated = form.querySelector('#is_repeated').checked;
                } else {
                    submitData.is_repeated = false; // Default for task or if checkbox not present
                }

                console.log('[handleEdit] Submit data after conversion:', submitData);

                try {
                    if (type === 'task') {
                        isEdit ? await api.updateTask(id, submitData) : await api.createTask(submitData);
                    } else {
                        isEdit ? await api.updateEvent(id, submitData) : await api.createEvent(submitData);
                    }
                    console.log('[handleEdit] API call successful, reloading page.');
                    window.location.reload();
                } catch (error) {
                    console.error(`[handleEdit] Ошибка сохранения ${type}:`, error);
                    alert(`Ошибка сохранения ${type}: ${error.message}`);
                }
            };
        } catch (error) {
            console.error(`[handleEdit] Ошибка загрузки или подготовки данных для ${type}:`, error);
            alert(`Ошибка загрузки или подготовки данных для ${type}: ${error.message}`);
        }
    }

    // --- HTML Generation ---

    function generateForm(type, data) {
        const toLocalISOString = (date) => {
            if (!date) return '';
            const d = new Date(date);
            return d.toISOString().slice(0, 16);
        }

        if (type === 'task') {
            return `
                <form id="edit-form" class="edit-form">
                    <div class="form-group">
                        <label for="title">Название</label>
                        <input type="text" id="title" name="title" value="${data.title || ''}" required>
                    </div>
                    <div class="form-group">
                        <label for="description">Описание</label>
                        <textarea id="description" name="description">${data.description || ''}</textarea>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="difficulty">Сложность (1-10)</label>
                            <input type="number" id="difficulty" name="difficulty" value="${data.difficulty || 5}" min="1" max="10">
                        </div>
                        <div class="form-group">
                            <label for="supposed_time">Время (мин)</label>
                            <input type="number" id="supposed_time" name="supposed_time" value="${data.supposed_time || 30}" min="1">
                        </div>
                    </div>
                     <div class="form-group">
                        <label for="start_time">Время начала</label>
                        <input type="datetime-local" id="start_time" name="start_time" value="${toLocalISOString(data.start_time)}">
                    </div>
                </form>
            `;
        } else { // event
            return `
                <form id="edit-form" class="edit-form">
                    <div class="form-group">
                        <label for="title">Название</label>
                        <input type="text" id="title" name="title" value="${data.title || ''}" required>
                    </div>
                    <div class="form-group">
                        <label for="description">Описание</label>
                        <textarea id="description" name="description">${data.description || ''}</textarea>
                    </div>
                     <div class="form-group">
                        <label for="start_time">Время начала</label>
                        <input type="datetime-local" id="start_time" name="start_time" value="${toLocalISOString(data.start_time)}" required>
                    </div>
                     <div class="form-group">
                        <label for="end_time">Время окончания</label>
                        <input type="datetime-local" id="end_time" name="end_time" value="${toLocalISOString(data.end_time)}">
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="difficulty">Важность (1-10)</label>
                            <input type="number" id="difficulty" name="difficulty" value="${data.difficulty || 1}" min="1" max="10">
                        </div>
                        <div class="form-group form-group-checkbox">
                             <label for="is_repeated">Повторять</label>
                            <input type="checkbox" id="is_repeated" name="is_repeated" ${data.is_repeated ? 'checked' : ''}>
                        </div>
                    </div>
                </form>
            `;
        }
    }
})
});