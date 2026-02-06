from abc import ABC

from flask import g
from sqlalchemy.orm import Session


class AbstractRepository(ABC):
    def __init__(self, db: Session = None):
        self.local_db = db

    @property
    def db(self) -> Session:
        if self.local_db:
            return self.local_db
        return g.db