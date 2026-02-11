// This file will contain core, shared logic such as the API handler
// and global event listeners.

// Potentially define a global namespace
window.wonderPlanner = {};

// API Handler
window.wonderPlanner.api = {
    async send(url, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorData = await response.json();
                // Use detailed Pydantic error if available
                const errorMessage = Array.isArray(errorData.error)
                    ? errorData.error.map(e => `${e.loc.join('.')}: ${e.msg}`).join('\n')
                    : (errorData.error || 'API request failed');
                throw new Error(errorMessage);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error (${method} ${url}):`, error);
            throw error;
        }
    },
    // Task endpoints
    getTask: (taskId) => window.wonderPlanner.api.send(`/api/task/${taskId}`),
    createTask: (data) => window.wonderPlanner.api.send('/tasks/create/task/', 'POST', data),
    updateTask: (taskId, data) => window.wonderPlanner.api.send(`/api/task/${taskId}`, 'PUT', data),
    deleteTask: (taskId) => window.wonderPlanner.api.send(`/api/task/${taskId}`, 'DELETE'),
    checkTask: (taskId, minutes) => window.wonderPlanner.api.send('/api/task/check', 'POST', { taskId, minutes }),
    // Event endpoints
    getEvent: (eventId) => window.wonderPlanner.api.send(`/api/event/${eventId}`),
    createEvent: (data) => window.wonderPlanner.api.send('/tasks/create/event/', 'POST', data),
    updateEvent: (eventId, data) => window.wonderPlanner.api.send(`/api/event/${eventId}`, 'PUT', data),
    deleteEvent: (eventId) => window.wonderPlanner.api.send(`/api/event/${eventId}`, 'DELETE'),
};

// Global modal management (initial definition)
// modals.js will then extend this object
window.wonderPlanner.modals = {
    closeAll() {
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.classList.add('hidden');
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    console.log("Core app.js loaded");

    // Global Escape key listener to close modals
    document.addEventListener('keydown', (e) => {
        if (e.key === "Escape") {
            window.wonderPlanner.modals.closeAll();
        }
    });
});