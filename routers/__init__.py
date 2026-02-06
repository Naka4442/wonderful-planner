"""
# Роутеры

### Слой, прописывающий маршруты контроллерам

Говоря проще, он создает адреса нашего сайта
"""
from .abstract_router import AbstractRouter
from .user_router import UserRouter
from .task_router import TaskRouter


__all__ = [
    "AbstractRouter",
    "UserRouter",
    "TaskRouter"
]