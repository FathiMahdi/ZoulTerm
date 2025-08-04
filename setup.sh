#!/bin/bash

set -e  # Exit on error unless pip fails

VENV_DIR="venv"

echo "🐍 Setting up Python virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
    echo "✅ Virtual environment created in ./$VENV_DIR"
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

echo "🔧 Installing Python dependencies inside virtual environment..."
pip install --upgrade pip
pip install -r requirements.txt || echo "⚠️ Failed to install some dependencies, continuing anyway..."

echo "🧹 Cleaning previous build artifacts..."
rm -rf build dist __pycache__ *.spec

echo "🎨 Converting UI files..."
bash ui_convert.sh

echo "📦 Generating resource files..."
bash rc_convert.sh

echo "🚀 Building executable with PyInstaller..."
pyinstaller \
    --windowed \
    --onefile \
    --name "ZoulTerm" \
    --hidden-import=PyQt5.QtSvg \
    src/main.py

echo "✅ Build complete. Output binary is in the 'dist' directory."
