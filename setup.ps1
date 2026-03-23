# E-Learning Analytics Platform - Setup Script
# This script automates the initial setup of the project

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "AI E-Learning Analytics Platform Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Python is installed
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.13+" -ForegroundColor Red
    exit 1
}

# Create virtual environment if not exists
Write-Host "`n[2/5] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n[3/5] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install requirements
Write-Host "`n[4/5] Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
pip install --progress-bar on -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Verify TensorFlow installation
Write-Host "`n[5/5] Verifying TensorFlow installation..." -ForegroundColor Yellow
python -c "import tensorflow as tf; print(f'TensorFlow version: {tf.__version__}')"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ TensorFlow verified" -ForegroundColor Green
} else {
    Write-Host "⚠ TensorFlow verification failed (this may be expected)" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Start MongoDB (if not running)"
Write-Host "     - Auto-starts as Windows Service"
Write-Host "     - Or run: mongosh --eval 'db.adminCommand(\"ping\")'"
Write-Host "`n  2. Run Flask Application:"
Write-Host "     python Backend\app.py"
Write-Host "`n  3. Open Browser:"
Write-Host "     http://127.0.0.1:5000"
Write-Host "`n  4. Register & Login"
Write-Host "`n========================================`n" -ForegroundColor Cyan
