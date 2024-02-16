# `rembg` API in docker

## On the `host` machine

**Prerequisites**

Make sure to have installed [`docker`](https://docker.com/) on your system.

**Build the image**

```
docker build -t $(whoami)/rembg-api .
```

**Run the microservice in a container on port `7000`**

```
docker run -it -dp 7000:7000 --ipc=host --name rembg-api $(whoami)/rembg-api:latest
```

**Keeping the models in a docker volume**

If you are removing and re-creating containers often, consider mounting a volume in which to keep the downloaded models, so that they don't get re-downloaded everytime.

Create a docker volume:

```
docker volume create rembg_models
```

Run a container with the attached volume:

```
docker run -it -dp 7000:7000 -v rembg_models:~/.u2net/ --ipc=host --name rembg-api $(whoami)/rembg-api:latest
```

## On the `client` machine

**Start `napari`**

Make sure to have installed the `napari-rembg` plugin.

```
napari
```

**Generate segmentations in Napari using the `rembg` microservice**

Open the plugin's remote segmentation widget:

```
Plugins > Napari Select Foreground > Select foreground (Web API)
```

Make sure the `Network` and `Port` parameters are correctly set up (they should point to where the docker container is running).
