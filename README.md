# Polyfeed_Backend

## Setting up

1. Install python3.8
2. if not installed using pyenv
3. Install pip
4. pip install requirements.txt

newgrp docker

## Deployment

### build image

```
Dev:
docker image build --tag polyfeed-backend .

Production:
docker image build --tag polyfeed-backend-prod .
```

### run container

```
docker run -d -p 8000:8000 polyfeed-backend

docker run -d -p 8002:8002 polyfeed-backend-prod

```

### Apache Http server config

added the follow configuration on /etc/httpd/conf/httpd.conf

```
<VirtualHost *:80>
    ServerName polyfeed.com.au

    DocumentRoot /var/www/html

    # Serve /static directly
    Alias /static /var/www/html/static

    # Proxy all other requests
    ProxyPreserveHost On
    # database dashboard
    ProxyPass /phpMyAdmin !
    # dashboard
    ProxyPass /dashboard !
    ProxyPass / http://localhost:8000/
    ProxyPassReverse / http://localhost:8000/

</VirtualHost>
```

### reload the httpd

sudo systemctl restart httpd
