#!/bin/bash

echo "Starting Diet AI Application..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please update .env with your actual values!"
fi

# Start with docker-compose
docker-compose up --build
