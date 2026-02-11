from flask import Flask
from controllers.user_controller import UserController
from routers.abstract_router import AbstractRouter


class UserRouter(AbstractRouter):
    def __init__(self, app: Flask, url_name: str, user_controller: UserController):
        self.user_controller = user_controller
        super().__init__(app, url_name)

    def setup_routes(self):
        self.router.add_url_rule(
            "/signup/", 
            view_func=self.user_controller.signup, 
            methods=["GET", "POST"],
            endpoint="signup"
        )
        self.router.add_url_rule(
            "/signin/",
            view_func=self.user_controller.signin,
            methods=["GET", "POST"],
            endpoint="signin"
        )