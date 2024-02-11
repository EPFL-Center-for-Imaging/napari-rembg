FROM python:3.9-slim

WORKDIR /app

RUN python -m pip install "rembg[cli]"

EXPOSE 7000

CMD ["rembg", "s", "--host", "0.0.0.0", "--port", "7000", "--log_level", "info"]