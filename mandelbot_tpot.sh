#!/bin/bash

ACTION=$1
IMAGE="mandelbot/tpot"

if [[ -z $ACTION ]]; then
    echo "Usage: mandelbot_tpot.sh [build/run]"
    exit 1
fi

if [[ $ACTION = 'build' ]];
then
    echo "Building Docker image: $IMAGE"
    docker build . -t $IMAGE
elif [[ $ACTION = 'run' ]];
then
    echo "Running flask"
    docker run -p 8080:8080 -it $IMAGE
else
    echo "Usage: mandelbot_tpot.sh [build/run]"
fi