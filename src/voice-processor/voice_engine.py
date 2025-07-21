"""
Voice Processing Engine for Intelligence OS
Handles speech recognition, audio processing, and voice synthesis
"""

import os
import io
import asyncio
import tempfile
import logging
from typing import Dict, List, Optional, Any, Union
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
import speech_recognition as sr
import openai
import whisper
import noisereduce as nr
from datetime import datetime
import structlog

from models import (
    VoiceProcessingResponse, TranscriptSegment, AudioMetadata, 
    AudioFormat, VoiceProvider, ProcessingStatus, AudioQualityMetrics
)

logger = structlog.get_logger(__name__)

class VoiceProcessingEngine:
    """Main voice processing engine"""
    
    def __init__(self):
        self.openai_client = None
        self.whisper_model = None
        self.speech_recognizer = None
        self.supported_formats = [
            AudioFormat.WAV, AudioFormat.MP3, AudioFormat.M4A, 
            AudioFormat.FLAC, AudioFormat.OGG, AudioFormat.WEBM
        ]
        self.current_provider = VoiceProvider.OPENAI
        self.processing_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_processing_time': 0.0
        }
    
    async def initialize(self):
        """Initialize the voice processing engine"""
        try:
            # Initialize OpenAI client
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized")
            
            # Initialize Whisper model
            whisper_model_name = os.getenv('WHISPER_MODEL', 'base')
            self.whisper_model = whisper.load_model(whisper_model_name)
            logger.info("Whisper model loaded", model=whisper_model_name)
            
            # Initialize speech recognizer
            self.speech_recognizer = sr.Recognizer()
            logger.info("Speech recognizer initialized")
            
            logger.info("Voice processing engine initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize voice processing engine", error=str(e))
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up voice processing engine")
        # Add cleanup logic if needed
    
    async def get_status(self) -> str:
        """Get engine status"""
        return "ready"
    
    async def process_audio(self, audio_data: bytes, filename: str = None) -> VoiceProcessingResponse:
        """Process audio data and return transcription with metadata"""
        start_time = datetime.utcnow()
        self.processing_stats['total_requests'] += 1
        
        try:
            logger.info("Starting audio processing", filename=filename, size=len(audio_data))
            
            # Convert audio data to proper format
            audio_segment, metadata = await self._prepare_audio(audio_data, filename)
            
            # Assess audio quality
            quality_metrics = await self._assess_audio_quality(audio_segment)
            
            # Apply noise reduction if needed
            if quality_metrics.signal_to_noise_ratio < 10:  # SNR threshold
                audio_segment = await self._reduce_noise(audio_segment)
                logger.info("Noise reduction applied")
            
            # Perform speech recognition
            transcript_result = await self._transcribe_audio(audio_segment)
            
            # Create response
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.processing_stats['successful_requests'] += 1
            self.processing_stats['total_processing_time'] += processing_time
            
            response = VoiceProcessingResponse(
                id=f"voice_{int(datetime.utcnow().timestamp())}",
                status=ProcessingStatus.COMPLETED,
                transcript=transcript_result['text'],
                segments=transcript_result['segments'],
                speakers=transcript_result.get('speakers', []),
                metadata=metadata,
                confidence=transcript_result['confidence'],
                processing_time=processing_time,
                language_detected=transcript_result.get('language', 'en')
            )
            
            logger.info("Audio processing completed", 
                       processing_time=processing_time,
                       transcript_length=len(response.transcript))
            
            return response
            
        except Exception as e:
            self.processing_stats['failed_requests'] += 1
            logger.error("Audio processing failed", error=str(e))
            raise
    
    async def _prepare_audio(self, audio_data: bytes, filename: str = None) -> tuple:
        """Prepare audio data for processing"""
        try:
            # Detect format from filename or data
            audio_format = self._detect_audio_format(audio_data, filename)
            
            # Load audio using pydub
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format=audio_format.value)
            
            # Convert to standard format (16kHz, mono, 16-bit)
            audio_segment = audio_segment.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            
            # Create metadata
            metadata = AudioMetadata(
                duration=len(audio_segment) / 1000.0,  # Convert to seconds
                sample_rate=audio_segment.frame_rate,
                channels=audio_segment.channels,
                format=AudioFormat.WAV,  # Standardized format
                size_bytes=len(audio_data)
            )
            
            return audio_segment, metadata
            
        except Exception as e:
            logger.error("Audio preparation failed", error=str(e))
            raise
    
    def _detect_audio_format(self, audio_data: bytes, filename: str = None) -> AudioFormat:
        """Detect audio format from data or filename"""
        if filename:
            extension = filename.lower().split('.')[-1]
            format_map = {
                'wav': AudioFormat.WAV,
                'mp3': AudioFormat.MP3,
                'm4a': AudioFormat.M4A,
                'flac': AudioFormat.FLAC,
                'ogg': AudioFormat.OGG,
                'webm': AudioFormat.WEBM
            }
            return format_map.get(extension, AudioFormat.WAV)
        
        # Try to detect from data headers
        if audio_data.startswith(b'RIFF'):
            return AudioFormat.WAV
        elif audio_data.startswith(b'ID3') or audio_data.startswith(b'\xff\xfb'):
            return AudioFormat.MP3
        elif audio_data.startswith(b'fLaC'):
            return AudioFormat.FLAC
        elif audio_data.startswith(b'OggS'):
            return AudioFormat.OGG
        else:
            return AudioFormat.WAV  # Default
    
    async def _assess_audio_quality(self, audio_segment: AudioSegment) -> AudioQualityMetrics:
        """Assess audio quality metrics"""
        try:
            # Convert to numpy array for analysis
            audio_array = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
            audio_array = audio_array / np.max(np.abs(audio_array))  # Normalize
            
            # Calculate signal-to-noise ratio
            signal_power = np.mean(audio_array ** 2)
            noise_power = np.var(audio_array - np.mean(audio_array))
            snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
            
            # Calculate clarity score (simplified)
            clarity_score = min(1.0, max(0.0, (snr + 10) / 30))
            
            # Calculate volume level
            volume_level = np.sqrt(np.mean(audio_array ** 2))
            
            # Frequency analysis
            fft = np.fft.fft(audio_array)
            freqs = np.fft.fftfreq(len(fft), 1/audio_segment.frame_rate)
            magnitude = np.abs(fft)
            
            frequency_range = {
                'low': np.mean(magnitude[(freqs >= 80) & (freqs <= 250)]),
                'mid': np.mean(magnitude[(freqs >= 250) & (freqs <= 2000)]),
                'high': np.mean(magnitude[(freqs >= 2000) & (freqs <= 8000)])
            }
            
            # Distortion level (simplified)
            distortion_level = min(1.0, np.std(audio_array) / (np.mean(np.abs(audio_array)) + 1e-10))
            
            return AudioQualityMetrics(
                signal_to_noise_ratio=snr,
                clarity_score=clarity_score,
                volume_level=volume_level,
                frequency_range=frequency_range,
                distortion_level=distortion_level
            )
            
        except Exception as e:
            logger.error("Audio quality assessment failed", error=str(e))
            # Return default metrics
            return AudioQualityMetrics(
                signal_to_noise_ratio=15.0,
                clarity_score=0.7,
                volume_level=0.5,
                frequency_range={'low': 0.3, 'mid': 0.5, 'high': 0.2},
                distortion_level=0.1
            )
    
    async def _reduce_noise(self, audio_segment: AudioSegment) -> AudioSegment:
        """Apply noise reduction to audio"""
        try:
            # Convert to numpy array
            audio_array = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
            sample_rate = audio_segment.frame_rate
            
            # Apply noise reduction
            reduced_noise = nr.reduce_noise(y=audio_array, sr=sample_rate)
            
            # Convert back to AudioSegment
            reduced_audio = AudioSegment(
                reduced_noise.tobytes(),
                frame_rate=sample_rate,
                sample_width=audio_segment.sample_width,
                channels=audio_segment.channels
            )
            
            return reduced_audio
            
        except Exception as e:
            logger.error("Noise reduction failed", error=str(e))
            return audio_segment  # Return original if noise reduction fails
    
    async def _transcribe_audio(self, audio_segment: AudioSegment) -> Dict[str, Any]:
        """Transcribe audio using the configured provider"""
        if self.current_provider == VoiceProvider.OPENAI and self.openai_client:
            return await self._transcribe_with_openai(audio_segment)
        elif self.current_provider == VoiceProvider.WHISPER and self.whisper_model:
            return await self._transcribe_with_whisper(audio_segment)
        else:
            return await self._transcribe_with_speech_recognition(audio_segment)
    
    async def _transcribe_with_openai(self, audio_segment: AudioSegment) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API"""
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                audio_segment.export(temp_file.name, format='wav')
                
                # Transcribe with OpenAI
                with open(temp_file.name, 'rb') as audio_file:
                    transcript = await self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"]
                    )
                
                # Clean up temp file
                os.unlink(temp_file.name)
            
            # Process segments
            segments = []
            for i, segment in enumerate(transcript.segments):
                segments.append(TranscriptSegment(
                    id=f"segment_{i}",
                    text=segment.text.strip(),
                    start_time=segment.start,
                    end_time=segment.end,
                    confidence=0.9  # OpenAI doesn't provide confidence scores
                ))
            
            return {
                'text': transcript.text,
                'segments': segments,
                'confidence': 0.9,
                'language': transcript.language
            }
            
        except Exception as e:
            logger.error("OpenAI transcription failed", error=str(e))
            raise
    
    async def _transcribe_with_whisper(self, audio_segment: AudioSegment) -> Dict[str, Any]:
        """Transcribe using local Whisper model"""
        try:
            # Convert to numpy array for Whisper
            audio_array = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
            audio_array = audio_array / np.max(np.abs(audio_array))  # Normalize
            
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(audio_array)
            
            # Process segments
            segments = []
            for i, segment in enumerate(result['segments']):
                segments.append(TranscriptSegment(
                    id=f"segment_{i}",
                    text=segment['text'].strip(),
                    start_time=segment['start'],
                    end_time=segment['end'],
                    confidence=segment.get('confidence', 0.8)
                ))
            
            return {
                'text': result['text'],
                'segments': segments,
                'confidence': 0.8,
                'language': result.get('language', 'en')
            }
            
        except Exception as e:
            logger.error("Whisper transcription failed", error=str(e))
            raise
    
    async def _transcribe_with_speech_recognition(self, audio_segment: AudioSegment) -> Dict[str, Any]:
        """Transcribe using SpeechRecognition library"""
        try:
            # Convert to wav format for speech_recognition
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                audio_segment.export(temp_file.name, format='wav')
                
                # Load with speech_recognition
                with sr.AudioFile(temp_file.name) as source:
                    audio = self.speech_recognizer.record(source)
                
                # Clean up temp file
                os.unlink(temp_file.name)
            
            # Transcribe
            text = self.speech_recognizer.recognize_google(audio)
            
            # Create single segment (speech_recognition doesn't provide timestamps)
            segments = [TranscriptSegment(
                id="segment_0",
                text=text,
                start_time=0.0,
                end_time=len(audio_segment) / 1000.0,
                confidence=0.7
            )]
            
            return {
                'text': text,
                'segments': segments,
                'confidence': 0.7,
                'language': 'en'
            }
            
        except Exception as e:
            logger.error("Speech recognition transcription failed", error=str(e))
            raise
    
    async def process_text(self, request) -> Dict[str, Any]:
        """Process text for voice synthesis or analysis"""
        # Placeholder for text processing functionality
        return {
            'status': 'success',
            'processed_text': request.text,
            'analysis': {
                'word_count': len(request.text.split()),
                'character_count': len(request.text),
                'language': 'en'
            }
        }
    
    async def get_available_models(self) -> List[str]:
        """Get list of available voice models"""
        models = ['whisper-base', 'whisper-small', 'whisper-medium', 'whisper-large']
        if self.openai_client:
            models.append('openai-whisper-1')
        return models
    
    async def set_model(self, model_name: str):
        """Set the voice recognition model"""
        if 'openai' in model_name.lower():
            self.current_provider = VoiceProvider.OPENAI
        elif 'whisper' in model_name.lower():
            self.current_provider = VoiceProvider.WHISPER
            # Reload Whisper model if different
            if model_name != f"whisper-{self.whisper_model.model_name}":
                whisper_model_name = model_name.replace('whisper-', '')
                self.whisper_model = whisper.load_model(whisper_model_name)
        
        logger.info("Voice model changed", model=model_name, provider=self.current_provider)