// Взяли все чекбоксы
const checkboxes = Array.from(document.querySelectorAll(".check"));

checkboxes.forEach(checkbox => {
    checkbox.addEventListener("input", () => {
        const taskId = Number(checkbox.parentElement.querySelector(".task-id").value);
        console.log(`Вы нажали на чекбокс ${taskId}`);
    })
})