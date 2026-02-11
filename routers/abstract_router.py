from abc import ABC, abstractmethod

from flask import Blueprint, Flask


class AbstractRouter(ABC):
    def __init__(self, app: Flask, url_name: str):
        self.app = app
        self.router = Blueprint(url_name, __name__)
        self.setup_routes()
        self.app.register_blueprint(self.router, url_prefix=f"/{url_name}")

    @abstractmethod
    def setup_routes(self):
        pass