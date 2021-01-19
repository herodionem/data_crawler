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
    try:
        if job[0][1]:
            job = job[0][1][0]
        else:
            log.info(f'No more available jobs in crawl_stream - going to sleep...')
            time.sleep(60)
            continue
    except Exception as e:
        log.error(e)
        log.warning(job)
    redis_id = job[0]
    job = dict((k.decode(), v.decode()) for k,v in job[1].items())
    if not job.get('url'):
        log.warn(f'This does not look like a job: Redis ID "{redis_id}" {str(job)}. Removing from stream...')
        r.xdel('crawl_stream', redis_id)
        r.xack('crawl_stream', 'crawlers', redis_id)
        continue
    status_code = 400
    attempt = 0
    while status_code != 200:
        attempt += 1
        log.info(f"Requesting <{job['url']}> - Attempt {attempt}")
        resp = requests.get(job['url'])
        log.info(f"Respone: {resp}")
        status_code = resp.status_code
    cur.execute(f"update crawl_schedule set attempts = attempts + {attempt} where id = {job['id']}")

    obj = json.loads(resp.content)
    sql = f"insert into crawl_results (url, response) values ('{job['url']}', '{resp.content.decode()}')"
    cur.execute(sql)
    r.xack('crawl_stream', 'crawlers', redis_id)

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
    sql = f"with t as (insert into analyze_words (word, opt) values {','.join(words)} returning word) select count(*) from t"
    cur.execute(sql)
    words_added = cur.fetchall()
    log.info(f"Added {words_added} to `analyze_words` table")

    conn.commit()
