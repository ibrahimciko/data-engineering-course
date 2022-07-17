FROM python:3.9

WORKDIR /app

COPY ny_taxi_data.parquet ny_taxi_data.parquet
COPY .env .env
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt 

RUN apt-get install curl

COPY ingestion.py ingestion.py
ENTRYPOINT [ "python", "./ingestion.py" ]