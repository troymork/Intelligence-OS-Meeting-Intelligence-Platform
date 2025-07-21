"""
Voice Processing Service for Intelligence OS
Real-time speech recognition with multi-speaker support
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import structlog
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from voice_engine import VoiceProcessingEngine
from speaker_identification import SpeakerIdentificationEngine
from real_time_processor import RealTimeVoiceProcessor
from models import VoiceProcessingRequest, VoiceProcessingResponse, SpeakerIdentificationResult

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Prometheus metrics
VOICE_PROCESSING_REQUESTS = Counter('voice_processing_requests_total', 'Total voice processing requests')
VOICE_PROCESSING_DURATION = Histogram('voice_processing_duration_seconds', 'Voice processing duration')
SPEAKER_IDENTIFICATION_REQUESTS = Counter('speaker_identification_requests_total', 'Total speaker identification requests')
WEBSOCKET_CONNECTIONS = Counter('websocket_connections_total', 'Total WebSocket connections')

# Global instances
voice_engine = None
speaker_engine = None
realtime_processor = None
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global voice_engine, speaker_engine, realtime_processor, redis_client
    
    logger.info("Starting Voice Processing Service")
    
    try:
        # Initialize Redis connection
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        redis_client = redis.from_url(redis_url)
        await redis_client.ping()
        logger.info("Redis connection established")
        
        # Initialize voice processing engines
        voice_engine = VoiceProcessingEngine()
        await voice_engine.initialize()
        logger.info("Voice processing engine initialized")
        
        speaker_engine = SpeakerIdentificationEngine()
        await speaker_engine.initialize()
        logger.info("Speaker identification engine initialized")
        
        realtime_processor = RealTimeVoiceProcessor(voice_engine, speaker_engine, redis_client)
        await realtime_processor.initialize()
        logger.info("Real-time voice processor initialized")
        
        logger.info("Voice Processing Service started successfully")
        
    except Exception as e:
        logger.error("Failed to initialize Voice Processing Service", error=str(e))
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down Voice Processing Service")
    if realtime_processor:
        await realtime_processor.cleanup()
    if voice_engine:
        await voice_engine.cleanup()
    if speaker_engine:
        await speaker_engine.cleanup()
    if redis_client:
        await redis_client.close()

# Create FastAPI app
app = FastAPI(
    title="Intelligence OS Voice Processing Service",
    description="Real-time speech recognition with multi-speaker support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        await redis_client.ping()
        
        # Check voice engine status
        voice_status = await voice_engine.get_status()
        speaker_status = await speaker_engine.get_status()
        
        return {
            "status": "healthy",
            "service": "voice-processor",
            "version": "1.0.0",
            "components": {
                "redis": "connected",
                "voice_engine": voice_status,
                "speaker_engine": speaker_status
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Voice processing endpoints
@app.post("/process-audio", response_model=VoiceProcessingResponse)
async def process_audio(file: UploadFile = File(...)):
    """Process uploaded audio file"""
    VOICE_PROCESSING_REQUESTS.inc()
    
    with VOICE_PROCESSING_DURATION.time():
        try:
            logger.info("Processing audio file", filename=file.filename)
            
            # Read audio data
            audio_data = await file.read()
            
            # Process audio
            result = await voice_engine.process_audio(
                audio_data=audio_data,
                filename=file.filename
            )
            
            logger.info("Audio processing completed", 
                       transcript_length=len(result.transcript),
                       speakers_detected=len(result.speakers))
            
            return result
            
        except Exception as e:
            logger.error("Audio processing failed", error=str(e))
            raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")

@app.post("/identify-speakers", response_model=SpeakerIdentificationResult)
async def identify_speakers(file: UploadFile = File(...)):
    """Identify speakers in audio file"""
    SPEAKER_IDENTIFICATION_REQUESTS.inc()
    
    try:
        logger.info("Identifying speakers", filename=file.filename)
        
        # Read audio data
        audio_data = await file.read()
        
        # Identify speakers
        result = await speaker_engine.identify_speakers(
            audio_data=audio_data,
            filename=file.filename
        )
        
        logger.info("Speaker identification completed", 
                   speakers_found=len(result.speakers))
        
        return result
        
    except Exception as e:
        logger.error("Speaker identification failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Speaker identification failed: {str(e)}")

@app.post("/process-text")
async def process_text(request: VoiceProcessingRequest):
    """Process text for voice synthesis or analysis"""
    try:
        logger.info("Processing text", text_length=len(request.text))
        
        result = await voice_engine.process_text(request)
        
        return result
        
    except Exception as e:
        logger.error("Text processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Text processing failed: {str(e)}")

# WebSocket endpoint for real-time voice processing
@app.websocket("/ws/realtime")
async def websocket_realtime_voice(websocket: WebSocket):
    """WebSocket endpoint for real-time voice processing"""
    WEBSOCKET_CONNECTIONS.inc()
    
    await websocket.accept()
    logger.info("WebSocket connection established", client=websocket.client)
    
    try:
        # Register client with real-time processor
        client_id = await realtime_processor.register_client(websocket)
        
        while True:
            # Receive audio data from client
            data = await websocket.receive_bytes()
            
            # Process audio in real-time
            await realtime_processor.process_audio_chunk(client_id, data)
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected", client=websocket.client)
        if 'client_id' in locals():
            await realtime_processor.unregister_client(client_id)
    except Exception as e:
        logger.error("WebSocket error", error=str(e), client=websocket.client)
        if 'client_id' in locals():
            await realtime_processor.unregister_client(client_id)

# Configuration endpoints
@app.get("/config")
async def get_config():
    """Get current voice processing configuration"""
    return {
        "voice_models": await voice_engine.get_available_models(),
        "speaker_models": await speaker_engine.get_available_models(),
        "supported_formats": ["wav", "mp3", "m4a", "flac", "ogg"],
        "max_file_size": "100MB",
        "real_time_enabled": True
    }

@app.post("/config/voice-model")
async def set_voice_model(model_name: str):
    """Set the voice recognition model"""
    try:
        await voice_engine.set_model(model_name)
        return {"status": "success", "model": model_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to set model: {str(e)}")

@app.post("/config/speaker-model")
async def set_speaker_model(model_name: str):
    """Set the speaker identification model"""
    try:
        await speaker_engine.set_model(model_name)
        return {"status": "success", "model": model_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to set model: {str(e)}")

# Training endpoints for speaker identification
@app.post("/train-speaker")
async def train_speaker(speaker_name: str, file: UploadFile = File(...)):
    """Train speaker identification with voice sample"""
    try:
        logger.info("Training speaker", speaker_name=speaker_name, filename=file.filename)
        
        audio_data = await file.read()
        
        result = await speaker_engine.train_speaker(
            speaker_name=speaker_name,
            audio_data=audio_data
        )
        
        return result
        
    except Exception as e:
        logger.error("Speaker training failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Speaker training failed: {str(e)}")

@app.get("/speakers")
async def list_speakers():
    """List all trained speakers"""
    return await speaker_engine.list_speakers()

@app.delete("/speakers/{speaker_name}")
async def delete_speaker(speaker_name: str):
    """Delete a trained speaker"""
    try:
        await speaker_engine.delete_speaker(speaker_name)
        return {"status": "success", "message": f"Speaker {speaker_name} deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete speaker: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8002))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("FLASK_ENV") == "development",
        log_config=None  # Use structlog configuration
    )