FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copie code Flask et scripts
COPY app/ ./app
COPY rutabaga/ ./rutabaga

#exposition port flask
EXPOSE 5000

#commande de lancement de l'app
CMD ["python", "app/app.py"]