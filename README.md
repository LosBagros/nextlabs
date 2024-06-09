# Nextlabs

There is multiple repositories for this project. This is server side of the project.

Frontend: https://github.com/LosBagros/nextlabs-website

## Setup

```
git clone https://github.com/LosBagros/nextlabs
cd nextlabs
git clone https://github.com/LosBagros/nextlabs-website nextauth
```

Copy .env.example to .env and fill it with your data.

Do the same in `/nextauth` directory.

Set up your domains in `/monitoring/Caddyfile`

Ports 80 and 443 must be free and exposed.

## Docker setup

Install docker https://docs.docker.com/engine/install/ubuntu/

Create network

```
docker network create nextlabs
```

Start project with

```
docker-compose up -d
```

## Monitoring

https://github.com/stefanprodan/dockprom/

## VPN

after several tries I am using solution from https://github.com/kylemanna/docker-openvpn/

## Build labs

```
cd labs
docker build -f Dockerfile.ubuntu -t nextlabs:ubuntu .
docker build -f Dockerfile.mariadb -t nextlabs:mariadb .
docker build -f Dockerfile.python -t nextlabs:python .
docker build -f Dockerfile.javascript -t nextlabs:javascript .
```
