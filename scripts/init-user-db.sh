#!/bin/bash
set -e

psql -U "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE "interagent";
EOSQL