from typing import List, Dict, Optional
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException

import structlog
logger = structlog.get_logger()

router = APIRouter()


class MemoryAddRequest(BaseModel):
    text: str
    metadata: Optional[Dict] = {}


class MemorySearchRequest(BaseModel):
    query: str
    k: int = 5


class MemoryResult(BaseModel):
    id: str
    text: str
    score: float
    metadata: Optional[Dict] = None


class MemoryAddResponse(BaseModel):
    id: str
    success: bool


class MemorySearchResponse(BaseModel):
    results: List[MemoryResult]


@router.post("/add", response_model=MemoryAddResponse)
async def add_memory(request: MemoryAddRequest):
    try:
        from server.main import get_memory_service
        
        memory_service = get_memory_service()
        
        if not memory_service:
            raise HTTPException(status_code=503, detail="Memory service not available")
        
        memory_id = await memory_service.add(request.text, request.metadata)
        
        return MemoryAddResponse(id=memory_id, success=True)
        
    except Exception as e:
        logger.error(f"Add memory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=MemorySearchResponse)
async def search_memory(request: MemorySearchRequest):
    try:
        from server.main import get_memory_service
        
        memory_service = get_memory_service()
        
        if not memory_service:
            raise HTTPException(status_code=503, detail="Memory service not available")
        
        results = await memory_service.search(request.query, request.k)
        
        return MemorySearchResponse(results=[
            MemoryResult(
                id=r['id'],
                text=r['text'],
                score=r['score'],
                metadata=r.get('metadata')
            )
            for r in results
        ])
        
    except Exception as e:
        logger.error(f"Search memory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    try:
        from server.main import get_memory_service
        
        memory_service = get_memory_service()
        
        if not memory_service:
            raise HTTPException(status_code=503, detail="Memory service not available")
        
        success = await memory_service.delete(memory_id)
        
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Delete memory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def memory_stats():
    try:
        from server.main import get_memory_service
        
        memory_service = get_memory_service()
        
        if not memory_service:
            raise HTTPException(status_code=503, detail="Memory service not available")
        
        stats = await memory_service.get_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"Memory stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
