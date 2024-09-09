CREATE DATABASE IF NOT EXISTS mmbot;

USE mmbot;

CREATE TABLE IF NOT EXISTS events (
    uuid VARCHAR(36) PRIMARY KEY,
    name VARCHAR(500),
    description TEXT,
    start_time DATETIME,
    end_time DATETIME,
    location VARCHAR(255),
    op_id INT,
    op_name VARCHAR(255),
    original_channel_id INT,
    event_id INT,
    event_forum_url VARCHAR(255),
    event_forum_id INT,
    status VARCHAR(20)
);
