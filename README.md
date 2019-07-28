# Kuiperbowl
![Build badge](https://travis-ci.org/jasmaa/kuiperbowl.svg?branch=master)

![Comet logo](./comet.png)

Real-time multiplayer quizbowl. Functionally similar to Protobowl but significantly worse.

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