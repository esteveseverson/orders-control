from datetime import UTC, datetime, timedelta
from http import HTTPStatus

from jwt import encode

from src.services.settings import Settings


def test_expired_token(client):
    # create expired token
    expired_payload = {
        'sub': 'test@example.com',
        'exp': datetime.now(UTC) - timedelta(minutes=1),
    }
    expired_token = encode(
        expired_payload,
        Settings().SECRET_KEY,
        algorithm=Settings().ALGORITHM,
    )

    response = client.post(
        '/auth/refresh-token',
        headers={'Authorization': f'Bearer {expired_token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Could not validate credentials'


def test_invalid_token(client):
    response = client.post(
        '/auth/refresh-token',
        headers={'Authorization': 'Bearer invalid_token'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Could not validate credentials'


def test_token_missing_sub(client):
    no_sub_payload = {
        'exp': datetime.now(UTC)
        + timedelta(minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    no_sub_token = encode(
        no_sub_payload, Settings().SECRET_KEY, algorithm=Settings().ALGORITHM
    )

    response = client.post(
        '/auth/refresh-token',
        headers={'Authorization': f'Bearer {no_sub_token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Could not validate credentials'


def test_user_not_found(client):
    valid_payload = {
        'sub': 'ghost@example.com',
        'exp': datetime.now(UTC)
        + timedelta(minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    valid_token = encode(
        valid_payload, Settings().SECRET_KEY, algorithm=Settings().ALGORITHM
    )

    response = client.post(
        '/auth/refresh-token',
        headers={'Authorization': f'Bearer {valid_token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Could not validate credentials'
