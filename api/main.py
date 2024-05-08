from fastapi import FastAPI, HTTPException
import docker
from pydantic import BaseModel, EmailStr


app = FastAPI()
client = docker.from_env()


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
            name=container.attrs["Config"]["Hostname"],
            hostname=container.name,
            state=container.attrs["State"]["Status"],
            running=container.attrs["State"]["Running"],
            ipaddress=container.attrs["NetworkSettings"]["Networks"]["nextlabs"]["IPAddress"],
            image=container.image.tags[0],
            user=container.labels.get("user")
        ) for container in nextlabs_containers
    ]
    return nextlabs_containers


@app.post("/containers/", response_model=Container, tags=["container"])
def run_container(email: EmailStr, containerImage: str):
    # Loop over all images to check if the image is a nextlabs image
    for image in client.images.list():
        labels = image.attrs.get("Config", {}).get("Labels", {})
        if labels.get("project") == "nextlabs":
            repotags = image.attrs.get("RepoTags", [])
            if containerImage in repotags:
                container = client.containers.run(
                    image=containerImage, detach=True, network="nextlabs", labels={"user": email})
                # Return a dictionary with container details you wish to expose
                return Container(
                    name=container.attrs["Config"]["Hostname"],
                    hostname=container.name,
                    state=container.attrs["State"]["Status"],
                    running=container.attrs["State"]["Running"],
                    ipaddress=container.attrs["NetworkSettings"]["Networks"]["nextlabs"]["IPAddress"],
                    image=container.image.tags[0],
                    user=container.labels.get("user"))

    raise HTTPException(status_code=404, detail="Image not found")


@app.delete("/containers/{container_name}", tags=["container"])
def delete_container(container_name: str):
    try:
        container = client.containers.get(container_name)
        if container.labels.get("project") != "nextlabs":
            raise HTTPException(status_code=404, detail="Container not found")
        container.remove(force=True)
        return {"message": "Container deleted"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")


@app.post("/containers/stop/{container_name}", tags=["container"])
def stop_container(container_name: str):
    try:
        container = client.containers.get(container_name)
        container.stop()
        return {"message": "Container stopped"}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")


@app.post("/containers/start/{container_name}", tags=["container"])
def start_container(container_name: str):
    try:
        container = client.containers.get(container_name)
        container.start()
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
            name=container.attrs["Config"]["Hostname"],
            hostname=container.name,
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
