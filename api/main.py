from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from fastapi import FastAPI, HTTPException, Depends
import docker
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine

app = FastAPI()
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
def list_nextlabs_containers():
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


@app.post("/containers/", response_model=Container, tags=["container"])
def run_container(email: EmailStr, container_image: str, public_key: str, db: Session = Depends(get_db)):
    images = list_images()
    if container_image in images:
        stop_time = datetime.now() + timedelta(hours=1)

        container = client.containers.run(
            image=container_image, detach=True, network="nextlabs", labels={"user": email})

        # add public key to the server
        cmd = f"echo '{admin_key}' >> /root/.ssh/authorized_keys"
        container.exec_run(cmd=['sh', '-c', cmd])

        cmd = f"echo '{public_key}' >> /root/.ssh/authorized_keys"
        container.exec_run(cmd=['sh', '-c', cmd])
        container.restart()

        db_container = dbContainer(
            hostname=container.attrs["Config"]["Hostname"], status="running", stop_at=stop_time, image=container_image)
        db.add(db_container)
        db.commit()

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


def stop_due_containers():
    db = SessionLocal()
    print("Stopping due containers")
    current_time = datetime.now()
    containers_to_stop = db.query(dbContainer).filter(
        dbContainer.stop_at <= current_time, dbContainer.status != "stopped").all()

    for container in containers_to_stop:
        try:
            docker_container = client.containers.get(container.hostname)
            docker_container.stop()
            container.status = "stopped"
            print(f"Container {container.hostname} stopped")
            container.stopped_at = datetime.now()
        except Exception as e:
            print(f"Failed to stop container {container.hostname}: {str(e)}")

    db.commit()


def delete_old_stopped_containers():
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


@app.delete("/containers/{container_hostname}", tags=["container"])
def delete_container(container_hostname: str):
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


@app.post("/containers/stop/{container_hostname}", tags=["container"])
def stop_container(container_hostname: str):
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


@app.post("/containers/start/{container_name}", tags=["container"])
def start_container(container_name: str):
    db = SessionLocal()
    stop_time = datetime.now() + timedelta(hours=1)
    try:
        container = client.containers.get(container_name)
        container.start()
        db.query(dbContainer).filter(
            dbContainer.hostname == container_name).update(
            {"status": "running", "stop_at": stop_time, "stopped_at": None})
        db.commit()
        return {"message": "Container started"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")


@app.post("/containers/restart/{container_name}", tags=["container"])
def restart_container(container_name: str):
    try:
        container = client.containers.get(container_name)
        container.restart()
        return {"message": "Container restarted"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")


@app.get("/user/containers/{user_email}", response_model=list[Container], tags=["user"])
def list_user_containers(user_email: EmailStr):
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


@app.post("/user/containers/stop/{user_email}", tags=["user"])
def stop_user_containers(user_email: EmailStr):
    containers = client.containers.list(all=True)
    user_containers = [
        container for container in containers
        if container.labels.get('user') == user_email
    ]
    for container in user_containers:
        container.stop()
    return {"message": "Containers stopped"}


@app.get("/images/", tags=["image"])
def list_images():
    nextlabs_images = []

    for image in client.images.list():
        # XGH
        if image.attrs.get("Config", {}).get("Labels", {}):
            if image.attrs.get("Config", {}).get("Labels", {}).get("project") == "nextlabs":
                if image.attrs.get("RepoTags"):
                    nextlabs_images.append(image.attrs["RepoTags"][0])

    return nextlabs_images


@app.post("/vpn/", tags=["vpn"])
def create_vpn_for_user():
    # TODO: Create a VPN for the user
    return {"message": "VPN created"}


scheduler = BackgroundScheduler()
scheduler.add_job(stop_due_containers, IntervalTrigger(minutes=1))
scheduler.add_job(delete_old_stopped_containers, IntervalTrigger(minutes=1))
scheduler.start()
