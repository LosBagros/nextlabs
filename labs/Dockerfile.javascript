FROM ubuntu:20.04	

# NEXTLABS
LABEL project="nextlabs"

RUN apt update && apt install -y \
    nano \
    vim \
    curl \
    wget \
    iputils-ping \
    git \
    build-essential \
    nodejs \
    npm \
    openssh-server \
    
RUN apt-get clean && rm -rf /var/lib/apt/lists/* 
RUN echo 'Acquire::HTTP::Proxy "http://apt-cache:3142";' >> /etc/apt/apt.conf.d/01proxy \
    && echo 'Acquire::HTTPS::Proxy "false";' >> /etc/apt/apt.conf.d/01proxy

RUN npm set registry http://verdaccio:4873/

RUN mkdir /var/run/sshd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

WORKDIR /workspace

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]