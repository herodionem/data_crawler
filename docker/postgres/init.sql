\connect public;

create schema if not exists archive;

create table if not exists manifest_log (
    id bigserial primary key,
    filename text,
    status smallint,
    attempts smallint,
    created_at timestamp,
    last_attempt timestamp
);

create table if not exists crawl_schedule (
    id bigserial primary key,
    service text,
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
    service text,
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

create table if not exists crawl_results (
    id serial primary key,
    url text,
    response text
);

create table if not exists analyze_words (
    id serial primary key,
    word text,
    opt bool
);
