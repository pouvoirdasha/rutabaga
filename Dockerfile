FROM python:3.13-slim

# Installer uv
COPY --from=ghcr.io/astral-sh/uv:0.9.18 /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache


#copie code Flask et scripts
COPY app/ ./app
COPY rooms/ ./rooms
COPY main.py ./

#exposition port flask
EXPOSE 5000

#commande de lancement de l'app

CMD ["uv", "run", "python", "main.py"]