from typing import List

from pydantic import BaseModel, EmailStr


class BaseClient(BaseModel):
    name: str
    email: EmailStr


class CreateClient(BaseClient):
    cpf: str


class PublicClient(BaseModel):
    id: int
    name: str
    email: EmailStr


class ListClients(BaseModel):
    clients: List[PublicClient]
