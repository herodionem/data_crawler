# data_crawler

A Data Crawler Demo!

This application will consist of a collection of microservices which, when tied together, will A) gather some data from an API and do some arbitrary processing on them and B) find links on a website and do something with them, like store them for later, or something...

At this point, things are pretty ugly. The logging could use some work, and code readability was, put kindly, a bit of an afterthought.


Technologies Used:
- Python
- S3
- PostgreSQL
- Redis
- Docker

In order to get things up and running:
#1 Navigate to the `docker` folder. Copy and re-name the `sample.env` file to `.env`
#2 Enter missing credentials (AWS keys). The email logging functionality isn't built yet, so you don't have to bother with those variables...
#3 Open a terminal, navigate into the `docker` folder, and enter
```
    docker-compose up -d
```
    This should get you up and running. You may want to
```
    docker exec -it docker_postgres_1 bash
    psql -U crawl -d public
    \dt
```
    to make sure that the postres entrypoint ran and created the resources in the `docker/postgres/init.sql` file.
    If that didn't, open a terminal and run
    `docker exec -it docker_postgres_1 bash -c "psql -U crawl -d public -c '\\i /docker-entrypoint-initdb.d/init.sql'"`
#4 If you have configured and started the thing properly, you should be able to observe the logs in
    - `docker/log/[scheduler|worker]/*.log
    - docker-compose logs
    and wait for the file `app/special_file.json` to be created. It will contain an object reflecting summarized data from some API responses that probably won't be working for much longer...

I would have liked to add things like a Slack webhook and an Email handler for the logs, as well as created a proxy IP address rotation service and set up a Graphite instance to monitor the app with, but that may be for another day...

Currently built on `docker-compose`, this can be scaled manually or adjusted to use Docker Swarm for a lightweight, distributed solution (I've not done that yet, technically, so instructions on how to use Swarm are forthcoming :D ).
I'm using Redis as a message broker instead of something like RabbitMQ because I like how Redis handles streams (even though you have to jump through some silly hoops to make it work with Python sometimes - I need to write a class on top of the redis library to make a few things easier...)

When moving records out of Redis to save space, wherever possible I'll want to be using range search functionality because it's much closer to O(1) than searching for most recent records which is O(n). It's also non-blocking.

When new workers are added, the scheduler or some other overlord should be present to register them with Redis and keep track of them. While I'm logging heartbeat things I'd want a sentinal service watching to make sure things were normal (e.g. We should have an average of "X" attempts to refresh manifests over a certain period - we just fell below threshold "Y").

I didn't use something like Airflow for this because I think it is better for batch jobs, not neceesarily handling the demands of a crawl service.

There is no indexing on the Postgres tables - I know... But it's a quick and dirty implementation, and I would also look into using a version of Postgres that's optimized for time-series (e.g. Timescale). Also, if this were a long term fixture, the `crawl_schedule` table would be a staging area, not a repository. As soon as a batch of jobs is identified as being done, we'll move them out of `crawl_schedule` and into the `crawl_log`.

when logging workers, I also might prefer to have each worker log their own file named after the ip address they are working on or some other feature; maybe something more descriptive such as the geographic area of the proxy they are using, and then their ip/proxy address.

Long term, S3 objects would also be compressed.

