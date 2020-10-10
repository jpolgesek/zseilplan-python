FROM python:3.8

COPY app /app
WORKDIR /app
RUN python3 -m pip install -r req.txt
CMD ["python3", "/app/run.py"]
