import logging.config
from importlib import import_module

from stargql import GraphQL
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app import settings
from app.db import database
from .redis import redis
from .rest import app as rest_app

# register resolvers
import_module('app.resolvers')


# init logging config
logging.config.dictConfig(settings.LOGGING)


async def startup():
    await database.connect()
    await redis.connect()


async def shutdown():
    await database.disconnect()
    await redis.disconnect()


routes = rest_app.router.routes
routes.append(Mount('/media', StaticFiles(directory='media'), name='media'))


if settings.WITH_JUMP:
    templates = Jinja2Templates(directory='build')

    async def homepage(request):
        return templates.TemplateResponse('index.html', {'request': request})

    routes.extend(
        [
            Route('/', endpoint=homepage),
            Mount('/jump', StaticFiles(directory='build'), name='static'),
        ]
    )


app = GraphQL(
    schema_file=settings.GRAPHQL_SCHEMA_FILE,
    path=settings.GRAPHQL_PATH,
    on_startup=[startup],
    on_shutdown=[shutdown],
    debug=settings.DEBUG,
    routes=routes,
)
