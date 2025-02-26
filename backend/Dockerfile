# Pull official base image
FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update
WORKDIR /app
COPY . .
RUN uv sync --frozen --no-cache 
CMD ["/app/.venv/bin/fastapi", "dev", "/app/main.py", "--port", "8000", "--host", "0.0.0.0"]