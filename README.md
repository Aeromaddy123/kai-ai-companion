# 🤖 KAI - Your Private AI Home Companion

<div align="center">

**K**eepers **A**rtificial **I**ntelligence - A privacy-first, voice & vision-enabled AI companion

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4%2F5-CC0000.svg)](https://www.raspberrypi.org/)
[![Powered by Qwen](https://img.shields.io/badge/Powered%20by-Qwen%202.5-7B68EE.svg)](https://huggingface.co/Qwen)
[![macOS](https://img.shields.io/badge/macOS-Silicon%20Ready-333333.svg)](https://www.apple.com/mac/)

</div>

---

## 🌟 Features

### Core Capabilities
- **🎤 Voice Interaction** - NaturalConversational AI through speech
- **👁️ Vision Perception** - See and understand the environment
- **🧠 Persistent Memory** - Remembers conversations and learns over time
- **🔒 Privacy First** - 100% offline, your data never leaves your home
- **⚡ Edge AI** - Smart processing on Raspberry Pi

### Technical Highlights
- **8B Parameter LLM** - Running Qwen 2.5 on local hardware
- **On-Device STT** - Vosk speech recognition (no cloud dependency)
- **Wake Word Detection** - "Hey KAI" activation
- **Multimodal AI** - LLaVA for image understanding
- **Vector Memory** - ChromaDB for semantic memory storage

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         KAI SYSTEM                                 │
│                                                                     │
│  ┌──────────────────┐        WiFi         ┌──────────────────────┐ │
│  │   RASPBERRY PI   │                    │    LOCAL SERVER       │ │
│  │                  │   REST API/WebSocket│    (Mac/PC/NAS)      │ │
│  │  ┌────────────┐  │◄──────────────────►│                      │ │
│  │  │  Camera    │  │                    │  ┌────────────────┐  │ │
│  │  │  Module    │  │                    │  │  Ollama        │  │ │
│  │  └────────────┘  │                    │  │  Qwen 2.5 8B   │  │ │
│  │                  │                    │  └────────────────┘  │ │
│  │  ┌────────────┐  │                    │  ┌────────────────┐  │ │
│  │  │  Microphone│  │                    │  │  LLaVA 1.6     │  │ │
│  │  │  Array     │  │                    │  │  (Vision)      │  │ │
│  │  └────────────┘  │                    │  └────────────────┘  │ │
│  │                  │                    │  ┌────────────────┐  │ │
│  │  ┌────────────┐  │                    │  │  Piper TTS     │  │ │
│  │  │  Speaker   │  │                    │  │  (Offline)     │  │ │
│  │  └────────────┘  │                    │  └────────────────┘  │ │
│  │                  │                    │  ┌────────────────┐  │ │
│  │  ┌────────────┐  │                    │  │  ChromaDB     │  │ │
│  │  │  KAI       │  │                    │  │  (Memory)      │  │ │
│  │  │  Client    │  │                    │  └────────────────┘  │ │
│  │  └────────────┘  │                    │                      │ │
│  │                  │                    │                      │ │
│  │  ┌────────────┐  │                    │                      │ │
│  │  │  Vosk STT  │  │   ON-DEVICE        │                      │ │
│  │  │  (Offline) │  │                    │                      │ │
│  │  └────────────┘  │                    │                      │ │
│  └──────────────────┘                    └──────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 📋 Requirements

### Hardware

| Component | Specification | Cost (Approx.) |
|-----------|---------------|----------------|
| Raspberry Pi | 4 (4GB) or 5 (4GB) | $35-80 |
| Camera | Raspberry Pi Camera v2 / USB Webcam | $10-30 |
| Microphone | USB Mic Array (ReSpeaker 2-Mic) | $10-20 |
| Speaker | USB Speaker or 3.5mm Jack | $10-25 |
| Power Supply | 5V/3A USB-C | $10-15 |
| SD Card | 32GB+ Class 10 | $10-15 |

**Total: ~$75-165**

### Software

#### Server Side (Mac/Linux/PC)
- Python 3.10+
- Ollama (latest)
- macOS / Linux / Windows

#### Client Side (Raspberry Pi)
- Raspberry Pi OS 64-bit (Bookworm)
- Python 3.9+
- WiFi connection to local network

---

## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/kai-ai-companion.git
cd kai-ai-companion
```

### Step 2: Server Setup (macOS)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull required models
ollama pull qwen2.5:8b
ollama pull llava:1.6

# Install Python dependencies
pip install -r requirements.txt

# Start the server
cd server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Step 3: Raspberry Pi Setup

```bash
# Install dependencies
chmod +x scripts/setup_rpi.sh
./scripts/setup_rpi.sh

# Configure server IP in config/config.yaml
# Start KAI client
python rpi/kai.py
```

---

## 📁 Project Structure

```
kai/
├── README.md                 # This file
├── LICENSE                   # MIT License
├── requirements.txt          # Python dependencies
├── config/
│   └── config.yaml          # Configuration file
├── rpi/                     # Raspberry Pi client
│   ├── kai.py              # Main client entry
│   ├── audio/
│   │   ├── listener.py     # Microphone input
│   │   ├── wakeword.py     # Wake word detection
│   │   ├── tts_player.py   # Speaker output
│   │   └── stt.py          # Vosk STT
│   ├── vision/
│   │   └── camera.py       # Camera capture
│   ├── api/
│   │   └── client.py      # Server communication
│   └── utils/
│       └── logger.py
├── server/                  # Local LLM server
│   ├── main.py             # FastAPI server
│   ├── routers/
│   │   ├── chat.py         # Chat endpoints
│   │   ├── vision.py       # Vision endpoints
│   │   ├── memory.py       # Memory endpoints
│   │   └── tts.py          # TTS endpoints
│   ├── services/
│   │   ├── llm.py         # LLM service
│   │   ├── vision.py       # Vision service
│   │   ├── memory.py       # Memory service
│   │   └── tts.py         # TTS service
│   └── models/
│       └── schemas.py      # Pydantic models
├── scripts/
│   ├── setup_rpi.sh        # RPI setup script
│   ├── setup_server.sh     # Server setup script
│   └── install_models.sh   # Model downloader
├── docs/
│   ├── ARCHITECTURE.md     # Detailed architecture
│   ├── API.md             # API documentation
│   └── TROUBLESHOOTING.md # Common issues
└── models/                 # Downloaded models (gitignored)
```

---

## 🎯 Usage Modes

### Voice Mode
```
User: "Hey KAI, what's the weather like today?"
KAI:  "Based on the time of year and typical patterns, it should be 
       pleasant. Would you like me to check a weather service?"
```

### Vision Mode
```
User: "Hey KAI, what do you see?"
KAI:  "I can see a living room with a comfortable couch, a coffee 
       table with some books, and large windows letting in natural light."
```

### Memory Mode
```
User: "Hey KAI, remember where I put my keys?"
KAI:  "I'll remember that. You last told me you put your keys on the 
       kitchen counter near the fruit bowl."

User: "Hey KAI, where are my keys?"
KAI:  "You told me earlier that you put your keys on the kitchen 
       counter near the fruit bowl."
```

---

## ⚙️ Configuration

Edit `config/config.yaml` to customize KAI:

```yaml
server:
  host: "192.168.1.100"      # Your server IP
  port: 8000
  protocol: "http"

kai:
  name: "KAI"
  wake_word: "hey kai"
  voice: "default"
  language: "en"

audio:
  sample_rate: 16000
  channels: 1
  chunk_size: 1024

vision:
  enabled: true
  stream_fps: 5
  capture_on_request: true

memory:
  enabled: true
  max_memories: 1000
  similarity_threshold: 0.7
```

---

## 🔧 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /chat` | Chat with KAI | Send text, receive response |
| `POST /vision/describe` | Describe image | Get image description |
| `POST /vision/chat` | Vision Q&A | Ask questions about images |
| `POST /tts` | Text-to-Speech | Convert text to audio |
| `POST /memory/search` | Search memory | Find relevant memories |
| `POST /memory/add` | Add memory | Store new memories |
| `GET /health` | Health check | Server status |

---

## 🧪 Testing

```bash
# Test server health
curl http://localhost:8000/health

# Test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?"}'

# Test vision
curl -X POST http://localhost:8000/vision/describe \
  -F "image=@path/to/image.jpg"
```

---

## 📚 Documentation

- [Architecture Details](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

---

## 🛠️ Technologies Used

### AI/ML
- [Qwen 2.5](https://huggingface.co/Qwen/Qwen2.5-8B) - Large Language Model
- [LLaVA 1.6](https://llava-vl.github.io/) - Vision Language Model
- [Vosk](https://alphacephei.com/vosk) - Offline Speech Recognition
- [Piper](https://github.com/rhasspy/piper) - Offline Text-to-Speech
- [ChromaDB](https://www.trychroma.com/) - Vector Database

### Hardware
- [Raspberry Pi](https://www.raspberrypi.org/) - Edge Computing
- [Picamera2](https://github.com/raspberrypi/picamera2) - Camera Interface

### Infrastructure
- [Ollama](https://ollama.com/) - LLM Runtime
- [FastAPI](https://fastapi.tiangolo.com/) - API Framework
- [Sentence Transformers](https://www.sbert.net/) - Embeddings

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Qwen Team** for the excellent Qwen 2.5 model
- **LLaVA Team** for multimodal vision capabilities
- **Alphacephei** for Vosk offline STT
- **Rhasspy** for Piper TTS
- **The Raspberry Pi Foundation** for the amazing computing platform

---

<div align="center">

**Made with ❤️ for privacy-conscious AI enthusiasts**

*"Your AI companion, running locally, respecting your privacy."*

</div>
