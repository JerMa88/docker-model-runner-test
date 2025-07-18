#!/usr/bin/env sh

# bring down any leftovers
docker compose down --remove-orphans

# build & run bench
docker compose up --build
