from fastapi import HTTPException

from app.core.security.password import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserLogin


class UserService:
    def __init__(self, repo: Annotated[UserRepository, Depends()]):
        self.repo = repo

    def create_user(self, data: UserCreate):
        existing_user = self.repo.get_by_email(data.email)

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            profile_image=data.profile_image,
        )

        return self.repo.create(user)


    def login(self, data: UserLogin) -> User:
        user = self.repo.get_by_email(data.email)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        return user
