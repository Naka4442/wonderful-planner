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
            
            // Handle successful responses (2xx status codes)
            if (response.ok) {
                if (response.status === 204) { // No content, often indicates successful deletion
                    return {}; // Return an empty object for successful no-content responses
                }
                // For other 2xx responses, parse JSON
                return await response.json();
            }
            
            // Handle error responses (non-2xx status codes)
            const errorData = await response.json(); // Attempt to parse error data
            console.error(`API Error Response: Status=${response.status}, Data=`, errorData); // Log status and data
            
            // Use detailed Pydantic error if available, or a generic message
            const errorMessage = Array.isArray(errorData.error)
                ? errorData.error.map(e => `${e.loc.join('.')}: ${e.msg}`).join('\n')
                : (errorData.error || `API request failed with status ${response.status}`);
            
            throw new Error(errorMessage);
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

// Utility function to get color based on difficulty
window.wonderPlanner.getDifficultyColor = (difficulty) => {
    // Difficulty is 1-10
    // Hue goes from Green (120) to Red (0)
    // Scale 1-10 to 0-119 for hue
    const hue = 120 - (difficulty - 1) * (120 / 9); // Interpolate hue from 120 to 0
    return `hsl(${hue}, 80%, 45%)`; // Adjust saturation and lightness as needed
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