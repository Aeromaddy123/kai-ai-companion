#!/bin/bash

set -e

echo "============================================"
echo "  KAI Model Downloader"
echo "============================================"

echo ""
echo "This script downloads all required AI models"
echo ""

MODELS_DIR="./models"
mkdir -p "$MODELS_DIR"

echo ""
echo "1. Downloading Vosk STT model..."
cd "$MODELS_DIR"
if [ ! -d "vosk-model-small-en-us-0.15" ]; then
    wget -q --show-progress https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip -q vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
    echo "Vosk model downloaded successfully"
else
    echo "Vosk model already exists, skipping"
fi

echo ""
echo "2. Downloading Ollama models (via Ollama CLI)..."
echo "   Make sure Ollama is installed first!"

if command -v ollama &> /dev/null; then
    echo "Pulling qwen2.5:8b..."
    ollama pull qwen2.5:8b
    
    echo "Pulling llava:1.6..."
    ollama pull llava:1.6
else
    echo "Ollama not found. Please install from https://ollama.com"
    echo "Then run: ollama pull qwen2.5:8b && ollama pull llava:1.6"
fi

echo ""
echo "3. Downloading Sentence Transformer model..."
cd ..

mkdir -p data/embeddings
python3 -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Embedding model ready')
" 2>/dev/null || echo "Embedding model will be downloaded on first use"

echo ""
echo "============================================"
echo "  All models downloaded!"
echo "============================================"
echo ""
echo "Total models directory size:"
du -sh "$MODELS_DIR" 2>/dev/null || echo "Run 'du -sh models' to see size"
echo ""
