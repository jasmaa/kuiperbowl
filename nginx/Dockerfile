FROM nginx:1.12-alpine

RUN apk update && apk add openssl

# Create dummy cert
RUN mkdir /etc/letsencrypt
RUN mkdir /etc/letsencrypt/live
RUN mkdir /etc/letsencrypt/live/kuiperbowl.com
RUN openssl req -x509 -nodes -newkey rsa:1024 -days 1 -keyout '/etc/letsencrypt/live/kuiperbowl.com/privkey.pem' -out '/etc/letsencrypt/live/kuiperbowl.com/fullchain.pem' -subj '/CN=localhost'

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d