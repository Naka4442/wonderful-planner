// This file will handle logic specific to the day view,
// such as the task list tab switcher and date navigation.

document.addEventListener('DOMContentLoaded', () => {
    console.log("day_view.js loaded");

    // --- Date Picker and Navigation ---
    const datePicker = document.getElementById('select-day');
    const dayNavigation = document.querySelector('.day-navigation'); // Get the parent container
    
    if (datePicker) {
        // Handle direct date picker change
        datePicker.addEventListener('change', function() {
            const selectedDate = this.value;
            window.location.href = `/?date=${selectedDate}`;
        });
    }

    if (dayNavigation) {
        dayNavigation.addEventListener('click', (e) => {
            const navBtn = e.target.closest('[data-action="previous-day"], [data-action="next-day"]');
            if (!navBtn) return;

            e.preventDefault(); // Prevent default link behavior

            const currentDate = new Date(datePicker.value);
            let newDate = new Date(currentDate);

            if (navBtn.dataset.action === 'previous-day') {
                newDate.setDate(currentDate.getDate() - 1);
            } else if (navBtn.dataset.action === 'next-day') {
                newDate.setDate(currentDate.getDate() + 1);
            }

            // Format new date to YYYY-MM-DD
            const formattedDate = newDate.toISOString().slice(0, 10);
            window.location.href = `/?date=${formattedDate}`;
        });
    }

    // --- Task List Tab Switcher ---
    const tabsContainer = document.querySelector('.tasks-tabs');
    const tasksLists = document.querySelector('.tasks-container');

    if (tabsContainer && tasksLists) {
        tabsContainer.addEventListener('click', (e) => {
            const tabButton = e.target.closest('.tab-btn');
            if (!tabButton) return;

            const tab = tabButton.dataset.tab;

            // Update buttons
            tabsContainer.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            tabButton.classList.add('active');

            // Update lists
            tasksLists.querySelectorAll('.tasks-list').forEach(list => list.classList.remove('active'));
            tasksLists.querySelector(`#${tab}-tasks`).classList.add('active');
        });
    }
});
