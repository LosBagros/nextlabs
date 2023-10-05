# Říjen

Docker CLI
- Vytvoření kontejneru
- Start / Stop kontejneru
- Snapshot kontejneru
- Spuštění příkazu
- Logy
- Kopírování souborů
- Uspěšné vytvoření a spuštění 3 různých Docker kontejnerů

## Vytvoření kontejneru

Nginx

```bash
docker run --name webserver -d -p 8080:80 nginx
```

MariaDB

```bash
docker run --name databaze -d -e MYSQL_ROOT_PASSWORD=tajnyheslo -p 8306:3306 mariadb
```

exposnu port na 8306 kdyby nahodou jela db na lokalnim portu
pak se na to da pripojit pres basic mysql klient 
`mysql -h 127.0.0.1 -P 3306 -u root -ptajnyheslo`

## Start / Stop kontejneru

### Start
```bash
docker start webserver
docker start databaze
```

### Stop
```bash
docker stop webserver
docker stop databaze
```

## Snapshot kontejneru
```bash
docker commit webserver webserver-snapshot
docker commit databaze databaze-snapshot
```

## Spuštění příkazu v kontejneru
```bash
docker exec webserver cat /etc/nginx/nginx.conf
```

## Logy
```bash
docker logs webserver
docker logs databaze
```

## Kopírování souborů

```bash
docker cp webserver:/etc/nginx/nginx.conf nginx.conf
docker cp nginx.conf webserver:/etc/nginx/nginx.conf
```

```bash
docker cp index.html webserver:/usr/share/nginx/html/
```

## Vytvoření a spuštění 3 různých Docker kontejnerů
```bash
docker run --name webserver -d -p 8080:80 nginx
docker run --name webserver2 -d -p 8081:80 nginx
docker run --name webserver3 -d -p 8082:80 nginx
```

## Vypis bezicich kontejneru
```bash
docker ps
```	

## Vypis vsech kontejneru
```bash
docker ps -a
```

## Vypis vsech obrazu
```bash
docker images
```

## Vycisteni vseho
```bash
docker system prune -a
```
