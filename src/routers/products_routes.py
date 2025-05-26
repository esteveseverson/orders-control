from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.auth_model import User
from src.models.products_model import Product
from src.schemas.products_schema import (
    BaseProduct,
    ListProducts,
    ProductOutput,
)
from src.services.database import get_session
from src.services.security import get_current_user
from src.utils.cloudinary_upload import upload_image

router = APIRouter(prefix='/products', tags=['Products'])

# types
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[Session, Depends(get_session)]
T_Multpart = Annotated[BaseProduct, Depends(BaseProduct.as_form)]


@router.get('/', status_code=HTTPStatus.OK, response_model=ListProducts)
def get_all_products(
    current_user: T_CurrentUser,
    session: T_Session,
    limit: int = 10,
    skip: int = 0,
    category: Optional[int] = Query(None),
    price: Optional[str] = Query(None),
    availability: Optional[str] = Query(None),
):
    stmt = select(Product)

    if category:
        stmt = stmt.where(Product.category.ilike(f'%{category}%'))
    if price:
        stmt = stmt.where(Product.price >= price * 100)
    if availability:
        stmt = stmt.where(Product.quantity >= 0)

    stmt = stmt.offset(skip).limit(limit).order_by(Product.id)
    products = session.scalars(stmt).all()

    return {'products': products}


@router.post('/', status_code=HTTPStatus.CREATED, response_model=ProductOutput)
async def create_product(
    current_user: T_CurrentUser,
    session: T_Session,
    product: T_Multpart,
    image: UploadFile = File(...),
):
    if product.price < 1:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Insert a valid price'
        )

    if product.quantity < 1:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Insert a valid quantity',
        )

    if product.expiration < datetime.now().date():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Insert a valid date'
        )

    db_product = session.scalar(
        select(Product).where(Product.barcode == product.barcode)
    )
    if db_product:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='This codebar already exists',
        )

    image_url = await upload_image(image=image)

    db_product = Product(
        name=product.name,
        description=product.description,
        category=product.category,
        price=product.price * 100,
        barcode=product.barcode,
        quantity=product.quantity,
        expiration=product.expiration,
        image=image_url,
    )
    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    db_product.price = product.price

    return db_product


@router.get('/{client_id}', response_model=ProductOutput)
def get_one_product(
    current_user: T_CurrentUser,
    session: T_Session,
    product_id: int,
):
    product = session.scalar(
        select(Product).where(Product.id == product_id),
    )

    if not product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Client not found',
        )

    product.price = product.price / 100
    return product


@router.put('/{client_id}', response_model=ProductOutput)
def update_product(
    current_user: T_CurrentUser,
    session: T_Session,
    product: BaseProduct,
    product_id: int,
):
    if product.price < 1:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Insert a valid price'
        )

    if product.quantity < 1:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Insert a valid quantity',
        )

    if product.expiration < datetime.now().date():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Insert a valid date'
        )

    db_product = session.scalar(
        select(Product).where(Product.id == product_id)
    )
    if not db_product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    barcode_registered = session.scalar(
        select(Product).where(Product.barcode == product.barcode),
    )
    if barcode_registered and barcode_registered.id != product_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='CPF already registered by another user',
        )

    db_product.name = product.name
    db_product.description = product.description
    db_product.category = product.category
    db_product.price = product.price * 100
    db_product.barcode = product.barcode
    db_product.quantity = product.quantity
    db_product.expiration = product.expiration

    session.commit()
    session.refresh(db_product)

    db_product.price = db_product.price / 100
    return db_product


@router.delete('/{client_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_product(
    current_user: T_CurrentUser,
    session: T_Session,
    product_id: int,
):
    if current_user.profile != 'admin':
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permission',
        )

    product = session.scalar(
        select(Product).where(Product.id == product_id),
    )
    if not product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Client not found'
        )

    session.delete(product)
    session.commit()

    return
