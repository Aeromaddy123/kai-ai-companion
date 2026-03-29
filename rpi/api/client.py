import asyncio
import structlog
from typing import Optional, Dict, List, Any

import httpx

logger = structlog.get_logger()


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        try:
            client = await self._get_client()
            response = await client.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def chat(self, text: str, context: Optional[List[Dict]] = None) -> Optional[str]:
        try:
            client = await self._get_client()
            
            payload = {
                "text": text,
                "context": context or []
            }
            
            response = await client.post("/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response")
            else:
                logger.error(f"Chat request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return None

    async def vision_chat(self, image_base64: str, question: str) -> Optional[str]:
        try:
            client = await self._get_client()
            
            payload = {
                "image_base64": image_base64,
                "question": question
            }
            
            response = await client.post("/vision/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response")
            else:
                logger.error(f"Vision chat failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Vision chat error: {e}")
            return None

    async def describe_image(self, image_base64: str) -> Optional[str]:
        try:
            client = await self._get_client()
            
            payload = {
                "image_base64": image_base64
            }
            
            response = await client.post("/vision/describe", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("description")
            else:
                logger.error(f"Describe image failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Describe image error: {e}")
            return None

    async def get_tts(self, text: str) -> Optional[bytes]:
        try:
            client = await self._get_client()
            
            response = await client.post("/tts", json={"text": text})
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"TTS request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None

    async def add_memory(self, text: str, metadata: Optional[Dict] = None) -> Optional[str]:
        try:
            client = await self._get_client()
            
            payload = {
                "text": text,
                "metadata": metadata or {}
            }
            
            response = await client.post("/memory/add", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("id")
            else:
                logger.error(f"Add memory failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Add memory error: {e}")
            return None

    async def search_memory(self, query: str, k: int = 5) -> Optional[List[Dict]]:
        try:
            client = await self._get_client()
            
            payload = {
                "query": query,
                "k": k
            }
            
            response = await client.post("/memory/search", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("results")
            else:
                logger.error(f"Search memory failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Search memory error: {e}")
            return None

    async def get_context(self, query: str, k: int = 5) -> List[Dict]:
        results = await self.search_memory(query, k)
        if results:
            return [{"text": r["text"], "score": r["score"]} for r in results]
        return []
