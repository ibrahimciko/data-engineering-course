#!/usr/bin/env zsh
docker network create pg-network
docker run \
-e POSTGRES_USER="postgres" \
-e POSTGRES_PASSWORD="root" \
-e POSTGRES_DB="ny_taxi" \
-v /Users/cikriibr/projects/learning/data-engineering-zoomcamp/week_1_basics_n_setup/2_docker_sql_my/ny_taxi_postgres_data:/var/lib/postgresql/data \
-p 5432:5432 \
--network=pg-network \
--name pg-database \
-it \
postgres:14