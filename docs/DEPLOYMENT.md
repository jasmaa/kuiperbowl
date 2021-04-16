# Deployment

## Deploy on EC2

### Configure EC2 instance

  - Launch Amazon Linux instance of your choosing
  - Add HTTP to Inbound Security Rules with CIDR block `0.0.0.0/0`

### Install Git, Docker, and Docker Compose

    sudo yum update -y

    sudo yum install git docker -y
	
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose


### Clone repository

    git clone https://github.com/jasmaa/kuiperbowl.git

### Set up database

Start application:

    sudo docker-compose up --build -d

Get container id of `kuiperbowl_web`:

    sudo docker ps

Get a shell into running web process:

    sudo docker exec -it <CONTAINER ID> bash

Bootstrap database:

    # Download and convert Protobowl question dumps
    python ./scripts/pb_load.py

    # Bootstrap database
    python manage.py migrate
    python manage.py loaddata fixtures/default_rooms.json
    python manage.py loaddata fixtures/pbdump.json # This will take a while

### Launch application

    sudo docker-compose up --build -d
