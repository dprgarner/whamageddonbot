#!/bin/bash
# Run as `. ./dotenv.sh`

if [ -f .env ]; then
    export $(cat .env | xargs)
fi
