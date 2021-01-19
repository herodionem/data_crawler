from app import *
import time
from datetime import timedelta
from datetime import datetime
import json
import os


check_special_file = True
check_manifest = True
check_manifest_interval = timedelta(minutes=1)
check_manifest_time = datetime.now()

now = lambda x=None: x.strftime('%Y-%m-%d %H:%M:%S.%f') if x else datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
pnow = lambda x=None: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f') if x else datetime.strptime(now(), '%Y-%m-%d %H:%M:%S.%f')

def check_for_new_manifests() -> list:
    log.debug('Checking for new manifests')
    global check_manifest_time
    keys = set(i['Key'] for i in s3.list_objects(Bucket='demo-guest', Prefix='crawl/manifest_')['Contents'])
    files = set(i.rsplit('/')[1] for i in keys)
    sql = f"select filename from manifest_log"
    cur.execute(sql)
    retrieve = files - set(i[0] for i in cur.fetchall())
    keys = [i for i in keys if i.rsplit('/')[1] in retrieve]
    log.info(f'{len(keys)} new manifests found.')
    for m in keys:
        sql = f"""insert into manifest_log (filename, status, attempts, created_at)
            values ('{m.rsplit('/')[1]}', 0, 0, '{datetime.utcnow().isoformat()}')"""
        cur.execute(sql)
        log.debug(f'executed sql: {sql}')
    conn.commit()
    check_manifest_time = datetime.now()
    return keys

def find_schedule(start, count=0, interval=0, duration=0):
    """
    ::start - datetime => the time when this job schedule should begin
    ::count - int => how many times overall the job should be executed
    ::interval - int => how many seconds between job execution instance
    ::duration - int => seconds from start time to allow jobs to be scheduled
    find_schedule(datetime(2021,2,1), 10, 3600, ('hours', 5))
    """
    global now
    duration = duration or 0
    assert count or (interval and duration), "You have to limit the schedule"
    times = [start.isoformat()]
    cur_time = start
    delt = timedelta(0, interval)
    dur = timedelta(0, duration)
    cnt = 0
    while (cur_time + delt < start + dur) and cnt < count:
        t = cur_time + delt
        times.append(now(t))
        cur_time = t
        cnt += 1
    return times

def update_crawl_schedule(manifest_list: list):
    for manifest in manifest_list:
        m = json.loads(s3.get_object(Bucket='demo-guest', Key=manifest)['Body'].read())
        for j in m:
            log.debug(f"{j['url']} --> find_schedule(pnow(j.get('start')), j['count'], j['interval'], j['duration'])")
            for scheduled in find_schedule(pnow(j.get('start')), j['count'], j['interval'], j['duration']):
                sql = f"""
                    insert into crawl_schedule(service, url, headers, cookies, scheduled, version, status, attempts, created_at)
                    values ('{j['service']}','{j['url']}','{j['headers']}','{j['cookies']}','{scheduled}','{j['version']}',0,0,'{now()}')"""
                try:
                    cur.execute(sql)
                    log.debug(f"Executed SQL: {sql}")
                except Exception as e:
                    log.error(e)
    conn.commit()

def sanitize_redis_inputs(d):
    ret = {}
    for k,v in d.items():
        if v is None:
            v = 'None'
        elif isinstance(v, datetime):
            v = now(v)
        ret[k] = v
    return ret

def backoff(i):
    return i ** 1.2

while True:
    manifest_list = None
    # Check for new manifest keys in S3
    if datetime.now() - check_manifest_time > check_manifest_interval:
        manifest_list = check_for_new_manifests()
        log.debug(f'retrieved manifests: {manifest_list}')
        update_crawl_schedule(manifest_list)

    # Add any new jobs to the message queue

    sql = f"""update crawl_schedule set status = 1 where status = 0 and scheduled < '{now()}' returning *"""
    cur.execute(sql)
    jobs = cur.fetchall()
    cols = [i.name for i in cur.description]
    jobs = [dict(zip(cols, i)) for i in jobs]
    log.debug(f"Trying to add to REDIS:\n{jobs}")
    for j in jobs:
        r.xadd('crawl_stream', sanitize_redis_inputs(j))
    log.info(f'Added {len(jobs)} jobs to the crawl stream')
    conn.commit()

    # log.debug(os.path.isfile('./app/special_file.txt'))
    # log.debug(check_special_file)
    if not os.path.isfile('./app/special_file.json') and check_special_file:
        jobs_submitted = r.xread({'crawl_stream':'0'})
        try:
            read_redis = jobs_submitted[0][1]
        except:
            read_redis = [['empty result', []]]
            log.warning(f"Use xread more reliably... {jobs_submitted}")
        jobs_pending = r.xreadgroup('crawlers', 'crawler1', {'crawl_stream': '0'})
        cur.execute('select count(*) from crawl_schedule')
        has_rows = cur.fetchall()[0][0]
        cur.execute('select count(*) from crawl_schedule where status = 0')
        not_complete = cur.fetchall()[0][0]
        log.info(f"Jobs Submitted: {len(read_redis[0][1])} Submitted Jobs: {has_rows} Unscheduled Jobs: {not_complete}")
        if len(read_redis[0][1]) > 0 and len(jobs_pending[0][1]) == 0 and has_rows > 1 and not_complete == 0:
            cur.execute('select right(word, 1) as letter, count(*) from analyze_words group by letter')
            cols = [i.name for i in cur.description]
            analysis = dict(cur.fetchall())
            if analysis:
                with open('./app/special_file.json', 'w') as sfile:
                    sfile.write(json.dumps(dict(sorted(analysis.items(), key=lambda x: x[0]))))
                check_special_files = False
                log.info('Special File Created :D')

    time.sleep(30)
