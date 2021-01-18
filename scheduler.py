from app import *
import time
from flask import Flask, request
log.debug('testing which log this goes to...')
cur.execute('select current_database()')
log.debug(f'current db: {cur.fetchall()}')
while True:
    time.sleep(10)