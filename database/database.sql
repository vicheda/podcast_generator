CREATE DATABASE IF NOT EXISTS podcastgenerator;


USE podcastgenerator;


DROP TABLE IF EXISTS queries;
DROP TABLE IF EXISTS articles;

CREATE TABLE queries
(
    queryid           int not null AUTO_INCREMENT, -- unique identifier for each request.
    querytext         varchar(256) not null, -- user’s search query (i.e. “Technology, Coffee, etc.”)
    status            varchar(256) not null,  -- uploaded, completed, error, processing...
    textkey           varchar(256) not null DEFAULT '', -- S3 bucket key for the combined article content .txt file
    scriptkey         varchar(256) not null DEFAULT '', -- S3 bucket key for the generated podcast script .txt file (the summarize of all articled fetched from the Guardian API)
    audiokey          varchar(256) not null DEFAULT '',  -- S3 bucket key for the generated audio file .mp3
    PRIMARY KEY (queryid)
);

ALTER TABLE queries AUTO_INCREMENT = 10001; -- starting value

CREATE TABLE articles
(
    articleid      int not null AUTO_INCREMENT,
    url             varchar(256) not null,
    headline       varchar(128) not null,
    querytext    varchar(128) not null,
    queryid    int not null,
    PRIMARY KEY (articleid),
    FOREIGN KEY (queryid) REFERENCES queries(queryid)
);

ALTER TABLE articles AUTO_INCREMENT = 20001;
