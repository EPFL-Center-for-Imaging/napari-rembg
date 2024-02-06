# Start a segmentation microservice for `rembg`

## Setup

Install the requirements:

```
pip install -r requirements.txt
```

Start a FastAPI server on port `8000`:

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

### In Docker

Build the image.

```
docker build -t $(whoami)/rembg_api .
```

Run the microservice on port `8000`.

```
docker run -dp 8000:8000 --ipc=host --name rembg-predict $(whoami)/rembg_api:latest
```

Then, run the processing via the endpoint `http://localhost:8000/process_image/`.