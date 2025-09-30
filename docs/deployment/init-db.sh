#!/bin/bash
# Database initialization script for LegalEdge

set -e

echo "🔧 Initializing LegalEdge database..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h postgres -p 5432 -U postgres; do
    sleep 1
done
echo "✅ PostgreSQL is ready"

# Run database migrations
echo "🔄 Running database migrations..."
cd /app
alembic upgrade head
echo "✅ Database migrations completed"

# Seed development data (only in development environment)
if [ "$LEGALEDGE_ENVIRONMENT" = "development" ]; then
    echo "🌱 Seeding development data..."
    python seed_development_data.py
    echo "✅ Development data seeded"
else
    echo "⚠️ Skipping data seeding in $LEGALEDGE_ENVIRONMENT environment"
fi

echo "🎉 Database initialization completed!"
