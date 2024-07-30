#!/bin/sh
exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}

# This script starts the Uvicorn server to run the FastAPI application.
