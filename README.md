# Nextlabs - Server

`docker run -dit --name ubuntu-container --network nextlabs ubuntu`

## Cache

There is cache containers for reducing network usage

### Apt cache

Using Apt-Cacher NG

http://homelab:3142/

http://homelab  :3142/acng-report.html/

#### Config for clients:

```bash
echo 'Acquire::HTTP::Proxy "http://apt-cache:3142";' >> /etc/apt/apt.conf.d/01proxy \
 && echo 'Acquire::HTTPS::Proxy "false";' >> /etc/apt/apt.conf.d/01proxy
```

### Pip cache

Using pypiserver


#### Config for clients:

```
echo "[global]
extra-index-url = http://pypi-cache:8080/simple/
trusted-host = pypi-cache:8080" >> /root/.pip/pip.conf
```


### NpmJS cache

Using verdaccio

```
npm set registry http://localhost:4873/
```