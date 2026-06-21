#!/bin/bash
set -e

# Setup environment variables or perform pre-flight checks here
echo "Starting ASTA1 Platform..."

# Hand off to the command passed via docker-compose
exec "$@"
