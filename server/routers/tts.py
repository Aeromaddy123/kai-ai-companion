from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

import structlog
logger = structlog.get_logger()

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    voice: str = "default"


@router.post("/")
async def text_to_speech(request: TTSRequest):
    try:
        from server.main import get_llm_service
        
        llm_service = get_llm_service()
        
        if not llm_service:
            raise HTTPException(status_code=503, detail="LLM service not available")
        
        audio_data = await llm_service.text_to_speech(request.text, request.voice)
        
        if audio_data:
            return Response(content=audio_data, media_type="audio/wav")
        else:
            raise HTTPException(status_code=500, detail="TTS generation failed")
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
