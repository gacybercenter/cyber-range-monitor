# Pull official base image
FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN apt-get update
RUN python -m venv .venv
COPY setup.py .
RUN . .venv/bin/activate
RUN pip install --no-cache-dir --upgrade -e . 
COPY ./src /app

CMD ["monitor", "container", "begin-api"]
