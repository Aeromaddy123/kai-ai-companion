from typing import Optional
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, UploadFile, File

import structlog
logger = structlog.get_logger()

router = APIRouter()


class VisionChatRequest(BaseModel):
    image_base64: str
    question: str


class VisionDescribeRequest(BaseModel):
    image_base64: str


class VisionResponse(BaseModel):
    response: str
    description: Optional[str] = None


@router.post("/describe")
async def describe_image(request: VisionDescribeRequest):
    try:
        from server.main import get_llm_service
        
        llm_service = get_llm_service()
        
        if not llm_service:
            raise HTTPException(status_code=503, detail="LLM service not available")
        
        description = await llm_service.describe_image(request.image_base64)
        
        return VisionResponse(description=description)
        
    except Exception as e:
        logger.error(f"Vision describe error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=VisionResponse)
async def vision_chat(request: VisionChatRequest):
    try:
        from server.main import get_llm_service
        
        llm_service = get_llm_service()
        
        if not llm_service:
            raise HTTPException(status_code=503, detail="LLM service not available")
        
        response = await llm_service.vision_chat(
            image_base64=request.image_base64,
            question=request.question
        )
        
        return VisionResponse(response=response)
        
    except Exception as e:
        logger.error(f"Vision chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        import base64
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode('utf-8')
        
        return {"filename": file.filename, "size": len(contents)}
        
    except Exception as e:
        logger.error(f"Image upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
