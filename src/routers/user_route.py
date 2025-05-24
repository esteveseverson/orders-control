from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_session
from src.models.auth_model import User
from src.schemas.user_schema import CreateUser, PublicUser
from src.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['Users'])

# types
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=PublicUser)
def create_user_normal_user(user: CreateUser, session: T_Session):
    db_user = session.scalar(
        select(User).where(User.email == user.email),
    )
    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Email already registered',
        )

    db_user = User(
        name=user.name,
        email=user.email,
        profile='normal',
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
