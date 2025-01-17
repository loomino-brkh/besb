#!/bin/bash
source /app/support/venv/bin/activate
cd /app/main

# Run uvicorn with enhanced verbose logging
exec uvicorn main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level debug \
    --use-colors \
    --reload-dir /app/main \
    --access-log \
    --log-config /app/main/logging_config.json
