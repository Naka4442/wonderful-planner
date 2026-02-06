from models.user import User, UserCreateDto, UserSchema, UserSigninDto
from repositories.abstract_repository import AbstractRepository


class UserRepository(AbstractRepository):
    def create(self, user_data: UserCreateDto) -> UserSchema:
        user = User(**user_data.model_dump())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return UserSchema.model_validate(user, from_attributes=True)

    def check_user_by_email(self, email: str) -> bool:
        user = self.db.query(User).filter(User.email == email).first()
        if user is None:
            return False
        return True
    
    def get_user_by_email_and_password(self, user_data: UserSigninDto) -> UserSchema | None:
        user = self.db.query(User).filter(
            User.email == user_data.email,
            User.password == user_data.password
        ).first()
        if user is None:
            return None
        return UserSchema.model_validate(user, from_attributes=True)