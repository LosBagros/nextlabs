FROM ubuntu	

# NEXTLABS
LABEL project="nextlabs"
LABEL ssh=1

RUN apt update && apt install --no-install-recommends -y \
    nano \
    vim \
    curl \
    wget \
    iputils-ping \
    git \
    build-essential \
    nodejs \
    npm \
    openssh-server
    
RUN apt clean && rm -rf /var/lib/apt/lists/* 
RUN echo 'Acquire::HTTP::Proxy "http://apt-cache:3142";' >> /etc/apt/apt.conf.d/01proxy \
    && echo 'Acquire::HTTPS::Proxy "false";' >> /etc/apt/apt.conf.d/01proxy

RUN npm set registry http://npm-cache:8081/repository/npm/

RUN mkdir /var/run/sshd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

WORKDIR /workspace

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]