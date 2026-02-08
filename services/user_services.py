from typing import List
from flask import session

from models.user import UserCreateDto, UserSchema, UserSigninDto, UserSignupDto
from models.user_info import UserInfoCreateDto, UserInfoQuestionSchema
from repositories.user_info_repository import UserInfoRepository
from repositories.user_repository import UserRepository


class UserServices:
    def __init__(
            self, 
            user_repository: UserRepository,
            user_info_repository: UserInfoRepository
        ):
        self.user_repo = user_repository
        self.user_info_repo = user_info_repository

    def get_user_info_questions(self) -> List[UserInfoQuestionSchema]:
        return self.user_info_repo.get_questions()

    def signup(self, user_data: UserSignupDto) -> UserSchema:
        if self.user_repo.check_user_by_email(user_data.email):
            raise ValueError("Пользователь с таким email уже существует")
        
        if user_data.password != user_data.password2:
            raise ValueError("Пароли не совпадают")

        user = self.user_repo.create(UserCreateDto(
            **user_data.model_dump(exclude=["password2", "info"])
        ))

        self.user_info_repo.bulk_create_info([
            UserInfoCreateDto(
                user_id=user.id,
                question_id=info.question_id,
                points=info.points
            ) for info in user_data.info
        ])

        return user

    def signin(self, user_data: UserSigninDto) -> UserSchema:
        user = self.user_repo.get_user_by_email_and_password(user_data)
        if user is None:
            raise ValueError("Пользователь не найден")
        session["user_id"] = user.id
        session["user_name"] = user.name
        return user