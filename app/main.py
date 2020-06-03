import logging.config
from importlib import import_module

import socketio
from stargql import GraphQL

from app import settings
from app.db import database
from .socket import sio
from .rest import app as rest_app

# register resolvers
import_module('app.resolvers')


# init logging config
logging.config.dictConfig(settings.LOGGING)


async def startup():
    await database.connect()


async def shutdown():
    await database.disconnect()


sio_app = socketio.ASGIApp(sio, other_asgi_app=rest_app)
rest_app.add_websocket_route('/socket.io/', sio_app)
rest_app.add_route('/socket.io/', route=sio_app, methods=['GET', 'POST'])

app = GraphQL(
    schema_file=settings.GRAPHQL_SCHEMA_FILE,
    path=settings.GRAPHQL_PATH,
    on_startup=[startup],
    on_shutdown=[shutdown],
    debug=settings.DEBUG,
    routes=rest_app.router.routes,
)
