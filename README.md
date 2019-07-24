# Kuiperbowl
![Build badge](https://travis-ci.org/jasmaa/kuiperbowl.svg?branch=master)

Real-time multiplayer quizbowl. Functionally similar to Protobowl but significantly worse.

## Setup
  - `pip install -r "requirements.txt"`
    - if on Windows, also install `pywin32`
  - `python manage.py migrate`

## Entering in Tossup Data
Tossup questions can be loaded easily from a fixture. Data can be downloaded
from the [Protobowl DB dumps repo](https://github.com/neotenic/database-dumps)
or custom made.

  - Creating Fixture Data
    - Load data from PB: `python scripts/pb_load.py`
  - Loading Data
    - Put fixture in `/fixtures`
	- `python manage.py loaddata fixtures/<fixture name>`

Sample fixture:

```
[
  {
    "model": "game.question",
    "pk": 1,
    "fields": {
      "category": "Fine Arts",
	  "difficulty": "HS",
	  "points": 20,
	  "content": "What do you call a ursine espresso drinker?"
      "answer": "Coffee bear",
	  "duration": 21.8
    }
  },
  ...
]
```

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