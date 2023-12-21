#!/bin/bash

set -eu

uvicorn --host ${UVICORN_HOST:-"0.0.0.0"} \
    --port ${UVICORN_PORT:-"80"} \
    --workers 1 \
    --date-header \
    --no-access-log \
    app:app
