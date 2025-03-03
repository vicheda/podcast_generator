CREATE DATABASE IF NOT EXISTS podcastgenerator;


USE podcastgenerator;


DROP TABLE IF EXISTS queries;
DROP TABLE IF EXISTS articles;


CREATE TABLE articles
(
    articleid       int not null AUTO_INCREMENT,
    searchid        varchar(256) not null,
    text            varchar(256) not null,
    headline        varchar(64) not null,
    trailtext       varchar(256) not null,
    querytext       varchar(256) not null,
    PRIMARY KEY  (articleid),
    UNIQUE       (searchid)
);


ALTER TABLE articles AUTO_INCREMENT = 80001;  -- starting value


CREATE TABLE queries
(
    queryid           int not null AUTO_INCREMENT,
    querytext         varchar(256) not null,
    status            varchar(256) not null,  -- uploaded, completed, error, processing...
    audiokey          varchar(256) not null,  -- results filename in S3 bucket
    PRIMARY KEY (queryid)
);


ALTER TABLE queries AUTO_INCREMENT = 10001;  -- starting value