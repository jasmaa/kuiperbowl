# Kuiperbowl

Real-time multiplayer quizbowl

![Quizbowl game page](docs/game.png)

## Local Development

Install and run [PostgreSQL](https://www.postgresql.org/) and [Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/) servers.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/).

Configure `.env` from `sample.env` with proper credentials.

Set up a virtual environment if desired:

```bash
uv venv
source .venv/bin/activate
```

Set up database:

```bash
uv run manage.py migrate
uv run manage.py loaddata fixtures/default_rooms.json
uv run manage.py loaddata fixtures/sample.json
```

Run dev server:

```bash
uv run manage.py runserver
```

### Entering Tossup Data

Tossup questions can be loaded from a fixture. Data can be downloaded from the [Protobowl DB dumps repo](https://github.com/neotenic/database-dumps) or custom made. See `fixtures/sample.json` for an example custom fixture.

```bash
# Load fixture data from PB db dump
uv run scripts/pb_load.py
uv run manage.py loaddata fixtures/pbdump.json
```

### Testing

Run unit tests with:

```bash
uv run pytest
```

## Deploying with Docker

### Set Up and Run

Configure `.env` with proper credentials.

Start application:

```bash
docker build -t kuiperbowl:latest .
docker run -p 127.0.0.1:8000:8000 kuiperbowl:latest
```

### Loading Data

```bash
# Get container name of kuiperbowl_web
docker ps

docker exec -it <CONTAINER ID> bash
python /usr/src/app/manage.py loaddata <FIXTURE PATH>
```