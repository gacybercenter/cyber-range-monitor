# syntax=docker/dockerfile:1

FROM python:3.10.11

WORKDIR "/cyber-range-monitor/"

COPY requirements.txt requirements.txt
COPY range_monitor range_monitor

RUN python -m venv .venv
RUN . .venv/bin/activate
RUN pip install -r requirements.txt

ENV FLASK_APP=range_monitor
EXPOSE 5000

RUN flask init-db
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]