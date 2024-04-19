# Dockerfile for MySQL
FROM mysql:latest

# Copy the initialization script to the Docker entrypoint init directory
COPY init.sql /docker-entrypoint-initdb.d/
