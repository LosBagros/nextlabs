# Nextlabs - Server

## TODO:

- [] Make vpn vork
- [] Fastapi for controlling containers
- [] Vpn account management for users using api
- [] Documentation

`docker run -dit --name ubuntu-container --network nextlabs ubuntu`

## Cache

There is cache containers for reducing network usage

### Apt cache

Using Apt-Cacher NG

http://homelab:3142/

http://homelab :3142/acng-report.html/

#### Config for clients:

```bash
echo 'Acquire::HTTP::Proxy "http://apt-cache:3142";' >> /etc/apt/apt.conf.d/01proxy \
 && echo 'Acquire::HTTPS::Proxy "false";' >> /etc/apt/apt.conf.d/01proxy
```

### Pip cache

Using pypiserver

#### Config for clients:

```
printf "[global]\nextra-index-url = http://pypi-cache:8080/simple/\ntrusted-host = pypi-cache:8080" > /root/.pip/pip.conf
```

### NpmJS cache

Using verdaccio

```
npm set registry http://verdaccio:4873/
```

## Docker setup

```
docker network create nextlabs

# firewall for my local network
sudo iptables -I DOCKER-USER -i docker0 -d 192.168.0.0/24 -j DROP
```

## Monitoring

https://github.com/stefanprodan/dockprom/

## VPN

after seversl tries, I found that the best way to make vpn work is to use the following script:

```bash
wget https://git.io/vpn -O openvpn-install.sh
chmod +x openvpn-install.sh
sudo ./openvpn-install.sh
```
