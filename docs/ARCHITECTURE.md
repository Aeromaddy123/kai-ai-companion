# How AEROMADDY Works

## Overview

Two-part system:
1. **Raspberry Pi** - handles microphone, camera, wake word
2. **Server (Mac/PC)** - runs the AI models

## Data Flow

### Voice
```
You speak → Microphone → Raspberry Pi (STT) → Server (LLM) → Response → Raspberry Pi (TTS) → Speaker
```

### Vision
```
Camera → Raspberry Pi → Server (LLaVA) → Description → Response
```

### Memory
```
Conversations → Embeddings stored locally → Retrieved when relevant
```

## Stack

- **LLM**: Qwen 2.5 8B via Ollama
- **Vision**: LLaVA 1.6
- **STT**: Vosk (offline)
- **TTS**: Piper (offline)
- **Memory**: ChromaDB
- **API**: FastAPI
