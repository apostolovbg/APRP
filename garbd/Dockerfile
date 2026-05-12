# Galera Arbitrator (garbd) for the APRP cluster layout.
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends galera-arbitrator-4 \
    && rm -rf /var/lib/apt/lists/*
