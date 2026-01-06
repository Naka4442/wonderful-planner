from sqlalchemy.orm import Session
from models import User


class UserServices:
    def __init__(self, db: Session ):
        self.db = db

    def signup(self, name: str, email: str, password: str, password2: str):
        same_email = self.db.query(User).filter(User.email == email).first()
        if same_email:
            raise ValueError("Пользователь с таким email уже существует")
        if password != password2:
            raise ValueError("Пароли не совпадают")

        user = User(name=name, email=email, password=password)
        self.db.add(user)
        self.db.commit()

    def signin(self, email: str, password: str):
        user = self.db.query(User).filter(User.email == email, User.password == password).first()
        if not user:
            raise ValueError("Пользователь не найден")
