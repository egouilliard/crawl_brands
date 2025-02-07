#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  sleep 2
done
echo "PostgreSQL is up and running."

# Run the Python script to test DB connection
python /app/src/main.py
