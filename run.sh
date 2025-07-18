#!/usr/bin/env sh

# Tear down any previous run
docker compose down --remove-orphans

# Build and start bench (Compose will handle the model for you)
docker compose up --build
