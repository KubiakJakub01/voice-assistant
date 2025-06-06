FROM python:3.11.4-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install uv

WORKDIR /app

COPY pyproject.toml ./

RUN uv sync --no-cache

COPY . .

RUN python create_db_tables.py

EXPOSE 8000

CMD ["python", "server.py"]
