from http import HTTPStatus

from fastapi import FastAPI

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK)
def server_status():
    return {'status': 'online'}
