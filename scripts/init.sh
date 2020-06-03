#!/bin/bash

export DATABASE_URL=${DATABASE_URL:='postgresql://postgres:postgres@postgres:5432/eam'}
postgres_ready() {
python << END

import asyncio
import sys

from databases import Database

url = '${DATABASE_URL}'
database = Database(url)

async def main():
    try:
        await database.connect()
    except Exception as exc:
        print(f'connect {url} error: ', exc)
        sys.exit(-1)
    else:
        await database.disconnect()
        sys.exit(0)

asyncio.run(main())

END
}
until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'

# migrate database
echo 'migrate database'
alembic upgrade head
