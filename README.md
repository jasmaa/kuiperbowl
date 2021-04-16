# Kuiperbowl

[![CircleCI](https://circleci.com/gh/jasmaa/kuiperbowl.svg?style=svg)](https://circleci.com/gh/jasmaa/kuiperbowl)

Real-time multiplayer quizbowl

![Comet logo](docs/comet.png)

## Local Development

Configure `.env` with proper credentials.

Set up a virtual environment if desired and run:

    cd web

    pip install -r "requirements.txt"
    python manage.py migrate
    python manage.py loaddata fixtures/default_rooms.json
    python manage.py loaddata fixtures/sample.json

    python manage.py runserver

## Entering Tossup Data

Tossup questions can be loaded easily from a fixture. Data can be downloaded
from the [Protobowl DB dumps repo](https://github.com/neotenic/database-dumps)
or custom made. See `fixtures/sample.json` for an example custom fixture.

    # Load fixture data from PB db dump
    cd web
    python scripts/pb_load.py
    python manage.py loaddata fixtures/pbdump.json

## Using Docker

### Set Up and Run

Configure `.env` with proper credentials.

Start application:

    docker-compose up --build

### Loading Data

    # Get container name of kuiperbowl_web
    docker ps

    docker exec -it <CONTAINER ID> bash
    python /usr/src/app/manage.py loaddata <FIXTURE PATH>