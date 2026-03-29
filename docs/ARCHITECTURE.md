# AEROMADDY Architecture Documentation

## System Overview

AEROMADDY (Keepers Artificial Intelligence) is a privacy-focused AI home companion that runs an 8B parameter language model locally. The system is designed with a client-server architecture where the Raspberry Pi handles edge processing (audio input, wake word detection, STT) while the more computationally intensive tasks (LLM inference, vision processing, TTS) run on a more powerful local server.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AEROMADDY SYSTEM                                 │
│                                                                     │
│  ┌──────────────────┐        WiFi         ┌──────────────────────┐ │
│  │   RASPBERRY PI   │                    │    LOCAL SERVER       │ │
│  │                  │   REST API/WebSocket│    (Mac/PC/NAS)      │ │
│  │                  │◄──────────────────►│                      │ │
│  │  ┌────────────┐  │                    │  ┌────────────────┐  │ │
│  │  │  Camera    │  │                    │  │  Ollama        │  │ │
│  │  └────────────┘  │                    │  │  Qwen 2.5 8B   │  │ │
│  │                  │                    │  └────────────────┘  │ │
│  │  ┌────────────┐  │                    │  ┌────────────────┐  │ │
│  │  │  Microphone│  │                    │  │  LLaVA 1.6     │  │ │
│  │  └────────────┘  │                    │  │  (Vision)      │  │ │
│  │                  │                    │  └────────────────┘  │ │
│  │  ┌────────────┐  │                    │  ┌────────────────┐  │ │
│  │  │  Speaker   │  │                    │  │  Piper TTS     │  │ │
│  │  └────────────┘  │                    │  └────────────────┘  │ │
│  │                  │                    │  ┌────────────────┐  │ │
│  │  ┌────────────┐  │                    │  │  ChromaDB     │  │ │
│  │  │  AEROMADDY       │  │                    │  │  (Memory)      │  │ │
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

## Component Details

### Raspberry Pi Client

The client runs on a Raspberry Pi (4 or 5 recommended) and handles:

1. **Audio Input (listener.py)**
   - Captures audio from USB microphone
   - Performs voice activity detection (VAD)
   - Handles audio streaming to server

2. **Wake Word Detection (wakeword.py)**
   - Listens for "Hey AEROMADDY" trigger
   - Uses SpeechBrain or Picovoice Porcupine
   - Runs continuously in background

3. **Speech-to-Text (stt.py)**
   - Uses Vosk for offline transcription
   - Converts speech to text locally
   - Reduces network bandwidth

4. **TTS Player (tts_player.py)**
   - Plays back audio responses
   - Handles streaming audio playback
   - Uses PyAudio for output

5. **Camera (camera.py)**
   - Captures images via picamera2 or OpenCV
   - Handles camera configuration
   - Provides image streaming

6. **API Client (client.py)**
   - HTTP client for server communication
   - Handles retries and timeouts
   - Manages connection state

### Local Server

The server runs on a more powerful machine (Mac, PC, or NAS) and provides:

1. **LLM Service (llm.py)**
   - Hosts Qwen 2.5 8B via Ollama
   - Handles chat completions
   - Supports streaming responses

2. **Vision Service (vision.py)**
   - Hosts LLaVA for image understanding
   - Handles image description
   - Vision-language conversations

3. **Memory Service (memory.py)**
   - ChromaDB vector database
   - Stores conversation embeddings
   - Enables semantic search

4. **TTS Service (tts.py)**
   - Piper offline TTS
   - Multiple voice options
   - WAV audio generation

## Communication Protocol

### REST API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `POST /chat` | Chat | Send text, receive response |
| `POST /vision/describe` | Vision | Get image description |
| `POST /vision/chat` | Vision Q&A | Ask questions about images |
| `POST /tts` | TTS | Convert text to speech |
| `POST /memory/search` | Memory | Find relevant memories |
| `POST /memory/add` | Memory | Store new memories |
| `GET /health` | Health | Server status |

### Data Flow

1. **Voice Interaction Flow:**
   ```
   User Speaks → Mic → Vosk STT → Text → Server LLM → Response → Piper TTS → Speaker
   ```

2. **Vision Interaction Flow:**
   ```
   Camera Capture → Image → Server LLaVA → Description → Response → TTS → Speaker
   ```

3. **Memory Flow:**
   ```
   Conversation → Embeddings → ChromaDB → Semantic Search → Context Injection → LLM
   ```

## Security & Privacy

- All data processing happens locally
- No cloud services required
- No data leaves the local network
- Wake word detection can run offline
- STT processed on-device

## Performance Considerations

- RPI 4/5 recommended for smooth operation
- Server should have 16GB+ RAM for LLM
- WiFi 5GHz recommended for low latency
- Ollama model quantization can improve speed

## Scalability

- Multiple AEROMADDY clients can connect to one server
- ChromaDB can be moved to dedicated vector DB
- TTS can be distributed to reduce latency
- LLM can be upgraded to larger models
