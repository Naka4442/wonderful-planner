from datetime import date
from typing import List

from sqlalchemy import func
from models.user_info import UserInfo, UserInfoCreateDto, UserInfoQuestion, UserInfoQuestionSchema, UserInfoSchema
from repositories.abstract_repository import AbstractRepository


class UserInfoRepository(AbstractRepository):
    def get_questions(self) -> List[UserInfoQuestionSchema]:
        return [
            UserInfoQuestionSchema.model_validate(question, from_attributes=True)
            for question in self.db.query(UserInfoQuestion).all()
        ]

    def bulk_create_info(self, user_infos: List[UserInfoCreateDto]) -> None:
        for user_info in user_infos:
            user_info_model = UserInfo(**user_info.model_dump())
            self.db.add(user_info_model)
        self.db.commit()
    
    def get_by_user_id(self, user_id: int) -> List[UserInfo]:
        return [
            UserInfoSchema(user_info, from_attributes=True)
            for user_info in
            self.db.query(UserInfo).filter(UserInfo.user_id == user_id).all()
        ]
    
    def get_by_user_id_and_day(self, user_id: int, day: date) -> List[UserInfo]:
        return [
            UserInfoSchema(user_info, from_attributes=True)
            for user_info in
            self.db.query(UserInfo).filter(
                UserInfo.user_id == user_id,
                func.date(UserInfo.created) == day
            ).all()
        ]