"""
Oracle Intelligence System - DiscrepancyResolver
Handles conflicts, disagreements, and resolution strategies with psychological intelligence

This module enables sophisticated conflict resolution through:
- Automatic discrepancy detection from debrief responses
- Psychological root cause analysis using MBTI/DISC/Big Five frameworks
- Adaptive resolution strategies tailored to personality combinations
- Asynchronous resolution workflows (voting or meeting scheduling)
- AI-powered mediation with personalized Tanka guidance
- Conflict pattern learning and prevention strategies
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict, Counter

from Mem0Manager import Mem0Manager, TeamMember, DebriefEntry
from EnhancedTankaProfileLoader import EnhancedTankaProfileLoader, PsychologicalProfile, MBTIType, DISCType
from InsightSynthesizer import InsightSynthesizer, SynthesizedInsight
from AsyncDecisionValidator import AsyncDecisionValidator, Decision, DecisionOption, DecisionType, VoteType

class DiscrepancyType(Enum):
    """Types of discrepancies that can occur"""
    FACTUAL_DISAGREEMENT = "factual_disagreement"
    PRIORITY_CONFLICT = "priority_conflict"
    APPROACH_DIFFERENCE = "approach_difference"
    RESOURCE_CONTENTION = "resource_contention"
    TIMELINE_DISPUTE = "timeline_dispute"
    RESPONSIBILITY_UNCLEAR = "responsibility_unclear"
    COMMUNICATION_BREAKDOWN = "communication_breakdown"
    VALUE_MISALIGNMENT = "value_misalignment"
    EXPECTATION_MISMATCH = "expectation_mismatch"
    DECISION_DISAGREEMENT = "decision_disagreement"

class DiscrepancySeverity(Enum):
    """Severity levels for discrepancies"""
    CRITICAL = "critical"      # Blocks progress, immediate resolution needed
    HIGH = "high"             # Significant impact, resolution within 24 hours
    MEDIUM = "medium"         # Moderate impact, resolution within 3 days
    LOW = "low"              # Minor impact, resolution within 1 week
    INFORMATIONAL = "informational"  # No immediate action needed

class ResolutionStrategy(Enum):
    """Strategies for resolving discrepancies"""
    ASYNC_VOTE = "async_vote"
    MEDIATED_DISCUSSION = "mediated_discussion"
    EXPERT_CONSULTATION = "expert_consultation"
    COMPROMISE_NEGOTIATION = "compromise_negotiation"
    ESCALATION_TO_LEADERSHIP = "escalation_to_leadership"
    DEFER_TO_NEXT_MEETING = "defer_to_next_meeting"
    SPLIT_DECISION = "split_decision"
    CONSENSUS_BUILDING = "consensus_building"

class ResolutionStatus(Enum):
    """Status of discrepancy resolution"""
    DETECTED = "detected"
    ANALYZING = "analyzing"
    STRATEGY_SELECTED = "strategy_selected"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    DEFERRED = "deferred"
    UNRESOLVABLE = "unresolvable"

@dataclass
class DiscrepancyParticipant:
    """A participant in a discrepancy"""
    participant_id: str
    participant_name: str
    position: str  # Their stance or position
    confidence_level: float  # 0.0 to 1.0
    reasoning: str
    emotional_state: str  # calm, frustrated, passionate, etc.
    psychological_factors: Dict[str, Any] = field(default_factory=dict)
    flexibility_score: float = 0.5  # How open to compromise (0.0 to 1.0)
    expertise_relevance: float = 0.5  # How relevant their expertise is

@dataclass
class Discrepancy:
    """A discrepancy requiring resolution"""
    discrepancy_id: str
    title: str
    description: str
    discrepancy_type: DiscrepancyType
    severity: DiscrepancySeverity
    
    # Source information
    source_meeting_id: Optional[str] = None
    source_debrief_ids: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)
    
    # Participants and positions
    participants: List[DiscrepancyParticipant] = field(default_factory=list)
    affected_projects: List[str] = field(default_factory=list)
    affected_decisions: List[str] = field(default_factory=list)
    
    # Resolution information
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolution_status: ResolutionStatus = ResolutionStatus.DETECTED
    resolution_deadline: Optional[datetime] = None
    assigned_mediator: Optional[str] = None
    
    # Analysis results
    root_cause_analysis: Dict[str, Any] = field(default_factory=dict)
    psychological_analysis: Dict[str, Any] = field(default_factory=dict)
    impact_assessment: Dict[str, Any] = field(default_factory=dict)
    resolution_options: List[Dict[str, Any]] = field(default_factory=list)
    
    # Resolution tracking
    resolution_attempts: List[Dict[str, Any]] = field(default_factory=list)
    final_resolution: Optional[str] = None
    resolution_satisfaction: Dict[str, float] = field(default_factory=dict)  # participant_id -> satisfaction score
    lessons_learned: List[str] = field(default_factory=list)

@dataclass
class ResolutionAttempt:
    """An attempt to resolve a discrepancy"""
    attempt_id: str
    strategy_used: ResolutionStrategy
    started_at: datetime
    completed_at: Optional[datetime] = None
    success: Optional[bool] = None
    participants_involved: List[str] = field(default_factory=list)
    actions_taken: List[str] = field(default_factory=list)
    outcomes: Dict[str, Any] = field(default_factory=dict)
    satisfaction_scores: Dict[str, float] = field(default_factory=dict)
    notes: str = ""

@dataclass
class MediationSession:
    """A mediation session for conflict resolution"""
    session_id: str
    discrepancy_id: str
    mediator_id: str
    participants: List[str]
    session_type: str  # "ai_mediated", "human_mediated", "hybrid"
    
    # Session configuration
    session_duration: timedelta
    scheduled_at: datetime
    ground_rules: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    
    # Session data
    conversation_log: List[Dict[str, Any]] = field(default_factory=list)
    agreements_reached: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    follow_up_needed: bool = False
    
    # Results
    resolution_achieved: bool = False
    participant_satisfaction: Dict[str, float] = field(default_factory=dict)
    effectiveness_score: float = 0.0

class DiscrepancyResolver:
    """
    Handles conflicts, disagreements, and resolution strategies with psychological intelligence
    
    Enables sophisticated conflict resolution for the Impact Launchpad team through
    automatic discrepancy detection, psychological analysis, adaptive resolution
    strategies, and AI-powered mediation.
    """
    
    def __init__(self, 
                 mem0_manager: Mem0Manager, 
                 enhanced_tanka: EnhancedTankaProfileLoader, 
                 insight_synthesizer: InsightSynthesizer,
                 async_decision_validator: AsyncDecisionValidator):
        """Initialize DiscrepancyResolver with integrated components"""
        self.mem0_manager = mem0_manager
        self.enhanced_tanka = enhanced_tanka
        self.insight_synthesizer = insight_synthesizer
        self.async_decision_validator = async_decision_validator
        
        # Discrepancy storage
        self.discrepancies: Dict[str, Discrepancy] = {}
        self.resolution_history: List[ResolutionAttempt] = []
        self.mediation_sessions: Dict[str, MediationSession] = {}
        
        # Configuration
        self.severity_thresholds = {
            DiscrepancySeverity.CRITICAL: timedelta(hours=4),
            DiscrepancySeverity.HIGH: timedelta(hours=24),
            DiscrepancySeverity.MEDIUM: timedelta(days=3),
            DiscrepancySeverity.LOW: timedelta(weeks=1),
            DiscrepancySeverity.INFORMATIONAL: timedelta(weeks=4)
        }
        
        # Psychological conflict patterns
        self.mbti_conflict_patterns = {
            # Thinking vs Feeling conflicts
            ("T", "F"): {
                "common_issues": ["Logic vs emotion in decision-making", "Task vs people focus"],
                "resolution_strategies": [ResolutionStrategy.MEDIATED_DISCUSSION, ResolutionStrategy.COMPROMISE_NEGOTIATION],
                "mediation_approach": "Balance analytical and empathetic perspectives"
            },
            # Judging vs Perceiving conflicts
            ("J", "P"): {
                "common_issues": ["Structure vs flexibility", "Planning vs adaptability"],
                "resolution_strategies": [ResolutionStrategy.COMPROMISE_NEGOTIATION, ResolutionStrategy.CONSENSUS_BUILDING],
                "mediation_approach": "Find structured flexibility that satisfies both preferences"
            },
            # Extraversion vs Introversion conflicts
            ("E", "I"): {
                "common_issues": ["Communication style differences", "Processing time needs"],
                "resolution_strategies": [ResolutionStrategy.ASYNC_VOTE, ResolutionStrategy.MEDIATED_DISCUSSION],
                "mediation_approach": "Provide both immediate discussion and reflection time"
            },
            # Sensing vs Intuition conflicts
            ("S", "N"): {
                "common_issues": ["Detail vs big picture focus", "Practical vs theoretical approaches"],
                "resolution_strategies": [ResolutionStrategy.EXPERT_CONSULTATION, ResolutionStrategy.COMPROMISE_NEGOTIATION],
                "mediation_approach": "Bridge concrete details with visionary thinking"
            }
        }
        
        # DISC conflict patterns
        self.disc_conflict_patterns = {
            ("D", "S"): {
                "common_issues": ["Fast pace vs steady pace", "Direct vs diplomatic communication"],
                "resolution_strategies": [ResolutionStrategy.MEDIATED_DISCUSSION, ResolutionStrategy.COMPROMISE_NEGOTIATION],
                "mediation_approach": "Balance urgency with stability needs"
            },
            ("I", "C"): {
                "common_issues": ["Optimism vs caution", "People focus vs task focus"],
                "resolution_strategies": [ResolutionStrategy.CONSENSUS_BUILDING, ResolutionStrategy.EXPERT_CONSULTATION],
                "mediation_approach": "Combine enthusiasm with analytical rigor"
            },
            ("D", "I"): {
                "common_issues": ["Results vs relationships", "Control vs collaboration"],
                "resolution_strategies": [ResolutionStrategy.COMPROMISE_NEGOTIATION, ResolutionStrategy.SPLIT_DECISION],
                "mediation_approach": "Find win-win solutions that achieve results through relationships"
            },
            ("S", "C"): {
                "common_issues": ["People harmony vs quality standards", "Acceptance vs criticism"],
                "resolution_strategies": [ResolutionStrategy.MEDIATED_DISCUSSION, ResolutionStrategy.CONSENSUS_BUILDING],
                "mediation_approach": "Maintain harmony while ensuring quality"
            }
        }
        
        print("🔧 DiscrepancyResolver initialized with conflict intelligence")
    
    def detect_discrepancies_from_debriefs(self, debrief_entries: List[DebriefEntry]) -> List[Discrepancy]:
        """Detect discrepancies from multiple debrief entries"""
        
        print(f"🔍 Analyzing {len(debrief_entries)} debrief entries for discrepancies...")
        
        detected_discrepancies = []
        
        # Group debriefs by meeting
        meeting_debriefs = defaultdict(list)
        for debrief in debrief_entries:
            meeting_debriefs[debrief.meeting_id].append(debrief)
        
        # Analyze each meeting's debriefs
        for meeting_id, debriefs in meeting_debriefs.items():
            meeting_discrepancies = self._analyze_meeting_debriefs(meeting_id, debriefs)
            detected_discrepancies.extend(meeting_discrepancies)
        
        # Store detected discrepancies
        for discrepancy in detected_discrepancies:
            self.discrepancies[discrepancy.discrepancy_id] = discrepancy
        
        print(f"✅ Detected {len(detected_discrepancies)} discrepancies")
        return detected_discrepancies
    
    def _analyze_meeting_debriefs(self, meeting_id: str, debriefs: List[DebriefEntry]) -> List[Discrepancy]:
        """Analyze debriefs from a single meeting for discrepancies"""
        
        discrepancies = []
        
        # Analyze decision disagreements
        decision_discrepancies = self._detect_decision_disagreements(meeting_id, debriefs)
        discrepancies.extend(decision_discrepancies)
        
        # Analyze priority conflicts
        priority_discrepancies = self._detect_priority_conflicts(meeting_id, debriefs)
        discrepancies.extend(priority_discrepancies)
        
        # Analyze approach differences
        approach_discrepancies = self._detect_approach_differences(meeting_id, debriefs)
        discrepancies.extend(approach_discrepancies)
        
        # Analyze communication breakdowns
        communication_discrepancies = self._detect_communication_breakdowns(meeting_id, debriefs)
        discrepancies.extend(communication_discrepancies)
        
        # Analyze responsibility unclear issues
        responsibility_discrepancies = self._detect_responsibility_issues(meeting_id, debriefs)
        discrepancies.extend(responsibility_discrepancies)
        
        return discrepancies
    
    def _detect_decision_disagreements(self, meeting_id: str, debriefs: List[DebriefEntry]) -> List[Discrepancy]:
        """Detect disagreements about decisions made in the meeting"""
        
        discrepancies = []
        
        # Collect all decision-related responses
        decision_responses = defaultdict(list)
        
        for debrief in debriefs:
            for response in debrief.responses:
                if "decision" in response.question.lower() or "agree" in response.question.lower():
                    decision_responses[response.question].append({
                        "participant_id": debrief.participant_id,
                        "participant_name": debrief.participant_name,
                        "response": response.response,
                        "confidence": response.confidence_level,
                        "debrief_id": debrief.debrief_id
                    })
        
        # Analyze each decision question for disagreements
        for question, responses in decision_responses.items():
            if len(responses) < 2:
                continue
            
            # Look for conflicting responses
            positive_responses = []
            negative_responses = []
            
            for resp in responses:
                response_text = resp["response"].lower()
                if any(word in response_text for word in ["disagree", "oppose", "against", "no", "reject"]):
                    negative_responses.append(resp)
                elif any(word in response_text for word in ["agree", "support", "yes", "approve", "endorse"]):
                    positive_responses.append(resp)
            
            # If we have both positive and negative responses, it's a discrepancy
            if positive_responses and negative_responses:
                discrepancy = self._create_decision_discrepancy(
                    meeting_id, question, positive_responses, negative_responses
                )
                discrepancies.append(discrepancy)
        
        return discrepancies
    
    def _create_decision_discrepancy(self, meeting_id: str, question: str, positive_responses: List[Dict], negative_responses: List[Dict]) -> Discrepancy:
        """Create a decision disagreement discrepancy"""
        
        discrepancy_id = str(uuid.uuid4())
        
        # Create participants
        participants = []
        
        for resp in positive_responses:
            participant = DiscrepancyParticipant(
                participant_id=resp["participant_id"],
                participant_name=resp["participant_name"],
                position="support",
                confidence_level=resp["confidence"],
                reasoning=resp["response"],
                emotional_state="supportive"
            )
            participants.append(participant)
        
        for resp in negative_responses:
            participant = DiscrepancyParticipant(
                participant_id=resp["participant_id"],
                participant_name=resp["participant_name"],
                position="oppose",
                confidence_level=resp["confidence"],
                reasoning=resp["response"],
                emotional_state="concerned"
            )
            participants.append(participant)
        
        # Determine severity based on number of people and confidence levels
        total_participants = len(participants)
        avg_confidence = np.mean([p.confidence_level for p in participants])
        
        if total_participants >= 4 and avg_confidence > 0.7:
            severity = DiscrepancySeverity.HIGH
        elif total_participants >= 3 or avg_confidence > 0.8:
            severity = DiscrepancySeverity.MEDIUM
        else:
            severity = DiscrepancySeverity.LOW
        
        discrepancy = Discrepancy(
            discrepancy_id=discrepancy_id,
            title=f"Decision disagreement: {question[:50]}...",
            description=f"Team members have conflicting views on: {question}",
            discrepancy_type=DiscrepancyType.DECISION_DISAGREEMENT,
            severity=severity,
            source_meeting_id=meeting_id,
            source_debrief_ids=[resp["debrief_id"] for resp in positive_responses + negative_responses],
            participants=participants
        )
        
        return discrepancy
    
    def _detect_priority_conflicts(self, meeting_id: str, debriefs: List[DebriefEntry]) -> List[Discrepancy]:
        """Detect conflicts in priorities or importance rankings"""
        
        discrepancies = []
        
        # Look for priority-related questions
        priority_responses = defaultdict(list)
        
        for debrief in debriefs:
            for response in debrief.responses:
                if any(word in response.question.lower() for word in ["priority", "important", "urgent", "focus"]):
                    priority_responses[response.question].append({
                        "participant_id": debrief.participant_id,
                        "participant_name": debrief.participant_name,
                        "response": response.response,
                        "confidence": response.confidence_level,
                        "debrief_id": debrief.debrief_id
                    })
        
        # Analyze for conflicting priorities
        for question, responses in priority_responses.items():
            if len(responses) >= 3:  # Need at least 3 responses to detect conflicts
                # Simple conflict detection: if responses mention different priorities
                mentioned_priorities = set()
                for resp in responses:
                    # Extract potential priority keywords
                    response_words = resp["response"].lower().split()
                    for word in response_words:
                        if len(word) > 4:  # Focus on meaningful words
                            mentioned_priorities.add(word)
                
                # If many different priorities mentioned, might be a conflict
                if len(mentioned_priorities) > len(responses) * 1.5:  # Heuristic for conflict
                    discrepancy = self._create_priority_discrepancy(meeting_id, question, responses)
                    discrepancies.append(discrepancy)
        
        return discrepancies
    
    def _create_priority_discrepancy(self, meeting_id: str, question: str, responses: List[Dict]) -> Discrepancy:
        """Create a priority conflict discrepancy"""
        
        discrepancy_id = str(uuid.uuid4())
        
        participants = []
        for resp in responses:
            participant = DiscrepancyParticipant(
                participant_id=resp["participant_id"],
                participant_name=resp["participant_name"],
                position=resp["response"][:100],  # First 100 chars as position
                confidence_level=resp["confidence"],
                reasoning=resp["response"],
                emotional_state="focused"
            )
            participants.append(participant)
        
        discrepancy = Discrepancy(
            discrepancy_id=discrepancy_id,
            title=f"Priority conflict: {question[:50]}...",
            description=f"Team members have different priority assessments for: {question}",
            discrepancy_type=DiscrepancyType.PRIORITY_CONFLICT,
            severity=DiscrepancySeverity.MEDIUM,
            source_meeting_id=meeting_id,
            source_debrief_ids=[resp["debrief_id"] for resp in responses],
            participants=participants
        )
        
        return discrepancy
    
    def _detect_approach_differences(self, meeting_id: str, debriefs: List[DebriefEntry]) -> List[Discrepancy]:
        """Detect differences in proposed approaches or methodologies"""
        
        discrepancies = []
        
        # Look for approach-related questions
        approach_responses = defaultdict(list)
        
        for debrief in debriefs:
            for response in debrief.responses:
                if any(word in response.question.lower() for word in ["approach", "method", "strategy", "how", "way"]):
                    approach_responses[response.question].append({
                        "participant_id": debrief.participant_id,
                        "participant_name": debrief.participant_name,
                        "response": response.response,
                        "confidence": response.confidence_level,
                        "debrief_id": debrief.debrief_id
                    })
        
        # Analyze for different approaches
        for question, responses in approach_responses.items():
            if len(responses) >= 2:
                # Check for significantly different response lengths or keywords
                response_lengths = [len(resp["response"]) for resp in responses]
                if max(response_lengths) > min(response_lengths) * 2:  # Significant difference in detail
                    discrepancy = self._create_approach_discrepancy(meeting_id, question, responses)
                    discrepancies.append(discrepancy)
        
        return discrepancies
    
    def _create_approach_discrepancy(self, meeting_id: str, question: str, responses: List[Dict]) -> Discrepancy:
        """Create an approach difference discrepancy"""
        
        discrepancy_id = str(uuid.uuid4())
        
        participants = []
        for resp in responses:
            participant = DiscrepancyParticipant(
                participant_id=resp["participant_id"],
                participant_name=resp["participant_name"],
                position=resp["response"][:100],
                confidence_level=resp["confidence"],
                reasoning=resp["response"],
                emotional_state="analytical"
            )
            participants.append(participant)
        
        discrepancy = Discrepancy(
            discrepancy_id=discrepancy_id,
            title=f"Approach difference: {question[:50]}...",
            description=f"Team members suggest different approaches for: {question}",
            discrepancy_type=DiscrepancyType.APPROACH_DIFFERENCE,
            severity=DiscrepancySeverity.LOW,
            source_meeting_id=meeting_id,
            source_debrief_ids=[resp["debrief_id"] for resp in responses],
            participants=participants
        )
        
        return discrepancy
    
    def _detect_communication_breakdowns(self, meeting_id: str, debriefs: List[DebriefEntry]) -> List[Discrepancy]:
        """Detect communication breakdowns or misunderstandings"""
        
        discrepancies = []
        
        # Look for communication issues in responses
        for debrief in debriefs:
            for response in debrief.responses:
                response_text = response.response.lower()
                
                # Check for communication breakdown indicators
                breakdown_indicators = [
                    "unclear", "confused", "misunderstood", "didn't understand",
                    "not clear", "ambiguous", "mixed messages", "contradictory"
                ]
                
                if any(indicator in response_text for indicator in breakdown_indicators):
                    discrepancy = self._create_communication_discrepancy(meeting_id, debrief, response)
                    discrepancies.append(discrepancy)
        
        return discrepancies
    
    def _create_communication_discrepancy(self, meeting_id: str, debrief: DebriefEntry, response) -> Discrepancy:
        """Create a communication breakdown discrepancy"""
        
        discrepancy_id = str(uuid.uuid4())
        
        participant = DiscrepancyParticipant(
            participant_id=debrief.participant_id,
            participant_name=debrief.participant_name,
            position="communication_issue",
            confidence_level=response.confidence_level,
            reasoning=response.response,
            emotional_state="confused"
        )
        
        discrepancy = Discrepancy(
            discrepancy_id=discrepancy_id,
            title=f"Communication breakdown reported by {debrief.participant_name}",
            description=f"Communication issue identified: {response.question}",
            discrepancy_type=DiscrepancyType.COMMUNICATION_BREAKDOWN,
            severity=DiscrepancySeverity.MEDIUM,
            source_meeting_id=meeting_id,
            source_debrief_ids=[debrief.debrief_id],
            participants=[participant]
        )
        
        return discrepancy
    
    def _detect_responsibility_issues(self, meeting_id: str, debriefs: List[DebriefEntry]) -> List[Discrepancy]:
        """Detect unclear responsibilities or role confusion"""
        
        discrepancies = []
        
        # Look for responsibility-related questions
        responsibility_responses = defaultdict(list)
        
        for debrief in debriefs:
            for response in debrief.responses:
                if any(word in response.question.lower() for word in ["responsible", "owner", "accountable", "who"]):
                    responsibility_responses[response.question].append({
                        "participant_id": debrief.participant_id,
                        "participant_name": debrief.participant_name,
                        "response": response.response,
                        "confidence": response.confidence_level,
                        "debrief_id": debrief.debrief_id
                    })
        
        # Analyze for unclear responsibilities
        for question, responses in responsibility_responses.items():
            unclear_responses = []
            for resp in responses:
                response_text = resp["response"].lower()
                if any(word in response_text for word in ["unclear", "not sure", "don't know", "uncertain"]):
                    unclear_responses.append(resp)
            
            if unclear_responses:
                discrepancy = self._create_responsibility_discrepancy(meeting_id, question, unclear_responses)
                discrepancies.append(discrepancy)
        
        return discrepancies
    
    def _create_responsibility_discrepancy(self, meeting_id: str, question: str, responses: List[Dict]) -> Discrepancy:
        """Create a responsibility unclear discrepancy"""
        
        discrepancy_id = str(uuid.uuid4())
        
        participants = []
        for resp in responses:
            participant = DiscrepancyParticipant(
                participant_id=resp["participant_id"],
                participant_name=resp["participant_name"],
                position="unclear",
                confidence_level=resp["confidence"],
                reasoning=resp["response"],
                emotional_state="uncertain"
            )
            participants.append(participant)
        
        discrepancy = Discrepancy(
            discrepancy_id=discrepancy_id,
            title=f"Responsibility unclear: {question[:50]}...",
            description=f"Team members are unclear about responsibilities for: {question}",
            discrepancy_type=DiscrepancyType.RESPONSIBILITY_UNCLEAR,
            severity=DiscrepancySeverity.MEDIUM,
            source_meeting_id=meeting_id,
            source_debrief_ids=[resp["debrief_id"] for resp in responses],
            participants=participants
        )
        
        return discrepancy
    
    def analyze_discrepancy_psychology(self, discrepancy: Discrepancy) -> Discrepancy:
        """Analyze psychological factors contributing to the discrepancy"""
        
        print(f"🧠 Analyzing psychological factors for discrepancy: {discrepancy.title}")
        
        psychological_analysis = {
            "mbti_factors": {},
            "disc_factors": {},
            "personality_conflicts": [],
            "communication_style_mismatches": [],
            "stress_indicators": [],
            "resolution_recommendations": []
        }
        
        # Analyze each participant's psychological profile
        participant_profiles = {}
        for participant in discrepancy.participants:
            profile = self.enhanced_tanka.get_psychological_profile(participant.participant_id)
            if profile:
                participant_profiles[participant.participant_id] = profile
                
                # Update participant psychological factors
                participant.psychological_factors = {
                    "mbti_type": profile.mbti_type.value,
                    "disc_primary": profile.disc_primary.value,
                    "big_five_traits": profile.big_five_traits,
                    "stress_indicators": profile.stress_indicators,
                    "communication_preferences": profile.communication_preferences
                }
        
        # Analyze MBTI conflicts
        mbti_types = [profile.mbti_type.value for profile in participant_profiles.values()]
        psychological_analysis["mbti_factors"] = self._analyze_mbti_conflicts(mbti_types)
        
        # Analyze DISC conflicts
        disc_types = [profile.disc_primary.value for profile in participant_profiles.values()]
        psychological_analysis["disc_factors"] = self._analyze_disc_conflicts(disc_types)
        
        # Identify personality conflicts
        psychological_analysis["personality_conflicts"] = self._identify_personality_conflicts(participant_profiles)
        
        # Analyze communication style mismatches
        psychological_analysis["communication_style_mismatches"] = self._analyze_communication_mismatches(participant_profiles)
        
        # Detect stress indicators
        psychological_analysis["stress_indicators"] = self._detect_stress_indicators(discrepancy.participants)
        
        # Generate resolution recommendations
        psychological_analysis["resolution_recommendations"] = self._generate_psychological_resolution_recommendations(
            discrepancy, participant_profiles
        )
        
        discrepancy.psychological_analysis = psychological_analysis
        
        print(f"✅ Psychological analysis complete")
        print(f"   MBTI conflicts: {len(psychological_analysis['mbti_factors'])}")
        print(f"   DISC conflicts: {len(psychological_analysis['disc_factors'])}")
        print(f"   Personality conflicts: {len(psychological_analysis['personality_conflicts'])}")
        print(f"   Resolution recommendations: {len(psychological_analysis['resolution_recommendations'])}")
        
        return discrepancy
    
    def _analyze_mbti_conflicts(self, mbti_types: List[str]) -> Dict[str, Any]:
        """Analyze MBTI-based conflicts"""
        
        mbti_analysis = {
            "type_distribution": Counter(mbti_types),
            "potential_conflicts": [],
            "cognitive_function_clashes": []
        }
        
        # Check for common MBTI conflicts
        for i, type1 in enumerate(mbti_types):
            for j, type2 in enumerate(mbti_types[i+1:], i+1):
                # Check for T vs F conflicts
                if type1[2] != type2[2]:  # Different thinking/feeling preference
                    conflict_key = tuple(sorted([type1[2], type2[2]]))
                    if conflict_key in self.mbti_conflict_patterns:
                        mbti_analysis["potential_conflicts"].append({
                            "types": [type1, type2],
                            "conflict_area": "Thinking vs Feeling",
                            "pattern": self.mbti_conflict_patterns[conflict_key]
                        })
                
                # Check for J vs P conflicts
                if type1[3] != type2[3]:  # Different judging/perceiving preference
                    conflict_key = tuple(sorted([type1[3], type2[3]]))
                    if conflict_key in self.mbti_conflict_patterns:
                        mbti_analysis["potential_conflicts"].append({
                            "types": [type1, type2],
                            "conflict_area": "Judging vs Perceiving",
                            "pattern": self.mbti_conflict_patterns[conflict_key]
                        })
        
        return mbti_analysis
    
    def _analyze_disc_conflicts(self, disc_types: List[str]) -> Dict[str, Any]:
        """Analyze DISC-based conflicts"""
        
        disc_analysis = {
            "type_distribution": Counter(disc_types),
            "potential_conflicts": [],
            "communication_clashes": []
        }
        
        # Check for common DISC conflicts
        for i, type1 in enumerate(disc_types):
            for j, type2 in enumerate(disc_types[i+1:], i+1):
                conflict_key = tuple(sorted([type1, type2]))
                if conflict_key in self.disc_conflict_patterns:
                    disc_analysis["potential_conflicts"].append({
                        "types": [type1, type2],
                        "pattern": self.disc_conflict_patterns[conflict_key]
                    })
        
        return disc_analysis
    
    def _identify_personality_conflicts(self, participant_profiles: Dict[str, PsychologicalProfile]) -> List[Dict[str, Any]]:
        """Identify specific personality-based conflicts"""
        
        conflicts = []
        
        profile_list = list(participant_profiles.items())
        for i, (id1, profile1) in enumerate(profile_list):
            for id2, profile2 in profile_list[i+1:]:
                # Check for Big Five conflicts
                big_five_conflicts = []
                
                for trait, score1 in profile1.big_five_traits.items():
                    score2 = profile2.big_five_traits.get(trait, 0.5)
                    if abs(score1 - score2) > 0.6:  # Significant difference
                        big_five_conflicts.append({
                            "trait": trait,
                            "participant1_score": score1,
                            "participant2_score": score2,
                            "difference": abs(score1 - score2)
                        })
                
                if big_five_conflicts:
                    conflicts.append({
                        "participants": [id1, id2],
                        "conflict_type": "big_five_differences",
                        "details": big_five_conflicts
                    })
        
        return conflicts
    
    def _analyze_communication_mismatches(self, participant_profiles: Dict[str, PsychologicalProfile]) -> List[Dict[str, Any]]:
        """Analyze communication style mismatches"""
        
        mismatches = []
        
        profile_list = list(participant_profiles.items())
        for i, (id1, profile1) in enumerate(profile_list):
            for id2, profile2 in profile_list[i+1:]:
                # Check communication preference conflicts
                comm_conflicts = []
                
                prefs1 = profile1.communication_preferences
                prefs2 = profile2.communication_preferences
                
                # Check for direct vs indirect communication
                if prefs1.get("directness", 0.5) > 0.7 and prefs2.get("directness", 0.5) < 0.3:
                    comm_conflicts.append("Direct vs Indirect communication styles")
                
                # Check for detail vs summary preferences
                if prefs1.get("detail_level", 0.5) > 0.7 and prefs2.get("detail_level", 0.5) < 0.3:
                    comm_conflicts.append("High detail vs Summary communication preferences")
                
                if comm_conflicts:
                    mismatches.append({
                        "participants": [id1, id2],
                        "mismatches": comm_conflicts
                    })
        
        return mismatches
    
    def _detect_stress_indicators(self, participants: List[DiscrepancyParticipant]) -> List[Dict[str, Any]]:
        """Detect stress indicators in participant responses"""
        
        stress_indicators = []
        
        for participant in participants:
            indicators = []
            
            # Check emotional state
            if participant.emotional_state in ["frustrated", "angry", "overwhelmed", "anxious"]:
                indicators.append(f"Emotional state: {participant.emotional_state}")
            
            # Check confidence level
            if participant.confidence_level < 0.3:
                indicators.append("Low confidence in position")
            elif participant.confidence_level > 0.9:
                indicators.append("Extremely high confidence (potential rigidity)")
            
            # Check reasoning for stress keywords
            stress_keywords = ["stressed", "overwhelmed", "frustrated", "urgent", "pressure"]
            reasoning_lower = participant.reasoning.lower()
            for keyword in stress_keywords:
                if keyword in reasoning_lower:
                    indicators.append(f"Stress keyword detected: {keyword}")
            
            if indicators:
                stress_indicators.append({
                    "participant_id": participant.participant_id,
                    "participant_name": participant.participant_name,
                    "indicators": indicators
                })
        
        return stress_indicators
    
    def _generate_psychological_resolution_recommendations(self, 
                                                         discrepancy: Discrepancy, 
                                                         participant_profiles: Dict[str, PsychologicalProfile]) -> List[str]:
        """Generate resolution recommendations based on psychological analysis"""
        
        recommendations = []
        
        # Base recommendations on discrepancy type
        if discrepancy.discrepancy_type == DiscrepancyType.DECISION_DISAGREEMENT:
            recommendations.append("Use structured decision-making framework to address logical and emotional concerns")
            recommendations.append("Provide time for both immediate discussion and individual reflection")
        
        elif discrepancy.discrepancy_type == DiscrepancyType.COMMUNICATION_BREAKDOWN:
            recommendations.append("Clarify communication preferences and establish common understanding")
            recommendations.append("Use multiple communication channels (written and verbal)")
        
        elif discrepancy.discrepancy_type == DiscrepancyType.PRIORITY_CONFLICT:
            recommendations.append("Create shared priority framework with clear criteria")
            recommendations.append("Use data-driven approach to evaluate competing priorities")
        
        # Add MBTI-specific recommendations
        mbti_types = [profile.mbti_type.value for profile in participant_profiles.values()]
        if any(t.endswith('J') for t in mbti_types) and any(t.endswith('P') for t in mbti_types):
            recommendations.append("Balance structure with flexibility to accommodate both J and P preferences")
        
        if any(t.startswith('E') for t in mbti_types) and any(t.startswith('I') for t in mbti_types):
            recommendations.append("Provide both group discussion and individual processing time")
        
        # Add DISC-specific recommendations
        disc_types = [profile.disc_primary.value for profile in participant_profiles.values()]
        if 'D' in disc_types and 'S' in disc_types:
            recommendations.append("Balance urgency with stability - provide clear timelines with adequate preparation time")
        
        if 'I' in disc_types and 'C' in disc_types:
            recommendations.append("Combine collaborative enthusiasm with analytical rigor")
        
        return recommendations
    
    def select_resolution_strategy(self, discrepancy: Discrepancy) -> ResolutionStrategy:
        """Select the optimal resolution strategy based on analysis"""
        
        print(f"🎯 Selecting resolution strategy for: {discrepancy.title}")
        
        # Analyze discrepancy to select strategy
        discrepancy = self.analyze_discrepancy_psychology(discrepancy)
        
        # Strategy selection based on multiple factors
        strategy_scores = {}
        
        # Base scores on discrepancy type
        type_strategies = {
            DiscrepancyType.DECISION_DISAGREEMENT: {
                ResolutionStrategy.ASYNC_VOTE: 0.8,
                ResolutionStrategy.MEDIATED_DISCUSSION: 0.7,
                ResolutionStrategy.CONSENSUS_BUILDING: 0.6
            },
            DiscrepancyType.COMMUNICATION_BREAKDOWN: {
                ResolutionStrategy.MEDIATED_DISCUSSION: 0.9,
                ResolutionStrategy.EXPERT_CONSULTATION: 0.5,
                ResolutionStrategy.DEFER_TO_NEXT_MEETING: 0.4
            },
            DiscrepancyType.PRIORITY_CONFLICT: {
                ResolutionStrategy.CONSENSUS_BUILDING: 0.8,
                ResolutionStrategy.EXPERT_CONSULTATION: 0.7,
                ResolutionStrategy.COMPROMISE_NEGOTIATION: 0.6
            },
            DiscrepancyType.APPROACH_DIFFERENCE: {
                ResolutionStrategy.EXPERT_CONSULTATION: 0.8,
                ResolutionStrategy.COMPROMISE_NEGOTIATION: 0.7,
                ResolutionStrategy.SPLIT_DECISION: 0.5
            },
            DiscrepancyType.RESPONSIBILITY_UNCLEAR: {
                ResolutionStrategy.MEDIATED_DISCUSSION: 0.8,
                ResolutionStrategy.ESCALATION_TO_LEADERSHIP: 0.6,
                ResolutionStrategy.DEFER_TO_NEXT_MEETING: 0.5
            }
        }
        
        base_strategies = type_strategies.get(discrepancy.discrepancy_type, {})
        strategy_scores.update(base_strategies)
        
        # Adjust scores based on severity
        severity_adjustments = {
            DiscrepancySeverity.CRITICAL: {
                ResolutionStrategy.ASYNC_VOTE: 0.2,
                ResolutionStrategy.ESCALATION_TO_LEADERSHIP: 0.3,
                ResolutionStrategy.DEFER_TO_NEXT_MEETING: -0.5
            },
            DiscrepancySeverity.HIGH: {
                ResolutionStrategy.MEDIATED_DISCUSSION: 0.2,
                ResolutionStrategy.DEFER_TO_NEXT_MEETING: -0.3
            },
            DiscrepancySeverity.LOW: {
                ResolutionStrategy.DEFER_TO_NEXT_MEETING: 0.3,
                ResolutionStrategy.ASYNC_VOTE: 0.1
            }
        }
        
        severity_adj = severity_adjustments.get(discrepancy.severity, {})
        for strategy, adjustment in severity_adj.items():
            strategy_scores[strategy] = strategy_scores.get(strategy, 0.5) + adjustment
        
        # Adjust based on psychological factors
        psych_analysis = discrepancy.psychological_analysis
        
        # If there are MBTI conflicts, favor mediated discussion
        if psych_analysis.get("mbti_factors", {}).get("potential_conflicts"):
            strategy_scores[ResolutionStrategy.MEDIATED_DISCUSSION] = strategy_scores.get(ResolutionStrategy.MEDIATED_DISCUSSION, 0.5) + 0.2
        
        # If there are communication mismatches, favor expert consultation
        if psych_analysis.get("communication_style_mismatches"):
            strategy_scores[ResolutionStrategy.EXPERT_CONSULTATION] = strategy_scores.get(ResolutionStrategy.EXPERT_CONSULTATION, 0.5) + 0.2
        
        # If there are stress indicators, favor async approaches
        if psych_analysis.get("stress_indicators"):
            strategy_scores[ResolutionStrategy.ASYNC_VOTE] = strategy_scores.get(ResolutionStrategy.ASYNC_VOTE, 0.5) + 0.2
            strategy_scores[ResolutionStrategy.MEDIATED_DISCUSSION] = strategy_scores.get(ResolutionStrategy.MEDIATED_DISCUSSION, 0.5) - 0.1
        
        # Select strategy with highest score
        if strategy_scores:
            selected_strategy = max(strategy_scores.items(), key=lambda x: x[1])[0]
        else:
            selected_strategy = ResolutionStrategy.MEDIATED_DISCUSSION  # Default
        
        discrepancy.resolution_strategy = selected_strategy
        
        # Set resolution deadline based on strategy and severity
        deadline_hours = {
            DiscrepancySeverity.CRITICAL: 4,
            DiscrepancySeverity.HIGH: 24,
            DiscrepancySeverity.MEDIUM: 72,
            DiscrepancySeverity.LOW: 168
        }
        
        hours = deadline_hours.get(discrepancy.severity, 72)
        discrepancy.resolution_deadline = datetime.now() + timedelta(hours=hours)
        
        print(f"✅ Selected strategy: {selected_strategy.value}")
        print(f"   Resolution deadline: {discrepancy.resolution_deadline.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Strategy score: {strategy_scores.get(selected_strategy, 0):.2f}")
        
        return selected_strategy
    
    def execute_resolution_strategy(self, discrepancy_id: str) -> bool:
        """Execute the selected resolution strategy"""
        
        if discrepancy_id not in self.discrepancies:
            print(f"❌ Discrepancy {discrepancy_id} not found")
            return False
        
        discrepancy = self.discrepancies[discrepancy_id]
        
        if not discrepancy.resolution_strategy:
            print(f"❌ No resolution strategy selected for {discrepancy_id}")
            return False
        
        print(f"🚀 Executing resolution strategy: {discrepancy.resolution_strategy.value}")
        
        strategy = discrepancy.resolution_strategy
        
        if strategy == ResolutionStrategy.ASYNC_VOTE:
            return self._execute_async_vote_resolution(discrepancy)
        elif strategy == ResolutionStrategy.MEDIATED_DISCUSSION:
            return self._execute_mediated_discussion(discrepancy)
        elif strategy == ResolutionStrategy.EXPERT_CONSULTATION:
            return self._execute_expert_consultation(discrepancy)
        elif strategy == ResolutionStrategy.COMPROMISE_NEGOTIATION:
            return self._execute_compromise_negotiation(discrepancy)
        elif strategy == ResolutionStrategy.CONSENSUS_BUILDING:
            return self._execute_consensus_building(discrepancy)
        elif strategy == ResolutionStrategy.DEFER_TO_NEXT_MEETING:
            return self._execute_defer_to_meeting(discrepancy)
        else:
            print(f"❌ Strategy {strategy.value} not implemented yet")
            return False
    
    def _execute_async_vote_resolution(self, discrepancy: Discrepancy) -> bool:
        """Execute async vote resolution strategy"""
        
        print(f"🗳️ Creating async vote for discrepancy resolution...")
        
        # Create decision options based on participant positions
        options = []
        
        # Group participants by position
        position_groups = defaultdict(list)
        for participant in discrepancy.participants:
            position_groups[participant.position].append(participant)
        
        # Create options for each position
        for position, participants in position_groups.items():
            option = DecisionOption(
                option_id=f"option_{position}",
                title=f"Position: {position}",
                description=f"Support the position held by {', '.join([p.participant_name for p in participants])}",
                impact_assessment={"discrepancy_resolution": "direct"},
                resource_requirements={"time": "minimal"},
                risk_factors=["May not address underlying concerns"],
                success_indicators=["Clear decision made", "Team alignment achieved"],
                implementation_timeline="Immediate",
                affected_projects=discrepancy.affected_projects,
                affected_team_members=[p.participant_id for p in discrepancy.participants]
            )
            options.append(option)
        
        # Create decision through AsyncDecisionValidator
        decision = self.async_decision_validator.create_decision(
            title=f"Resolve: {discrepancy.title}",
            description=f"Vote to resolve discrepancy: {discrepancy.description}",
            decision_type=DecisionType.OPERATIONAL,
            urgency=self._map_severity_to_urgency(discrepancy.severity),
            proposer_id="oracle_system",
            options=options,
            custom_deadline=discrepancy.resolution_deadline
        )
        
        # Open for voting
        success = self.async_decision_validator.open_for_voting(decision.decision_id)
        
        if success:
            discrepancy.resolution_status = ResolutionStatus.IN_PROGRESS
            discrepancy.affected_decisions.append(decision.decision_id)
            print(f"✅ Async vote created: {decision.decision_id}")
            return True
        else:
            print(f"❌ Failed to create async vote")
            return False
    
    def _execute_mediated_discussion(self, discrepancy: Discrepancy) -> bool:
        """Execute mediated discussion resolution strategy"""
        
        print(f"💬 Setting up mediated discussion...")
        
        # Create mediation session
        session_id = str(uuid.uuid4())
        
        # Select mediator (could be AI or human)
        mediator_id = self._select_mediator(discrepancy)
        
        # Schedule session
        session_duration = timedelta(hours=1)  # Default 1 hour
        scheduled_at = datetime.now() + timedelta(hours=2)  # 2 hours from now
        
        mediation_session = MediationSession(
            session_id=session_id,
            discrepancy_id=discrepancy.discrepancy_id,
            mediator_id=mediator_id,
            participants=[p.participant_id for p in discrepancy.participants],
            session_type="ai_mediated",
            session_duration=session_duration,
            scheduled_at=scheduled_at,
            ground_rules=[
                "Respectful communication only",
                "Focus on understanding, not winning",
                "One person speaks at a time",
                "Address the issue, not the person"
            ],
            objectives=[
                "Understand all perspectives",
                "Identify common ground",
                "Develop mutually acceptable solution",
                "Create action plan for implementation"
            ]
        )
        
        self.mediation_sessions[session_id] = mediation_session
        discrepancy.resolution_status = ResolutionStatus.IN_PROGRESS
        discrepancy.assigned_mediator = mediator_id
        
        print(f"✅ Mediation session scheduled: {session_id}")
        print(f"   Mediator: {mediator_id}")
        print(f"   Scheduled: {scheduled_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Participants: {len(mediation_session.participants)}")
        
        return True
    
    def _execute_expert_consultation(self, discrepancy: Discrepancy) -> bool:
        """Execute expert consultation resolution strategy"""
        
        print(f"👨‍💼 Setting up expert consultation...")
        
        # Identify relevant experts based on discrepancy type and affected projects
        experts = self._identify_relevant_experts(discrepancy)
        
        if not experts:
            print(f"❌ No relevant experts identified")
            return False
        
        # Create consultation request
        consultation_request = {
            "discrepancy_id": discrepancy.discrepancy_id,
            "experts": experts,
            "consultation_type": "expert_analysis",
            "questions": [
                "What is your assessment of this discrepancy?",
                "What would you recommend as the best resolution approach?",
                "What are the potential risks and benefits of each position?",
                "How would you prioritize the different concerns raised?"
            ],
            "deadline": discrepancy.resolution_deadline,
            "status": "requested"
        }
        
        discrepancy.resolution_status = ResolutionStatus.IN_PROGRESS
        
        print(f"✅ Expert consultation requested")
        print(f"   Experts: {', '.join(experts)}")
        print(f"   Deadline: {discrepancy.resolution_deadline.strftime('%Y-%m-%d %H:%M')}")
        
        return True
    
    def _execute_compromise_negotiation(self, discrepancy: Discrepancy) -> bool:
        """Execute compromise negotiation resolution strategy"""
        
        print(f"🤝 Setting up compromise negotiation...")
        
        # Analyze positions for potential compromise areas
        compromise_areas = self._identify_compromise_areas(discrepancy)
        
        # Create negotiation framework
        negotiation_framework = {
            "discrepancy_id": discrepancy.discrepancy_id,
            "participants": [p.participant_id for p in discrepancy.participants],
            "compromise_areas": compromise_areas,
            "negotiation_rounds": 3,
            "current_round": 1,
            "proposals": [],
            "agreements": [],
            "status": "active"
        }
        
        discrepancy.resolution_status = ResolutionStatus.IN_PROGRESS
        
        print(f"✅ Compromise negotiation initiated")
        print(f"   Compromise areas: {len(compromise_areas)}")
        print(f"   Participants: {len(negotiation_framework['participants'])}")
        
        return True
    
    def _execute_consensus_building(self, discrepancy: Discrepancy) -> bool:
        """Execute consensus building resolution strategy"""
        
        print(f"🎯 Setting up consensus building process...")
        
        # Create consensus building process
        consensus_process = {
            "discrepancy_id": discrepancy.discrepancy_id,
            "participants": [p.participant_id for p in discrepancy.participants],
            "phases": [
                "Information gathering",
                "Perspective sharing",
                "Common ground identification",
                "Solution development",
                "Consensus testing"
            ],
            "current_phase": "Information gathering",
            "facilitator": "oracle_system",
            "consensus_threshold": 0.8,
            "status": "active"
        }
        
        discrepancy.resolution_status = ResolutionStatus.IN_PROGRESS
        
        print(f"✅ Consensus building process initiated")
        print(f"   Phases: {len(consensus_process['phases'])}")
        print(f"   Consensus threshold: {consensus_process['consensus_threshold']:.1%}")
        
        return True
    
    def _execute_defer_to_meeting(self, discrepancy: Discrepancy) -> bool:
        """Execute defer to next meeting resolution strategy"""
        
        print(f"📅 Deferring to next meeting...")
        
        # Create meeting agenda item
        agenda_item = {
            "discrepancy_id": discrepancy.discrepancy_id,
            "title": discrepancy.title,
            "description": discrepancy.description,
            "participants": [p.participant_id for p in discrepancy.participants],
            "estimated_time": "15 minutes",
            "preparation_materials": [
                "Discrepancy summary",
                "Participant positions",
                "Psychological analysis",
                "Recommended resolution approaches"
            ],
            "priority": "high" if discrepancy.severity in [DiscrepancySeverity.CRITICAL, DiscrepancySeverity.HIGH] else "medium"
        }
        
        discrepancy.resolution_status = ResolutionStatus.DEFERRED
        
        print(f"✅ Discrepancy deferred to next meeting")
        print(f"   Priority: {agenda_item['priority']}")
        print(f"   Estimated time: {agenda_item['estimated_time']}")
        
        return True
    
    def _map_severity_to_urgency(self, severity: DiscrepancySeverity):
        """Map discrepancy severity to decision urgency"""
        from AsyncDecisionValidator import DecisionUrgency
        
        mapping = {
            DiscrepancySeverity.CRITICAL: DecisionUrgency.CRITICAL,
            DiscrepancySeverity.HIGH: DecisionUrgency.HIGH,
            DiscrepancySeverity.MEDIUM: DecisionUrgency.MEDIUM,
            DiscrepancySeverity.LOW: DecisionUrgency.LOW,
            DiscrepancySeverity.INFORMATIONAL: DecisionUrgency.PLANNING
        }
        
        return mapping.get(severity, DecisionUrgency.MEDIUM)
    
    def _select_mediator(self, discrepancy: Discrepancy) -> str:
        """Select appropriate mediator for the discrepancy"""
        
        # For now, use AI mediation (Oracle system)
        # In future, could select human mediators based on expertise and availability
        
        # Check if any team member has mediation expertise
        potential_mediators = []
        
        for member_id, member in self.mem0_manager.team_members.items():
            # Skip participants in the discrepancy
            if any(p.participant_id == member_id for p in discrepancy.participants):
                continue
            
            # Check for mediation-related expertise
            if any(expertise in member.expertise_areas for expertise in ["mediation", "conflict_resolution", "leadership"]):
                potential_mediators.append(member_id)
        
        if potential_mediators:
            # Select based on psychological fit for mediation
            best_mediator = potential_mediators[0]  # Simple selection for now
            return best_mediator
        else:
            return "oracle_system"  # AI mediation
    
    def _identify_relevant_experts(self, discrepancy: Discrepancy) -> List[str]:
        """Identify team members with relevant expertise for consultation"""
        
        experts = []
        
        # Map discrepancy types to relevant expertise
        expertise_mapping = {
            DiscrepancyType.DECISION_DISAGREEMENT: ["strategic_planning", "leadership", "decision_making"],
            DiscrepancyType.PRIORITY_CONFLICT: ["project_management", "strategic_planning", "resource_management"],
            DiscrepancyType.APPROACH_DIFFERENCE: ["methodology", "best_practices", "innovation"],
            DiscrepancyType.RESOURCE_CONTENTION: ["resource_management", "finance", "operations"],
            DiscrepancyType.COMMUNICATION_BREAKDOWN: ["communication", "team_dynamics", "leadership"]
        }
        
        relevant_expertise = expertise_mapping.get(discrepancy.discrepancy_type, [])
        
        # Find team members with relevant expertise who aren't participants
        for member_id, member in self.mem0_manager.team_members.items():
            # Skip participants in the discrepancy
            if any(p.participant_id == member_id for p in discrepancy.participants):
                continue
            
            # Check for relevant expertise
            if any(expertise in member.expertise_areas for expertise in relevant_expertise):
                experts.append(member_id)
        
        # Also consider project-specific expertise
        for project in discrepancy.affected_projects:
            project_experts = self._get_project_experts(project)
            for expert in project_experts:
                if expert not in experts and not any(p.participant_id == expert for p in discrepancy.participants):
                    experts.append(expert)
        
        return experts
    
    def _get_project_experts(self, project: str) -> List[str]:
        """Get experts for a specific project"""
        
        project_leaders = {
            "100_percent_project": ["daniel"],
            "spark": ["troy"],
            "ecoco": ["marc"],
            "treegens": ["jimi"]
        }
        
        return project_leaders.get(project, [])
    
    def _identify_compromise_areas(self, discrepancy: Discrepancy) -> List[Dict[str, Any]]:
        """Identify potential areas for compromise"""
        
        compromise_areas = []
        
        # Analyze participant positions for compromise potential
        positions = [p.position for p in discrepancy.participants]
        
        # Look for partial overlaps or middle ground
        if len(set(positions)) > 1:  # Multiple different positions
            compromise_areas.append({
                "area": "Position integration",
                "description": "Combine elements from different positions",
                "potential": "medium"
            })
        
        # Check confidence levels for flexibility
        low_confidence_participants = [p for p in discrepancy.participants if p.confidence_level < 0.6]
        if low_confidence_participants:
            compromise_areas.append({
                "area": "Uncertainty resolution",
                "description": "Address areas of uncertainty to build confidence",
                "potential": "high"
            })
        
        # Check for resource or timeline flexibility
        if discrepancy.discrepancy_type in [DiscrepancyType.RESOURCE_CONTENTION, DiscrepancyType.TIMELINE_DISPUTE]:
            compromise_areas.append({
                "area": "Resource/timeline adjustment",
                "description": "Find flexible resource allocation or timeline adjustments",
                "potential": "high"
            })
        
        return compromise_areas
    
    def get_discrepancy_status(self, discrepancy_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive status of a discrepancy"""
        
        if discrepancy_id not in self.discrepancies:
            return None
        
        discrepancy = self.discrepancies[discrepancy_id]
        
        status = {
            "discrepancy_id": discrepancy.discrepancy_id,
            "title": discrepancy.title,
            "type": discrepancy.discrepancy_type.value,
            "severity": discrepancy.severity.value,
            "status": discrepancy.resolution_status.value,
            "participants": len(discrepancy.participants),
            "resolution_strategy": discrepancy.resolution_strategy.value if discrepancy.resolution_strategy else None,
            "resolution_deadline": discrepancy.resolution_deadline.isoformat() if discrepancy.resolution_deadline else None,
            "psychological_analysis": discrepancy.psychological_analysis,
            "resolution_attempts": len(discrepancy.resolution_attempts),
            "affected_projects": discrepancy.affected_projects,
            "affected_decisions": discrepancy.affected_decisions
        }
        
        return status
    
    def get_team_conflict_summary(self) -> Dict[str, Any]:
        """Get summary of all team conflicts and resolutions"""
        
        summary = {
            "total_discrepancies": len(self.discrepancies),
            "discrepancies_by_type": defaultdict(int),
            "discrepancies_by_severity": defaultdict(int),
            "discrepancies_by_status": defaultdict(int),
            "resolution_strategies_used": defaultdict(int),
            "average_resolution_time": 0.0,
            "resolution_success_rate": 0.0,
            "psychological_patterns": {},
            "recent_discrepancies": []
        }
        
        resolved_discrepancies = []
        
        for discrepancy in self.discrepancies.values():
            summary["discrepancies_by_type"][discrepancy.discrepancy_type.value] += 1
            summary["discrepancies_by_severity"][discrepancy.severity.value] += 1
            summary["discrepancies_by_status"][discrepancy.resolution_status.value] += 1
            
            if discrepancy.resolution_strategy:
                summary["resolution_strategies_used"][discrepancy.resolution_strategy.value] += 1
            
            if discrepancy.resolution_status == ResolutionStatus.RESOLVED:
                resolved_discrepancies.append(discrepancy)
        
        # Calculate resolution metrics
        if resolved_discrepancies:
            resolution_times = []
            for discrepancy in resolved_discrepancies:
                if discrepancy.resolution_deadline:
                    # Estimate resolution time (would be actual in real implementation)
                    estimated_resolution_time = (discrepancy.resolution_deadline - discrepancy.detected_at).total_seconds() / 3600
                    resolution_times.append(estimated_resolution_time)
            
            if resolution_times:
                summary["average_resolution_time"] = np.mean(resolution_times)
        
        summary["resolution_success_rate"] = len(resolved_discrepancies) / len(self.discrepancies) if self.discrepancies else 0
        
        # Recent discrepancies (last 5)
        recent_discrepancies = sorted(self.discrepancies.values(), key=lambda d: d.detected_at, reverse=True)[:5]
        summary["recent_discrepancies"] = [
            {
                "title": d.title,
                "type": d.discrepancy_type.value,
                "severity": d.severity.value,
                "status": d.resolution_status.value,
                "detected_at": d.detected_at.isoformat()
            }
            for d in recent_discrepancies
        ]
        
        return summary

