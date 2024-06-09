import json
from io import StringIO
import csv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from fastapi import FastAPI, HTTPException, Depends, Response, Security, Request
import docker
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine
from fastapi.security import APIKeyHeader
from fastapi.security.api_key import APIKeyHeader
import os

app = FastAPI(
    title="Nextlabs API",
    description="API for Nextlabs project",
)

header_scheme = APIKeyHeader(name="secret")
secret_key = os.getenv("SECRET_KEY", "Heslo")


def check_secret_key(header: str = Security(header_scheme)):
    if header in secret_key:
        return header
    else:
        raise HTTPException(status_code=401)


client = docker.from_env()

# read bagros.pub
admin_key = open("bagros.pub", "r").read()

# db

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class dbContainer(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, index=True)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    stop_at = Column(DateTime, nullable=True)
    stopped_at = Column(DateTime, nullable=True)
    image = Column(String)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Container(BaseModel):
    name: str
    hostname: str
    state: str
    running: bool
    ipaddress: str
    image: str
    user: EmailStr | None = None


@app.get("/containers/", response_model=list[Container], tags=["container"])
def list_nextlabs_containers(api_key: str = Depends(check_secret_key)):
    containers = client.containers.list(all=True)
    nextlabs_containers = [
        container for container in containers
        if container.labels.get('project') == 'nextlabs'
    ]
    nextlabs_containers = [
        Container(
            name=container.name,
            hostname=container.attrs["Config"]["Hostname"],
            state=container.attrs["State"]["Status"],
            running=container.attrs["State"]["Running"],
            ipaddress=container.attrs["NetworkSettings"]["Networks"]["nextlabs"]["IPAddress"],
            image=container.image.tags[0],
            user=container.labels.get("user")
        ) for container in nextlabs_containers
    ]
    return nextlabs_containers


class ContainerRequest(BaseModel):
    email: EmailStr
    container_image: str
    public_key: str


@app.post("/containers/", tags=["container"])
def run_container(request: ContainerRequest, db: Session = Depends(get_db),  api_key: str = Depends(check_secret_key)):
    email = request.email
    container_image = request.container_image
    public_key = request.public_key

    images = list_images()
    if container_image in images:
        stop_time = datetime.now() + timedelta(hours=1)

        container = client.containers.run(
            image=container_image,
            detach=True,
            network="nextlabs",
            labels={"user": email},
            mem_limit="1g",
            cpu_period=100000,
            cpu_quota=25000,
        )

        labels = client.images.get(container_image).attrs.get(
            "Config", {}).get("Labels", {})
        if labels.get("ssh") == "1":
            # add public key to the server
            cmd = f"mkdir -p /root/.ssh ;echo '{admin_key}' >> /root/.ssh/authorized_keys"
            container.exec_run(cmd=['sh', '-c', cmd])

            cmd = f"echo '{public_key}' >> /root/.ssh/authorized_keys"
            container.exec_run(cmd=['sh', '-c', cmd])
            container.restart()

        db_container = dbContainer(
            hostname=container.attrs["Config"]["Hostname"], status="running", stop_at=stop_time, image=container_image)
        db.add(db_container)
        db.commit()

        container = client.containers.get(container.name)

        return Container(
            name=container.name,
            hostname=container.attrs["Config"]["Hostname"],
            state=container.attrs["State"]["Status"],
            running=container.attrs["State"]["Running"],
            ipaddress=container.attrs["NetworkSettings"]["Networks"]["nextlabs"]["IPAddress"],
            image=container.image.tags[0],
            user=container.labels.get("user"))
    else:
        raise HTTPException(status_code=404, detail="Image not found")


def stop_due_containers(api_key: str = Depends(check_secret_key)):
    db = SessionLocal()
    print("Stopping due containers")
    current_time = datetime.now()
    containers_to_stop = db.query(dbContainer).filter(
        dbContainer.stop_at <= current_time, dbContainer.status != "stopped").all()

    for container in containers_to_stop:
        try:
            docker_container = client.containers.get(container.hostname)
            print(container.hostname, "is due to stop")
            docker_container.stop()
            db.query(dbContainer).filter(
                dbContainer.hostname == container.hostname).update(
                {"status": "stopped", "stopped_at": datetime.now()})
        except Exception as e:
            print(f"Failed to stop container {container.hostname}: {str(e)}")

    db.commit()


