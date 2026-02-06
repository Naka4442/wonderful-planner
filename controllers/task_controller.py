from datetime import date
from flask import redirect, render_template, request
from typing import Tuple
from controllers.abstract_controller import AbstractController
from models.event import EventCreateDto
from models.task import TaskCreateDto
from services.task_services import TaskServices


class TaskController(AbstractController):
    def __init__(self, task_services: TaskServices):
        self.task_services = task_services

    def _check_auth(self) -> Tuple[int, str]:
        user_id = self._get_user_id()
        if user_id is None:
            return redirect("signin")
        user_name = self._get_user_name()
        return user_id, user_name

    def create_task(self):
        user_id, user_name = self._check_auth()
        if request.method == "POST":
            try:
                task_data = TaskCreateDto(**request.form, user_id=user_id)
                self.task_services.create_task(task_data)
            except Exception as e:
                return render_template("create.html", error=str(e), user_name=user_name)
        return render_template("create.html", user_name=user_name)
    
    def create_event(self):
        user_id, user_name = self._check_auth()
        if request.method == "POST":
            try:
                event_data = EventCreateDto(**request.form, user_id=user_id)
                self.task_services.create_task(event_data)
            except Exception as e:
                return render_template("create.html", error=str(e), user_name=user_name)
        return render_template("create.html", user_name=user_name)

    def day_index(self):
        user_id, user_name = self._check_auth()
        if request.args.get("date") is not None:
            d = request.args.get("date").split("-")
            day = date(
                int(d[0]),
                int(d[1]),
                int(d[2])
            )
        else:
            day = date.today()
        schedule = self.task_services.get_shedule_by_day(user_id, day)
        return render_template(
            "index.html", 
            user_name=user_name,
            schedule=schedule
        )