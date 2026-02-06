from abc import ABC

from flask import session


class AbstractController(ABC):
    def _get_user_id(self) -> int:
        return session.get("user_id")
    
    def _get_user_name(self) -> str:
        return session.get("user_name")
