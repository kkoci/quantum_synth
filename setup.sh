#!/bin/bash

echo "🎹 Quantum Synth Setup Script"
echo "=============================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if Redis is running
if ! redis-cli ping &> /dev/null; then
    echo "⚠️  Redis is not running. Please install and start Redis."
    echo "   On macOS: brew install redis && brew services start redis"
    echo "   On Ubuntu: sudo apt install redis-server && sudo systemctl start redis"
fi

echo ""
echo "📦 Setting up Backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file (please update with your settings)"
fi

# Run migrations
python manage.py migrate

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "📦 Setting up Frontend..."
cd ../frontend

# Install npm dependencies
npm install

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "=============================="
echo "🚀 Quick Start Commands:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend && source venv/bin/activate && python manage.py runserver"
echo ""
echo "Terminal 2 - Celery:"
echo "  cd backend && source venv/bin/activate && celery -A config worker -l info"
echo ""
echo "Terminal 3 - Frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "Or use Docker Compose:"
echo "  docker-compose up"
echo ""
echo "Then open: http://localhost:5173"
echo "=============================="
