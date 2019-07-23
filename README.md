# Kuiperbowl
![Build badge](https://travis-ci.org/jasmaa/kuiperbowl.svg?branch=master)

Real-time multiplayer quizbowl. Functionally similar to Protobowl but significantly worse.

## Setup
  - `pip install -r "requirements.txt"`
    - if on Windows, also install `pywin32`
  - `python manage.py migrate`
  - `python manage.py loaddata <question fixture name>`

## Run

### Development
  - `python manage.py runserver`

### Production
  - Make sure in `quizbowl/settings.py`
    - `SECRET_KEY = <new secret key>`
    - `DEBUG = False`
	- `ALLOWED_HOSTS = [<hostnames>]`
  - `python manage.py collectstatic`
  - Run `sudo daphne -p 8001 quizbowl.asgi:channel_layer` and `python manage.py runworker` on separate screens
  - Paste blocks from `nginx.conf` in this repo to `/etc/nginx/nginx.conf`
  