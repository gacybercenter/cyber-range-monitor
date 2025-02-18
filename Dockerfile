# syntax=docker/dockerfile:1

FROM python:latest


WORKDIR /src
COPY /src .
RUN apt-get update
RUN python -m venv .venv
RUN . .venv/bin/activate
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8000
CMD ["./entrypoint.sh"]

