#!/usr/bin/env bash
# Render.com build script for Library Management System
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "📂 Collecting static files..."
python manage.py collectstatic --no-input

echo "🗄️ Running migrations..."
python manage.py migrate

echo "🌱 Seeding sample data..."
python manage.py seed_data

echo "✅ Build complete!"
