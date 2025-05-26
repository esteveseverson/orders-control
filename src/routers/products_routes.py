from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.auth_model import User
from src.models.products_model import Product
from src.schemas.products_schema import BaseProduct, ProductOutput
from src.services.database import get_session
from src.services.security import get_current_user
from src.utils.cloudinary_upload import upload_image

router = APIRouter(prefix='/products', tags=['Products'])

# types
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[Session, Depends(get_session)]
T_Multpart = Annotated[BaseProduct, Depends(BaseProduct.as_form)]


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
