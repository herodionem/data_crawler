# data_crawler

Title (A Title Image too if possible…Edit them on canva.com if you are not a graphic designer.)
A Data Crawler Demo!


Description(Describe by words and images alike)
This application will consist of a collection of microservices which, when tied together, will A) gather some data from an API and do some arbitrary processing on them and B) find links on a website and do something with them, like store them for later, or something...

Demo(Images, Video links, Live Demo links)
Technologies Used
Python
S3
(Maybe) PostgreSQL
(Probably) Redis
Docker
EC2...?

I'll want to know how many times a particular job was tried
    -- different channels:
        -- new job
        -- failed job
        -- trying job
        -- job stats
* Make a note that when retrieving messages from redis it's better to retrieve based on time range bc it's non-blocking (i.e. faster!)
* In redis, you create groups that consume streams in a particular way.
    * Then you create consumers bound to a particular group and governed by the group's consumption configuration
    * In order to scale that, you'd need some sort of consumer overlord adding and removing consumers
* Would prefer to use time-series version of postgres
* when logging workers, I might have each worker log their own file named after the ip address they are working on or some other feature; maybe something more descriptive such as the geographic area of the proxy they are using, and then their ip/proxy address.
database with s3 object list
* Depending on how I wanted to scale this out I would probably use *async*=True for postgres connections.
* I didn't bother with any user management or security measures in the containers...
* The manifest would be compressed
* not sure why the docker image isn't install init sql script like it should - if you find you have no tables, just run
    `docker exec -it docker_postgres_1 bash -c "psql -U crawl -d public -c '\\i /docker-entrypoint-initdb.d/init.sql'"`
    and restart the scheduler
    `docker-compose py_scheduler`
* While I'm logging heartbeat things I'd want a sentinal service watching to make sure things were normal (e.g. We should have an average of "X" attempts to refresh manifests over a certain period - we just fell below threshold "Y")

Special Gotchas of your projects (Problems you faced, unique elements of your project)
Technical Description of your project like- Installation, Setup, How to contribute.