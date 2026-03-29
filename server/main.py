"""
KAI Server - FastAPI Application
Runs on your Mac/PC/NAS to provide LLM capabilities to KAI client
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import structlog
import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routers import chat, vision, memory, tts
from server.services.llm import LLMService
from server.services.memory import MemoryService

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

app = FastAPI(
    title="KAI API Server",
    description="Backend API for KAI AI Companion",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(vision.router, prefix="/vision", tags=["vision"])
app.include_router(memory.router, prefix="/memory", tags=["memory"])
app.include_router(tts.router, prefix="/tts", tags=["tts"])

llm_service = None
memory_service = None


@app.on_event("startup")
async def startup_event():
    global llm_service, memory_service
    
    logger.info("Starting KAI server...")
    
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    llm_service = LLMService(config)
    await llm_service.initialize()
    
    if config.get('memory', {}).get('enabled', True):
        memory_service = MemoryService(config)
        await memory_service.initialize()
    
    logger.info("KAI server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down KAI server...")
    if llm_service:
        await llm_service.close()
    if memory_service:
        await memory_service.close()
    logger.info("KAI server shut down complete")


@app.get("/")
async def root():
    return {
        "name": "KAI API Server",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "llm_service": "ready" if llm_service else "not_initialized",
        "memory_service": "ready" if memory_service else "not_initialized"
    }


def get_llm_service() -> LLMService:
    return llm_service


def get_memory_service() -> MemoryService:
    return memory_service