# Example usage and testing
if __name__ == "__main__":
    # Test DiscrepancyResolver (requires components from previous phases)
    try:
        # Initialize components
        mem0_manager = Mem0Manager()
        enhanced_tanka = EnhancedTankaProfileLoader(mem0_manager)
        insight_synthesizer = InsightSynthesizer(mem0_manager, enhanced_tanka, None)
        async_validator = AsyncDecisionValidator(mem0_manager, enhanced_tanka, insight_synthesizer)
        discrepancy_resolver = DiscrepancyResolver(mem0_manager, enhanced_tanka, insight_synthesizer, async_validator)
        
        print("🔧 DiscrepancyResolver initialized successfully!")
        
        # Test discrepancy detection (would use real debrief data)
        print("\n🧪 Testing discrepancy detection...")
        
        # Create sample discrepancy
        sample_participants = [
            DiscrepancyParticipant(
                participant_id="daniel",
                participant_name="Daniel Matalon",
                position="support",
                confidence_level=0.9,
                reasoning="This aligns with our strategic vision for human rights impact",
                emotional_state="passionate"
            ),
            DiscrepancyParticipant(
                participant_id="troy",
                participant_name="Troy Mork",
                position="oppose",
                confidence_level=0.8,
                reasoning="The implementation timeline is too aggressive for proper SPARK methodology",
                emotional_state="analytical"
            )
        ]
        
        sample_discrepancy = Discrepancy(
            discrepancy_id=str(uuid.uuid4()),
            title="Timeline disagreement for 100% Project expansion",
            description="Daniel and Troy disagree on the implementation timeline for global expansion",
            discrepancy_type=DiscrepancyType.TIMELINE_DISPUTE,
            severity=DiscrepancySeverity.MEDIUM,
            participants=sample_participants,
            affected_projects=["100_percent_project"]
        )
        
        discrepancy_resolver.discrepancies[sample_discrepancy.discrepancy_id] = sample_discrepancy
        
        # Test strategy selection
        strategy = discrepancy_resolver.select_resolution_strategy(sample_discrepancy)
        print(f"✅ Strategy selected: {strategy.value}")
        
        # Test strategy execution
        success = discrepancy_resolver.execute_resolution_strategy(sample_discrepancy.discrepancy_id)
        print(f"✅ Strategy execution: {success}")
        
        # Test status retrieval
        status = discrepancy_resolver.get_discrepancy_status(sample_discrepancy.discrepancy_id)
        print(f"✅ Status retrieved: {status is not None}")
        
        # Test team summary
        summary = discrepancy_resolver.get_team_conflict_summary()
        print(f"✅ Team summary: {summary}")
        
        print("\n✅ DiscrepancyResolver successfully tested!")
        
    except Exception as e:
        print(f"❌ Error testing DiscrepancyResolver: {e}")
        print("💡 This requires components from previous phases to be properly initialized")

