const isRepeatedCheckbox = document.querySelector("#is_repeated");
const repeatedBlock = document.querySelector(".repeated-block");
const notRepeatedBlock = document.querySelector(".not-repeated-block");
const EventRadio = document.querySelectorAll('input[name="event"]');
const eventBlock = document.querySelector(".event-block");
const taskBlock = document.querySelector(".task-block");


isRepeatedCheckbox.addEventListener("input", (e) => {
    if(e.target.checked){
        repeatedBlock.classList.remove("hidden");
        notRepeatedBlock.classList.add("hidden");
    } else {
        notRepeatedBlock.classList.remove("hidden");
        repeatedBlock.classList.add("hidden");
    }
})

EventRadio.forEach(radio => {
    radio.addEventListener("input", (e) => {
        const value = Number(e.target.value);
        if(value === 1){
        eventBlock.classList.remove("hidden");
        taskBlock.classList.add("hidden");
        }
        else {
        taskBlock.classList.remove("hidden");
        eventBlock.classList.add("hidden");
        }

    })
})