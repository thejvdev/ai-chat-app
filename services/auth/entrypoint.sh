#!/bin/bash
set -e

echo "Running migrations..."
alembic upgrade head

echo "Starting auth service..."
exec "$@"
