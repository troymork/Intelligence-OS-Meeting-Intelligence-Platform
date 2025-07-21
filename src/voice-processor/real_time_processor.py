"""
Real-Time Voice Processor for Intelligence OS
Handles real-time voice processing and WebSocket connections
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import numpy as np
from datetime import datetime
import structlog
import redis.asyncio as redis
from fastapi import WebSocket
import uuid

from models import (
    RealTimeAudioChunk, RealTimeTranscriptUpdate, WebSocketMessage,
    VoiceProcessingConfig, ProcessingStatus
)

logger = structlog.get_logger(__name__)

class RealTimeVoiceProcessor:
    """Real-time voice processing manager"""
    
    def __init__(self, voice_engine, speaker_engine, redis_client):
        self.voice_engine = voice_engine
        self.speaker_engine = speaker_engine
        self.redis_client = redis_client
        
        # Active connections
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        
        # Processing configuration
        self.chunk_duration = 2.0  # seconds
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        
        # Buffer management
        self.audio_buffers: Dict[str, List[bytes]] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        
    async def initialize(self):
        """Initialize the real-time processor"""
        try:
            logger.info("Initializing real-time voice processor")
            
            # Start background processing task
            self.background_task = asyncio.create_task(self._background_processor())
            
            logger.info("Real-time voice processor initialized")
            
        except Exception as e:
            logger.error("Failed to initialize real-time processor", error=str(e))
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up real-time voice processor")
        
        # Cancel background task
        if hasattr(self, 'background_task'):
            self.background_task.cancel()
        
        # Cancel all processing tasks
        for task in self.processing_tasks.values():
            task.cancel()
        
        # Close all connections
        for client_id in list(self.active_connections.keys()):
            await self.unregister_client(client_id)
    
    async def register_client(self, websocket: WebSocket) -> str:
        """Register a new WebSocket client"""
        client_id = str(uuid.uuid4())
        
        self.active_connections[client_id] = {
            'websocket': websocket,
            'session_id': f"session_{client_id}",
            'connected_at': datetime.utcnow(),
            'config': VoiceProcessingConfig(),
            'last_activity': datetime.utcnow(),
            'transcript_buffer': [],
            'speaker_context': {}
        }
        
        self.audio_buffers[client_id] = []
        
        logger.info("Client registered", client_id=client_id)
        
        # Send welcome message
        await self._send_message(client_id, {
            'type': 'connection_established',
            'data': {
                'client_id': client_id,
                'session_id': self.active_connections[client_id]['session_id'],
                'config': self.active_connections[client_id]['config'].dict()
            }
        })
        
        return client_id
    
    async def unregister_client(self, client_id: str):
        """Unregister a WebSocket client"""
        if client_id in self.active_connections:
            # Cancel processing task if exists
            if client_id in self.processing_tasks:
                self.processing_tasks[client_id].cancel()
                del self.processing_tasks[client_id]
            
            # Clean up buffers
            if client_id in self.audio_buffers:
                del self.audio_buffers[client_id]
            
            # Remove connection
            del self.active_connections[client_id]
            
            logger.info("Client unregistered", client_id=client_id)
    
    async def process_audio_chunk(self, client_id: str, audio_data: bytes):
        """Process incoming audio chunk from client"""
        if client_id not in self.active_connections:
            logger.warning("Received audio from unregistered client", client_id=client_id)
            return
        
        try:
            # Update last activity
            self.active_connections[client_id]['last_activity'] = datetime.utcnow()
            
            # Add to buffer
            self.audio_buffers[client_id].append(audio_data)
            
            # Check if we have enough data to process
            total_samples = sum(len(chunk) for chunk in self.audio_buffers[client_id]) // 2  # 16-bit samples
            
            if total_samples >= self.chunk_size:
                # Start processing task if not already running
                if client_id not in self.processing_tasks or self.processing_tasks[client_id].done():
                    self.processing_tasks[client_id] = asyncio.create_task(
                        self._process_client_audio(client_id)
                    )
        
        except Exception as e:
            logger.error("Error processing audio chunk", client_id=client_id, error=str(e))
    
    async def _process_client_audio(self, client_id: str):
        """Process accumulated audio for a client"""
        try:
            if client_id not in self.audio_buffers or not self.audio_buffers[client_id]:
                return
            
            # Combine audio chunks
            combined_audio = b''.join(self.audio_buffers[client_id])
            
            # Clear buffer (keep last chunk for overlap)
            if len(self.audio_buffers[client_id]) > 1:
                self.audio_buffers[client_id] = [self.audio_buffers[client_id][-1]]
            else:
                self.audio_buffers[client_id] = []
            
            # Create audio chunk object
            chunk_id = f"chunk_{int(datetime.utcnow().timestamp())}"
            audio_chunk = RealTimeAudioChunk(
                chunk_id=chunk_id,
                audio_data=combined_audio,
                timestamp=datetime.utcnow(),
                sample_rate=self.sample_rate,
                channels=self.channels
            )
            
            # Process with voice engine (simplified for real-time)
            transcript_result = await self._quick_transcribe(combined_audio)
            
            # Perform speaker identification if enabled
            speaker_id = None
            if self.active_connections[client_id]['config'].speaker_diarization.enabled:
                speaker_id = await self._quick_speaker_identification(combined_audio, client_id)
            
            # Create transcript update
            transcript_update = RealTimeTranscriptUpdate(
                session_id=self.active_connections[client_id]['session_id'],
                chunk_id=chunk_id,
                text=transcript_result['text'],
                is_final=transcript_result['is_final'],
                confidence=transcript_result['confidence'],
                speaker=speaker_id,
                timestamp=datetime.utcnow()
            )
            
            # Send to client
            await self._send_message(client_id, {
                'type': 'transcript_update',
                'data': transcript_update.dict()
            })
            
            # Store in Redis for persistence
            await self._store_transcript_update(client_id, transcript_update)
            
            logger.debug("Processed audio chunk", 
                        client_id=client_id, 
                        chunk_id=chunk_id,
                        text_length=len(transcript_result['text']))
        
        except Exception as e:
            logger.error("Error in client audio processing", client_id=client_id, error=str(e))
    
    async def _quick_transcribe(self, audio_data: bytes) -> Dict[str, Any]:
        """Quick transcription for real-time processing"""
        try:
            # Use a faster, less accurate model for real-time processing
            # This is a simplified version - in production you might use streaming ASR
            
            # Convert audio data to format expected by voice engine
            from pydub import AudioSegment
            import io
            
            audio_segment = AudioSegment.from_raw(
                io.BytesIO(audio_data),
                sample_width=2,  # 16-bit
                frame_rate=self.sample_rate,
                channels=self.channels
            )
            
            # Quick transcription (using simpler method for speed)
            result = await self.voice_engine._transcribe_with_speech_recognition(audio_segment)
            
            return {
                'text': result['text'],
                'confidence': result['confidence'],
                'is_final': True  # For simplicity, treating all as final
            }
            
        except Exception as e:
            logger.error("Quick transcription failed", error=str(e))
            return {
                'text': '',
                'confidence': 0.0,
                'is_final': True
            }
    
    async def _quick_speaker_identification(self, audio_data: bytes, client_id: str) -> Optional[str]:
        """Quick speaker identification for real-time processing"""
        try:
            # Simplified speaker identification for real-time
            # In production, you might use streaming speaker diarization
            
            from pydub import AudioSegment
            import io
            
            audio_segment = AudioSegment.from_raw(
                io.BytesIO(audio_data),
                sample_width=2,
                frame_rate=self.sample_rate,
                channels=self.channels
            )
            
            # Extract simple features for speaker comparison
            audio_array = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
            embedding = self.speaker_engine._extract_speaker_embedding(audio_array, self.sample_rate)
            
            # Compare with known speakers (simplified)
            best_match = None
            best_similarity = 0.0
            
            for speaker_name, known_embedding in self.speaker_engine.speaker_embeddings.items():
                from sklearn.metrics.pairwise import cosine_similarity
                similarity = cosine_similarity([embedding], [known_embedding])[0][0]
                
                if similarity > best_similarity and similarity > 0.7:
                    best_similarity = similarity
                    best_match = speaker_name
            
            return best_match
            
        except Exception as e:
            logger.error("Quick speaker identification failed", error=str(e))
            return None
    
    async def _send_message(self, client_id: str, message_data: Dict[str, Any]):
        """Send message to WebSocket client"""
        if client_id not in self.active_connections:
            return
        
        try:
            websocket = self.active_connections[client_id]['websocket']
            message = WebSocketMessage(
                type=message_data['type'],
                data=message_data['data'],
                session_id=self.active_connections[client_id]['session_id']
            )
            
            await websocket.send_text(message.json())
            
        except Exception as e:
            logger.error("Failed to send message to client", client_id=client_id, error=str(e))
            # Remove disconnected client
            await self.unregister_client(client_id)
    
    async def _store_transcript_update(self, client_id: str, transcript_update: RealTimeTranscriptUpdate):
        """Store transcript update in Redis"""
        try:
            key = f"transcript:{transcript_update.session_id}"
            value = transcript_update.json()
            
            # Store with expiration (24 hours)
            await self.redis_client.lpush(key, value)
            await self.redis_client.expire(key, 86400)
            
        except Exception as e:
            logger.error("Failed to store transcript update", error=str(e))
    
    async def _background_processor(self):
        """Background task for cleanup and maintenance"""
        while True:
            try:
                await asyncio.sleep(30)  # Run every 30 seconds
                
                # Clean up inactive connections
                current_time = datetime.utcnow()
                inactive_clients = []
                
                for client_id, connection_info in self.active_connections.items():
                    last_activity = connection_info['last_activity']
                    if (current_time - last_activity).total_seconds() > 300:  # 5 minutes timeout
                        inactive_clients.append(client_id)
                
                for client_id in inactive_clients:
                    logger.info("Removing inactive client", client_id=client_id)
                    await self.unregister_client(client_id)
                
                # Log statistics
                logger.info("Real-time processor stats", 
                           active_connections=len(self.active_connections),
                           processing_tasks=len(self.processing_tasks))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Background processor error", error=str(e))
    
    async def get_session_transcript(self, session_id: str) -> List[RealTimeTranscriptUpdate]:
        """Get complete transcript for a session"""
        try:
            key = f"transcript:{session_id}"
            transcript_data = await self.redis_client.lrange(key, 0, -1)
            
            transcripts = []
            for data in transcript_data:
                transcript_update = RealTimeTranscriptUpdate.parse_raw(data)
                transcripts.append(transcript_update)
            
            # Sort by timestamp
            transcripts.sort(key=lambda x: x.timestamp)
            return transcripts
            
        except Exception as e:
            logger.error("Failed to get session transcript", error=str(e))
            return []
    
    async def update_client_config(self, client_id: str, config: VoiceProcessingConfig):
        """Update configuration for a client"""
        if client_id in self.active_connections:
            self.active_connections[client_id]['config'] = config
            
            # Send config update to client
            await self._send_message(client_id, {
                'type': 'config_updated',
                'data': config.dict()
            })
            
            logger.info("Client config updated", client_id=client_id)