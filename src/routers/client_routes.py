from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.auth_model import User
from src.models.client_model import Client
from src.schemas.client_schema import CreateClient, ListClients, PublicClient
from src.services.database import get_session
from src.services.security import get_current_user
from src.utils.cpf_validator import clean_cpf, validate_cpf

router = APIRouter(prefix='/clients', tags=['Clients'])

# types
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[Session, Depends(get_session)]


@router.get('/', status_code=HTTPStatus.OK, response_model=ListClients)
def see_all_clients(
    current_user: T_CurrentUser,
    session: T_Session,
    limit: int = 10,
    skip: int = 0,
    name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
):
    stmt = select(Client)

    if name:
        stmt = stmt.where(Client.name.ilike(f'%{name}%'))
    if email:
        stmt = stmt.where(Client.email.ilike(f'%{email}%'))

    stmt = stmt.offset(skip).limit(limit).order_by(Client.id)
    clients = session.scalars(stmt).all()

    return {'clients': clients}


@router.post('/', status_code=HTTPStatus.CREATED, response_model=PublicClient)
def create_client(
    client: CreateClient,
    current_user: T_CurrentUser,
    session: T_Session,
):
    cleaned_cpf = clean_cpf(client.cpf)
    valid_cpf = validate_cpf(cleaned_cpf)
    if not valid_cpf:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Invalid CPF',
        )

    db_client = session.scalar(
        select(Client).where(
            (Client.email == client.email) | (Client.cpf == client.cpf)
        )
    )

    if db_client:
        if db_client.email == client.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )

        if db_client.cpf == client.cpf:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='CPF already exists',
            )

    db_client = Client(name=client.name, email=client.email, cpf=client.cpf)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    return db_client


@router.get('/{client_id}', response_model=PublicClient)
def get_one_client(
    current_user: T_CurrentUser,
    session: T_Session,
    client_id: int,
):
    client = session.scalar(
        select(Client).where(Client.id == client_id),
    )

    if not client:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Client not found',
        )

    return client


@router.put('/{client_id}', response_model=PublicClient)
def update_user(
    current_user: T_CurrentUser,
    session: T_Session,
    client_id: int,
    client: CreateClient,
):
    cleaned_cpf = clean_cpf(client.cpf)
    valid_cpf = validate_cpf(cleaned_cpf)
    if not valid_cpf:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Invalid CPF',
        )

    db_client = session.scalar(select(Client).where(Client.id == client_id))
    if not db_client:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    email_already_registered = session.scalar(
        select(Client).where(Client.email == client.email),
    )
    if email_already_registered and email_already_registered.id != client_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Email already registered by another user',
        )

    cpf_already_registered = session.scalar(
        select(Client).where(Client.cpf == client.cpf),
    )
    if cpf_already_registered and cpf_already_registered.id != client_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='CPF already registered by another user',
        )

    db_client.name = client.name
    db_client.email = client.email
    db_client.cpf = client.cpf
    session.commit()
    session.refresh(db_client)

    return db_client


@router.delete('/{client_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(
    current_user: T_CurrentUser,
    session: T_Session,
    client_id: int,
):
    if current_user.profile != 'admin':
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permission',
        )

    client = session.scalar(
        select(Client).where(Client.id == client_id),
    )
    if not client:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Client not found'
        )

    session.delete(client)
    session.commit()

    return
