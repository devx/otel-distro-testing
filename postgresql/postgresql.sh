# Copyright (c) 2023 Victor Palma
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
podman run --name postgres15 -p 5432:5432 --rm -e POSTGRES_PASSWORD=RQBP8395VaZHDDdkxw15 -d postgres:15
podman run --name postgres14 -p 5433:5432 --rm -e POSTGRES_PASSWORD=RQBP8395VaZHDDdkxw14 -d postgres:14
podman run --name postgres13 -p 5434:5432 --rm -e POSTGRES_PASSWORD=RQBP8395VaZHDDdkxw13 -d postgres:13
podman run --name postgres12 -p 5435:5432 --rm -e POSTGRES_PASSWORD=RQBP8395VaZHDDdkxw12 -d postgres:12
podman run --name postgres11 -p 5436:5432 --rm -e POSTGRES_PASSWORD=RQBP8395VaZHDDdkxw11 -d postgres:11
podman run --name postgres10 -p 5437:5432 --rm -e POSTGRES_PASSWORD=RQBP8395VaZHDDdkxw10 -d postgres:10
podman run --name postgres09 -p 5438:5432 --rm -e POSTGRES_PASSWORD=RQBP8395VaZHDDdkxw09 -d postgres:9

sleep 10

for i in postgres09 postgres10 postgres11 postgres12 postgres13 postgres14 postgres15; do
	podman exec -ti $i psql -U postgres -c "CREATE DATABASE currency;"
	podman exec -ti $i psql -U postgres -d currency -c "CREATE TABLE asset ( id TEXT PRIMARY KEY, timestamp TIMESTAMP, symbol TEXT NOT NULL, currency_symbol TEXT, type TEXT NOT NULL, rate_usd NUMERIC(20,10) NOT NULL);"
done
