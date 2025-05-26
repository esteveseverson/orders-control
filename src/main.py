from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import auth_routes, client_routes, products_routes

app = FastAPI()
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(auth_routes.router)
app.include_router(client_routes.router)
app.include_router(products_routes.router)


@app.get('/', status_code=HTTPStatus.OK)
def server_status():
    return {'status': 'online'}
