# KAI Setup Guide for macOS

This guide will help you set up the KAI server on your Mac.

## Prerequisites

- macOS 12.0 or later (Apple Silicon or Intel)
- Python 3.10 or later
- At least 16GB RAM recommended for 8B model
- 20GB free disk space

## Step 1: Install Ollama

### For Apple Silicon (M1/M2/M3):
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### For Intel Mac:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Verify Installation:
```bash
ollama --version
```

## Step 2: Pull AI Models

This will download the required models. It may take 10-30 minutes depending on your internet speed.

```bash
# Qwen 2.5 8B (Language Model)
ollama pull qwen2.5:8b

# LLaVA 1.6 (Vision Model)
ollama pull llava:1.6
```

### Alternative: Smaller Models

If you have limited RAM, use smaller models:
```bash
ollama pull qwen2.5:4b
ollama pull llava:1.5
```

## Step 3: Install Python Dependencies

```bash
# Navigate to project
cd kai

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Get Your Mac's IP Address

```bash
# For WiFi connection
ipconfig getifaddr en0

# For Ethernet
ipconfig getifaddr en1
```

Note this IP address - you'll need it for the Raspberry Pi client.

## Step 5: Create Necessary Directories

```bash
mkdir -p data/chroma
mkdir -p logs
mkdir -p voices
```

## Step 6: Start the Server

### Basic Start:
```bash
cd server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### With Auto-reload (for development):
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### As a Background Service:

Create a plist file at `~/Library/LaunchAgents/com.kai.server.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.kai.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/YOUR_USERNAME/kai/venv/bin/uvicorn</string>
        <string>main:app</string>
        <string>--host</string>
        <string>0.0.0.0</string>
        <string>--port</string>
        <string>8000</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/kai/server</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.kai.server.plist
```

## Step 7: Verify Server is Running

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

You should see:
```json
{"status":"healthy","llm_service":"ready","memory_service":"ready"}
```

Test chat:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!"}'
```

## Step 8: Configure Firewall (Optional)

If you want to access from other devices:
```bash
# Allow incoming connections on port 8000
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --addapp=/Users/YOUR_USERNAME/kai/venv/bin/python3.11
```

## Troubleshooting

### Ollama not starting:
```bash
# Check if port 11434 is in use
lsof -i :11434

# Kill any existing process
pkill -f ollama
```

### Model download failing:
```bash
# Retry with verbose output
ollama pull qwen2.5:8b -v
```

### Server not accessible from RPI:
- Check your Mac's firewall settings
- Ensure you're on the same network
- Try pinging your Mac from the Raspberry Pi

## Next Steps

Once the server is running, proceed to set up the Raspberry Pi client following the main README instructions.
