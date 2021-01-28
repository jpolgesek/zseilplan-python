FROM python:3.8.7-slim-buster

COPY app /app
WORKDIR /app
RUN python3 -m pip install -r req.txt && apt install -y curl
CMD ["python3", "/app/run.py"]
