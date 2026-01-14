// Взяли все чекбоксы
const checkboxes = Array.from(document.querySelectorAll(".check"));
const modal = document.querySelector(".modal");
const taskTitleElement = document.querySelector(".check-task-modal-title");

const taskHoursElement = document.querySelector("#time-hours");
const taskMinutesElement = document.querySelector("#time-minutes");
const taskCheckButton = document.querySelector(".check-task-modal-button");

let activeTaskId;

checkboxes.forEach(checkbox => {
    checkbox.addEventListener("input", (e) => {
        e.target.checked = false;
        activeTaskId = Number(checkbox.parentElement.querySelector(".task-id").value);
        const taskTitle = checkbox.parentElement.querySelector("h4").textContent;
        modal.classList.remove("hidden");
        taskTitleElement.textContent = taskTitle;
    })
})

modal.addEventListener("click", (e) => {
    if(e.target === modal){
        modal.classList.add("hidden");
    }
})

taskCheckButton.addEventListener("click", (e) => {
    const taskTime = Number(taskHoursElement.value) * 60 + Number(taskMinutesElement.value);
    console.log(activeTaskId, taskTime);
    modal.classList.add("hidden");
})