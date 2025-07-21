"""
Organizational Learning Analytics Service
Measures knowledge creation, transfer, and wisdom development
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog
from collections import defaultdict, Counter
import numpy as np
from .knowledge_graph_service import KnowledgeGraphService, Concept, Relationship, ConceptType

logger = structlog.get_logger(__name__)

class LearningType(Enum):
    """Types of organizational learning"""
    SINGLE_LOOP = "single_loop"  # Correcting errors within existing frameworks
    DOUBLE_LOOP = "double_loop"  # Questioning underlying assumptions
    TRIPLE_LOOP = "triple_loop"  # Learning how to learn
    ADAPTIVE = "adaptive"  # Responding to changes
    GENERATIVE = "generative"  # Creating new possibilities

class KnowledgeTransferMode(Enum):
    """Modes of knowledge transfer"""
    SOCIALIZATION = "socialization"  # Tacit to tacit
    EXTERNALIZATION = "externalization"  # Tacit to explicit
    COMBINATION = "combination"  # Explicit to explicit
    INTERNALIZATION = "internalization"  # Explicit to tacit

class WisdomIndicator(Enum):
    """Indicators of organizational wisdom"""
    PATTERN_RECOGNITION = "pattern_recognition"
    SYSTEMS_THINKING = "systems_thinking"
    LONG_TERM_PERSPECTIVE = "long_term_perspective"
    ETHICAL_REASONING = "ethical_reasoning"
    CONTEXTUAL_JUDGMENT = "contextual_judgment"
    UNCERTAINTY_TOLERANCE = "uncertainty_tolerance"
    COLLECTIVE_INTELLIGENCE = "collective_intelligence"

@dataclass
class LearningEvent:
    """A specific learning event in the organization"""
    id: str
    event_type: LearningType
    timestamp: datetime
    description: str
    participants: List[str]
    concepts_involved: List[str]
    knowledge_created: Dict[str, Any]
    knowledge_transferred: Dict[str, Any]
    learning_depth: float  # 0-1 scale
    learning_breadth: float  # 0-1 scale
    impact_score: float
    evidence: List[str]
    meeting_id: Optional[str] = None

@dataclass
class KnowledgeFlow:
    """Tracks how knowledge flows through the organization"""
    id: str
    source_concept: str
    target_concept: str
    transfer_mode: KnowledgeTransferMode
    flow_strength: float
    flow_direction: str  # bidirectional, unidirectional
    participants_involved: List[str]
    transfer_mechanisms: List[str]
    barriers_encountered: List[str]
    success_indicators: List[str]
    timestamp: datetime

@dataclass
class WisdomAssessment:
    """Assessment of organizational wisdom development"""
    id: str
    assessment_period: Dict[str, datetime]
    wisdom_indicators: Dict[WisdomIndicator, float]
    collective_intelligence_score: float
    decision_quality_trend: float
    learning_agility_score: float
    knowledge_integration_ability: float
    contextual_awareness_level: float
    long_term_thinking_capacity: float
    ethical_reasoning_maturity: float
    overall_wisdom_score: float
    improvement_recommendations: List[str]

@dataclass
class LearningCapability:
    """Organizational learning capability assessment"""
    id: str
    capability_type: str
    current_level: float  # 0-1 scale
    target_level: float
    development_trend: str  # improving, stable, declining
    key_strengths: List[str]
    development_areas: List[str]
    enhancement_strategies: List[str]
    success_metrics: List[str]
    assessment_confidence: float

class OrganizationalLearningAnalytics:
    """Service for analyzing organizational learning patterns and capabilities"""
    
    def __init__(self, knowledge_graph_service: KnowledgeGraphService):
        self.knowledge_graph = knowledge_graph_service
        self.learning_events = []
        self.knowledge_flows = []
        self.wisdom_assessments = []
        self.learning_capabilities = {}
        
        # Analytics configuration
        self.config = {
            'learning_event_detection_threshold': 0.6,
            'knowledge_flow_strength_threshold': 0.4,
            'wisdom_assessment_window_days': 90,
            'learning_velocity_window_days': 30,
            'capability_assessment_frequency_days': 30
        }
    
    async def analyze_meeting_learning(self, meeting_data: Dict[str, Any], 
                                     knowledge_graph_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze learning that occurred in a meeting"""
        try:
            meeting_id = meeting_data.get('meeting_id', str(uuid.uuid4()))
            
            logger.info("Analyzing meeting learning", meeting_id=meeting_id)
            
            # Detect learning events
            learning_events = await self._detect_learning_events(meeting_data, knowledge_graph_result)
            
            # Analyze knowledge flows
            knowledge_flows = await self._analyze_knowledge_flows(meeting_data, knowledge_graph_result)
            
            # Assess learning quality
            learning_quality = await self._assess_learning_quality(learning_events, knowledge_flows)
            
            # Calculate learning metrics
            learning_metrics = await self._calculate_meeting_learning_metrics(
                learning_events, knowledge_flows, learning_quality
            )
            
            # Update organizational learning state
            await self._update_learning_state(learning_events, knowledge_flows)
            
            result = {
                'meeting_id': meeting_id,
                'learning_events': [self._serialize_learning_event(le) for le in learning_events],
                'knowledge_flows': [self._serialize_knowledge_flow(kf) for kf in knowledge_flows],
                'learning_quality': learning_quality,
                'learning_metrics': learning_metrics,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info("Meeting learning analysis completed",
                       meeting_id=meeting_id,
                       learning_events_count=len(learning_events),
                       knowledge_flows_count=len(knowledge_flows))
            
            return result
            
        except Exception as e:
            logger.error("Meeting learning analysis failed", error=str(e))
            raise
    
    async def _detect_learning_events(self, meeting_data: Dict[str, Any], 
                                    knowledge_graph_result: Dict[str, Any]) -> List[LearningEvent]:
        """Detect learning events from meeting data"""
        try:
            learning_events = []
            meeting_id = meeting_data.get('meeting_id')
            participants = meeting_data.get('participants', [])
            
            # Detect single-loop learning (error correction)
            single_loop_events = await self._detect_single_loop_learning(meeting_data)
            learning_events.extend(single_loop_events)
            
            # Detect double-loop learning (assumption questioning)
            double_loop_events = await self._detect_double_loop_learning(meeting_data)
            learning_events.extend(double_loop_events)
            
            # Detect adaptive learning (responding to changes)
            adaptive_events = await self._detect_adaptive_learning(meeting_data)
            learning_events.extend(adaptive_events)
            
            # Detect generative learning (creating new possibilities)
            generative_events = await self._detect_generative_learning(meeting_data, knowledge_graph_result)
            learning_events.extend(generative_events)
            
            # Set common attributes
            for event in learning_events:
                event.meeting_id = meeting_id
                event.participants = participants
                event.timestamp = datetime.utcnow()
            
            return learning_events
            
        except Exception as e:
            logger.error("Learning event detection failed", error=str(e))
            return []
    
    async def _detect_single_loop_learning(self, meeting_data: Dict[str, Any]) -> List[LearningEvent]:
        """Detect single-loop learning events (error correction)"""
        events = []
        
        try:
            # Look for problem-solving and error correction patterns
            transcript_data = meeting_data.get('transcript_analysis', {})
            segments = transcript_data.get('segments', [])
            
            error_correction_keywords = [
                'fix', 'correct', 'mistake', 'error', 'wrong', 'issue', 'problem',
                'bug', 'defect', 'improve', 'adjust', 'modify'
            ]
            
            solution_keywords = [
                'solution', 'resolve', 'answer', 'fix', 'approach', 'method',
                'way', 'strategy', 'plan', 'action'
            ]
            
            for segment in segments:
                text = segment.get('text', '').lower()
                
                # Check for error correction patterns
                error_mentions = sum(1 for keyword in error_correction_keywords if keyword in text)
                solution_mentions = sum(1 for keyword in solution_keywords if keyword in text)
                
                if error_mentions >= 2 and solution_mentions >= 1:
                    events.append(LearningEvent(
                        id=str(uuid.uuid4()),
                        event_type=LearningType.SINGLE_LOOP,
                        timestamp=datetime.utcnow(),
                        description=f"Error correction learning: {segment.get('text', '')[:100]}...",
                        participants=[segment.get('speaker', 'Unknown')],
                        concepts_involved=[],
                        knowledge_created={'type': 'error_correction', 'content': text},
                        knowledge_transferred={},
                        learning_depth=0.3,  # Single-loop is relatively shallow
                        learning_breadth=0.4,
                        impact_score=0.5,
                        evidence=[segment.get('text', '')]
                    ))
            
            return events
            
        except Exception as e:
            logger.error("Single-loop learning detection failed", error=str(e))
            return []
    
    async def _detect_double_loop_learning(self, meeting_data: Dict[str, Any]) -> List[LearningEvent]:
        """Detect double-loop learning events (assumption questioning)"""
        events = []
        
        try:
            transcript_data = meeting_data.get('transcript_analysis', {})
            segments = transcript_data.get('segments', [])
            
            assumption_questioning_keywords = [
                'why', 'assumption', 'believe', 'think', 'suppose', 'assume',
                'question', 'challenge', 'reconsider', 'rethink', 'fundamental',
                'underlying', 'root cause', 'paradigm', 'framework'
            ]
            
            for segment in segments:
                text = segment.get('text', '').lower()
                
                # Check for assumption questioning patterns
                questioning_score = sum(1 for keyword in assumption_questioning_keywords if keyword in text)
                
                # Look for questioning phrases
                questioning_phrases = [
                    'why do we', 'what if we', 'should we', 'do we need to',
                    'is it necessary', 'could we instead', 'what about'
                ]
                
                phrase_score = sum(1 for phrase in questioning_phrases if phrase in text)
                
                if questioning_score >= 2 or phrase_score >= 1:
                    events.append(LearningEvent(
                        id=str(uuid.uuid4()),
                        event_type=LearningType.DOUBLE_LOOP,
                        timestamp=datetime.utcnow(),
                        description=f"Assumption questioning: {segment.get('text', '')[:100]}...",
                        participants=[segment.get('speaker', 'Unknown')],
                        concepts_involved=[],
                        knowledge_created={'type': 'assumption_questioning', 'content': text},
                        knowledge_transferred={},
                        learning_depth=0.7,  # Double-loop is deeper
                        learning_breadth=0.6,
                        impact_score=0.7,
                        evidence=[segment.get('text', '')]
                    ))
            
            return events
            
        except Exception as e:
            logger.error("Double-loop learning detection failed", error=str(e))
            return []
    
    async def _detect_generative_learning(self, meeting_data: Dict[str, Any], 
                                        knowledge_graph_result: Dict[str, Any]) -> List[LearningEvent]:
        """Detect generative learning events (creating new possibilities)"""
        events = []
        
        try:
            # Look for innovation and creative thinking patterns
            new_concepts = knowledge_graph_result.get('concepts_processed', 0)
            new_relationships = knowledge_graph_result.get('relationships_processed', 0)
            
            # High concept/relationship creation indicates generative learning
            if new_concepts > 5 or new_relationships > 3:
                events.append(LearningEvent(
                    id=str(uuid.uuid4()),
                    event_type=LearningType.GENERATIVE,
                    timestamp=datetime.utcnow(),
                    description=f"Generative learning through concept creation: {new_concepts} concepts, {new_relationships} relationships",
                    participants=meeting_data.get('participants', []),
                    concepts_involved=[],
                    knowledge_created={
                        'type': 'concept_creation',
                        'new_concepts': new_concepts,
                        'new_relationships': new_relationships
                    },
                    knowledge_transferred={},
                    learning_depth=0.9,  # Generative learning is very deep
                    learning_breadth=0.8,
                    impact_score=0.8,
                    evidence=[f"Created {new_concepts} new concepts and {new_relationships} relationships"]
                ))
            
            # Look for innovation keywords in transcript
            transcript_data = meeting_data.get('transcript_analysis', {})
            segments = transcript_data.get('segments', [])
            
            innovation_keywords = [
                'innovate', 'creative', 'new idea', 'breakthrough', 'invention',
                'novel', 'original', 'unique', 'revolutionary', 'transform',
                'reimagine', 'reinvent', 'disrupt', 'paradigm shift'
            ]
            
            for segment in segments:
                text = segment.get('text', '').lower()
                innovation_score = sum(1 for keyword in innovation_keywords if keyword in text)
                
                if innovation_score >= 2:
                    events.append(LearningEvent(
                        id=str(uuid.uuid4()),
                        event_type=LearningType.GENERATIVE,
                        timestamp=datetime.utcnow(),
                        description=f"Innovation-focused generative learning: {segment.get('text', '')[:100]}...",
                        participants=[segment.get('speaker', 'Unknown')],
                        concepts_involved=[],
                        knowledge_created={'type': 'innovation_thinking', 'content': text},
                        knowledge_transferred={},
                        learning_depth=0.8,
                        learning_breadth=0.7,
                        impact_score=0.7,
                        evidence=[segment.get('text', '')]
                    ))
            
            return events
            
        except Exception as e:
            logger.error("Generative learning detection failed", error=str(e))
            return []
    
    async def assess_organizational_wisdom(self, assessment_period_days: int = 90) -> WisdomAssessment:
        """Assess organizational wisdom development"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=assessment_period_days)
            
            logger.info("Assessing organizational wisdom",
                       start_date=start_date.isoformat(),
                       end_date=end_date.isoformat())
            
            # Assess each wisdom indicator
            wisdom_scores = {}
            
            # Pattern recognition ability
            wisdom_scores[WisdomIndicator.PATTERN_RECOGNITION] = await self._assess_pattern_recognition()
            
            # Systems thinking capability
            wisdom_scores[WisdomIndicator.SYSTEMS_THINKING] = await self._assess_systems_thinking()
            
            # Long-term perspective
            wisdom_scores[WisdomIndicator.LONG_TERM_PERSPECTIVE] = await self._assess_long_term_perspective()
            
            # Ethical reasoning
            wisdom_scores[WisdomIndicator.ETHICAL_REASONING] = await self._assess_ethical_reasoning()
            
            # Contextual judgment
            wisdom_scores[WisdomIndicator.CONTEXTUAL_JUDGMENT] = await self._assess_contextual_judgment()
            
            # Uncertainty tolerance
            wisdom_scores[WisdomIndicator.UNCERTAINTY_TOLERANCE] = await self._assess_uncertainty_tolerance()
            
            # Collective intelligence
            collective_intelligence_score = await self._assess_collective_intelligence()
            wisdom_scores[WisdomIndicator.COLLECTIVE_INTELLIGENCE] = collective_intelligence_score
            
            # Calculate overall wisdom score
            overall_wisdom_score = sum(wisdom_scores.values()) / len(wisdom_scores)
            
            # Assess other dimensions
            decision_quality_trend = await self._assess_decision_quality_trend(start_date, end_date)
            learning_agility_score = await self._assess_learning_agility()
            knowledge_integration_ability = await self._assess_knowledge_integration()
            contextual_awareness_level = await self._assess_contextual_awareness()
            long_term_thinking_capacity = await self._assess_long_term_thinking()
            ethical_reasoning_maturity = await self._assess_ethical_maturity()
            
            # Generate improvement recommendations
            improvement_recommendations = await self._generate_wisdom_improvement_recommendations(wisdom_scores)
            
            assessment = WisdomAssessment(
                id=str(uuid.uuid4()),
                assessment_period={'start': start_date, 'end': end_date},
                wisdom_indicators=wisdom_scores,
                collective_intelligence_score=collective_intelligence_score,
                decision_quality_trend=decision_quality_trend,
                learning_agility_score=learning_agility_score,
                knowledge_integration_ability=knowledge_integration_ability,
                contextual_awareness_level=contextual_awareness_level,
                long_term_thinking_capacity=long_term_thinking_capacity,
                ethical_reasoning_maturity=ethical_reasoning_maturity,
                overall_wisdom_score=overall_wisdom_score,
                improvement_recommendations=improvement_recommendations
            )
            
            self.wisdom_assessments.append(assessment)
            
            logger.info("Organizational wisdom assessment completed",
                       overall_score=overall_wisdom_score,
                       collective_intelligence=collective_intelligence_score)
            
            return assessment
            
        except Exception as e:
            logger.error("Organizational wisdom assessment failed", error=str(e))
            raise
    
    async def _assess_pattern_recognition(self) -> float:
        """Assess the organization's pattern recognition ability"""
        try:
            # Look at detected patterns and their accuracy
            from .pattern_recognition_engine import PatternRecognitionEngine
            
            # This would typically analyze the quality and accuracy of detected patterns
            # For now, we'll use a simplified approach based on pattern detection frequency
            
            recent_learning_events = [
                event for event in self.learning_events
                if event.timestamp > datetime.utcnow() - timedelta(days=30)
            ]
            
            pattern_learning_events = [
                event for event in recent_learning_events
                if 'pattern' in event.description.lower()
            ]
            
            if not recent_learning_events:
                return 0.5  # Default score
            
            pattern_recognition_ratio = len(pattern_learning_events) / len(recent_learning_events)
            return min(pattern_recognition_ratio * 2, 1.0)  # Scale to 0-1
            
        except Exception as e:
            logger.error("Pattern recognition assessment failed", error=str(e))
            return 0.5
    
    async def _assess_collective_intelligence(self) -> float:
        """Assess collective intelligence of the organization"""
        try:
            # Analyze collaboration patterns and knowledge sharing
            knowledge_flows_count = len(self.knowledge_flows)
            
            if knowledge_flows_count == 0:
                return 0.5
            
            # Calculate average flow strength
            avg_flow_strength = sum(kf.flow_strength for kf in self.knowledge_flows) / knowledge_flows_count
            
            # Calculate bidirectional flow ratio (indicates collaborative learning)
            bidirectional_flows = sum(1 for kf in self.knowledge_flows if kf.flow_direction == 'bidirectional')
            bidirectional_ratio = bidirectional_flows / knowledge_flows_count if knowledge_flows_count > 0 else 0
            
            # Combine metrics
            collective_intelligence = (avg_flow_strength * 0.6) + (bidirectional_ratio * 0.4)
            
            return min(collective_intelligence, 1.0)
            
        except Exception as e:
            logger.error("Collective intelligence assessment failed", error=str(e))
            return 0.5
    
    def _serialize_learning_event(self, event: LearningEvent) -> Dict[str, Any]:
        """Serialize learning event for JSON response"""
        return {
            'id': event.id,
            'event_type': event.event_type.value,
            'timestamp': event.timestamp.isoformat(),
            'description': event.description,
            'participants': event.participants,
            'concepts_involved': event.concepts_involved,
            'knowledge_created': event.knowledge_created,
            'knowledge_transferred': event.knowledge_transferred,
            'learning_depth': event.learning_depth,
            'learning_breadth': event.learning_breadth,
            'impact_score': event.impact_score,
            'evidence': event.evidence,
            'meeting_id': event.meeting_id
        }
    
    def _serialize_knowledge_flow(self, flow: KnowledgeFlow) -> Dict[str, Any]:
        """Serialize knowledge flow for JSON response"""
        return {
            'id': flow.id,
            'source_concept': flow.source_concept,
            'target_concept': flow.target_concept,
            'transfer_mode': flow.transfer_mode.value,
            'flow_strength': flow.flow_strength,
            'flow_direction': flow.flow_direction,
            'participants_involved': flow.participants_involved,
            'transfer_mechanisms': flow.transfer_mechanisms,
            'barriers_encountered': flow.barriers_encountered,
            'success_indicators': flow.success_indicators,
            'timestamp': flow.timestamp.isoformat()
        }

# Global service instance
organizational_learning_analytics = OrganizationalLearningAnalytics(
    knowledge_graph_service=None  # Will be injected when needed
)