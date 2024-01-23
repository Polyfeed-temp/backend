FROM python:3.8-slim
RUN apt-get update \
    && apt-get -yy install libmariadb-dev libpq-dev gcc python3-dev 

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "server.py"]
