# Kuiperbowl
![Build badge](https://travis-ci.org/jasmaa/kuiperbowl.svg?branch=master)
![Comet logo](https://github.com/jasmaa/kuiperbowl/blob/docker/game/static/game/comet.png)

Real-time multiplayer quizbowl. Functionally similar to Protobowl but significantly worse.

## Setup
  - `pip install -r "requirements.txt"`
    - if on Windows, also install `pywin32`
  - `python manage.py migrate`

## Run
  - Development
    - Run `python manage.py runserver`

  - Production
    - Make sure in `quizbowl/settings.py`:
      - `SECRET_KEY = <new secret key>`
      - `DEBUG = False`
	  - `ALLOWED_HOSTS = [<hostnames>]`
    - `python manage.py collectstatic`
    - `sudo daphne -p 8001 quizbowl.asgi:channel_layer` and `python manage.py runworker` on separate terminal screens
    - Paste blocks from `nginx.conf` in this repo to `/etc/nginx/nginx.conf`

## Entering Tossup Data
Tossup questions can be loaded easily from a fixture. Data can be downloaded
from the [Protobowl DB dumps repo](https://github.com/neotenic/database-dumps)
or custom made. See `fixtures/sample.json` for an example custom fixture.

```
# Load fixture data from PB db dump
python scripts/pb_load.py
python manage.py loaddata fixtures/pbdump.json
```

## Using Docker

### Setup and Run
```
docker-compose up --build
docker-machine ip
# Site will be hosted at <docker machine ip>:8000`
```

### Loading Data
```
docker ps
# Get container id of kuiperbowl_web

docker exec -t -i <container id> bash
python manage.py loaddata <fixture path>
```