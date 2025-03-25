#!/bin/sh
echo "Starting tests..."
pytest --maxfail=1 --disable-warnings
TEST_RESULT=$?
echo "Tests finished with exit code: $TEST_RESULT"
exit $TEST_RESULT
