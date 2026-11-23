# spatialquery-service

Flask API that runs SpatialQuery analyses on spatially resolved HuBMAP datasets and returns JSON.

To call the service, see [API.md](API.md).

## Run with Docker

1. Copy `app/instance/app.cfg.example` to `app/instance/app.cfg` and fill in the client ID, secret, and the entity-api and ingest-api URLs (full URLs, no trailing slash).
2. From `docker/`:

        ./docker-development.sh check
        ./docker-development.sh build
        ./docker-development.sh start

Use `stop` or `down` to stop it. The container mounts `/hive` read-only, so the paths returned by ingest-api must exist on the host.

## Run locally

Needs Python 3.10+ and a C++ compiler.

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r app/requirements.txt
    cd app
    python3 app.py