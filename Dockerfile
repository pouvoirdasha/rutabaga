FROM python:3.13-slim
ENV FLASK_DEBUG=1

WORKDIR /rutabaga
COPY requirements.txt ./
RUN pip install -r requirements.txt

#copie code Flask et scripts
COPY app/ ./app
COPY rooms/ ./rooms
COPY main.py ./

#exposition port flask
EXPOSE 5000

#commande de lancement de l'app

CMD ["python3", "main.py"]