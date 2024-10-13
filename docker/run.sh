#!/bin/bash

IMAGE_NAME="bgm-gen"
CONTAINER_NAME="bgm-gen-container"

DOCKER_OPTIONS="
    --rm
    --name $CONTAINER_NAME
    -v /mnt/d/work/BGM-gen/main:/app
    --env-file .env
    $IMAGE_NAME
"
# TEST_CMD="python src/gen_data.py"
# TEST_CMD="python src/modify_video.py"
# TEST_CMD="python src/upload_video.py"

TEST_CMD="python src/main.py"

if [ "$1" != "1" ]; then
    docker run $DOCKER_OPTIONS $TEST_CMD
else
    docker run -it $DOCKER_OPTIONS /bin/bash
fi
