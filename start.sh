#!/bin/sh
wait-for-it.sh -h pg_db -p 5432 -t 30 -- python -m disco.cli --config config.yaml --log-level debug

