# KAI API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

Check if the server is running and healthy.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "llm_service": "ready",
  "memory_service": "ready"
}
```

---

### Chat

Send a text message and receive a response from KAI.

**Endpoint:** `POST /chat`

**Request Body:**
```json
{
  "text": "Hello, how are you?",
  "context": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ],
  "stream": false
}
```

**Response:**
```json
{
  "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "model": "qwen2.5:8b"
}
```

**Streaming Response:** Set `stream: true` for Server-Sent Events (SSE).

---

### Vision - Describe Image

Get a description of an image.

**Endpoint:** `POST /vision/describe`

**Request Body:**
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
}
```

**Response:**
```json
{
  "description": "A living room with a comfortable gray couch, wooden coffee table, and large windows letting in natural light."
}
```

---

### Vision - Chat with Image

Ask a question about an image.

**Endpoint:** `POST /vision/chat`

**Request Body:**
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "question": "What color is the couch?"
}
```

**Response:**
```json
{
  "response": "The couch is gray in color."
}
```

---

### Text-to-Speech

Convert text to speech and receive audio.

**Endpoint:** `POST /tts`

**Request Body:**
```json
{
  "text": "Hello! This is KAI speaking.",
  "voice": "default"
}
```

**Response:** Audio file (WAV format)

---

### Memory - Add

Store a new memory.

**Endpoint:** `POST /memory/add`

**Request Body:**
```json
{
  "text": "User keeps their keys on the kitchen counter",
  "metadata": {
    "category": "personal",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Response:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "success": true
}
```

---

### Memory - Search

Search for relevant memories.

**Endpoint:** `POST /memory/search`

**Request Body:**
```json
{
  "query": "where did I put my keys",
  "k": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "text": "User keeps their keys on the kitchen counter",
      "score": 0.92,
      "metadata": {
        "category": "personal"
      }
    }
  ]
}
```

---

### Memory - Delete

Delete a specific memory.

**Endpoint:** `DELETE /memory/{memory_id}`

**Response:**
```json
{
  "success": true
}
```

---

### Memory - Stats

Get memory statistics.

**Endpoint:** `GET /memory/stats`

**Response:**
```json
{
  "total_memories": 42,
  "max_memories": 1000,
  "collection_name": "kai_memories"
}
```

## Error Responses

All endpoints may return error responses:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request
- `500` - Internal Server Error
- `503` - Service Unavailable
