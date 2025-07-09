FROM python:3.12-slim-bookworm
WORKDIR /app
RUN pip install uv
COPY ../pyproject.toml ../uv.lock ./
RUN uv sync
COPY .. .
EXPOSE 8000
CMD ["uv", "run", "main.py"]
