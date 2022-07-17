import pandas as pd
import os
from sqlalchemy import create_engine
import pyarrow.parquet as pq
from dotenv import load_dotenv
import argparse


def load_engine(username, password, db_name="ny_taxi", host="localhost"):
    url = f"postgresql://{username}:{password}@{host}:5432/{db_name}"
    return create_engine(url)

def _ingest_one_batch(iterator, cols_to_change=None):
    df = next(iterator).to_pandas()
    if cols_to_change:
        df[cols_to_change] = df[cols_to_change].apply(pd.to_datetime, format='%Y-%m-%d %H:%M:%S')
    return df


def ingest_to_sql(parquet_file: pq.ParquetFile,
                  engine,
                  batch_size=10000,
                  table_name="yellow_taxi_data",
                  if_exists="append",
                  is_test=False):
    data_iterator = parquet_file.iter_batches(batch_size)
    # change column type to dtype
    cols_to_change = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]
    counter = 0
    
    # first iteration
    df = _ingest_one_batch(data_iterator, cols_to_change)
    counter += 1
    df.to_sql(table_name, con=engine, if_exists=if_exists)
    if_exists = "append"
    print(f"*** Iteration *** {counter}")
    if is_test:
        print("Only one batch is being ingested for testing")
        print("test successfully completed")
        return
    while True:
        try: 
            counter +=1
            df = _ingest_one_batch(data_iterator, cols_to_change)
            df.to_sql(table_name, con=engine, if_exists=if_exists)
            print(f"*** Iteration *** {counter}")
            
        except StopIteration as e:
            print(f"Ingestion has been completed in {counter} steps.")
            break
    
def main(params:argparse.Namespace):
    # load environment variables and connect to db
    load_dotenv()
    engine = load_engine(os.getenv("user"), os.getenv("password"), "ny_taxi", params.host)
    # print(f"Connection: {engine.connect()}")
    # fetch data
    print(f"fetching data from {params.data_url} and writing into {params.output_name}")
    # check data is already downloaded
    if os.path.exists(params.output_name):
        print(f"Data already available skipping downloading")
    else:
        os.system(f"curl {params.data_url} -o {params.output_name}")
    # load file
    parquet_file = pq.ParquetFile(params.output_name)
    # ingest
    ingest_to_sql(parquet_file, engine, params.batch_size, params.table_name, params.if_exists, params.test)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ingest nytaxi data")
    parser.add_argument('data_url', help="data_url from which it is fetched")
    parser.add_argument('--host', help="database host", default="localhost")
    parser.add_argument('--output_name', '-o', help="output_name for downloaded file", default="nytaxi.parquet")
    parser.add_argument('--batch_size', "-bs", help="batch size for ingesting data in each iteration", default=10000, type=int)
    parser.add_argument("--table_name", "-tb", help="name of the table in the database where ingestion happens", default="yellow_taxi_data")
    parser.add_argument("--if_exists", "-ie", help="ingestion mode", choices=["append", "replace"], default="append")
    parser.add_argument("--test", action=argparse.BooleanOptionalAction)
    params = parser.parse_args()
    print(f"Args: {params}")
    main(params)