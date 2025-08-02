-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS project1;
USE project1;

-- Table: user_agents
CREATE TABLE IF NOT EXISTS user_agents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_agent_string TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: log_entries
CREATE TABLE IF NOT EXISTS log_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45),
    timestamp DATETIME,
    method VARCHAR(10),
    path TEXT,
    status_code INT,
    bytes_sent INT,
    referrer TEXT,
    user_agent_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_agent_id) REFERENCES user_agents(id)
);
