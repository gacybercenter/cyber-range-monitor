FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . /app
WORKDIR /app
RUN uv pip install --system --no-cache -e .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--port", "8000", "--host", "0.0.0.0"]