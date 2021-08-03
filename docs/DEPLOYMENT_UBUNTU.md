# Ubuntu Deployment

Deployment instructions for Ubuntu 20.04 on Digital Ocean.


## Set up Postgres

Install Postgresql:

```
apt-get install postgresql postgresql-contrib libpq-dev
```

Set up user with password:

```
sudo -u postgres psql
ALTER USER postgres PASSWORD '<INSERT DB PASS>';
```

Create database:

```
sudo -u postgres createdb <INSERT DB NAME>
```


## Set up Redis

```
sudo apt install redis-server
```


## Set up web app

Clone repo to `/opt` and enter repo root:

```
cd /opt
git clone https://github.com/jasmaa/kuiperbowl.git
cd kuiperbowl
```

Install Python dependencies:

```
apt-get install python3-pip python-is-python3
pip install -r "requirements.txt"
```

Create `web/.env.local` from `.env` and populate with credentials.

Bootstrap the database:

**NOTE**: `pb_load.py` script may fail due to memory limitations. This
can be fixed by running the script locally and transferring
`fixtures/pbdump.json` to the server using SFTP.

```
# Download and convert Protobowl question dumps
python ./scripts/pb_load.py

# Bootstrap database
python manage.py migrate
python manage.py loaddata fixtures/default_rooms.json
python manage.py loaddata fixtures/pbdump.json # This will take a while
```

Set up static assets:

```
python manage.py collectstatic --noinput --clear
```


## Set up Nginx

Adapted from
[Digital Ocean's Nginx guide](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-20-04)
and [Django's Nginx guide](https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html).

Install Nginx:

```
sudo apt install nginx
```

Copy `docs/kuiperbowl_nginx.conf` into `etc/nginx/sites-available`.

Symlink to sites enabled:

```
sudo ln -s /etc/nginx/sites-available/kuiperbowl_nginx.conf /etc/nginx/sites-enabled/
```

Restart Nginx:

```
sudo systemctl restart nginx
```


## Set up web systemd service

Copy `docs/kuiperbowl.service` into `/etc/systemd/system`.

Reload systemd and start server with:

```
systemctl daemon-reload
systemctl enable kuiperbowl.service
systemctl start kuiperbowl.service
```


## Set up DNS

Add the following `A` records on DNS host:

- Host: `@`, Value: <IP ADDRESS>
- Host: `www`, Value: <IP ADDRESS>


## Set up Certbot

Adapted from
[Digital Ocean's Certbot guide](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-20-04).

Install Certbot:

```
sudo apt install certbot python3-certbot-nginx
```

Get certificate:

```
sudo certbot --nginx -d kuiperbowl.com -d www.kuiperbowl.com

# Choose Redirect(2) when prompted
```

Enable auto-renewal:

```
sudo systemctl status certbot.timer
```