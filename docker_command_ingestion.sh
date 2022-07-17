#!/usr/bin/env zsh
URL=https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-01.parquet

docker run \
--network=pg-network \
-it taxi_ingest:v001 \
$URL\
--host pg-database \
--output_name ny_taxi_data.parquet \
--batch_size 100000 \
--table_name yellow_taxi \
--if_exist replace
--test