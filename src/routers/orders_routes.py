from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.auth_model import User
from src.models.order_model import Order, OrderItem, OrderStatus
from src.models.products_model import Product
from src.schemas.order_schema import (
    ListOrders,
    OrderCreate,
    OrderOutput,
    OrderUpdate,
)
from src.services.database import get_session
from src.services.security import get_current_user

router = APIRouter(prefix='/orders', tags=['Orders'])

# types
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[Session, Depends(get_session)]


@router.get('/', status_code=HTTPStatus.OK, response_model=ListOrders)
def get_all_orders(
    current_user: T_CurrentUser,
    session: T_Session,
    order_id: Optional[int] = Query(None),
    client_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = 10,
    skip: int = 0,
):
    stmt = select(Order)

    if order_id:
        stmt = stmt.where(Order.id == order_id)
    if client_id:
        stmt = stmt.where(Order.client_id == client_id)
    if status:
        stmt = stmt.where(Order.status.ilike(f'%{status}%'))

    stmt = stmt.offset(skip).limit(limit).order_by(Order.id.desc())
    orders = session.scalars(stmt).all()

    return {'orders': orders}


@router.post('/', status_code=HTTPStatus.CREATED, response_model=OrderOutput)
def create_order(
    current_user: T_CurrentUser,
    session: T_Session,
    order: OrderCreate,
):
    try:
        with session.begin_nested():
            new_order = Order(
                client_id=order.client_id,
                status=OrderStatus.PENDING,
                total=0,
                items=[],
            )
            session.add(new_order)
            session.flush()

            total = 0
            for item in order.items:
                product = session.get(Product, item.product_id)
                if not product:
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND,
                        detail=f'Item {item.product_id} not found',
                    )
                if product.quantity < item.quantity:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail=f'Not enough {product.name} in stock',
                    )

                product.quantity -= item.quantity
                price_cents = product.price

                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=price_cents,
                )
                session.add(order_item)
                total += price_cents * item.quantity

            new_order.total = total
            session.commit()

    except HTTPException:
        session.rollback()
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f'Error creating order {e}',
        )

    new_order.total = new_order.total / 100
    return new_order


@router.get(
    '/{order_id}', status_code=HTTPStatus.OK, response_model=OrderOutput
)
def get_one_order(
    current_user: T_CurrentUser, session: T_Session, order_id: int
):
    order = session.scalar(select(Order).where(Order.id == order_id))
    if not order:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Order not found',
        )

    order.total = order.total / 100

    return order_id


@router.put(
    '/{order_id}', status_code=HTTPStatus.OK, response_model=OrderOutput
)
def update_order(
    current_user: T_CurrentUser,
    session: T_Session,
    order_id: int,
    order: OrderUpdate,
):
    db_order = session.scalar(select(Order).where(Order.id == order_id))
    if not db_order:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Order not found'
        )

    if order.status:
        db_order.status = order.status

    session.commit()
    session.refresh(db_order)
    db_order.total = db_order.total / 100

    return db_order


@router.delete('/{order_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_order(
    current_user: T_CurrentUser,
    session: T_Session,
    order_id: int,
):
    if current_user.profile != 'admin':
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permission',
        )

    db_order = session.scalar(select(Order).where(Order.id == order_id))
    if not db_order:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Order not found',
        )

    session.delete(db_order)
    session.commit()
    return
