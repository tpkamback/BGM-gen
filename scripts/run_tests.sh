#!/bin/bash

# run pytests
./docker/run.sh t
RESULT=$?

if [ $RESULT -ne 0 ]; then
    echo "Tests failed with exit code $RESULT"
    exit 1
fi

echo "Tests passed."
exit 0
