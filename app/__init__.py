import os
import logging
import logging.config

import boto3
import psycopg2
import redis


logging.config.fileConfig(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf'))

AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
MAIL_HOST = os.getenv('MAIL_HOST')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_FROM = os.getenv('MAIL_FROM')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', POSTGRES_USER)
POSTGRES_PORT = os.getenv('POSTGRES_PORT', 5432)
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'secret')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)


def get_postgres_conn(host=POSTGRES_HOST, port=POSTGRES_PORT, user=POSTGRES_USER, password=POSTGRES_PASSWORD, dbname=POSTGRES_DB, ret_cur=False):
    log.info(f'Establishing DB connection with host={host}, port={port}, user={user}, password={password}, dbname={dbname}')
    conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)
    if ret_cur:
        return conn, conn.cursor()
    return conn


def get_s3_client(key=AWS_ACCESS_KEY_ID, secret=AWS_SECRET_ACCESS_KEY):
    s3 = boto3.client('s3',
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        region_name=AWS_REGION
    )
    return s3


def get_redis_cursor(host=REDIS_HOST, port=REDIS_PORT):
    r = redis.Redis(host=host, port=port)
    return r


log = logging.getLogger(os.getenv('LOG_CONTEXT'))
conn, cur = get_postgres_conn(ret_cur=True)
s3 = get_s3_client()
r = get_redis_cursor()

for group in ['crawlers', 'parsers']:
    try:
        r.xgroup_create('crawl_stream', group, '0', True)
    except Exception as e:
        log.info(e)


__all__ = [
    'log',
    's3',
    'r',
    'conn',
    'cur',
    'get_s3_client',
    'get_redis_cursor',
    'get_postgres_conn',
]
