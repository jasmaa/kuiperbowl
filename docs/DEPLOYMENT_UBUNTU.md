# Ubuntu Deployment

Deployment instructions for Ubuntu 20.04 on Digital Ocean.


## Set up Postgres

Install Postgresql:

```bash
apt-get install postgresql postgresql-contrib libpq-dev
```

Set up user with password:

```bash
sudo -u postgres psql
ALTER USER postgres PASSWORD '<INSERT DB PASS>';
```

Create database:

```bash
sudo -u postgres createdb kuiperbowl
```


## Set up Redis

```bash
sudo apt install redis-server
```


## Set up web app

Clone repo to `/opt` and enter repo root:

```bash
cd /opt
git clone https://github.com/jasmaa/kuiperbowl.git
cd kuiperbowl
```

Install UV:

```bash
export UV_INSTALL_DIR="/usr/local/bin/uv"
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install Python dependencies:

```bash
apt-get install python3-pip python-is-python3
```

Create `.env` from `sample.env` and populate with credentials.

Bootstrap the database:

**NOTE**: `pb_load.py` script may fail due to memory limitations. This
can be fixed by running the script locally and transferring
`fixtures/pbdump.json` to the server using SFTP.

```bash
# Download and convert Protobowl question dumps
uv run ./scripts/pb_load.py

# Bootstrap database
uv run manage.py migrate
uv run manage.py loaddata fixtures/default_rooms.json
uv run manage.py loaddata fixtures/pbdump.json # This will take a while
```

Set up static assets:

```bash
uv run manage.py collectstatic --noinput --clear
```


## Set up Nginx

Adapted from
[Digital Ocean's Nginx guide](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-20-04)
and [Django's Nginx guide](https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html).

Install Nginx:

```bash
sudo apt install nginx
```

Copy `docs/kuiperbowl_nginx.conf` into `/etc/nginx/sites-available`.

```bash
cp docs/kuiperbowl_nginx.conf /etc/nginx/sites-available/kuiperbowl_nginx.conf
```

Symlink to sites enabled:

```bash
sudo ln -s /etc/nginx/sites-available/kuiperbowl_nginx.conf /etc/nginx/sites-enabled/
```

Restart Nginx:

```bash
sudo systemctl restart nginx
```

## Set up web systemd service

Copy `docs/kuiperbowl.service` into `/etc/systemd/system`:

```bash
cp docs/kuiperbowl.service /etc/systemd/system/kuiperbowl.service
```

Reload systemd and start server with:

```bash
sudo systemctl daemon-reload
sudo systemctl enable kuiperbowl.service
sudo systemctl start kuiperbowl.service
```

Check status of service with:

```bash
sudo systemctl status kuiperbowl.service

# or

sudo journalctl -u kuiperbowl.service | tail
```

## Set up DNS

Add the following `A` records on DNS host:

- Host: `@`, Value: <IP ADDRESS>
- Host: `www`, Value: <IP ADDRESS>


## Set up Certbot

Adapted from
[Digital Ocean's Certbot guide](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-20-04).

Install Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
```

Get certificate:

```bash
sudo certbot --nginx -d kuiperbowl.com -d www.kuiperbowl.com

# Choose Redirect(2) when prompted
```

Enable auto-renewal:

```bash
sudo systemctl status certbot.timer
```


## Set up daily reboot

Edit crontab with:

```bash
crontab -e
```

And add:

```bash
0 0 * * * reboot
```