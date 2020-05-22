# Kuiperbowl

[![CircleCI](https://circleci.com/gh/jasmaa/kuiperbowl.svg?style=svg)](https://circleci.com/gh/jasmaa/kuiperbowl)

Real-time multiplayer quizbowl

![Comet logo](docs/comet.png)

## Local Development

Set up a virtual environment if desired and run:

    pip install -r "web/requirements.txt"
    python web/manage.py runserver

## Entering Tossup Data
Tossup questions can be loaded easily from a fixture. Data can be downloaded
from the [Protobowl DB dumps repo](https://github.com/neotenic/database-dumps)
or custom made. See `fixtures/sample.json` for an example custom fixture.

    # Load fixture data from PB db dump
    cd web
    python scripts/pb_load.py
    python manage.py loaddata fixtures/pbdump.json

## Using Docker

### Setup and Run
    docker-compose up --build

    # Get the ip for the app
    docker-machine ip

### Loading Data
    # Get container name of kuiperbowl_web
    docker ps

    docker exec -it [container name] bash
    python /usr/src/app/manage.py loaddata [fixture path]