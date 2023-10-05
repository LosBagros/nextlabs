#!/bin/bash

# Počet instancí
instances=2

# Základní porty pro databázi a phpMyAdmin
db_port_base=8306
pma_port_base=8080

# Vytvoření instancí
for i in $(seq 1 $instances); do
    db_port=$(($db_port_base + $i))
    pma_port=$(($pma_port_base + $i))

    # Spuštění instancí MariaDB a phpMyAdmin s unikátními porty
    docker run -d \
        --name databaze$i \
        -e MYSQL_ROOT_PASSWORD=tajnyheslo \
        -e MYSQL_DATABASE=Pizzerie \
        -e MYSQL_USER=user \
        -e MYSQL_PASSWORD=password \
        -p $db_port:3306 \
        -v ./pizzerie.sql:/docker-entrypoint-initdb.d/pizzerie.sql \
        mariadb:latest

    docker run -d \
        --name phpmyadmin$i \
        -e PMA_HOST=databaze$i \
        -e PMA_USER=user \
        -e PMA_PASSWORD=password \
        -e PMA_PORT=3306 \
        -p $pma_port:80 \
        phpmyadmin/phpmyadmin:latest
done
