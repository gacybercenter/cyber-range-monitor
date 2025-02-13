# syntax=docker/dockerfile:1

FROM python:latest

WORKDIR "/version_2/"

RUN apt-get update
COPY ./requirements.txt .
RUN python -m venv .venv
RUN . .venv/bin/activate
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .


RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]
 


