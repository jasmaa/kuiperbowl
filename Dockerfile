FROM python:3.13-alpine

RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev libffi-dev bash

RUN python3 -m pip install --upgrade pip

# Install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /usr/src/app

COPY . .

RUN uv run manage.py collectstatic --noinput --clear

ENTRYPOINT uv run daphne -b 0.0.0.0 -p 8000 quizbowl.asgi:application