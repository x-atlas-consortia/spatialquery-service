#!/bin/bash

echo
echo "==================== SPATIALQUERY-SERVICE ===================="

if [[ "$1" != "start" && "$1" != "stop" && "$1" != "down" ]]; then
    echo "Unknown command '$1', specify one of the following: start|stop|down"
else
    if [ "$1" = "start" ]; then
        docker compose -f docker-compose.yml -p spatialquery-service up -d
    elif [ "$1" = "stop" ]; then
        docker compose -f docker-compose.yml -p spatialquery-service stop
    elif [ "$1" = "down" ]; then
        docker compose -f docker-compose.yml -p spatialquery-service down
    fi
fi