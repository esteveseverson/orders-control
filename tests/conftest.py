import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.main import app
from src.models import table_registry
from src.services.database import get_session


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def auth_client(client: TestClient):
    user_data = {
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'SecurePass123!',
    }
    client.post('/auth/register', json=user_data)

    login_res = client.post(
        '/auth/login',
        data={
            'username': user_data['email'],
            'password': user_data['password'],
        },
    )
    token = login_res.json()['access_token']
    client.headers = {'Authorization': f'Bearer {token}'}
    return client


@pytest.fixture
def admin_client(client):
    admin_data = {
        'name': 'Admin User',
        'email': 'admin@example.com',
        'password': 'AdminPass123!',
    }
    client.post('/auth/register-admin', json=admin_data)

    login_res = client.post(
        '/auth/login',
        data={
            'username': admin_data['email'],
            'password': admin_data['password'],
        },
    )
    token = login_res.json()['access_token']
    client.headers = {'Authorization': f'Bearer {token}'}

    return client


@pytest.fixture
def sample_client(auth_client):
    response = auth_client.post(
        '/clients/',
        json={
            'name': 'Initial Client',
            'email': 'client@example.com',
            'cpf': '529.982.247-25',
        },
    )
    return response.json()
