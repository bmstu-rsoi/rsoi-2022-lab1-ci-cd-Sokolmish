-- file: 10-create-user-and-db.sql
CREATE DATABASE persons;
CREATE ROLE program WITH PASSWORD 'test';
GRANT ALL PRIVILEGES ON DATABASE persons TO program;
ALTER ROLE program WITH LOGIN;

CREATE TABLE persons (
    "id" serial PRIMARY KEY,
    "name" varchar(50) NOT NULL,
    "age" int,
    "address" varchar(100),
    "work" varchar(50)
)
