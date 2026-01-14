// Взяли все чекбоксы
const checkboxes = Array.from(document.querySelectorAll(".check"));
const modal = document.querySelector(".modal");


checkboxes.forEach(checkbox => {
    checkbox.addEventListener("input", () => {
        const taskId = Number(checkbox.parentElement.querySelector(".task-id").value);
        console.log(`Вы нажали на чекбокс ${taskId}`);
        modal.classList.remove("hidden");
    })
})

modal.addEventListener("click", () => {
    modal.classList.add("hidden");
})