#!/bin/bash
# Production deployment script

set -e

echo "🚀 Yōsai Intel Dashboard - Production Deployment"

# Build and start with Docker Compose
echo "🐳 Building and starting services..."
docker-compose down
docker-compose build
docker-compose up -d

echo "✅ Services started!"
echo "Dashboard: http://localhost:8050"
echo "Database: localhost:5432"

# Show logs
echo "📋 Following logs (Ctrl+C to exit)..."
docker-compose logs -f dashboard
