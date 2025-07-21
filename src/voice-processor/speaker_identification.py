"""
Speaker Identification Engine for Intelligence OS
Handles speaker diarization and identification
"""

import os
import io
import asyncio
import tempfile
import pickle
import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
import torch
from datetime import datetime
import structlog

from models import Speaker, SpeakerIdentificationResult, SpeakerTrainingResponse, ProcessingStatus

logger = structlog.get_logger(__name__)

class SpeakerIdentificationEngine:
    """Speaker identification and diarization engine"""
    
    def __init__(self):
        self.speaker_embeddings = {}  # Store trained speaker embeddings
        self.speaker_models_path = "models/speakers"
        self.embedding_model = None
        self.clustering_threshold = 0.7
        self.min_segment_duration = 1.0  # Minimum segment duration in seconds
        
    async def initialize(self):
        """Initialize the speaker identification engine"""
        try:
            # Create models directory
            os.makedirs(self.speaker_models_path, exist_ok=True)
            
            # Load pre-trained speaker embeddings
            await self._load_speaker_models()
            
            # Initialize embedding model (using a simple MFCC-based approach for now)
            # In production, you might want to use more sophisticated models like:
            # - pyannote.audio
            # - SpeechBrain
            # - Resemblyzer
            logger.info("Speaker identification engine initialized")
            
        except Exception as e:
            logger.error("Failed to initialize speaker identification engine", error=str(e))
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up speaker identification engine")
    
    async def get_status(self) -> str:
        """Get engine status"""
        return "ready"
    
    async def identify_speakers(self, audio_data: bytes, filename: str = None) -> SpeakerIdentificationResult:
        """Identify speakers in audio data"""
        start_time = datetime.utcnow()
        
        try:
            logger.info("Starting speaker identification", filename=filename)
            
            # Convert audio data
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
            audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
            
            # Perform speaker diarization
            speakers = await self._perform_diarization(audio_segment)
            
            # Identify known speakers
            identified_speakers = await self._identify_known_speakers(speakers, audio_segment)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = SpeakerIdentificationResult(
                speakers=identified_speakers,
                total_speakers=len(identified_speakers),
                confidence=self._calculate_overall_confidence(identified_speakers),
                processing_time=processing_time,
                method_used="mfcc_clustering"
            )
            
            logger.info("Speaker identification completed", 
                       speakers_found=len(identified_speakers),
                       processing_time=processing_time)
            
            return result
            
        except Exception as e:
            logger.error("Speaker identification failed", error=str(e))
            raise
    
    async def _perform_diarization(self, audio_segment: AudioSegment) -> List[Dict[str, Any]]:
        """Perform speaker diarization to separate different speakers"""
        try:
            # Convert to numpy array
            audio_array = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
            sample_rate = audio_segment.frame_rate
            
            # Segment audio into windows
            window_size = int(sample_rate * 2.0)  # 2-second windows
            hop_size = int(sample_rate * 1.0)     # 1-second hop
            
            segments = []
            embeddings = []
            
            for i in range(0, len(audio_array) - window_size, hop_size):
                segment = audio_array[i:i + window_size]
                start_time = i / sample_rate
                end_time = (i + window_size) / sample_rate
                
                # Extract features (MFCC-based embedding)
                embedding = self._extract_speaker_embedding(segment, sample_rate)
                
                segments.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'embedding': embedding,
                    'audio_data': segment
                })
                embeddings.append(embedding)
            
            if not embeddings:
                return []
            
            # Cluster segments by speaker
            embeddings_array = np.array(embeddings)
            
            # Use agglomerative clustering
            n_clusters = self._estimate_speaker_count(embeddings_array)
            clustering = AgglomerativeClustering(
                n_clusters=n_clusters,
                linkage='average',
                metric='cosine'
            )
            
            cluster_labels = clustering.fit_predict(embeddings_array)
            
            # Group segments by speaker
            speakers = {}
            for segment, label in zip(segments, cluster_labels):
                speaker_id = f"speaker_{label}"
                if speaker_id not in speakers:
                    speakers[speaker_id] = {
                        'id': speaker_id,
                        'segments': [],
                        'embeddings': []
                    }
                speakers[speaker_id]['segments'].append(segment)
                speakers[speaker_id]['embeddings'].append(segment['embedding'])
            
            # Calculate average embeddings for each speaker
            for speaker_id, speaker_data in speakers.items():
                speaker_data['average_embedding'] = np.mean(speaker_data['embeddings'], axis=0)
            
            return list(speakers.values())
            
        except Exception as e:
            logger.error("Speaker diarization failed", error=str(e))
            return []
    
    def _extract_speaker_embedding(self, audio_segment: np.ndarray, sample_rate: int) -> np.ndarray:
        """Extract speaker embedding from audio segment"""
        try:
            # Extract MFCC features
            mfccs = librosa.feature.mfcc(
                y=audio_segment,
                sr=sample_rate,
                n_mfcc=13,
                n_fft=2048,
                hop_length=512
            )
            
            # Calculate statistics over time
            mfcc_mean = np.mean(mfccs, axis=1)
            mfcc_std = np.std(mfccs, axis=1)
            mfcc_delta = librosa.feature.delta(mfccs)
            mfcc_delta_mean = np.mean(mfcc_delta, axis=1)
            
            # Combine features
            embedding = np.concatenate([mfcc_mean, mfcc_std, mfcc_delta_mean])
            
            return embedding
            
        except Exception as e:
            logger.error("Feature extraction failed", error=str(e))
            return np.zeros(39)  # Return zero vector if extraction fails
    
    def _estimate_speaker_count(self, embeddings: np.ndarray) -> int:
        """Estimate the number of speakers using silhouette analysis"""
        try:
            if len(embeddings) < 2:
                return 1
            
            max_speakers = min(10, len(embeddings) // 2)
            best_score = -1
            best_n_clusters = 1
            
            for n_clusters in range(2, max_speakers + 1):
                clustering = AgglomerativeClustering(
                    n_clusters=n_clusters,
                    linkage='average',
                    metric='cosine'
                )
                labels = clustering.fit_predict(embeddings)
                
                # Calculate silhouette score
                from sklearn.metrics import silhouette_score
                score = silhouette_score(embeddings, labels, metric='cosine')
                
                if score > best_score:
                    best_score = score
                    best_n_clusters = n_clusters
            
            return best_n_clusters
            
        except Exception as e:
            logger.error("Speaker count estimation failed", error=str(e))
            return 2  # Default to 2 speakers
    
    async def _identify_known_speakers(self, diarized_speakers: List[Dict], audio_segment: AudioSegment) -> List[Speaker]:
        """Identify known speakers from diarized segments"""
        identified_speakers = []
        
        for i, speaker_data in enumerate(diarized_speakers):
            speaker_embedding = speaker_data['average_embedding']
            
            # Try to match with known speakers
            best_match = None
            best_similarity = 0.0
            
            for known_speaker_name, known_embedding in self.speaker_embeddings.items():
                similarity = cosine_similarity(
                    [speaker_embedding], 
                    [known_embedding]
                )[0][0]
                
                if similarity > best_similarity and similarity > self.clustering_threshold:
                    best_similarity = similarity
                    best_match = known_speaker_name
            
            # Create speaker object
            speaker_id = f"speaker_{i}"
            speaker_name = best_match if best_match else None
            confidence = best_similarity if best_match else 0.5
            
            # Get segment IDs for this speaker
            segment_ids = [f"segment_{j}" for j, seg in enumerate(speaker_data['segments'])]
            
            # Calculate voice characteristics
            voice_characteristics = self._analyze_voice_characteristics(speaker_data['segments'])
            
            speaker = Speaker(
                id=speaker_id,
                name=speaker_name,
                confidence=confidence,
                segments=segment_ids,
                voice_characteristics=voice_characteristics
            )
            
            identified_speakers.append(speaker)
        
        return identified_speakers
    
    def _analyze_voice_characteristics(self, segments: List[Dict]) -> Dict[str, Any]:
        """Analyze voice characteristics from speaker segments"""
        try:
            all_audio = []
            for segment in segments:
                all_audio.extend(segment['audio_data'])
            
            if not all_audio:
                return {}
            
            audio_array = np.array(all_audio, dtype=np.float32)
            
            # Calculate basic characteristics
            characteristics = {
                'average_pitch': float(np.mean(audio_array)),
                'pitch_variance': float(np.var(audio_array)),
                'speaking_rate': len(segments) / sum(seg['end_time'] - seg['start_time'] for seg in segments),
                'volume_level': float(np.sqrt(np.mean(audio_array ** 2))),
                'total_speaking_time': sum(seg['end_time'] - seg['start_time'] for seg in segments)
            }
            
            return characteristics
            
        except Exception as e:
            logger.error("Voice characteristics analysis failed", error=str(e))
            return {}
    
    def _calculate_overall_confidence(self, speakers: List[Speaker]) -> float:
        """Calculate overall confidence score for speaker identification"""
        if not speakers:
            return 0.0
        
        return sum(speaker.confidence for speaker in speakers) / len(speakers)
    
    async def train_speaker(self, speaker_name: str, audio_data: bytes) -> SpeakerTrainingResponse:
        """Train speaker identification with voice sample"""
        try:
            logger.info("Training speaker", speaker_name=speaker_name)
            
            # Convert audio data
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
            audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
            
            # Extract speaker embedding
            audio_array = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
            embedding = self._extract_speaker_embedding(audio_array, audio_segment.frame_rate)
            
            # Store embedding
            self.speaker_embeddings[speaker_name] = embedding
            
            # Save to disk
            await self._save_speaker_model(speaker_name, embedding)
            
            response = SpeakerTrainingResponse(
                speaker_id=f"speaker_{len(self.speaker_embeddings)}",
                speaker_name=speaker_name,
                training_status=ProcessingStatus.COMPLETED,
                accuracy_score=0.9,  # Placeholder
                samples_processed=1
            )
            
            logger.info("Speaker training completed", speaker_name=speaker_name)
            return response
            
        except Exception as e:
            logger.error("Speaker training failed", error=str(e))
            raise
    
    async def _save_speaker_model(self, speaker_name: str, embedding: np.ndarray):
        """Save speaker model to disk"""
        try:
            model_path = os.path.join(self.speaker_models_path, f"{speaker_name}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(embedding, f)
            logger.info("Speaker model saved", speaker_name=speaker_name, path=model_path)
        except Exception as e:
            logger.error("Failed to save speaker model", error=str(e))
    
    async def _load_speaker_models(self):
        """Load all saved speaker models"""
        try:
            if not os.path.exists(self.speaker_models_path):
                return
            
            for filename in os.listdir(self.speaker_models_path):
                if filename.endswith('.pkl'):
                    speaker_name = filename[:-4]  # Remove .pkl extension
                    model_path = os.path.join(self.speaker_models_path, filename)
                    
                    with open(model_path, 'rb') as f:
                        embedding = pickle.load(f)
                        self.speaker_embeddings[speaker_name] = embedding
            
            logger.info("Loaded speaker models", count=len(self.speaker_embeddings))
            
        except Exception as e:
            logger.error("Failed to load speaker models", error=str(e))
    
    async def list_speakers(self) -> List[str]:
        """List all trained speakers"""
        return list(self.speaker_embeddings.keys())
    
    async def delete_speaker(self, speaker_name: str):
        """Delete a trained speaker"""
        try:
            # Remove from memory
            if speaker_name in self.speaker_embeddings:
                del self.speaker_embeddings[speaker_name]
            
            # Remove from disk
            model_path = os.path.join(self.speaker_models_path, f"{speaker_name}.pkl")
            if os.path.exists(model_path):
                os.remove(model_path)
            
            logger.info("Speaker deleted", speaker_name=speaker_name)
            
        except Exception as e:
            logger.error("Failed to delete speaker", error=str(e))
            raise
    
    async def get_available_models(self) -> List[str]:
        """Get list of available speaker identification models"""
        return ["mfcc_clustering", "deep_embedding", "pyannote"]
    
    async def set_model(self, model_name: str):
        """Set the speaker identification model"""
        logger.info("Speaker identification model set", model=model_name)
        # Placeholder for model switching logic