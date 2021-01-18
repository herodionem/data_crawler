FROM python:latest
RUN apt-get update && apt-get install -y netcat
COPY ./scheduler_requirements.txt /var/lib/data_crawler/python/requirements.txt
COPY ./entrypoint.sh /var/lib/data_crawler/python/entrypoint.sh
RUN pip install -r /var/lib/data_crawler/python/requirements.txt
WORKDIR /var/www/data_crawler
ARG POSTGRES_DB_HOST
ARG POSTGRES_PORT
ENTRYPOINT ["/var/lib/data_crawler/python/entrypoint.sh"]