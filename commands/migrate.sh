#!/bin/sh
echo "Applying migrations"
alembic upgrade head
if [ $? -eq 0 ]; then
  echo "Migrations applied successfully"
else
  echo "Migration application failed"
  exit 1
fi
