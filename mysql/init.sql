-- init.sql
CREATE DATABASE IF NOT EXISTS cc_project;
USE cc_project;

CREATE TABLE IF NOT EXISTS history (
    details JSON,
    bill float
);

CREATE TABLE IF NOT EXISTS items (
    itemID VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    price FLOAT,
    quantity INT
);


