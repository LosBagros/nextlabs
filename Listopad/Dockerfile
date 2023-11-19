# Stažení základního obrazu Ubuntu
FROM ubuntu:latest AS base

# Nastavení argumentů
ARG USERNAME=default
ARG PASSWORD=secret
ARG VERSION=2.0

# Aktualizace systému
RUN apt-get update -y && apt-get upgrade -y

# Vytvoření uživatele s přijatými argumenty
RUN useradd -ms /bin/bash $USERNAME && echo "$USERNAME:$PASSWORD" | chpasswd

# Nastavení pracovního adresáře
WORKDIR /home/$USERNAME

# Mount souboru do kontejneru (soubor bude muset být připojen při spuštění kontejneru)
VOLUME ["/home/$USERNAME/data"]

# Otagování obrazu
LABEL description="Basic Ubuntu Image"
LABEL version="${VERSION}"

# Informační výstup
CMD ["echo", "Image was built successfully! "]
CMD ["echo", "Version: ${VERSION}"]


# Shell při spuštění kontejneru
CMD ["/bin/bash"]

# postavení docker image
# docker build -t ubuntuimage --build-arg USERNAME=bagros --build-arg PASSWORD=tajnyheslo .

# spuštění kontejneru Docker
# docker run -it -v "$(pwd)/:/home/bagros/data" ubuntuimage