def delete_old_stopped_containers(api_key: str = Depends(check_secret_key)):
    db = SessionLocal()
    print("Deleting old stopped containers")
    one_hour_ago = datetime.now() - timedelta(hours=1)
    old_stopped_containers = db.query(dbContainer).filter(
        dbContainer.stop_at < one_hour_ago).all()

    for container in old_stopped_containers:
        try:
            docker_container = client.containers.get(container.hostname)
            print(f"Removing container {container.hostname}")
            docker_container.remove(force=True)
            db.delete(container)
        except Exception as e:
            print(f"Failed to remove container {container.hostname}: {str(e)}")

    db.commit()


@app.delete("/containers/", tags=["container"])
def delete_container(container_hostname: str, api_key: str = Depends(check_secret_key)):
    try:
        container = client.containers.get(container_hostname)
        if container.labels.get("project") != "nextlabs":
            raise HTTPException(status_code=404, detail="Container not found")
        container.remove(force=True)
        try:
            db = SessionLocal()
            db.query(dbContainer).filter(
                dbContainer.hostname == container_hostname).delete()
            db.commit()
        except Exception as e:
            print(f"Failed to remove container from db: {str(e)}")
        return {"message": "Container deleted"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")


@app.post("/containers/stop/", tags=["container"])
def stop_container(container_hostname: str, api_key: str = Depends(check_secret_key)):
    db = SessionLocal()
    try:
        container = client.containers.get(container_hostname)
        db.query(dbContainer).filter(
            dbContainer.hostname == container_hostname).update(
            {"status": "stopped", "stopped_at": datetime.now()})
        db.commit()
        container.stop()
        return {"message": "Container stopped"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")


@app.post("/containers/start/", tags=["container"])
def start_container(container_hostname: str, api_key: str = Depends(check_secret_key)):
    db = SessionLocal()
    stop_time = datetime.now() + timedelta(hours=1)
    try:
        container = client.containers.get(container_hostname)
        container.start()
        db.query(dbContainer).filter(
            dbContainer.hostname == container_hostname).update(
            {"status": "running", "stop_at": stop_time, "stopped_at": None})
        db.commit()
        return {"message": "Container started"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")


@app.post("/containers/restart/", tags=["container"])
def restart_container(container_hostname: str, api_key: str = Depends(check_secret_key)):
    try:
        container = client.containers.get(container_hostname)
        container.restart()
        return {"message": "Container restarted"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")


@app.get("/user/containers/", response_model=list[Container], tags=["user"])
def list_user_containers(user_email: EmailStr, api_key: str = Depends(check_secret_key)):
    containers = client.containers.list(all=True)
    user_containers = [
        container for container in containers
        if container.labels.get('user') == user_email
    ]
    user_containers = [
        Container(
            name=container.name,
            hostname=container.attrs["Config"]["Hostname"],
            state=container.attrs["State"]["Status"],
            running=container.attrs["State"]["Running"],
            ipaddress=container.attrs["NetworkSettings"]["Networks"]["nextlabs"]["IPAddress"],
            image=container.image.tags[0],
            user=container.labels.get("user")
        ) for container in user_containers
    ]
    return user_containers


@app.post("/user/containers/stop/", tags=["user"])
def stop_user_containers(user_email: EmailStr, api_key: str = Depends(check_secret_key)):
    db = SessionLocal()
    containers = client.containers.list(all=True)
    user_containers = [
        container for container in containers
        if container.labels.get('user') == user_email
    ]
    for container in user_containers:
        container.stop()
        container_hostname = container.attrs["Config"]["Hostname"]
        db.query(dbContainer).filter(dbContainer.hostname == container_hostname).update(
            {"status": "stopped", "stopped_at": datetime.now(), "stop_at": None})
        db.commit()

    return {"message": "Containers stopped"}


@app.get("/images/", tags=["image"])
def list_images(api_key: str = Depends(check_secret_key)):
    nextlabs_images = []

    for image in client.images.list():
        # XGH
        if image.attrs.get("Config", {}).get("Labels", {}):
            if image.attrs.get("Config", {}).get("Labels", {}).get("project") == "nextlabs":
                if image.attrs.get("RepoTags"):
                    nextlabs_images.append(image.attrs["RepoTags"][0])

    return nextlabs_images


# VPN CRUD
vpn_image = "kylemanna/openvpn"
vpn_data = "/root/vpn"
volume_mapping = {vpn_data: {'bind': '/etc/openvpn', 'mode': 'rw'}}


def check_existing_vpn(email: EmailStr):
    vpn_clients = vpn_list()
    for client in vpn_clients:
        if client['name'] == email:
            return True
    return False


def download_vpn(email: EmailStr):
    # docker run -v /root/vpn:/etc/openvpn --rm kylemanna/openvpn ovpn_getclient CLIENTNAME > CLIENTNAME.ovpn
    container = client.containers.run(
        image=vpn_image,
        command=f"ovpn_getclient {email}",
        volumes=volume_mapping,
        remove=False,
        detach=True
    )
    container.wait()
    vpn_client = container.logs()
    container.remove()
    return vpn_client


# @app.post("/vpn/create", tags=["vpn"])
# let's assume that vpn does not exist
def create_vpn_for_user(email: EmailStr):
    client.containers.run(
        vpn_image,
        command=f"easyrsa build-client-full {email} nopass",
        volumes=volume_mapping,
        remove=True,
        detach=True,
        tty=True
    )
    print("VPN created")
    return {"message": "VPN created"}


@app.get("/vpn/list", tags=["vpn"])
def vpn_list(api_key: str = Depends(check_secret_key)):
    # docker run --rm -it -v $OVPN_DATA:/etc/openvpn kylemanna/openvpn ovpn_listclients
    container = client.containers.run(
        vpn_image,
        command="ovpn_listclients",
        volumes=volume_mapping,
        detach=True,
        remove=False,
        tty=True
    )
    container.wait()
    f = StringIO(container.logs().decode('utf-8'))
    reader = csv.DictReader(f)

    output = []
    for row in reader:
        row['begin'] = datetime.strptime(
            row['begin'], '%b %d %H:%M:%S %Y %Z').strftime('%Y-%m-%d %H:%M:%S %Z')
        row['end'] = datetime.strptime(
            row['end'], '%b %d %H:%M:%S %Y %Z').strftime('%Y-%m-%d %H:%M:%S %Z')
        output.append(row)

    container.remove()
    return output

# this is so dumb implementation, but fuck it


@app.get("/vpn/download", tags=["vpn"])
def get_user_vpn(email: EmailStr, api_key: str = Depends(check_secret_key)):
    print("Requesting vpn for ", email)
    if not check_existing_vpn(email):
        print("vpn not does not exist")
        create_vpn_for_user(email)
    return Response(content=download_vpn(email), media_type="text/plain")


@app.delete("/vpn/delete", tags=["vpn"], deprecated=True)
def delete_vpn_for_user(email: EmailStr, api_key: str = Depends(check_secret_key)):
    raise HTTPException(status_code=404, detail="Not implemented")
    if check_existing_vpn(email):
        client.containers.run(
            vpn_image,
            command=f"ovpn_revokeclient {email}",
            volumes={vpn_data: {'bind': '/etc/openvpn', 'mode': 'rw'}},
            remove=True,
            detach=True,
            tty=True
        )
        # TODO: need to type yes to revoke the client
        return {"message": "VPN deleted"}
    raise HTTPException(status_code=404, detail="Client not found")


scheduler = BackgroundScheduler()
scheduler.add_job(stop_due_containers, IntervalTrigger(minutes=1))
# scheduler.add_job(delete_old_stopped_containers, IntervalTrigger(minutes=1))
scheduler.start()
