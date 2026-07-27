#!/bin/bash
set -e

echo "=== Running Database Migrations ==="
alembic upgrade head

echo "=== Starting Application ==="
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
