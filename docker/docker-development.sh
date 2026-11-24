#!/bin/bash

echo
echo "==================== SPATIALQUERY-SERVICE ===================="

# Stage a fresh copy of app/ into the build context
function stage_source() {
    if [ -d "spatialquery-service/app" ]; then
        rm -rf spatialquery-service/app
    fi
    cp -r ../app spatialquery-service/

    # Generate BUILD at the repo root, then stage VERSION and BUILD into the build context
    (cd .. && ./generate-build-version.sh)
    cp ../VERSION spatialquery-service/
    cp ../BUILD spatialquery-service/
}

if [[ "$1" != "check" && "$1" != "config" && "$1" != "build" && "$1" != "start" && "$1" != "stop" && "$1" != "down" ]]; then
    echo "Unknown command '$1', specify one of the following: check|config|build|start|stop|down"
else
    if [ "$1" = "check" ]; then
        if [ ! -e ../app/instance/app.cfg ]; then
            echo "Missing file (relative to docker/): ../app/instance/app.cfg"
            exit 1
        fi
        echo 'Checks complete, all good :)'
    elif [ "$1" = "config" ]; then
        docker compose -f docker-compose.yml -p spatialquery-service config
    elif [ "$1" = "build" ]; then
        stage_source
        docker compose -f docker-compose.yml -p spatialquery-service build --no-cache
    elif [ "$1" = "start" ]; then
        docker compose -f docker-compose.yml -p spatialquery-service up -d
    elif [ "$1" = "stop" ]; then
        docker compose -f docker-compose.yml -p spatialquery-service stop
    elif [ "$1" = "down" ]; then
        docker compose -f docker-compose.yml -p spatialquery-service down
    fi
fi