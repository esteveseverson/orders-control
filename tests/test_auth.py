from http import HTTPStatus


def test_register_user(client):
    user_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'SecurePass123!',
    }
    response = client.post('/auth/register', json=user_data)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['name'] == user_data['name']
    assert response.json()['email'] == user_data['email']


def test_register_duplicate_email(client):
    user_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'SecurePass123!',
    }
    client.post('/auth/register', json=user_data)
    response = client.post('/auth/register', json=user_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Email already registered' in response.json()['detail']


def test_register_admin_user(client):
    admin_data = {
        'name': 'Admin user',
        'email': 'admin@example.com',
        'password': 'AdminPass123!',
    }
    response = client.post('/auth/register-admin', json=admin_data)

    assert response.status_code == HTTPStatus.CREATED


def test_register_admin_duplicate_email(client):
    admin_data = {
        'name': 'Admin user',
        'email': 'admin@example.com',
        'password': 'AdminPass123!',
    }
    client.post('/auth/register-admin', json=admin_data)
    response = client.post('/auth/register-admin', json=admin_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Email already registered' in response.json()['detail']


def test_login_success(client):
    user_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'SecurePass123!',
    }
    client.post('/auth/register', json=user_data)

    response = client.post(
        '/auth/login',
        data={'username': 'test@example.com', 'password': 'SecurePass123!'},
    )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()


def test_login_invalid_credentials(client):
    response = client.post(
        '/auth/login',
        data={
            'username': 'nonexistent@example.com',
            'password': 'nonexistent',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Incorrect email or password' in response.json()['detail']


def test_refresh_token(client):
    user_data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'SecurePass123!',
    }
    client.post('auth/register', json=user_data)

    login = client.post(
        '/auth/login',
        data={'username': 'test@example.com', 'password': 'SecurePass123!'},
    )
    token = login.json()['access_token']

    response = client.post(
        '/auth/refresh-token', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()
