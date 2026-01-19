const selectDayInput = document.querySelector("#select-day");

selectDayInput.addEventListener("change", (e) => {
    const date = e.target.value;
    window.location.href = `/?date=${date}`;
});

const dateFromParams = new URLSearchParams(window.location.search).get("date");
if (dateFromParams) {
    selectDayInput.value = dateFromParams;
}