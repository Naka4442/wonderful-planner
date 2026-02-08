from flask import Flask
from controllers.task_controller import TaskController
from routers.abstract_router import AbstractRouter


class TaskRouter(AbstractRouter):
    def __init__(self, app: Flask, url_name: str, task_controller: TaskController):
        self.task_controller = task_controller
        super().__init__(app, url_name)

    def setup_routes(self):
        self.app.add_url_rule(
            "/",
            view_func=self.task_controller.day_index,
            methods=["GET"],
            endpoint="day_index"
        )
        self.app.add_url_rule(
            "/week/",
            view_func=self.task_controller.week_index,
            methods=["GET"],
            endpoint="week_index"
        )
        self.router.add_url_rule(
            "/create/task/",
            view_func=self.task_controller.create_task,
            methods=["GET", "POST"],
            endpoint="create_task"
        )
        self.router.add_url_rule(
            "/create/event/",
            view_func=self.task_controller.create_event,
            methods=["GET", "POST"],
            endpoint="create_event"
        )
        # API
        self.app.add_url_rule(
            "/api/task/<int:task_id>",
            view_func=self.task_controller.get_task_details,
            methods=["GET"],
            endpoint="get_task_details"
        )
        self.app.add_url_rule(
            "/api/task/check",
            view_func=self.task_controller.check_task,
            methods=["POST"],
            endpoint="check_task"
        )