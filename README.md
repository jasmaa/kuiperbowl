# Kuiperbowl

Real-time multiplayer quizbowl. Functionally similar to Protobowl but significantly worse.

## Setup
  - `pip install -r "requirements.txt"`
    - if on Windows, also install `pywin32`
  - `python manage.py migrate`
  - `python manage.py loaddata <question fixture name>`

## Run

### Using built-in Django test server
  - `python manage.py runserver`

### Using Daphne
  - `sudo daphne -p 8001 quizbowl.asgi:channel_layer`
  - `python manage.py runworkers`
  - Configure `nginx.conf` properly