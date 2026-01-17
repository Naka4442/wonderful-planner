const isRepeatedCheckbox = document.querySelector("#is_repeated");
const repeatedBlock = document.querySelector(".repeated-block");
const notRepeatedBlock = document.querySelector(".not-repeated-block");


isRepeatedCheckbox.addEventListener("input", (e) => {
    if(e.target.checked){
        repeatedBlock.classList.remove("hidden");
        notRepeatedBlock.classList.add("hidden");
    } else {
        notRepeatedBlock.classList.remove("hidden");
        repeatedBlock.classList.add("hidden");
    }
})