#!/bin/bash
# Build Graze frontend and backend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/src/django"
FRONTEND_DIR="$PROJECT_ROOT/src/graze"

# --- Backend ---
echo "=== Backend ==="

cd "$BACKEND_DIR"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3.9 -m venv venv
fi

source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ] || [ requirements.txt -nt venv/.installed ]; then
    echo "Upgrading pip..."
    pip install --upgrade pip
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Backend build complete."

# --- Frontend ---
echo ""
echo "=== Frontend ==="

cd "$FRONTEND_DIR"

# Install node dependencies if needed
if [ ! -d "node_modules" ] || [ package.json -nt node_modules/.yarn-integrity ]; then
    echo "Installing node dependencies..."
    yarn install --frozen-lockfile
fi

# Build
echo "Building frontend..."
yarn build

echo "Frontend build complete."

# --- Done ---
echo ""
echo "=== Build finished ==="
echo "Backend static files: $BACKEND_DIR/staticfiles/"
echo "Frontend dist:        $FRONTEND_DIR/dist/"
