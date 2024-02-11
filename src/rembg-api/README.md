# `rembg s` API in docker

Build the image:

```
docker build -t $(whoami)/rembg-api .
```

Run the microservice in a container on port `7000`:

```
docker run -it -dp 7000:7000 --ipc=host --name rembg-api $(whoami)/rembg-api:latest
```