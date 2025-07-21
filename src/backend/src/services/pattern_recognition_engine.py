"""
Cross-Meeting Pattern Detection and Analysis Engine
Identifies recurring challenges, behavioral patterns, and organizational learning opportunities
"""

import os
import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import structlog
from collections import defaultdict, Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

logger = structlog.get_logger(__name__)

class PatternType(Enum):
    """Types of patterns that can be detected"""
    RECURRING_CHALLENGE = "recurring_challenge"
    BEHAVIORAL_PATTERN = "behavioral_pattern"
    DECISION_PATTERN = "decision_pattern"
    COMMUNICATION_PATTERN = "communication_pattern"
    EMOTIONAL_PATTERN = "emotional_pattern"
    STRATEGIC_PATTERN = "strategic_pattern"
    COLLABORATION_PATTERN = "collaboration_pattern"
    LEARNING_PATTERN = "learning_pattern"

class PatternSeverity(Enum):
    """Severity levels for detected patterns"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PatternTrend(Enum):
    """Trend direction for patterns over time"""
    IMPROVING = "improving"
    STABLE = "stable"
    WORSENING = "worsening"
    EMERGING = "emerging"
    DECLINING = "declining"

@dataclass
class PatternInstance:
    """Individual instance of a pattern occurrence"""
    id: str
    meeting_id: str
    timestamp: datetime
    context: Dict[str, Any]
    severity: float  # 0-1 scale
    participants_involved: List[str]
    evidence: List[str]  # Supporting evidence for the pattern
    metadata: Dict[str, Any]

@dataclass
class DetectedPattern:
    """A detected pattern across multiple meetings"""
    id: str
    pattern_type: PatternType
    title: str
    description: str
    frequency: int  # Number of occurrences
    severity: PatternSeverity
    trend: PatternTrend
    first_occurrence: datetime
    last_occurrence: datetime
    instances: List[PatternInstance]
    affected_participants: Set[str]
    root_causes: List[str]
    impact_analysis: Dict[str, Any]
    intervention_recommendations: List[str]
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BestPractice:
    """Identified best practice from successful patterns"""
    id: str
    title: str
    description: str
    category: str
    success_indicators: List[str]
    implementation_guidance: str
    applicable_contexts: List[str]
    evidence_meetings: List[str]
    effectiveness_score: float
    adoption_recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class EmotionalFatigueIndicator:
    """Indicator of emotional fatigue or misalignment"""
    id: str
    indicator_type: str  # fatigue, misalignment, stress, disengagement
    severity: PatternSeverity
    affected_participants: List[str]
    symptoms: List[str]
    contributing_factors: List[str]
    intervention_urgency: str  # immediate, soon, monitor
    recommended_actions: List[str]
    monitoring_metrics: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SystemicIssue:
    """Systemic organizational issue identified through pattern analysis"""
    id: str
    issue_title: str
    issue_description: str
    root_causes: List[str]
    affected_areas: List[str]  # departments, processes, systems
    impact_assessment: Dict[str, Any]
    urgency_level: PatternSeverity
    intervention_strategy: Dict[str, Any]
    success_metrics: List[str]
    timeline_recommendations: Dict[str, Any]
    stakeholder_involvement: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

class PatternRecognitionEngine:
    """Engine for detecting patterns across multiple meetings"""
    
    def __init__(self):
        self.meeting_history = []  # Store meeting data for analysis
        self.detected_patterns = {}  # Cache of detected patterns
        self.best_practices = {}  # Cache of identified best practices
        self.emotional_indicators = {}  # Cache of emotional fatigue indicators
        self.systemic_issues = {}  # Cache of systemic issues
        
        # Pattern detection thresholds
        self.pattern_thresholds = {
            'min_occurrences': 3,  # Minimum occurrences to consider a pattern
            'min_confidence': 0.6,  # Minimum confidence score
            'similarity_threshold': 0.7,  # Similarity threshold for clustering
            'time_window_days': 90  # Time window for pattern analysis
        }
        
        # Text analysis components
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
        # Pattern templates for common organizational patterns
        self.pattern_templates = self._initialize_pattern_templates()
    
    def _initialize_pattern_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize templates for common organizational patterns"""
        return {
            'recurring_challenges': {
                'keywords': [
                    'problem', 'issue', 'challenge', 'difficulty', 'obstacle',
                    'blocker', 'concern', 'risk', 'barrier', 'constraint'
                ],
                'context_indicators': [
                    'same issue', 'again', 'recurring', 'repeatedly',
                    'still having', 'continues to', 'ongoing'
                ],
                'severity_indicators': {
                    'high': ['critical', 'urgent', 'blocking', 'major'],
                    'medium': ['important', 'significant', 'concerning'],
                    'low': ['minor', 'small', 'slight']
                }
            },
            'behavioral_patterns': {
                'communication_styles': [
                    'interrupting', 'dominating', 'quiet', 'withdrawn',
                    'collaborative', 'supportive', 'defensive', 'aggressive'
                ],
                'decision_making': [
                    'decisive', 'hesitant', 'consensus-seeking', 'authoritative',
                    'collaborative', 'avoidant', 'impulsive', 'analytical'
                ],
                'conflict_resolution': [
                    'avoiding', 'confrontational', 'mediating', 'compromising',
                    'accommodating', 'competing', 'collaborating'
                ]
            },
            'emotional_indicators': {
                'fatigue': [
                    'tired', 'exhausted', 'overwhelmed', 'burned out',
                    'stressed', 'drained', 'frustrated'
                ],
                'disengagement': [
                    'disinterested', 'checked out', 'going through motions',
                    'minimal participation', 'lack of enthusiasm'
                ],
                'misalignment': [
                    'confused', 'unclear', 'different understanding',
                    'not on same page', 'conflicting views'
                ]
            }
        }
    
    async def analyze_meeting_patterns(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in a single meeting and update historical analysis"""
        try:
            meeting_id = meeting_data.get('meeting_id', str(uuid.uuid4()))
            
            logger.info("Analyzing meeting patterns", meeting_id=meeting_id)
            
            # Add meeting to history
            self.meeting_history.append(meeting_data)
            
            # Detect patterns in current meeting
            current_patterns = await self._detect_current_meeting_patterns(meeting_data)
            
            # Update cross-meeting pattern analysis
            cross_meeting_patterns = await self._analyze_cross_meeting_patterns()
            
            # Detect best practices
            best_practices = await self._detect_best_practices()
            
            # Identify emotional fatigue indicators
            emotional_indicators = await self._detect_emotional_fatigue()
            
            # Identify systemic issues
            systemic_issues = await self._identify_systemic_issues()
            
            analysis_result = {
                'meeting_id': meeting_id,
                'current_meeting_patterns': current_patterns,
                'cross_meeting_patterns': cross_meeting_patterns,
                'best_practices': best_practices,
                'emotional_indicators': emotional_indicators,
                'systemic_issues': systemic_issues,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'confidence_score': self._calculate_analysis_confidence(
                    current_patterns, cross_meeting_patterns
                )
            }
            
            logger.info("Meeting pattern analysis completed", 
                       meeting_id=meeting_id,
                       patterns_detected=len(cross_meeting_patterns),
                       best_practices_found=len(best_practices))
            
            return analysis_result
            
        except Exception as e:
            logger.error("Meeting pattern analysis failed", error=str(e))
            raise
    
    async def _detect_current_meeting_patterns(self, meeting_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect patterns within a single meeting"""
        try:
            patterns = []
            
            # Analyze transcript for pattern indicators
            transcript_data = meeting_data.get('transcript_analysis', {})
            if transcript_data:
                patterns.extend(await self._analyze_transcript_patterns(transcript_data, meeting_data))
            
            # Analyze decision patterns
            decisions = meeting_data.get('decisions', [])
            if decisions:
                patterns.extend(await self._analyze_decision_patterns(decisions, meeting_data))
            
            # Analyze communication patterns
            discussion_dynamics = meeting_data.get('discussion_dynamics', {})
            if discussion_dynamics:
                patterns.extend(await self._analyze_communication_patterns(discussion_dynamics, meeting_data))
            
            # Analyze emotional patterns
            human_needs = meeting_data.get('human_needs_intelligence', {})
            if human_needs:
                patterns.extend(await self._analyze_emotional_patterns(human_needs, meeting_data))
            
            return patterns
            
        except Exception as e:
            logger.error("Current meeting pattern detection failed", error=str(e))
            return []  
  async def _analyze_transcript_patterns(self, transcript_data: Dict[str, Any], 
                                          meeting_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze transcript for recurring challenge and behavioral patterns"""
        try:
            patterns = []
            segments = transcript_data.get('segments', [])
            
            if not segments:
                return patterns
            
            # Combine all text for analysis
            full_text = ' '.join([segment.get('text', '') for segment in segments])
            
            # Detect recurring challenges
            challenge_patterns = self._detect_challenge_patterns(segments, meeting_data)
            patterns.extend(challenge_patterns)
            
            # Detect behavioral patterns
            behavioral_patterns = self._detect_behavioral_patterns(segments, meeting_data)
            patterns.extend(behavioral_patterns)
            
            # Detect emotional patterns
            emotional_patterns = self._detect_emotional_patterns_in_transcript(segments, meeting_data)
            patterns.extend(emotional_patterns)
            
            return patterns
            
        except Exception as e:
            logger.error("Transcript pattern analysis failed", error=str(e))
            return []
    
    def _detect_challenge_patterns(self, segments: List[Dict[str, Any]], 
                                 meeting_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect recurring challenge patterns in transcript"""
        patterns = []
        
        try:
            challenge_template = self.pattern_templates['recurring_challenges']
            challenge_keywords = challenge_template['keywords']
            context_indicators = challenge_template['context_indicators']
            
            for segment in segments:
                text = segment.get('text', '').lower()
                speaker = segment.get('speaker', 'Unknown')
                
                # Check for challenge keywords
                challenge_mentions = [kw for kw in challenge_keywords if kw in text]
                
                if challenge_mentions:
                    # Check for recurring context indicators
                    recurring_indicators = [ci for ci in context_indicators if ci in text]
                    
                    if recurring_indicators:
                        # This might be a recurring challenge
                        severity = self._assess_challenge_severity(text, challenge_template)
                        
                        patterns.append({
                            'type': PatternType.RECURRING_CHALLENGE.value,
                            'title': f"Recurring Challenge Mentioned by {speaker}",
                            'description': text[:200] + "..." if len(text) > 200 else text,
                            'severity': severity,
                            'speaker': speaker,
                            'timestamp': segment.get('timestamp'),
                            'evidence': challenge_mentions + recurring_indicators,
                            'meeting_id': meeting_data.get('meeting_id')
                        })
            
            return patterns
            
        except Exception as e:
            logger.error("Challenge pattern detection failed", error=str(e))
            return []
    
    def _detect_behavioral_patterns(self, segments: List[Dict[str, Any]], 
                                  meeting_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect behavioral patterns in participant interactions"""
        patterns = []
        
        try:
            behavioral_template = self.pattern_templates['behavioral_patterns']
            
            # Analyze communication styles
            communication_patterns = self._analyze_communication_styles(segments, behavioral_template)
            patterns.extend(communication_patterns)
            
            # Analyze decision-making patterns
            decision_patterns = self._analyze_decision_making_styles(segments, behavioral_template)
            patterns.extend(decision_patterns)
            
            # Analyze conflict resolution patterns
            conflict_patterns = self._analyze_conflict_resolution_styles(segments, behavioral_template)
            patterns.extend(conflict_patterns)
            
            return patterns
            
        except Exception as e:
            logger.error("Behavioral pattern detection failed", error=str(e))
            return []
    
    def _analyze_communication_styles(self, segments: List[Dict[str, Any]], 
                                    behavioral_template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze communication style patterns"""
        patterns = []
        
        try:
            communication_styles = behavioral_template['communication_styles']
            speaker_styles = defaultdict(list)
            
            for segment in segments:
                text = segment.get('text', '').lower()
                speaker = segment.get('speaker', 'Unknown')
                
                # Identify communication style indicators
                for style in communication_styles:
                    if style in text or self._check_style_context(text, style):
                        speaker_styles[speaker].append({
                            'style': style,
                            'context': text[:100],
                            'timestamp': segment.get('timestamp')
                        })
            
            # Generate patterns for speakers with consistent styles
            for speaker, styles in speaker_styles.items():
                if len(styles) >= 2:  # Multiple instances suggest a pattern
                    style_counts = Counter([s['style'] for s in styles])
                    dominant_style = style_counts.most_common(1)[0]
                    
                    patterns.append({
                        'type': PatternType.BEHAVIORAL_PATTERN.value,
                        'title': f"{speaker} Communication Style Pattern",
                        'description': f"{speaker} consistently demonstrates {dominant_style[0]} communication style",
                        'severity': 'medium',
                        'speaker': speaker,
                        'pattern_frequency': dominant_style[1],
                        'evidence': [s['context'] for s in styles],
                        'style_type': dominant_style[0]
                    })
            
            return patterns
            
        except Exception as e:
            logger.error("Communication style analysis failed", error=str(e))
            return []
    
    async def _analyze_cross_meeting_patterns(self) -> List[DetectedPattern]:
        """Analyze patterns across multiple meetings"""
        try:
            if len(self.meeting_history) < 2:
                return []  # Need at least 2 meetings for cross-meeting analysis
            
            detected_patterns = []
            
            # Analyze recurring challenges across meetings
            challenge_patterns = await self._detect_recurring_challenges()
            detected_patterns.extend(challenge_patterns)
            
            # Analyze behavioral consistency across meetings
            behavioral_patterns = await self._detect_cross_meeting_behavioral_patterns()
            detected_patterns.extend(behavioral_patterns)
            
            # Analyze decision-making patterns
            decision_patterns = await self._detect_decision_making_patterns()
            detected_patterns.extend(decision_patterns)
            
            # Analyze strategic alignment patterns
            strategic_patterns = await self._detect_strategic_patterns()
            detected_patterns.extend(strategic_patterns)
            
            # Update pattern cache
            for pattern in detected_patterns:
                self.detected_patterns[pattern.id] = pattern
            
            return detected_patterns
            
        except Exception as e:
            logger.error("Cross-meeting pattern analysis failed", error=str(e))
            return []
    
    async def _detect_recurring_challenges(self) -> List[DetectedPattern]:
        """Detect challenges that appear across multiple meetings"""
        try:
            patterns = []
            
            # Extract all challenge mentions from meeting history
            all_challenges = []
            for meeting in self.meeting_history[-10:]:  # Last 10 meetings
                meeting_challenges = self._extract_meeting_challenges(meeting)
                all_challenges.extend(meeting_challenges)
            
            if not all_challenges:
                return patterns
            
            # Cluster similar challenges
            challenge_clusters = self._cluster_similar_challenges(all_challenges)
            
            # Create patterns for clusters with multiple occurrences
            for cluster_id, cluster_challenges in challenge_clusters.items():
                if len(cluster_challenges) >= self.pattern_thresholds['min_occurrences']:
                    pattern = self._create_recurring_challenge_pattern(cluster_challenges)
                    if pattern.confidence_score >= self.pattern_thresholds['min_confidence']:
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error("Recurring challenge detection failed", error=str(e))
            return []
    
    def _extract_meeting_challenges(self, meeting_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract challenge mentions from a single meeting"""
        challenges = []
        
        try:
            # Extract from transcript
            transcript_data = meeting_data.get('transcript_analysis', {})
            segments = transcript_data.get('segments', [])
            
            challenge_keywords = self.pattern_templates['recurring_challenges']['keywords']
            
            for segment in segments:
                text = segment.get('text', '').lower()
                
                # Check for challenge keywords
                if any(keyword in text for keyword in challenge_keywords):
                    challenges.append({
                        'text': segment.get('text', ''),
                        'speaker': segment.get('speaker', 'Unknown'),
                        'timestamp': segment.get('timestamp'),
                        'meeting_id': meeting_data.get('meeting_id'),
                        'meeting_date': meeting_data.get('date'),
                        'context': self._extract_challenge_context(text)
                    })
            
            # Extract from identified risks
            risks = meeting_data.get('risks', [])
            for risk in risks:
                challenges.append({
                    'text': risk.get('description', ''),
                    'speaker': 'System Analysis',
                    'timestamp': risk.get('timestamp'),
                    'meeting_id': meeting_data.get('meeting_id'),
                    'meeting_date': meeting_data.get('date'),
                    'context': risk.get('category', 'general')
                })
            
            return challenges
            
        except Exception as e:
            logger.error("Challenge extraction failed", error=str(e))
            return []
    
    def _cluster_similar_challenges(self, challenges: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """Cluster similar challenges using text similarity"""
        try:
            if len(challenges) < 2:
                return {}
            
            # Extract text for vectorization
            challenge_texts = [challenge['text'] for challenge in challenges]
            
            # Vectorize challenge texts
            try:
                tfidf_matrix = self.vectorizer.fit_transform(challenge_texts)
            except ValueError:
                # Handle case where all texts are empty or too similar
                return {}
            
            # Determine optimal number of clusters
            n_clusters = min(len(challenges) // 2, 10)  # Max 10 clusters
            if n_clusters < 2:
                return {}
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            # Group challenges by cluster
            clusters = defaultdict(list)
            for i, label in enumerate(cluster_labels):
                clusters[label].append(challenges[i])
            
            return dict(clusters)
            
        except Exception as e:
            logger.error("Challenge clustering failed", error=str(e))
            return {}
    
    def _create_recurring_challenge_pattern(self, cluster_challenges: List[Dict[str, Any]]) -> DetectedPattern:
        """Create a DetectedPattern from a cluster of similar challenges"""
        try:
            pattern_id = str(uuid.uuid4())
            
            # Analyze cluster characteristics
            meeting_ids = list(set([c['meeting_id'] for c in cluster_challenges]))
            speakers = list(set([c['speaker'] for c in cluster_challenges]))
            contexts = [c.get('context', '') for c in cluster_challenges]
            
            # Determine pattern severity
            severity = self._determine_pattern_severity(cluster_challenges)
            
            # Analyze trend
            trend = self._analyze_pattern_trend(cluster_challenges)
            
            # Generate root cause analysis
            root_causes = self._analyze_root_causes(cluster_challenges)
            
            # Generate intervention recommendations
            interventions = self._generate_intervention_recommendations(cluster_challenges, root_causes)
            
            # Create pattern instances
            instances = []
            for challenge in cluster_challenges:
                instance = PatternInstance(
                    id=str(uuid.uuid4()),
                    meeting_id=challenge['meeting_id'],
                    timestamp=datetime.fromisoformat(challenge['timestamp']) if challenge.get('timestamp') else datetime.utcnow(),
                    context={'text': challenge['text'], 'context': challenge.get('context', '')},
                    severity=self._calculate_instance_severity(challenge),
                    participants_involved=[challenge['speaker']],
                    evidence=[challenge['text']],
                    metadata={'meeting_date': challenge.get('meeting_date')}
                )
                instances.append(instance)
            
            # Calculate confidence score
            confidence_score = self._calculate_pattern_confidence(cluster_challenges, instances)
            
            # Create the detected pattern
            pattern = DetectedPattern(
                id=pattern_id,
                pattern_type=PatternType.RECURRING_CHALLENGE,
                title=f"Recurring Challenge: {self._generate_pattern_title(cluster_challenges)}",
                description=self._generate_pattern_description(cluster_challenges),
                frequency=len(cluster_challenges),
                severity=severity,
                trend=trend,
                first_occurrence=min([datetime.fromisoformat(c['timestamp']) for c in cluster_challenges if c.get('timestamp')], default=datetime.utcnow()),
                last_occurrence=max([datetime.fromisoformat(c['timestamp']) for c in cluster_challenges if c.get('timestamp')], default=datetime.utcnow()),
                instances=instances,
                affected_participants=set(speakers),
                root_causes=root_causes,
                impact_analysis=self._analyze_pattern_impact(cluster_challenges),
                intervention_recommendations=interventions,
                confidence_score=confidence_score
            )
            
            return pattern
            
        except Exception as e:
            logger.error("Pattern creation failed", error=str(e))
            # Return minimal pattern
            return DetectedPattern(
                id=str(uuid.uuid4()),
                pattern_type=PatternType.RECURRING_CHALLENGE,
                title="Pattern Analysis Error",
                description="Unable to analyze pattern due to processing error",
                frequency=len(cluster_challenges),
                severity=PatternSeverity.LOW,
                trend=PatternTrend.STABLE,
                first_occurrence=datetime.utcnow(),
                last_occurrence=datetime.utcnow(),
                instances=[],
                affected_participants=set(),
                root_causes=["Analysis error"],
                impact_analysis={},
                intervention_recommendations=["Review pattern analysis methodology"],
                confidence_score=0.1
            )   
 async def _detect_best_practices(self) -> List[BestPractice]:
        """Detect best practices from successful meeting patterns"""
        try:
            best_practices = []
            
            if len(self.meeting_history) < 3:
                return best_practices  # Need sufficient data for best practice detection
            
            # Analyze successful meetings
            successful_meetings = self._identify_successful_meetings()
            
            if not successful_meetings:
                return best_practices
            
            # Extract common success factors
            success_patterns = self._extract_success_patterns(successful_meetings)
            
            # Generate best practices from patterns
            for pattern_type, pattern_data in success_patterns.items():
                if pattern_data['frequency'] >= 3:  # Minimum occurrences for best practice
                    best_practice = self._create_best_practice(pattern_type, pattern_data)
                    best_practices.append(best_practice)
                    self.best_practices[best_practice.id] = best_practice
            
            return best_practices
            
        except Exception as e:
            logger.error("Best practice detection failed", error=str(e))
            return []
    
    def _identify_successful_meetings(self) -> List[Dict[str, Any]]:
        """Identify meetings that demonstrate successful patterns"""
        successful_meetings = []
        
        try:
            for meeting in self.meeting_history:
                success_score = self._calculate_meeting_success_score(meeting)
                
                if success_score >= 0.7:  # High success threshold
                    meeting['success_score'] = success_score
                    successful_meetings.append(meeting)
            
            return successful_meetings
            
        except Exception as e:
            logger.error("Successful meeting identification failed", error=str(e))
            return []
    
    def _calculate_meeting_success_score(self, meeting_data: Dict[str, Any]) -> float:
        """Calculate success score for a meeting based on multiple factors"""
        try:
            score_factors = []
            
            # Decision quality factor
            decisions = meeting_data.get('decisions', [])
            if decisions:
                decision_scores = [d.get('confidence_score', 0.5) for d in decisions]
                score_factors.append(sum(decision_scores) / len(decision_scores))
            
            # Action clarity factor
            actions = meeting_data.get('actions', [])
            if actions:
                action_scores = [a.get('confidence_score', 0.5) for a in actions]
                score_factors.append(sum(action_scores) / len(action_scores))
            
            # Participation balance factor
            discussion_dynamics = meeting_data.get('discussion_dynamics', {})
            if discussion_dynamics:
                participation = discussion_dynamics.get('participation_analysis', {})
                balance_score = participation.get('participation_balance', 0.5)
                score_factors.append(balance_score)
            
            # Sentiment factor
            if discussion_dynamics:
                sentiment = discussion_dynamics.get('sentiment_analysis', {})
                positive_percentage = sentiment.get('overall_sentiment', {}).get('positive_percentage', 50)
                sentiment_score = min(positive_percentage / 100, 1.0)
                score_factors.append(sentiment_score)
            
            # Human needs fulfillment factor
            human_needs = meeting_data.get('human_needs_intelligence', {})
            if human_needs:
                team_analysis = human_needs.get('team_analysis', {})
                balance_score = team_analysis.get('team_balance_score', 0.5)
                score_factors.append(balance_score)
            
            # Calculate overall score
            if score_factors:
                return sum(score_factors) / len(score_factors)
            else:
                return 0.5  # Default neutral score
                
        except Exception as e:
            logger.error("Meeting success score calculation failed", error=str(e))
            return 0.5
    
    async def _detect_emotional_fatigue(self) -> List[EmotionalFatigueIndicator]:
        """Detect emotional fatigue and misalignment indicators"""
        try:
            indicators = []
            
            if len(self.meeting_history) < 2:
                return indicators
            
            # Analyze recent meetings for fatigue indicators
            recent_meetings = self.meeting_history[-5:]  # Last 5 meetings
            
            # Detect fatigue patterns
            fatigue_indicators = self._analyze_fatigue_patterns(recent_meetings)
            indicators.extend(fatigue_indicators)
            
            # Detect misalignment patterns
            misalignment_indicators = self._analyze_misalignment_patterns(recent_meetings)
            indicators.extend(misalignment_indicators)
            
            # Detect stress patterns
            stress_indicators = self._analyze_stress_patterns(recent_meetings)
            indicators.extend(stress_indicators)
            
            # Detect disengagement patterns
            disengagement_indicators = self._analyze_disengagement_patterns(recent_meetings)
            indicators.extend(disengagement_indicators)
            
            # Update cache
            for indicator in indicators:
                self.emotional_indicators[indicator.id] = indicator
            
            return indicators
            
        except Exception as e:
            logger.error("Emotional fatigue detection failed", error=str(e))
            return []
    
    def _analyze_fatigue_patterns(self, meetings: List[Dict[str, Any]]) -> List[EmotionalFatigueIndicator]:
        """Analyze patterns indicating emotional fatigue"""
        indicators = []
        
        try:
            fatigue_keywords = self.pattern_templates['emotional_indicators']['fatigue']
            
            # Track fatigue mentions by participant
            participant_fatigue = defaultdict(list)
            
            for meeting in meetings:
                transcript_data = meeting.get('transcript_analysis', {})
                segments = transcript_data.get('segments', [])
                
                for segment in segments:
                    text = segment.get('text', '').lower()
                    speaker = segment.get('speaker', 'Unknown')
                    
                    fatigue_mentions = [kw for kw in fatigue_keywords if kw in text]
                    if fatigue_mentions:
                        participant_fatigue[speaker].append({
                            'meeting_id': meeting.get('meeting_id'),
                            'text': segment.get('text'),
                            'keywords': fatigue_mentions,
                            'timestamp': segment.get('timestamp')
                        })
            
            # Create indicators for participants with multiple fatigue mentions
            for participant, mentions in participant_fatigue.items():
                if len(mentions) >= 2:  # Multiple mentions suggest pattern
                    severity = self._assess_fatigue_severity(mentions)
                    
                    indicator = EmotionalFatigueIndicator(
                        id=str(uuid.uuid4()),
                        indicator_type='fatigue',
                        severity=severity,
                        affected_participants=[participant],
                        symptoms=[m['text'] for m in mentions],
                        contributing_factors=self._identify_fatigue_factors(mentions),
                        intervention_urgency=self._determine_intervention_urgency(severity),
                        recommended_actions=self._generate_fatigue_interventions(participant, mentions),
                        monitoring_metrics=self._define_fatigue_monitoring_metrics()
                    )
                    indicators.append(indicator)
            
            return indicators
            
        except Exception as e:
            logger.error("Fatigue pattern analysis failed", error=str(e))
            return []
    
    async def _identify_systemic_issues(self) -> List[SystemicIssue]:
        """Identify systemic organizational issues through pattern analysis"""
        try:
            systemic_issues = []
            
            if len(self.meeting_history) < 5:
                return systemic_issues  # Need sufficient data for systemic analysis
            
            # Analyze cross-cutting patterns that indicate systemic issues
            
            # Communication breakdown patterns
            communication_issues = self._detect_communication_breakdowns()
            systemic_issues.extend(communication_issues)
            
            # Decision-making dysfunction patterns
            decision_issues = self._detect_decision_making_dysfunction()
            systemic_issues.extend(decision_issues)
            
            # Resource constraint patterns
            resource_issues = self._detect_resource_constraints()
            systemic_issues.extend(resource_issues)
            
            # Cultural misalignment patterns
            cultural_issues = self._detect_cultural_misalignment()
            systemic_issues.extend(cultural_issues)
            
            # Process inefficiency patterns
            process_issues = self._detect_process_inefficiencies()
            systemic_issues.extend(process_issues)
            
            # Update cache
            for issue in systemic_issues:
                self.systemic_issues[issue.id] = issue
            
            return systemic_issues
            
        except Exception as e:
            logger.error("Systemic issue identification failed", error=str(e))
            return []
    
    def _detect_communication_breakdowns(self) -> List[SystemicIssue]:
        """Detect systemic communication breakdown patterns"""
        issues = []
        
        try:
            # Look for recurring communication problems across meetings
            communication_problems = []
            
            for meeting in self.meeting_history[-10:]:  # Last 10 meetings
                discussion_dynamics = meeting.get('discussion_dynamics', {})
                
                # Check for communication issues
                if discussion_dynamics:
                    participation = discussion_dynamics.get('participation_analysis', {})
                    balance_score = participation.get('participation_balance', 1.0)
                    
                    if balance_score < 0.3:  # Poor participation balance
                        communication_problems.append({
                            'meeting_id': meeting.get('meeting_id'),
                            'issue_type': 'participation_imbalance',
                            'severity': 'high' if balance_score < 0.2 else 'medium',
                            'details': participation
                        })
                    
                    # Check for interruption patterns
                    communication_patterns = discussion_dynamics.get('communication_patterns', {})
                    interruption_rate = communication_patterns.get('interruption_patterns', {}).get('interruption_rate', 0)
                    
                    if interruption_rate > 0.4:  # High interruption rate
                        communication_problems.append({
                            'meeting_id': meeting.get('meeting_id'),
                            'issue_type': 'high_interruptions',
                            'severity': 'high' if interruption_rate > 0.6 else 'medium',
                            'details': communication_patterns
                        })
            
            # If communication problems are frequent, create systemic issue
            if len(communication_problems) >= 3:
                issue = SystemicIssue(
                    id=str(uuid.uuid4()),
                    issue_title="Systemic Communication Breakdown",
                    issue_description=f"Communication issues detected in {len(communication_problems)} recent meetings",
                    root_causes=self._analyze_communication_root_causes(communication_problems),
                    affected_areas=["team_dynamics", "decision_making", "collaboration"],
                    impact_assessment=self._assess_communication_impact(communication_problems),
                    urgency_level=self._determine_communication_urgency(communication_problems),
                    intervention_strategy=self._develop_communication_intervention_strategy(communication_problems),
                    success_metrics=["Participation balance score > 0.6", "Interruption rate < 0.3", "Positive sentiment > 60%"],
                    timeline_recommendations={"immediate": "Communication training", "short_term": "Meeting facilitation improvements", "long_term": "Culture change initiatives"},
                    stakeholder_involvement=["Team leads", "HR", "Communication specialists"]
                )
                issues.append(issue)
            
            return issues
            
        except Exception as e:
            logger.error("Communication breakdown detection failed", error=str(e))
            return []
    
    # Helper methods for pattern analysis
    def _assess_challenge_severity(self, text: str, template: Dict[str, Any]) -> str:
        """Assess severity of a challenge based on text content"""
        severity_indicators = template['severity_indicators']
        
        text_lower = text.lower()
        
        for severity, keywords in severity_indicators.items():
            if any(keyword in text_lower for keyword in keywords):
                return severity
        
        return 'medium'  # Default severity
    
    def _check_style_context(self, text: str, style: str) -> bool:
        """Check if text context matches a communication style"""
        style_contexts = {
            'interrupting': ['but', 'however', 'wait', 'actually'],
            'dominating': ['i think', 'we should', 'let me', 'i will'],
            'collaborative': ['what do you think', 'together', 'we could', 'how about'],
            'supportive': ['great idea', 'i agree', 'that makes sense', 'good point']
        }
        
        if style in style_contexts:
            return any(context in text for context in style_contexts[style])
        
        return False
    
    def _calculate_analysis_confidence(self, current_patterns: List[Dict[str, Any]], 
                                     cross_patterns: List[DetectedPattern]) -> float:
        """Calculate overall confidence score for pattern analysis"""
        try:
            confidence_factors = []
            
            # Data quality factor
            if len(self.meeting_history) >= 5:
                confidence_factors.append(0.8)
            elif len(self.meeting_history) >= 3:
                confidence_factors.append(0.6)
            else:
                confidence_factors.append(0.4)
            
            # Pattern consistency factor
            if cross_patterns:
                pattern_confidences = [p.confidence_score for p in cross_patterns]
                avg_confidence = sum(pattern_confidences) / len(pattern_confidences)
                confidence_factors.append(avg_confidence)
            
            # Current meeting pattern factor
            if current_patterns:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.5)
            
            return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
            
        except Exception as e:
            logger.error("Confidence calculation failed", error=str(e))
            return 0.5