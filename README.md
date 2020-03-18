# Kuiperbowl

[![CircleCI](https://circleci.com/gh/jasmaa/kuiperbowl.svg?style=svg)](https://circleci.com/gh/jasmaa/kuiperbowl)

Real-time multiplayer quizbowl

![Comet logo](./comet.png)

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


## Entering Tossup Data
Tossup questions can be loaded easily from a fixture. Data can be downloaded
from the [Protobowl DB dumps repo](https://github.com/neotenic/database-dumps)
or custom made. See `fixtures/sample.json` for an example custom fixture.

    # Load fixture data from PB db dump
    python scripts/pb_load.py
    python manage.py loaddata fixtures/pbdump.json