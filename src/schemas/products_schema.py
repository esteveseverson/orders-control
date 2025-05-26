from datetime import date, datetime
from typing import List

from pydantic import BaseModel, field_validator


class Product(BaseModel):
    name: str
    description: str
    category: str
    price: int
    barcode: str
    quantity: str
    expiration: date

    @field_validator('expiration', mode='before')
    def date_validation(cls, value):
        if isinstance(value, date):
            return value

        try:
            return datetime.strptime(value, '%d/%m/%Y').date()
        except ValueError:
            raise ValueError('The data must be in the format dd/mm/yyyy')


class ProductOutput(BaseModel):
    name: str
    description: str
    category: str
    price: int
    barcode: str
    quantity: str
    expiration: date
    image: str


class ListClients(BaseModel):
    products: List[ProductOutput]
