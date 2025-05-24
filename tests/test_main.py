from http import HTTPStatus


def test_read_root_and_server_status(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'status': 'online'}
