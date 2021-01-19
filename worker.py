from app import *
import requests
import time
import json


while True:
    job = r.xreadgroup('crawlers', 'crawler1', {'crawl_stream': '>'})
    if job:
        job = job[0][1][0]
    if not job:
        job = r.xreadgroup('crawlers', 'crawler1', {'crawl_stream': '0'})
    if job:
        job = job[0][1][0]
    else:
        log.info(f'No more available jobs in crawl_stream - going to sleep...')
        time.sleep(60)
        continue
    redis_id = job[0]
    job = dict((k.decode(), v.decode()) for k,v in job[1].items())
    status_code = 400
    attempt = 0
    while status_code != 200:
        attempt += 1
        log.info(f"Requesting <{job['url']}> - Attempt {attempt}")
        resp = requests.get(job['url'])
        status_code = resp.status_code
    cur.execute(f"update crawl_schedule set attempts = attempts + {attempt} where id = {job['id']}")

    obj = json.loads(resp.content)
    sql = f"insert into crawl_results (url, response) values ('{job['url']}', '{resp.content.decode()}')"
    cur.execute(sql)

    words = []
    for k,v in obj.items():
        if not isinstance(v, list):
            log.warn(f"SKIPPING UNEXPECTED DATA TYPE: <{job['url']}> {v}")
            continue
        for vv in v:
            if not isinstance(vv, dict):
                log.warn(f"SKIPPING UNEXPECTED DATA TYPE: <{job['url']}> {v}")
                continue
            words.append(f"('{vv['word']}',NULL)")
    sql = f"insert into analyze (word, opt) values {','.join(words)}"
    cur.execute(sql)

    conn.commit()


