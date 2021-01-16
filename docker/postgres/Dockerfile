FROM postgres:12.0

RUN apt-get update && apt-get clean && apt-get install -y apt-utils nano

COPY ./init.sql /docker-entrypoint-initdb.d/

CMD ["postgres"]