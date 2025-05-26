from http import HTTPStatus


def test_create_client_success(auth_client):
    response = auth_client.post(
        '/clients/',
        json={
            'name': 'Test Client',
            'email': 'newclient@example.com',
            'cpf': '123.456.789-09',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['email'] == 'newclient@example.com'


def test_create_client_invalid_cpf(auth_client):
    response = auth_client.post(
        '/clients/',
        json={
            'name': 'Test Client',
            'email': 'invalidcpf@example.com',
            'cpf': '111.111.111-11',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Invalid CPF' in response.json()['detail']


def test_create_client_duplicate_email(auth_client, sample_client):
    response = auth_client.post(
        '/clients/',
        json={
            'name': 'duplicate email',
            'email': sample_client['email'],
            'cpf': '987.654.321-00',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Email already exists' in response.json()['detail']


def test_create_client_duplicate_cpf(auth_client, sample_client):
    response = auth_client.post(
        '/clients/',
        json={
            'name': 'duplicate cpf',
            'email': 'duplicate@cpf.com',
            'cpf': '529.982.247-25',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'CPF already exists' in response.json()['detail']


def test_get_all_clients(auth_client, sample_client):
    response = auth_client.get('/clients/')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['clients']) >= 1


def test_get_all_clients_with_filter(auth_client, sample_client):
    response_with_name = auth_client.get(
        f'/clients/?name={sample_client["name"]}'
    )

    response_with_email = auth_client.get(
        f'/clients/?email={sample_client["email"]}'
    )

    assert response_with_name.status_code == HTTPStatus.OK
    assert response_with_email.status_code == HTTPStatus.OK


def test_get_single_client(auth_client, sample_client):
    response = auth_client.get(
        f'/clients/{sample_client["id"]}',
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['name'] == sample_client['name']


def test_get_non_existent_client(auth_client):
    response = auth_client.get('/clients/1')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_client(auth_client, sample_client):
    update_data = {
        'name': 'Updated',
        'email': 'updated@example.com',
        'cpf': '529.982.247-25',
    }
    response = auth_client.put(
        f'/clients/{sample_client["id"]}',
        json=update_data,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['name'] == 'Updated'


def test_update_inexistent_client(auth_client):
    update_data = {
        'name': 'inexistent',
        'email': 'inexistent@example.com',
        'cpf': '123.123.123-12',
    }
    response = auth_client.put('/clients/1', json=update_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'User not found' in response.json()['detail']


def test_update_client_conflict(auth_client, sample_client):
    new_user_data = {
        'name': 'Another Client',
        'email': 'another@example.com',
        'cpf': '987.654.321-00',
    }
    auth_client.post('/clients/', json=new_user_data)

    response_with_same_email = auth_client.put(
        f'clients/{sample_client["id"]}',
        json={
            'name': 'Conflict 1',
            'email': new_user_data['email'],
            'cpf': '123.123.123.12',
        },
    )

    response_with_same_cpf = auth_client.put(
        f'/clients/{sample_client["id"]}',
        json={
            'name': 'Conflict 2',
            'email': 'new@email.com',
            'cpf': new_user_data['cpf'],
        },
    )

    response_with_invalid_cpf = auth_client.put(
        f'/clients/{sample_client["id"]}',
        json={
            'name': 'Conflict 3',
            'email': sample_client['email'],
            'cpf': '111.111.111-11',
        },
    )

    assert response_with_same_email.status_code == HTTPStatus.BAD_REQUEST
    assert (
        'Email already registered' in response_with_same_email.json()['detail']
    )

    assert response_with_same_cpf.status_code == HTTPStatus.BAD_REQUEST
    assert 'CPF already registered' in response_with_same_cpf.json()['detail']

    assert response_with_invalid_cpf.status_code == HTTPStatus.BAD_REQUEST
    assert 'Invalid CPF' in response_with_invalid_cpf.json()['detail']


def test_delete_client_as_admin(admin_client):
    response = admin_client.post(
        '/clients/',
        json={
            'name': 'Initial Client',
            'email': 'client@example.com',
            'cpf': '529.982.247-25',
        },
    )
    client_id = response.json()['id']
    delete_response = admin_client.delete(f'/clients/{client_id}')

    assert delete_response.status_code == HTTPStatus.NO_CONTENT


def test_delete_client_as_normal_user(auth_client, sample_client):
    response = auth_client.delete(f'clients/{sample_client["id"]}')

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert 'Not enough permission' in response.json()['detail']


def test_delete_inexistent_client(admin_client):
    response = admin_client.delete('clients/2')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'Client not found' in response.json()['detail']
