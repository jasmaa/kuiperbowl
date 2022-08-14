# Kuiperbowl

Real-time multiplayer quizbowl

![Quizbowl game page](docs/game.png)

## Local Development

Configure `web/.env.local` from `.env` with proper credentials.

Set up a virtual environment if desired and run:

```
cd web

pip install -r "requirements.txt"
python manage.py migrate
python manage.py loaddata fixtures/default_rooms.json
python manage.py loaddata fixtures/sample.json

# Start redist cache for channel layer
# https://channels.readthedocs.io/en/stable/tutorial/part_2.html#enable-a-channel-layer
docker run -p 6379:6379 -d redis:5

python manage.py runserver --insecure
```

## Entering Tossup Data

Tossup questions can be loaded easily from a fixture. Data can be downloaded
from the [Protobowl DB dumps repo](https://github.com/neotenic/database-dumps)
or custom made. See `fixtures/sample.json` for an example custom fixture.

```
# Load fixture data from PB db dump
cd web
python scripts/pb_load.py
python manage.py loaddata fixtures/pbdump.json
```

## Using Docker

### Set Up and Run

Configure `.env` with proper credentials.

Start application:

```
docker-compose up --build
```

### Loading Data

```
# Get container name of kuiperbowl_web
docker ps

docker exec -it <CONTAINER ID> bash
python /usr/src/app/manage.py loaddata <FIXTURE PATH>
```