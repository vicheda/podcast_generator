CREATE DATABASE IF NOT EXISTS articles_db;

USE articles_db;

CREATE TABLE IF NOT EXISTS requested_articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_id VARCHAR(255) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    url TEXT,
);
