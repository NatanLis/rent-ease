#!/bin/bash

if [ -f "./app/gunicorn.pid" ]; then
    echo "Remove gunicorn pid file."
    rm -rf ./app/gunicorn.pid
fi

./scripts/wait-for-it.sh -t 15 $POSTGRES_HOST:$POSTGRES_PORT

status=$?
if [ $status -ne 0 ]; then
    echo "Failed to connect to database: $status"
    exit $status
fi

poetry run alembic upgrade head
status=$?
if [ $status -ne 0 ]; then
    echo "Failed to apply migrations: $status"
    exit $status
fi

cd app/api

echo "RUN DEV SERVER"
poetry run uvicorn api.main:app --reload --host= --port=$PORT
