from typing import List, Dict, Optional
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, Depends

import structlog
logger = structlog.get_logger()

router = APIRouter()


class ChatRequest(BaseModel):
    text: str
    context: Optional[List[Dict]] = []
    stream: bool = False


class ChatResponse(BaseModel):
    response: str
    model: str = "qwen2.5"


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        from server.main import get_llm_service, get_memory_service
        
        llm_service = get_llm_service()
        memory_service = get_memory_service()
        
        if not llm_service:
            raise HTTPException(status_code=503, detail="LLM service not available")
        
        context = request.context or []
        
        if memory_service:
            relevant_memories = await memory_service.search(request.text, k=3)
            if relevant_memories:
                memory_context = "\n\nRelevant memories:\n" + "\n".join([
                    f"- {m['text']} (relevance: {m['score']:.2f})"
                    for m in relevant_memories
                ])
                context.append({"role": "system", "content": memory_context})
        
        response = await llm_service.chat(
            prompt=request.text,
            context=context
        )
        
        if memory_service and len(request.text.split()) > 5:
            if any(word in request.text.lower() for word in ["remember", "forget", "note"]):
                await memory_service.add(request.text)
        
        return ChatResponse(response=response, model="qwen2.5")
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    from sse_starlette.sse import EventSourceResponse
    
    async def event_generator():
        try:
            from server.main import get_llm_service
            llm_service = get_llm_service()
            
            if not llm_service:
                yield {"event": "error", "data": "LLM service not available"}
                return
            
            async for chunk in llm_service.chat_stream(request.text, request.context):
                yield {"event": "message", "data": chunk}
                
        except Exception as e:
            logger.error(f"Chat stream error: {e}")
            yield {"event": "error", "data": str(e)}
    
    return EventSourceResponse(event_generator())
