# https://razinj.dev/build-and-run-apt-cacher-ng-proxy-in-docker/
FROM ubuntu

VOLUME ["/var/cache/apt-cacher-ng"]

RUN apt-get update -y && \
    apt-get install apt-cacher-ng -y && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 3142

CMD chmod 777 /var/cache/apt-cacher-ng && \
    echo "PassThroughPattern: .*" >> /etc/apt-cacher-ng/acng.conf && \
    /etc/init.d/apt-cacher-ng start && \
    tail -f /var/log/apt-cacher-ng/*