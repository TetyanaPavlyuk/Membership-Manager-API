#!/bin/sh
echo "Creating new migrations..."
alembic revision --autogenerate -m "Autogenerate migration" --version-path=alembic/versions
if [ $? -eq 0 ]; then
  echo "Migration was created successfully"
else
  echo "Migration creation failed"
  exit 1
fi
