\connect public

create schema if not exists archive;

create table if not exists crawl_schedule (
    id bigserial,
    url text,
    headers text,
    cookies text,
    scheduled timestamp,
    version varchar(10),
    status smallint,
    attempts smallint,
    created_at timestamp,
    first_attempted timestamp,
    completed_at timestamp
);

create table if not exists archive.crawl_log (
    id bigint,
    url text,
    headers text,
    cookies text,
    scheduled timestamp,
    version varchar(10),
    status smallint,
    attempts smallint,
    created_at timestamp,
    first_attempted timestamp,
    completed_at timestamp
);
