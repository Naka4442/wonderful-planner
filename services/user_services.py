from flask import session

from models.user import UserCreateDto, UserSchema, UserSigninDto, UserSignupDto
from repositories.user_repository import UserRepository


class UserServices:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    def signup(self, user_data: UserSignupDto) -> None:
        if self.user_repo.check_user_by_email(user_data.email):
            raise ValueError("Пользователь с таким email уже существует")
        
        if user_data.password != user_data.password2:
            raise ValueError("Пароли не совпадают")

        self.user_repo.create(UserCreateDto(
            **user_data.model_dump(exclude=["password2"])
        ))

    def signin(self, user_data: UserSigninDto) -> UserSchema:
        user = self.user_repo.get_user_by_email_and_password(user_data)
        if user is None:
            raise ValueError("Пользователь не найден")
        session["user_id"] = user.id
        session["user_name"] = user.name
        return user