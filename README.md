# Kuiperbowl

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
  - `python manage.py collectstatic`
  - Run `sudo daphne -p 8001 quizbowl.asgi:channel_layer` and `python manage.py runworkers` on separate screens
  - Replace `/etc/nginx/nginx.conf` with the `nginx.conf` in this repo
  