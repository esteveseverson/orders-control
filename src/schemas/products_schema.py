from datetime import date, datetime
from typing import List

from fastapi import Form
from pydantic import BaseModel, field_validator


class BaseProduct(BaseModel):
    name: str
    description: str
    category: str
    price: float
    barcode: str
    quantity: int
    expiration: date

    @field_validator('expiration', mode='before')
    def date_validation(cls, value):
        if isinstance(value, date):
            return value

        try:
            return datetime.strptime(value, '%d/%m/%Y').date()
        except ValueError:
            raise ValueError('The data must be in the format dd/mm/yyyy')

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: str = Form(...),
        category: str = Form(...),
        price: float = Form(...),
        barcode: str = Form(...),
        quantity: int = Form(...),
        expiration: str = Form(...),
    ):
        return cls(
            name=name,
            description=description,
            category=category,
            price=price,
            barcode=barcode,
            quantity=quantity,
            expiration=expiration,
        )


class ProductOutput(BaseModel):
    id: int
    name: str
    description: str
    category: str
    price: float
    barcode: str
    quantity: int
    expiration: date
    image: str


class ListProducts(BaseModel):
    products: List[ProductOutput]
