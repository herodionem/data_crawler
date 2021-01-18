#!/bin/sh
echo "Waiting for postgres..."
echo "attempting to connect : ${POSTGRES_HOST} ${POSTGRES_PORT}"
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 1
done

echo "PostgreSQL started"
exec "$@"