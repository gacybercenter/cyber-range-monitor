# syntax=docker/dockerfile:1

FROM python:3.10

WORKDIR "/cyber-range-monitor/"

COPY requirements.txt requirements.txt
COPY range_monitor range_monitor
COPY instance instance
COPY entrypoint.sh entrypoint.sh

RUN python -m venv .venv
RUN . .venv/bin/activate
RUN pip install -r requirements.txt

ENV FLASK_APP=range_monitor
EXPOSE 5000

RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]