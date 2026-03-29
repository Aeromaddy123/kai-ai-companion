# AEROMADDY

A privacy-first AI home companion running on Raspberry Pi + local LLM server.

## What is this?

A personal AI assistant that can see, hear, and talk to you. Everything runs locally on your own hardware - no cloud, no subscriptions, your data stays at home.

Built with Qwen 2.5 8B for natural conversations, LLaVA for vision, and Vosk for offline speech recognition.

## Quick Setup

### Server (your Mac/PC)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull qwen2.5:8b
ollama pull llava:1.6

# Run server
cd server
pip install -r ../requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Raspberry Pi Client

```bash
# Run setup script
chmod +x scripts/setup_rpi.sh
./scripts/setup_rpi.sh

# Update config/aeromaddy.yaml with your server IP

# Start
python rpi/aeromaddy.py
```

## Features

- Voice conversations (wake word: "hey aeromaddy")
- Vision - ask what it sees
- Remembers things you tell it
- Works completely offline
- 100% private

## Hardware Needed

- Raspberry Pi 4 or 5
- USB microphone
- Camera (optional)
- Speaker or headphones

## Author

Built by [@Aeromaddy123](https://github.com/Aeromaddy123)
