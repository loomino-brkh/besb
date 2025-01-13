#!/bin/bash
source /app/support/venv/bin/activate
cd /app/main

# Run uvicorn with simplified logging
exec uvicorn main:app   --reload   --host 0.0.0.0   --port 8000   --workers 4   --log-level debug   --access-log   --use-colors   --reload-dir /app/main
