"""
Data models for Voice Processing Service
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum

class AudioFormat(str, Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    M4A = "m4a"
    FLAC = "flac"
    OGG = "ogg"
    WEBM = "webm"

class VoiceProvider(str, Enum):
    """Voice processing providers"""
    OPENAI = "openai"
    GOOGLE = "google"
    AZURE = "azure"
    WHISPER = "whisper"

class ProcessingStatus(str, Enum):
    """Processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscriptSegment(BaseModel):
    """Individual transcript segment"""
    id: str
    text: str
    start_time: float
    end_time: float
    speaker: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    language: Optional[str] = None
    
class Speaker(BaseModel):
    """Speaker information"""
    id: str
    name: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    segments: List[str] = Field(default_factory=list)  # Segment IDs
    voice_characteristics: Dict[str, Any] = Field(default_factory=dict)
    
class AudioMetadata(BaseModel):
    """Audio file metadata"""
    duration: float
    sample_rate: int
    channels: int
    format: AudioFormat
    size_bytes: int
    quality_score: Optional[float] = None
    noise_level: Optional[float] = None

class VoiceProcessingRequest(BaseModel):
    """Request for voice processing"""
    text: Optional[str] = None
    audio_url: Optional[str] = None
    language: str = "en-US"
    provider: VoiceProvider = VoiceProvider.OPENAI
    enable_speaker_identification: bool = True
    enable_noise_reduction: bool = True
    enable_diarization: bool = True
    custom_vocabulary: List[str] = Field(default_factory=list)
    meeting_context: Optional[Dict[str, Any]] = None

class VoiceProcessingResponse(BaseModel):
    """Response from voice processing"""
    id: str
    status: ProcessingStatus
    transcript: str
    segments: List[TranscriptSegment]
    speakers: List[Speaker]
    metadata: AudioMetadata
    confidence: float = Field(ge=0.0, le=1.0)
    processing_time: float
    language_detected: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
class SpeakerIdentificationResult(BaseModel):
    """Result from speaker identification"""
    speakers: List[Speaker]
    total_speakers: int
    confidence: float = Field(ge=0.0, le=1.0)
    processing_time: float
    method_used: str

class RealTimeAudioChunk(BaseModel):
    """Real-time audio chunk"""
    chunk_id: str
    audio_data: bytes
    timestamp: datetime
    sample_rate: int = 16000
    channels: int = 1

class RealTimeTranscriptUpdate(BaseModel):
    """Real-time transcript update"""
    session_id: str
    chunk_id: str
    text: str
    is_final: bool
    confidence: float
    speaker: Optional[str] = None
    timestamp: datetime

class VoiceCommand(BaseModel):
    """Voice command recognition"""
    command: str
    intent: str
    entities: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    
class VoiceResponse(BaseModel):
    """Voice response generation"""
    text: str
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    voice_id: Optional[str] = None

class SpeakerTrainingRequest(BaseModel):
    """Request for speaker training"""
    speaker_name: str
    audio_samples: List[str]  # URLs or file paths
    voice_characteristics: Optional[Dict[str, Any]] = None

class SpeakerTrainingResponse(BaseModel):
    """Response from speaker training"""
    speaker_id: str
    speaker_name: str
    training_status: ProcessingStatus
    accuracy_score: Optional[float] = None
    samples_processed: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NoiseReductionConfig(BaseModel):
    """Noise reduction configuration"""
    enabled: bool = True
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    preserve_speech: bool = True
    
class SpeakerDiarizationConfig(BaseModel):
    """Speaker diarization configuration"""
    enabled: bool = True
    min_speakers: int = 1
    max_speakers: int = 10
    clustering_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class VoiceProcessingConfig(BaseModel):
    """Voice processing configuration"""
    provider: VoiceProvider = VoiceProvider.OPENAI
    language: str = "en-US"
    model: Optional[str] = None
    noise_reduction: NoiseReductionConfig = Field(default_factory=NoiseReductionConfig)
    speaker_diarization: SpeakerDiarizationConfig = Field(default_factory=SpeakerDiarizationConfig)
    enable_punctuation: bool = True
    enable_profanity_filter: bool = False
    custom_vocabulary: List[str] = Field(default_factory=list)

class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str  # 'audio', 'config', 'command', 'response'
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None

class AudioQualityMetrics(BaseModel):
    """Audio quality assessment metrics"""
    signal_to_noise_ratio: float
    clarity_score: float = Field(ge=0.0, le=1.0)
    volume_level: float
    frequency_range: Dict[str, float]
    distortion_level: float = Field(ge=0.0, le=1.0)
    
class ProcessingStats(BaseModel):
    """Processing statistics"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_processing_time: float
    average_confidence: float
    uptime: float
    
class ServiceStatus(BaseModel):
    """Service status information"""
    status: str
    version: str
    uptime: float
    active_sessions: int
    processing_queue_size: int
    available_models: List[str]
    system_resources: Dict[str, Any]
    last_health_check: datetime = Field(default_factory=datetime.utcnow)