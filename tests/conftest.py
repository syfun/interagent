import psycopg2
import pytest
from sqlalchemy import create_engine
from sqlalchemy_utils import drop_database
from starlette.testclient import TestClient

from app.db import database as db
from app.db.base import Base
from app.main import app
from app.settings import DATABASE_URL
from .utils import create_database, read_schema, read_schema_operations

QUERIES_DIR = 'queries'
MUTATION_DIR = 'mutations'
FAKER_SEED = 123456


@pytest.fixture(scope="session")
def recreate_db():
    engine = create_engine(DATABASE_URL)
    create_database(engine.url)
    Base.metadata.create_all(engine)
    yield
    drop_database(engine.url)


@pytest.fixture(autouse=True)
async def init_db(recreate_db):
    await db.connect()
    yield
    await db.disconnect()


@pytest.fixture(scope="session")
async def db_cursor(recreate_db):
    con = psycopg2.connect(DATABASE_URL)
    con.autocommit = True
    cur = con.cursor()
    yield cur
    con.close()


@pytest.fixture()
def client(recreate_db):
    client = TestClient(app)
    yield client


@pytest.fixture(scope="session")
def queries() -> dict:
    query_operations = read_schema_operations(QUERIES_DIR)
    return {q: read_schema(QUERIES_DIR, q) for q in query_operations}


@pytest.fixture(scope="session")
def mutations() -> dict:
    mutation_operations = read_schema_operations(MUTATION_DIR)
    return {q: read_schema(MUTATION_DIR, q) for q in mutation_operations}


@pytest.fixture(scope='session', autouse=True)
def faker_seed():
    return FAKER_SEED


@pytest.fixture(scope='session', autouse=True)
def faker_session_locale():
    return ['zh_CN']
