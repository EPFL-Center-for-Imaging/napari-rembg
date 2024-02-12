# `rembg` API in docker

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

Make sure the `Network` and `port` parameters are correctly set up.