import os

import psycopg2


def get_resource_path():
    full_path = os.path.realpath(__file__)
    path, _ = os.path.split(full_path)
    return f'{path}/resource'


def read_schema(action: str, operation: str) -> str:
    resource_path = get_resource_path()
    with open(f'{resource_path}/schema/{action}/{operation}.gql', 'rb') as f:
        data = f.read()
        return data.decode('utf-8')


def read_schema_operations(action: str):
    resource_path = get_resource_path()
    schema_path = f'{resource_path}/schema/{action}'
    return [f.split('.')[0] for f in os.listdir(schema_path) if f.endswith('.gql')]


def create_database(url):
    db_name = url.database
    db_user = url.username
    db_password = url.password
    db_host = url.host
    db_port = url.port

    con = psycopg2.connect(user=db_user, password=db_password, host=db_host, port=db_port)
    con.autocommit = True
    cur = con.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS \"{db_name}\";")
    cur.execute(f'CREATE DATABASE \"{db_name}\" owner {db_user};')
    cur.execute(f"grant all privileges on database \"{db_name}\" to {db_user};")
