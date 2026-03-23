#!/bin/bash

# E-Learning Analytics Platform - Setup Script (Linux/Mac)
# This script automates the initial setup of the project

echo ""
echo "========================================"
echo "AI E-Learning Analytics Platform Setup"
echo "========================================"
echo ""

# Check if Python is installed
echo "[1/5] Checking Python installation..."
python_version=$(python3 --version 2>&1)
if [ $? -eq 0 ]; then
    echo "✓ Python found: $python_version"
else
    echo "✗ Python not found. Please install Python 3.13+"
    exit 1
fi

# Create virtual environment if not exists
echo ""
echo "[2/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install requirements
echo ""
echo "[4/5] Installing dependencies (this may take a few minutes)..."
pip install --progress-bar on -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Verify TensorFlow installation
echo ""
echo "[5/5] Verifying TensorFlow installation..."
python -c "import tensorflow as tf; print(f'TensorFlow version: {tf.__version__}')"
if [ $? -eq 0 ]; then
    echo "✓ TensorFlow verified"
else
    echo "⚠ TensorFlow verification failed (this may be expected)"
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "📋 Next Steps:"
echo "  1. Start MongoDB (if not running)"
echo "     - macOS: brew services start mongodb-community"
echo "     - Linux: sudo systemctl start mongod"
echo ""
echo "  2. Run Flask Application:"
echo "     python Backend/app.py"
echo ""
echo "  3. Open Browser:"
echo "     http://127.0.0.1:5000"
echo ""
echo "  4. Register & Login"
echo ""
echo "========================================"
echo ""
