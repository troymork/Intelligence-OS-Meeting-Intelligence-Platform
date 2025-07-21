#!/bin/bash

# Intelligence OS Platform - Railway Deployment Script
set -euo pipefail

echo "🚀 Starting Intelligence OS Platform on Railway..."

# Set default port
export PORT=${PORT:-8000}

# Start the backend server
cd /app/backend
python app.py