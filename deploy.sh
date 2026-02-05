#!/bin/bash

# Agentic Honeypot Deployment Script
# This script sets up and deploys the honeypot system

set -e

echo "🚀 Starting Agentic Honeypot Deployment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed."
    exit 1
fi

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Set environment variables if not already set
if [ -z "$API_KEY" ]; then
    echo "🔑 Setting default API key..."
    export API_KEY="SECRET123"
fi

echo "✅ Setup completed successfully!"

# Run tests to verify installation
echo "🧪 Running tests..."
python -m pytest test_honeypot.py -v

if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed. Please check the output above."
    exit 1
fi

# Start the server
echo "🌐 Starting the honeypot API server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📖 API docs available at: http://localhost:8000/docs"
echo "🔍 Health check at: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py
