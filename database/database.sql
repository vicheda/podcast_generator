CREATE DATABASE IF NOT EXISTS podcastgenerator;


USE podcastgenerator;


DROP TABLE IF EXISTS queries;
DROP TABLE IF EXISTS articles;

CREATE TABLE queries
(
    queryid           int not null AUTO_INCREMENT,
    querytext         varchar(256) not null,
    status            varchar(256) not null,  -- uploaded, completed, error, processing...
    textkey           varchar(256) not null,
    scriptkey         varchar(256) not null,
    audiokey          varchar(256) not null,  -- results filename in S3 bucket
    PRIMARY KEY (queryid)
);


ALTER TABLE queries AUTO_INCREMENT = 10001; -- starting value