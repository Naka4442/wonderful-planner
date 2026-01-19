const selectWeekInput = document.querySelector("#select-week");

selectWeekInput.addEventListener("change", (e) => {
    const week = e.target.value;
    const [yearNum, weekNum] = week.split("-W");
    
    const year = Number(yearNum);
    const weekNumber = Number(weekNum);

    const janFourth = new Date(year, 0, 4);

    const janFourthWeekday = janFourth.getDay() || 7;

    let firstMonday;
    if(janFourthWeekday === 1){
        firstMonday = new Date(year, 0, 1);
    }
    else{
        firstMonday = new Date(year, 0, 4 - (janFourthWeekday - 1));
    }

    const targetMonday = new Date(firstMonday);
    targetMonday.setDate(firstMonday.getDate() + (weekNumber - 1) * 7);

    const date = targetMonday.toISOString().split("T")[0];
    window.location.href = `/weekly?date=${date}`;

});