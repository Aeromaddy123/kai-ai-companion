import asyncio
import subprocess
import structlog
from typing import List, Dict, Optional, AsyncGenerator

import yaml

logger = structlog.get_logger()


class LLMService:
    def __init__(self, config: dict):
        self.config = config
        self.server_config = config['server']
        self.model = "qwen2.5:8b"
        self.ollama_base_url = "http://localhost:11434"
        self._initialized = False
        self._client = None

    async def initialize(self):
        if self._initialized:
            return
        
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"{self.ollama_base_url}/api/tags")
                    if response.status_code == 200:
                        models = response.json().get('models', [])
                        model_names = [m['name'] for m in models]
                        
                        logger.info(f"Available Ollama models: {model_names}")
                        
                        if self.model not in model_names:
                            logger.warning(f"Model {self.model} not found. Please run: ollama pull {self.model}")
                        else:
                            logger.info(f"Model {self.model} is available")
                except Exception as e:
                    logger.warning(f"Could not connect to Ollama: {e}")
            
            self._client = httpx.AsyncClient(timeout=120.0)
            self._initialized = True
            logger.info("LLM service initialized")
            
        except Exception as e:
            logger.error(f"LLM service initialization failed: {e}")
            raise

    async def chat(self, prompt: str, context: Optional[List[Dict]] = None) -> str:
        if not self._initialized:
            await self.initialize()
        
        messages = context or []
        
        system_prompt = self.config['kai'].get('system_prompt', 
            "You are KAI, a friendly and helpful AI home companion. Be conversational.")
        
        full_messages = [
            {"role": "system", "content": system_prompt}
        ] + messages + [
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self._client.post(
                f"{self.ollama_base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": full_messages,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('message', {}).get('content', '')
            else:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return f"I apologize, but I encountered an error. Please ensure Ollama is running with the {self.model} model."
                
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"

    async def chat_stream(self, prompt: str, context: Optional[List[Dict]] = None) -> AsyncGenerator[str, None]:
        if not self._initialized:
            await self.initialize()
        
        messages = context or []
        
        system_prompt = self.config['kai'].get('system_prompt', 
            "You are KAI, a friendly and helpful AI home companion.")
        
        full_messages = [
            {"role": "system", "content": system_prompt}
        ] + messages + [
            {"role": "user", "content": prompt}
        ]
        
        try:
            async with self._client.stream(
                'POST',
                f"{self.ollama_base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": full_messages,
                    "stream": True
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        try:
                            data = json.loads(line)
                            if 'message' in data:
                                content = data['message'].get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Chat stream error: {e}")
            yield f"Error: {str(e)}"

    async def describe_image(self, image_base64: str) -> str:
        if not self._initialized:
            await self.initialize()
        
        try:
            response = await self._client.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": "llava:1.6",
                    "prompt": "Describe what you see in this image in detail.",
                    "images": [image_base64],
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                logger.error(f"LLaVA error: {response.status_code}")
                return "I couldn't analyze the image."
                
        except Exception as e:
            logger.error(f"Vision describe error: {e}")
            return f"I encountered an error analyzing the image: {str(e)}"

    async def vision_chat(self, image_base64: str, question: str) -> str:
        if not self._initialized:
            await self.initialize()
        
        try:
            response = await self._client.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": "llava:1.6",
                    "prompt": question,
                    "images": [image_base64],
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                logger.error(f"LLaVA chat error: {response.status_code}")
                return "I couldn't analyze the image."
                
        except Exception as e:
            logger.error(f"Vision chat error: {e}")
            return f"I encountered an error: {str(e)}"

    async def text_to_speech(self, text: str, voice: str = "default") -> Optional[bytes]:
        try:
            import io
            import wave
            
            try:
                result = subprocess.run(
                    ['piper', '--model', f'voices/{voice}.onnx', '--output-raw'],
                    input=text.encode(),
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    audio_data = result.stdout
                    
                    wav_buffer = io.BytesIO()
                    with wave.open(wav_buffer, 'wb') as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(22050)
                        wf.writeframes(audio_data)
                    
                    return wav_buffer.getvalue()
                    
            except FileNotFoundError:
                logger.warning("Piper TTS not installed. Using fallback.")
            
            return None
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None

    async def close(self):
        if self._client:
            await self._client.aclose()
        logger.info("LLM service closed")
