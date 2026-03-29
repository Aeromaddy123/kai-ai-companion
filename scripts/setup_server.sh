#!/bin/bash

set -e

echo "============================================"
echo "  AEROMADDY Server Setup Script (macOS/Linux)"
echo "============================================"

echo ""
echo "Step 1: Checking Python version..."
python3 --version || { echo "Python 3 required"; exit 1; }

echo ""
echo "Step 2: Installing Ollama..."

if command -v ollama &> /dev/null; then
    echo "Ollama already installed"
    ollama --version
else
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Installing Ollama for macOS..."
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo "Installing Ollama for Linux..."
        curl -fsSL https://ollama.com/install.sh | sh
    fi
fi

echo ""
echo "Step 3: Pulling AI models (this may take a while)..."
echo "Downloading Qwen 2.5 8B model..."
ollama pull qwen2.5:8b

echo "Downloading LLaVA 1.6 vision model..."
ollama pull llava:1.6

echo ""
echo "Step 4: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Step 5: Creating necessary directories..."
mkdir -p data/chroma
mkdir -p logs
mkdir -p voices

echo ""
echo "============================================"
echo "  Server Setup Complete!"
echo "============================================"
echo ""
echo "To start the server, run:"
echo "  cd server"
echo "  uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "Or with auto-reload for development:"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Make sure to update config/aeromaddy.yaml with your server IP"
echo "when configuring the Raspberry Pi client."
echo ""
