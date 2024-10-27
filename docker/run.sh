#!/bin/bash

IMAGE_NAME="bgm-gen"
CONTAINER_NAME="bgm-gen-container"

DOCKER_OPTIONS="
    --rm
    --name $CONTAINER_NAME
    -v /mnt/d/work/BGM-gen/main:/app
    -v /mnt/d/work/BGM-gen/thumbnail:/thumbnail
    -v /mnt/c/Users/kamiy/Downloads:/downloads
    --env-file .env
    -e PYTHONPATH=/app/src
    $IMAGE_NAME
"

if [ "$1" == "t" ]; then
    TEST_CMD="pytest"
    echo "Running tests with command: $TEST_CMD"
    docker run $DOCKER_OPTIONS $TEST_CMD
elif [ "$1" != "1" ]; then
    # TEST_CMD="python src/gen_data.py"
    # TEST_CMD="python src/modify_video.py"
    # TEST_CMD="python src/upload_video.py"

    TEST_CMD="python src/main.py"

    docker run $DOCKER_OPTIONS $TEST_CMD
else
    docker run -it $DOCKER_OPTIONS /bin/bash
fi
