#!/bin/bash

set -e

echo "============================================"
echo "  KAI Raspberry Pi Setup Script"
echo "============================================"

echo ""
echo "Step 1: Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo "Step 2: Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    libportaudio2 \
    libasound2-dev \
    libavcodec-extra \
    ffmpeg \
    git \
    curl \
    portaudio19-dev

echo ""
echo "Step 3: Enabling camera interface..."
if grep -q "start_x=1" /boot/config.txt; then
    echo "Camera already enabled"
else
    echo "Adding camera support to /boot/config.txt..."
    echo "start_x=1" | sudo tee -a /boot/config.txt
    echo "gpu_mem=256" | sudo tee -a /boot/config.txt
fi

echo ""
echo "Step 4: Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "Step 5: Installing Python dependencies..."
pip install --upgrade pip
pip install numpy
pip install pyaudio
pip install pvporcupine || echo "Picovoice not installed (optional)"

pip install -r requirements.txt

echo ""
echo "Step 6: Installing picamera2 (if using Raspberry Pi camera)..."
pip install picamera2

echo ""
echo "Step 7: Downloading Vosk STT model..."
mkdir -p models
cd models

if [ ! -d "vosk-model-small-en-us-0.15" ]; then
    echo "Downloading Vosk model..."
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
else
    echo "Vosk model already exists"
fi

cd ..

echo ""
echo "Step 8: Creating necessary directories..."
mkdir -p logs
mkdir -p data/chroma

echo ""
echo "Step 9: Configuring audio..."
echo ""
echo "Check your microphone with:"
echo "  arecord -l"
echo "  pactl list sources short"
echo ""
echo "Check your speaker with:"
echo "  aplay -l"
echo "  pactl list sinks short"
echo ""

echo ""
echo "============================================"
echo "  Raspberry Pi Setup Complete!"
echo "============================================"
echo ""
echo "1. Edit config/config.yaml and set your server IP"
echo ""
echo "2. To run KAI:"
echo "   source venv/bin/activate"
echo "   python rpi/kai.py"
echo ""
echo "3. For audio testing:"
echo "   python -c 'import pyaudio; p = pyaudio.PyAudio(); print(p.get_device_count())'"
echo ""
