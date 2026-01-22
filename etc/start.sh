#!/bin/bash
# Run Graze backend server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
DATA_DIR="$PROJECT_ROOT/data"

cd "$BACKEND_DIR"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from example..."
    cp .env.example .env
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Import data if flag passed and data exists
if [ "$1" = "--import" ] || [ "$1" = "-i" ]; then
    if [ -f "$DATA_DIR/restaurants.csv" ] && [ -f "$DATA_DIR/menu_items.csv" ]; then
        echo "Importing data..."
        python manage.py import_data \
            --restaurants "$DATA_DIR/restaurants.csv" \
            --items "$DATA_DIR/menu_items.csv"
    else
        echo "Data files not found in $DATA_DIR"
    fi
fi

# Start server
echo "Starting backend server on http://localhost:8000"
python manage.py runserver
