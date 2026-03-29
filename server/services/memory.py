import uuid
import structlog
from typing import List, Dict, Optional
from pathlib import Path

logger = structlog.get_logger()


class MemoryService:
    def __init__(self, config: dict):
        self.config = config['memory']
        self.collection_name = self.config.get('collection_name', 'aeromaddy_memories')
        self.max_memories = self.config.get('max_memories', 1000)
        self.similarity_threshold = self.config.get('similarity_threshold', 0.7)
        self.persist_directory = Path(self.config.get('persist_directory', './data/chroma'))
        self._client = None
        self._collection = None
        self._embedding_model = None

    async def initialize(self):
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            self._client = chromadb.Client(Settings(
                persist_directory=str(self.persist_directory),
                anonymized_telemetry=False
            ))
            
            try:
                self._collection = self._client.get_collection(name=self.collection_name)
                logger.info(f"Loaded existing memory collection: {self.collection_name}")
            except:
                self._collection = self._client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "AEROMADDY's persistent memories"}
                )
                logger.info(f"Created new memory collection: {self.collection_name}")
            
            try:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Embedding model loaded")
            except ImportError:
                logger.warning("sentence-transformers not installed. Using mock embeddings.")
            
            self._initialized = True
            logger.info("Memory service initialized")
            
        except Exception as e:
            logger.error(f"Memory service initialization failed: {e}")
            self._initialized = False

    async def add(self, text: str, metadata: Optional[Dict] = None) -> str:
        if not self._initialized:
            await self.initialize()
        
        memory_id = str(uuid.uuid4())
        
        try:
            if self._embedding_model:
                embedding = self._embedding_model.encode(text).tolist()
            else:
                embedding = self._mock_embedding(text)
            
            self._collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata or {}]
            )
            
            count = self._collection.count()
            if count > self.max_memories:
                await self._cleanup_old_memories()
            
            logger.info(f"Added memory: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Add memory error: {e}")
            return memory_id

    async def search(self, query: str, k: int = 5) -> List[Dict]:
        if not self._initialized:
            await self.initialize()
        
        try:
            if self._embedding_model:
                query_embedding = self._embedding_model.encode(query).tolist()
            else:
                query_embedding = self._mock_embedding(query)
            
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )
            
            memories = []
            if results['ids'] and results['ids'][0]:
                for i, mem_id in enumerate(results['ids'][0]):
                    score = results['distances'][0][i] if 'distances' in results else 1.0
                    
                    if score < (1 - self.similarity_threshold):
                        memories.append({
                            'id': mem_id,
                            'text': results['documents'][0][i],
                            'score': 1 - score,
                            'metadata': results['metadatas'][0][i] if results.get('metadatas') else {}
                        })
            
            return memories
            
        except Exception as e:
            logger.error(f"Search memory error: {e}")
            return []

    async def delete(self, memory_id: str) -> bool:
        if not self._initialized:
            await self.initialize()
        
        try:
            self._collection.delete(ids=[memory_id])
            logger.info(f"Deleted memory: {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Delete memory error: {e}")
            return False

    async def get_stats(self) -> Dict:
        if not self._initialized:
            await self.initialize()
        
        try:
            count = self._collection.count()
            return {
                "total_memories": count,
                "max_memories": self.max_memories,
                "collection_name": self.collection_name
            }
        except Exception as e:
            logger.error(f"Get stats error: {e}")
            return {"error": str(e)}

    async def _cleanup_old_memories(self):
        try:
            results = self._collection.get()
            if results['ids'] and len(results['ids']) > self.max_memories:
                ids_to_delete = results['ids'][:-self.max_memories]
                self._collection.delete(ids=ids_to_delete)
                logger.info(f"Cleaned up {len(ids_to_delete)} old memories")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def _mock_embedding(self, text: str) -> List[float]:
        import hashlib
        import struct
        
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        embedding = []
        for i in range(0, min(len(hash_bytes), 384), 4):
            value = struct.unpack('f', hash_bytes[i:i+4])[0]
            embedding.append(value)
        
        while len(embedding) < 384:
            embedding.append(0.0)
        
        import math
        norm = math.sqrt(sum(x*x for x in embedding))
        if norm > 0:
            embedding = [x/norm for x in embedding]
        
        return embedding[:384]

    async def close(self):
        logger.info("Memory service closed")
