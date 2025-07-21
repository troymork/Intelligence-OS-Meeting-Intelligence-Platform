"""
Transcript Processing Service for Intelligence OS
Handles conversation transcript processing, storage, and management
"""

import os
import re
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import structlog
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = structlog.get_logger(__name__)

class TranscriptStatus(Enum):
    """Transcript processing status"""
    RAW = "raw"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ANALYZED = "analyzed"
    ARCHIVED = "archived"
    ERROR = "error"

class SegmentType(Enum):
    """Types of transcript segments"""
    SPEECH = "speech"
    SILENCE = "silence"
    NOISE = "noise"
    MUSIC = "music"
    APPLAUSE = "applause"
    LAUGHTER = "laughter"

@dataclass
class TranscriptSegment:
    """Individual transcript segment with metadata"""
    id: str
    start_time: float
    end_time: float
    speaker_id: Optional[str]
    speaker_name: Optional[str]
    text: str
    confidence: float
    segment_type: SegmentType = SegmentType.SPEECH
    language: str = "en"
    emotions: Dict[str, float] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SpeakerProfile:
    """Speaker profile information"""
    id: str
    name: Optional[str]
    role: Optional[str]
    speaking_time: float
    word_count: int
    average_confidence: float
    speaking_rate: float  # words per minute
    interruptions: int
    questions_asked: int
    statements_made: int
    sentiment_scores: Dict[str, float]
    voice_characteristics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationTranscript:
    """Complete conversation transcript"""
    id: str
    meeting_id: Optional[str]
    session_id: str
    title: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: float
    status: TranscriptStatus
    segments: List[TranscriptSegment]
    speakers: List[SpeakerProfile]
    summary: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    sentiment_analysis: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class TranscriptService:
    """Service for processing and managing conversation transcripts"""
    
    def __init__(self):
        self.active_transcripts: Dict[str, ConversationTranscript] = {}
        self.processing_queue: List[str] = []
        self.db_session = None
        
        # Text processing patterns
        self.sentence_endings = re.compile(r'[.!?]+')
        self.word_pattern = re.compile(r'\b\w+\b')
        self.question_pattern = re.compile(r'\?|^(what|how|why|when|where|who|which|can|could|would|should|do|does|did|is|are|was|were)\b', re.IGNORECASE)
        
        # Emotion keywords for basic sentiment analysis
        self.emotion_keywords = {
            'positive': ['happy', 'excited', 'great', 'excellent', 'good', 'love', 'like', 'amazing', 'wonderful', 'fantastic'],
            'negative': ['sad', 'angry', 'frustrated', 'bad', 'terrible', 'hate', 'dislike', 'awful', 'horrible', 'disappointed'],
            'neutral': ['okay', 'fine', 'normal', 'average', 'standard', 'typical', 'regular', 'usual']
        }
        
        # Topic keywords for basic topic detection
        self.topic_keywords = {
            'project': ['project', 'task', 'deliverable', 'milestone', 'deadline', 'timeline'],
            'budget': ['budget', 'cost', 'expense', 'money', 'financial', 'funding', 'price'],
            'team': ['team', 'member', 'colleague', 'staff', 'employee', 'person', 'people'],
            'strategy': ['strategy', 'plan', 'approach', 'method', 'direction', 'goal', 'objective'],
            'technology': ['technology', 'system', 'software', 'platform', 'tool', 'application'],
            'customer': ['customer', 'client', 'user', 'stakeholder', 'audience', 'market']
        }
    
    async def initialize(self):
        """Initialize the transcript service"""
        try:
            # Initialize database connection if needed
            database_url = os.getenv('DATABASE_URL')
            if database_url and 'postgresql' in database_url:
                engine = create_engine(database_url)
                Session = sessionmaker(bind=engine)
                self.db_session = Session()
            
            logger.info("Transcript service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize transcript service", error=str(e))
            raise
    
    async def create_transcript(self, session_id: str, meeting_id: str = None, 
                              title: str = None) -> ConversationTranscript:
        """Create a new conversation transcript"""
        try:
            transcript_id = str(uuid.uuid4())
            
            transcript = ConversationTranscript(
                id=transcript_id,
                meeting_id=meeting_id,
                session_id=session_id,
                title=title or f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                start_time=datetime.utcnow(),
                end_time=None,
                duration=0.0,
                status=TranscriptStatus.RAW,
                segments=[],
                speakers=[]
            )
            
            self.active_transcripts[transcript_id] = transcript
            
            logger.info("Transcript created", 
                       transcript_id=transcript_id,
                       session_id=session_id,
                       meeting_id=meeting_id)
            
            return transcript
            
        except Exception as e:
            logger.error("Failed to create transcript", error=str(e))
            raise
    
    async def add_segment(self, transcript_id: str, start_time: float, end_time: float,
                         speaker_id: str = None, speaker_name: str = None,
                         text: str = "", confidence: float = 1.0,
                         segment_type: SegmentType = SegmentType.SPEECH) -> TranscriptSegment:
        """Add a segment to a transcript"""
        try:
            if transcript_id not in self.active_transcripts:
                raise ValueError(f"Transcript not found: {transcript_id}")
            
            transcript = self.active_transcripts[transcript_id]
            
            segment_id = f"{transcript_id}_segment_{len(transcript.segments)}"
            
            # Process text for additional metadata
            keywords = await self._extract_keywords(text)
            topics = await self._detect_topics(text)
            emotions = await self._analyze_emotions(text)
            
            segment = TranscriptSegment(
                id=segment_id,
                start_time=start_time,
                end_time=end_time,
                speaker_id=speaker_id,
                speaker_name=speaker_name,
                text=text.strip(),
                confidence=confidence,
                segment_type=segment_type,
                emotions=emotions,
                keywords=keywords,
                topics=topics
            )
            
            transcript.segments.append(segment)
            
            # Update transcript duration
            transcript.duration = max(transcript.duration, end_time)
            
            logger.debug("Segment added to transcript",
                        transcript_id=transcript_id,
                        segment_id=segment_id,
                        speaker=speaker_name or speaker_id,
                        text_length=len(text))
            
            return segment
            
        except Exception as e:
            logger.error("Failed to add segment", error=str(e))
            raise
    
    async def process_transcript(self, transcript_id: str) -> ConversationTranscript:
        """Process a raw transcript to extract insights and metadata"""
        try:
            if transcript_id not in self.active_transcripts:
                raise ValueError(f"Transcript not found: {transcript_id}")
            
            transcript = self.active_transcripts[transcript_id]
            transcript.status = TranscriptStatus.PROCESSING
            
            logger.info("Processing transcript", transcript_id=transcript_id)
            
            # Process speakers
            await self._process_speakers(transcript)
            
            # Generate summary
            transcript.summary = await self._generate_summary(transcript)
            
            # Extract overall topics and keywords
            transcript.topics = await self._extract_overall_topics(transcript)
            transcript.keywords = await self._extract_overall_keywords(transcript)
            
            # Perform sentiment analysis
            transcript.sentiment_analysis = await self._analyze_overall_sentiment(transcript)
            
            # Calculate quality metrics
            transcript.quality_metrics = await self._calculate_quality_metrics(transcript)
            
            # Update status
            transcript.status = TranscriptStatus.PROCESSED
            transcript.end_time = datetime.utcnow()
            
            logger.info("Transcript processing completed",
                       transcript_id=transcript_id,
                       segments=len(transcript.segments),
                       speakers=len(transcript.speakers),
                       duration=transcript.duration)
            
            return transcript
            
        except Exception as e:
            logger.error("Failed to process transcript", error=str(e))
            if transcript_id in self.active_transcripts:
                self.active_transcripts[transcript_id].status = TranscriptStatus.ERROR
            raise
    
    async def _process_speakers(self, transcript: ConversationTranscript):
        """Process speaker information and statistics"""
        try:
            speaker_stats = {}
            
            for segment in transcript.segments:
                if segment.segment_type != SegmentType.SPEECH or not segment.speaker_id:
                    continue
                
                speaker_id = segment.speaker_id
                
                if speaker_id not in speaker_stats:
                    speaker_stats[speaker_id] = {
                        'name': segment.speaker_name,
                        'speaking_time': 0.0,
                        'word_count': 0,
                        'confidence_scores': [],
                        'segments': [],
                        'questions': 0,
                        'statements': 0,
                        'interruptions': 0,
                        'emotions': {'positive': 0, 'negative': 0, 'neutral': 0}
                    }
                
                stats = speaker_stats[speaker_id]
                
                # Calculate speaking time
                speaking_time = segment.end_time - segment.start_time
                stats['speaking_time'] += speaking_time
                
                # Count words
                words = len(self.word_pattern.findall(segment.text))
                stats['word_count'] += words
                
                # Track confidence
                stats['confidence_scores'].append(segment.confidence)
                
                # Count questions vs statements
                if self.question_pattern.search(segment.text):
                    stats['questions'] += 1
                else:
                    stats['statements'] += 1
                
                # Aggregate emotions
                for emotion, score in segment.emotions.items():
                    if emotion in stats['emotions']:
                        stats['emotions'][emotion] += score
                
                stats['segments'].append(segment)
            
            # Create speaker profiles
            transcript.speakers = []
            for speaker_id, stats in speaker_stats.items():
                if stats['speaking_time'] > 0:  # Only include speakers who actually spoke
                    speaking_rate = (stats['word_count'] / stats['speaking_time']) * 60 if stats['speaking_time'] > 0 else 0
                    avg_confidence = sum(stats['confidence_scores']) / len(stats['confidence_scores']) if stats['confidence_scores'] else 0
                    
                    # Normalize emotion scores
                    total_emotions = sum(stats['emotions'].values())
                    sentiment_scores = {}
                    if total_emotions > 0:
                        sentiment_scores = {k: v / total_emotions for k, v in stats['emotions'].items()}
                    
                    profile = SpeakerProfile(
                        id=speaker_id,
                        name=stats['name'],
                        role=None,  # Could be enhanced with role detection
                        speaking_time=stats['speaking_time'],
                        word_count=stats['word_count'],
                        average_confidence=avg_confidence,
                        speaking_rate=speaking_rate,
                        interruptions=stats['interruptions'],
                        questions_asked=stats['questions'],
                        statements_made=stats['statements'],
                        sentiment_scores=sentiment_scores
                    )
                    
                    transcript.speakers.append(profile)
            
        except Exception as e:
            logger.error("Speaker processing failed", error=str(e))
    
    async def _generate_summary(self, transcript: ConversationTranscript) -> str:
        """Generate a summary of the conversation"""
        try:
            if not transcript.segments:
                return "No conversation content to summarize."
            
            # Extract key information
            total_speakers = len(transcript.speakers)
            total_duration = transcript.duration
            total_words = sum(len(self.word_pattern.findall(seg.text)) for seg in transcript.segments if seg.segment_type == SegmentType.SPEECH)
            
            # Find most active speaker
            most_active_speaker = None
            if transcript.speakers:
                most_active_speaker = max(transcript.speakers, key=lambda s: s.speaking_time)
            
            # Count questions and key topics
            total_questions = sum(s.questions_asked for s in transcript.speakers)
            main_topics = transcript.topics[:3] if hasattr(transcript, 'topics') else []
            
            # Build summary
            summary_parts = []
            summary_parts.append(f"Conversation with {total_speakers} participants")
            summary_parts.append(f"Duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
            summary_parts.append(f"Total words spoken: {total_words}")
            
            if most_active_speaker:
                summary_parts.append(f"Most active speaker: {most_active_speaker.name or most_active_speaker.id} ({most_active_speaker.speaking_time:.1f}s)")
            
            if total_questions > 0:
                summary_parts.append(f"Questions asked: {total_questions}")
            
            if main_topics:
                summary_parts.append(f"Main topics: {', '.join(main_topics)}")
            
            return ". ".join(summary_parts) + "."
            
        except Exception as e:
            logger.error("Summary generation failed", error=str(e))
            return "Summary generation failed."
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        try:
            if not text:
                return []
            
            # Simple keyword extraction - could be enhanced with NLP libraries
            words = self.word_pattern.findall(text.lower())
            
            # Filter out common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
            
            keywords = [word for word in words if len(word) > 3 and word not in stop_words]
            
            # Return unique keywords
            return list(set(keywords))[:10]  # Limit to top 10
            
        except Exception as e:
            logger.error("Keyword extraction failed", error=str(e))
            return []
    
    async def _detect_topics(self, text: str) -> List[str]:
        """Detect topics in text"""
        try:
            if not text:
                return []
            
            text_lower = text.lower()
            detected_topics = []
            
            for topic, keywords in self.topic_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    detected_topics.append(topic)
            
            return detected_topics
            
        except Exception as e:
            logger.error("Topic detection failed", error=str(e))
            return []
    
    async def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotions in text"""
        try:
            if not text:
                return {}
            
            text_lower = text.lower()
            emotion_scores = {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}
            
            for emotion, keywords in self.emotion_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                emotion_scores[emotion] = float(score)
            
            # Normalize scores
            total_score = sum(emotion_scores.values())
            if total_score > 0:
                emotion_scores = {k: v / total_score for k, v in emotion_scores.items()}
            else:
                emotion_scores['neutral'] = 1.0
            
            return emotion_scores
            
        except Exception as e:
            logger.error("Emotion analysis failed", error=str(e))
            return {'neutral': 1.0}
    
    async def _extract_overall_topics(self, transcript: ConversationTranscript) -> List[str]:
        """Extract overall topics from the entire transcript"""
        try:
            topic_counts = {}
            
            for segment in transcript.segments:
                if segment.segment_type == SegmentType.SPEECH:
                    for topic in segment.topics:
                        topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # Sort by frequency and return top topics
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            return [topic for topic, count in sorted_topics[:5]]
            
        except Exception as e:
            logger.error("Overall topic extraction failed", error=str(e))
            return []
    
    async def _extract_overall_keywords(self, transcript: ConversationTranscript) -> List[str]:
        """Extract overall keywords from the entire transcript"""
        try:
            keyword_counts = {}
            
            for segment in transcript.segments:
                if segment.segment_type == SegmentType.SPEECH:
                    for keyword in segment.keywords:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            # Sort by frequency and return top keywords
            sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
            return [keyword for keyword, count in sorted_keywords[:10]]
            
        except Exception as e:
            logger.error("Overall keyword extraction failed", error=str(e))
            return []
    
    async def _analyze_overall_sentiment(self, transcript: ConversationTranscript) -> Dict[str, Any]:
        """Analyze overall sentiment of the conversation"""
        try:
            if not transcript.speakers:
                return {}
            
            # Aggregate sentiment across all speakers
            total_emotions = {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}
            
            for speaker in transcript.speakers:
                for emotion, score in speaker.sentiment_scores.items():
                    if emotion in total_emotions:
                        total_emotions[emotion] += score
            
            # Normalize
            total_score = sum(total_emotions.values())
            if total_score > 0:
                overall_sentiment = {k: v / total_score for k, v in total_emotions.items()}
            else:
                overall_sentiment = {'neutral': 1.0}
            
            # Determine dominant sentiment
            dominant_sentiment = max(overall_sentiment.items(), key=lambda x: x[1])
            
            return {
                'overall_sentiment': overall_sentiment,
                'dominant_sentiment': dominant_sentiment[0],
                'sentiment_confidence': dominant_sentiment[1],
                'sentiment_distribution': overall_sentiment
            }
            
        except Exception as e:
            logger.error("Overall sentiment analysis failed", error=str(e))
            return {}
    
    async def _calculate_quality_metrics(self, transcript: ConversationTranscript) -> Dict[str, float]:
        """Calculate quality metrics for the transcript"""
        try:
            if not transcript.segments:
                return {}
            
            speech_segments = [s for s in transcript.segments if s.segment_type == SegmentType.SPEECH]
            
            if not speech_segments:
                return {}
            
            # Average confidence
            avg_confidence = sum(s.confidence for s in speech_segments) / len(speech_segments)
            
            # Speech to silence ratio
            total_speech_time = sum(s.end_time - s.start_time for s in speech_segments)
            speech_ratio = total_speech_time / transcript.duration if transcript.duration > 0 else 0
            
            # Speaker balance (how evenly distributed speaking time is)
            if transcript.speakers:
                speaking_times = [s.speaking_time for s in transcript.speakers]
                max_time = max(speaking_times)
                min_time = min(speaking_times)
                speaker_balance = min_time / max_time if max_time > 0 else 1.0
            else:
                speaker_balance = 1.0
            
            # Interaction quality (questions vs statements ratio)
            total_questions = sum(s.questions_asked for s in transcript.speakers)
            total_statements = sum(s.statements_made for s in transcript.speakers)
            interaction_ratio = total_questions / (total_questions + total_statements) if (total_questions + total_statements) > 0 else 0
            
            return {
                'average_confidence': avg_confidence,
                'speech_ratio': speech_ratio,
                'speaker_balance': speaker_balance,
                'interaction_ratio': interaction_ratio,
                'overall_quality': (avg_confidence + speech_ratio + speaker_balance) / 3
            }
            
        except Exception as e:
            logger.error("Quality metrics calculation failed", error=str(e))
            return {}
    
    async def get_transcript(self, transcript_id: str) -> Optional[ConversationTranscript]:
        """Get a transcript by ID"""
        return self.active_transcripts.get(transcript_id)
    
    async def list_transcripts(self, session_id: str = None, meeting_id: str = None) -> List[ConversationTranscript]:
        """List transcripts with optional filtering"""
        transcripts = list(self.active_transcripts.values())
        
        if session_id:
            transcripts = [t for t in transcripts if t.session_id == session_id]
        
        if meeting_id:
            transcripts = [t for t in transcripts if t.meeting_id == meeting_id]
        
        return transcripts
    
    async def search_transcripts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search transcripts by content"""
        try:
            results = []
            query_lower = query.lower()
            
            for transcript in self.active_transcripts.values():
                matches = []
                
                # Search in segments
                for segment in transcript.segments:
                    if segment.segment_type == SegmentType.SPEECH and query_lower in segment.text.lower():
                        matches.append({
                            'segment_id': segment.id,
                            'text': segment.text,
                            'speaker': segment.speaker_name or segment.speaker_id,
                            'start_time': segment.start_time,
                            'confidence': segment.confidence
                        })
                
                if matches:
                    results.append({
                        'transcript_id': transcript.id,
                        'title': transcript.title,
                        'session_id': transcript.session_id,
                        'meeting_id': transcript.meeting_id,
                        'matches': matches[:5],  # Limit matches per transcript
                        'total_matches': len(matches)
                    })
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            logger.error("Transcript search failed", error=str(e))
            return []
    
    async def export_transcript(self, transcript_id: str, format: str = 'json') -> Dict[str, Any]:
        """Export transcript in specified format"""
        try:
            transcript = await self.get_transcript(transcript_id)
            if not transcript:
                raise ValueError(f"Transcript not found: {transcript_id}")
            
            if format.lower() == 'json':
                return {
                    'transcript_id': transcript.id,
                    'title': transcript.title,
                    'session_id': transcript.session_id,
                    'meeting_id': transcript.meeting_id,
                    'start_time': transcript.start_time.isoformat(),
                    'end_time': transcript.end_time.isoformat() if transcript.end_time else None,
                    'duration': transcript.duration,
                    'status': transcript.status.value,
                    'summary': transcript.summary,
                    'topics': transcript.topics,
                    'keywords': transcript.keywords,
                    'sentiment_analysis': transcript.sentiment_analysis,
                    'quality_metrics': transcript.quality_metrics,
                    'speakers': [
                        {
                            'id': s.id,
                            'name': s.name,
                            'speaking_time': s.speaking_time,
                            'word_count': s.word_count,
                            'speaking_rate': s.speaking_rate,
                            'questions_asked': s.questions_asked,
                            'statements_made': s.statements_made,
                            'sentiment_scores': s.sentiment_scores
                        } for s in transcript.speakers
                    ],
                    'segments': [
                        {
                            'id': seg.id,
                            'start_time': seg.start_time,
                            'end_time': seg.end_time,
                            'speaker_id': seg.speaker_id,
                            'speaker_name': seg.speaker_name,
                            'text': seg.text,
                            'confidence': seg.confidence,
                            'segment_type': seg.segment_type.value,
                            'emotions': seg.emotions,
                            'keywords': seg.keywords,
                            'topics': seg.topics
                        } for seg in transcript.segments
                    ]
                }
            
            elif format.lower() == 'text':
                lines = []
                lines.append(f"Transcript: {transcript.title}")
                lines.append(f"Duration: {transcript.duration:.1f} seconds")
                lines.append(f"Speakers: {len(transcript.speakers)}")
                lines.append("")
                
                for segment in transcript.segments:
                    if segment.segment_type == SegmentType.SPEECH:
                        speaker = segment.speaker_name or segment.speaker_id or "Unknown"
                        timestamp = f"[{segment.start_time:.1f}s]"
                        lines.append(f"{timestamp} {speaker}: {segment.text}")
                
                return {'content': '\n'.join(lines)}
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error("Transcript export failed", error=str(e))
            raise
    
    async def delete_transcript(self, transcript_id: str) -> bool:
        """Delete a transcript"""
        try:
            if transcript_id in self.active_transcripts:
                del self.active_transcripts[transcript_id]
                logger.info("Transcript deleted", transcript_id=transcript_id)
                return True
            return False
            
        except Exception as e:
            logger.error("Transcript deletion failed", error=str(e))
            return False

# Global transcript service instance
transcript_service = TranscriptService()