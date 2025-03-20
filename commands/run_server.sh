#!/bin/sh
echo "Starting server..."
uvicorn app.main:server.app --host $BACKEND_HOST --port $BACKEND_PORT
