from typing import List

from pydantic import BaseModel, EmailStr


class BaseClient(BaseModel):
    name: str
    email: EmailStr


class CreateUser(BaseClient):
    cpf: str


class PublicClient(BaseModel):
    id: int
    name: str
    email: EmailStr


class ListUser(BaseModel):
    users: List[PublicClient]
