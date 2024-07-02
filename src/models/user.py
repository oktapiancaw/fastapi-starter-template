from hashlib import sha256
from uuid import uuid4
from typing import Optional

from pydantic import (
    BaseModel,
    RootModel,
    EmailStr,
    Field,
)


class AccountModel(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserMeta(BaseModel):
    name: str
    image: Optional[str] = None


class UserCreate(UserMeta, AccountModel): ...


class UserMetaSafe(UserMeta):
    id: str
    username: str
    email: EmailStr


class UserModel(UserCreate):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")

    def hash_password(self):
        self.password = sha256(self.password.encode("utf-8")).hexdigest()
        return self

    def verify_password(self, password):
        return self.password == sha256(password.encode("utf-8")).hexdigest()

    @property
    def safe(self):
        return UserMetaSafe(**self.model_dump()).model_dump()


UserList = RootModel[list[UserModel]]
