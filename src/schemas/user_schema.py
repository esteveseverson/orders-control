from typing import List

from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    name: str
    email: EmailStr


class CreateUser(BaseUser):
    password: str


class PublicUser(BaseModel):
    id: int
    name: str
    email: EmailStr


class ListUser(BaseModel):
    users: List[PublicUser]
