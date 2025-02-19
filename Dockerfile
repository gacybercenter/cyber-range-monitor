# Pull official base image
FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN apt-get update
RUN python -m venv .venv
RUN . .venv/bin/activate
RUN pip install -r requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt 

COPY ./src /app

CMD ["python", "cli.py", "docker-run-api"]
