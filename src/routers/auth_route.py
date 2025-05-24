from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import get_session
from src.models.auth_model import User
from src.schemas.auth_schema import Token
from src.schemas.user_schema import CreateUser, PublicUser
from src.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['Authentication'])

# types
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[Session, Depends(get_session)]
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/login', response_model=Token)
def login_for_access_token(form_data: T_OAuth2Form, session: T_Session):
    user = session.scalar(
        select(User).where(User.email == form_data.username),
    )

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.post(
    '/register',
    status_code=HTTPStatus.CREATED,
    response_model=PublicUser,
)
def create_normal_user(user: CreateUser, session: T_Session):
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


@router.post(
    '/register-admin',
    status_code=HTTPStatus.CREATED,
    response_model=PublicUser,
)
def create_admin_user(user: CreateUser, session: T_Session):
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
        profile='admin',
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post('/refresh-token', response_model=Token)
def refresh_access_token(user: T_CurrentUser):
    new_access_token = create_access_token(data={'sub': user.email})
    return {'access_token': new_access_token, 'token_type': 'Bearer'}
