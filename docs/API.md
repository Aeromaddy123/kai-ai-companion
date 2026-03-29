# API Reference

## Base URL
```
http://localhost:8000
```

## Endpoints

### GET /health
Check if server is running.

### POST /chat
Send a message and get a response.
```json
{"text": "Hello"}
```

### POST /vision/describe
Describe an image.
```json
{"image_base64": "..."}
```

### POST /vision/chat
Ask something about an image.
```json
{"image_base64": "...", "question": "What's in this image?"}
```

### POST /tts
Convert text to speech. Returns audio.

### POST /memory/add
Store something in memory.
```json
{"text": "Remember that..."}
```

### POST /memory/search
Search your memory.
```json
{"query": "what did I say about..."}
```
