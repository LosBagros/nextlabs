FROM alpine:latest
RUN apk add --no-cache openvpn

FROM alpine:latest

RUN apk add --update easy-rsa && \
    ln -s /usr/share/easy-rsa/easyrsa /usr/local/bin

WORKDIR /etc/openvpn

# Initialize the PKI directory
RUN easyrsa init-pki

# Generate a new CA
RUN easyrsa build-ca nopass

# Generate server key and certificate
RUN easyrsa gen-req server nopass && \
    easyrsa sign-req server server

# Generate Diffie-Hellman parameters (may take a long time)
RUN easyrsa gen-dh

# Configuration and credential files
COPY ./server.conf /etc/openvpn/server.conf

CMD ["openvpn", "/etc/openvpn/server.conf"]
