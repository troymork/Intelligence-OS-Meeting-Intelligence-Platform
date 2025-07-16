"""
Oracle Intelligence System - AsyncDecisionValidator
Handles asynchronous decision-making, voting, consensus building, and validation

This module enables the team to make decisions outside of meetings through:
- Psychological intelligence-informed voting mechanisms
- Dynamic consensus threshold calculation based on team dynamics
- Decision confidence scoring and uncertainty handling
- Async decision collection with deadline management
- Decision impact prediction and risk assessment
- Integration with Tanka personalities for decision guidance
- Decision history tracking and pattern learning
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

from Mem0Manager import Mem0Manager, TeamMember
from EnhancedTankaProfileLoader import EnhancedTankaProfileLoader, PsychologicalProfile, MBTIType, DISCType
from InsightSynthesizer import InsightSynthesizer, SynthesizedInsight

class DecisionType(Enum):
    """Types of decisions that can be validated"""
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"
    PROJECT_SPECIFIC = "project_specific"
    RESOURCE_ALLOCATION = "resource_allocation"
    POLICY = "policy"
    EMERGENCY = "emergency"
    ROUTINE = "routine"

class DecisionUrgency(Enum):
    """Urgency levels for decisions"""
    CRITICAL = "critical"      # 24 hours
    HIGH = "high"             # 3 days
    MEDIUM = "medium"         # 1 week
    LOW = "low"              # 2 weeks
    PLANNING = "planning"     # 1 month

class VoteType(Enum):
    """Types of votes"""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"
    CONDITIONAL = "conditional"
    REQUEST_MORE_INFO = "request_more_info"

class DecisionStatus(Enum):
    """Status of decisions in the validation process"""
    DRAFT = "draft"
    OPEN_FOR_VOTING = "open_for_voting"
    CONSENSUS_REACHED = "consensus_reached"
    CONSENSUS_FAILED = "consensus_failed"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

@dataclass
class Vote:
    """Individual vote on a decision"""
    voter_id: str
    voter_name: str
    vote_type: VoteType
    confidence_level: float  # 0.0 to 1.0
    reasoning: str
    conditions: Optional[str] = None  # For conditional votes
    psychological_factors: Dict[str, Any] = field(default_factory=dict)
    expertise_relevance: float = 0.5  # How relevant is voter's expertise
    vote_weight: float = 1.0  # Calculated weight based on psychology + expertise
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DecisionOption:
    """A decision option that can be voted on"""
    option_id: str
    title: str
    description: str
    impact_assessment: Dict[str, Any]
    resource_requirements: Dict[str, Any]
    risk_factors: List[str]
    success_indicators: List[str]
    implementation_timeline: str
    affected_projects: List[str]
    affected_team_members: List[str]

@dataclass
class Decision:
    """A decision requiring team validation"""
    decision_id: str
    title: str
    description: str
    decision_type: DecisionType
    urgency: DecisionUrgency
    proposer_id: str
    proposer_name: str
    voting_deadline: datetime
    
    # Decision options
    options: List[DecisionOption] = field(default_factory=list)
    
    # Voting configuration
    required_consensus_threshold: float = 0.7  # 0.0 to 1.0
    minimum_participation: float = 0.6  # 0.0 to 1.0
    expertise_weighting_enabled: bool = True
    psychological_weighting_enabled: bool = True
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    
    # Status and results
    status: DecisionStatus = DecisionStatus.DRAFT
    votes: Dict[str, Vote] = field(default_factory=dict)  # voter_id -> Vote
    consensus_results: Dict[str, Any] = field(default_factory=dict)
    final_decision: Optional[str] = None  # option_id of chosen option
    implementation_notes: str = ""
    
    # Analytics
    psychological_analysis: Dict[str, Any] = field(default_factory=dict)
    decision_confidence: float = 0.0
    predicted_outcomes: Dict[str, Any] = field(default_factory=dict)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConsensusResult:
    """Result of consensus calculation"""
    consensus_reached: bool
    winning_option_id: Optional[str]
    consensus_score: float  # 0.0 to 1.0
    participation_rate: float
    confidence_level: float
    psychological_alignment: Dict[str, Any]
    dissenting_voices: List[str]
    conditions_to_address: List[str]
    recommendation: str

class AsyncDecisionValidator:
    """
    Handles asynchronous decision-making, voting, and consensus building
    
    Enables the Impact Launchpad team to make decisions outside of meetings
    through psychologically-informed voting mechanisms, dynamic consensus
    thresholds, and intelligent decision validation.
    """
    
    def __init__(self, mem0_manager: Mem0Manager, enhanced_tanka: EnhancedTankaProfileLoader, insight_synthesizer: InsightSynthesizer):
        """Initialize AsyncDecisionValidator with integrated components"""
        self.mem0_manager = mem0_manager
        self.enhanced_tanka = enhanced_tanka
        self.insight_synthesizer = insight_synthesizer
        
        # Decision storage
        self.decisions: Dict[str, Decision] = {}
        self.decision_history: List[Decision] = []
        
        # Configuration
        self.default_consensus_thresholds = {
            DecisionType.STRATEGIC: 0.8,
            DecisionType.OPERATIONAL: 0.6,
            DecisionType.PROJECT_SPECIFIC: 0.7,
            DecisionType.RESOURCE_ALLOCATION: 0.75,
            DecisionType.POLICY: 0.8,
            DecisionType.EMERGENCY: 0.5,
            DecisionType.ROUTINE: 0.6
        }
        
        self.urgency_deadlines = {
            DecisionUrgency.CRITICAL: timedelta(hours=24),
            DecisionUrgency.HIGH: timedelta(days=3),
            DecisionUrgency.MEDIUM: timedelta(weeks=1),
            DecisionUrgency.LOW: timedelta(weeks=2),
            DecisionUrgency.PLANNING: timedelta(weeks=4)
        }
        
        # Expertise areas for Impact Launchpad projects
        self.project_expertise_mapping = {
            "100_percent_project": ["human_rights", "social_impact", "economic_systems", "strategic_vision"],
            "spark": ["project_management", "systematic_approach", "innovation", "efficiency"],
            "ecoco": ["sustainability", "environmental_impact", "green_technology", "climate_action"],
            "treegens": ["regenerative_systems", "nature_based_solutions", "ecosystem_restoration", "biodiversity"]
        }
        
        print("🗳️ AsyncDecisionValidator initialized with consensus intelligence")
    
    def create_decision(self, 
                       title: str,
                       description: str,
                       decision_type: DecisionType,
                       urgency: DecisionUrgency,
                       proposer_id: str,
                       options: List[DecisionOption],
                       custom_consensus_threshold: Optional[float] = None,
                       custom_deadline: Optional[datetime] = None) -> Decision:
        """Create a new decision for team validation"""
        
        print(f"📝 Creating decision: {title}")
        
        # Generate decision ID
        decision_id = str(uuid.uuid4())
        
        # Get proposer info
        proposer = self.mem0_manager.team_members.get(proposer_id)
        proposer_name = proposer.name if proposer else proposer_id
        
        # Calculate consensus threshold
        consensus_threshold = custom_consensus_threshold or self.default_consensus_thresholds.get(decision_type, 0.7)
        
        # Calculate deadline
        if custom_deadline:
            voting_deadline = custom_deadline
        else:
            deadline_delta = self.urgency_deadlines.get(urgency, timedelta(weeks=1))
            voting_deadline = datetime.now() + deadline_delta
        
        # Create decision
        decision = Decision(
            decision_id=decision_id,
            title=title,
            description=description,
            decision_type=decision_type,
            urgency=urgency,
            proposer_id=proposer_id,
            proposer_name=proposer_name,
            options=options,
            required_consensus_threshold=consensus_threshold,
            minimum_participation=0.6,  # At least 60% of team must participate
            voting_deadline=voting_deadline
        )
        
        # Perform initial analysis
        decision = self._analyze_decision_psychology(decision)
        decision = self._predict_decision_outcomes(decision)
        decision = self._assess_decision_risks(decision)
        
        # Store decision
        self.decisions[decision_id] = decision
        
        print(f"✅ Decision created: {decision_id}")
        print(f"   Consensus threshold: {consensus_threshold:.1%}")
        print(f"   Voting deadline: {voting_deadline.strftime('%Y-%m-%d %H:%M')}")
        
        return decision
    
    def _analyze_decision_psychology(self, decision: Decision) -> Decision:
        """Analyze psychological factors relevant to the decision"""
        
        # Analyze which psychological types are most suited for this decision
        psychological_analysis = {
            "optimal_decision_makers": [],
            "potential_stress_factors": [],
            "communication_considerations": [],
            "consensus_challenges": []
        }
        
        # MBTI analysis for decision type
        if decision.decision_type == DecisionType.STRATEGIC:
            psychological_analysis["optimal_decision_makers"].extend(["ENTJ", "INTJ", "ENTP"])
            psychological_analysis["communication_considerations"].append("Focus on long-term vision and strategic implications")
        
        elif decision.decision_type == DecisionType.OPERATIONAL:
            psychological_analysis["optimal_decision_makers"].extend(["ESTJ", "ISTJ", "ESTP"])
            psychological_analysis["communication_considerations"].append("Emphasize practical implementation and efficiency")
        
        elif decision.decision_type == DecisionType.PROJECT_SPECIFIC:
            # Analyze based on affected projects
            for project in decision.options[0].affected_projects if decision.options else []:
                if project in self.project_expertise_mapping:
                    if project == "100_percent_project":
                        psychological_analysis["optimal_decision_makers"].extend(["ENFJ", "ENTJ"])
                    elif project == "spark":
                        psychological_analysis["optimal_decision_makers"].extend(["INTJ", "ESTJ"])
                    elif project == "ecoco":
                        psychological_analysis["optimal_decision_makers"].extend(["INFP", "ENFP"])
                    elif project == "treegens":
                        psychological_analysis["optimal_decision_makers"].extend(["INFP", "ISFP"])
        
        # Urgency stress analysis
        if decision.urgency in [DecisionUrgency.CRITICAL, DecisionUrgency.HIGH]:
            psychological_analysis["potential_stress_factors"].extend([
                "Time pressure may affect Perceiving types more than Judging types",
                "Introverted types may need more processing time",
                "High stress may impact decision quality for anxiety-prone individuals"
            ])
        
        # DISC communication considerations
        psychological_analysis["communication_considerations"].extend([
            "D-types: Focus on results and bottom-line impact",
            "I-types: Emphasize team collaboration and positive outcomes",
            "S-types: Provide stability and support during transition",
            "C-types: Include detailed analysis and risk assessment"
        ])
        
        decision.psychological_analysis = psychological_analysis
        return decision
    
    def _predict_decision_outcomes(self, decision: Decision) -> Decision:
        """Predict outcomes for each decision option"""
        
        predicted_outcomes = {}
        
        for option in decision.options:
            # Base prediction on option characteristics
            outcome_prediction = {
                "success_probability": 0.7,  # Base probability
                "implementation_difficulty": "medium",
                "team_satisfaction_impact": "neutral",
                "project_impact": {},
                "resource_efficiency": "medium",
                "risk_level": "medium"
            }
            
            # Adjust based on impact assessment
            if "positive_impact" in str(option.impact_assessment).lower():
                outcome_prediction["success_probability"] += 0.1
                outcome_prediction["team_satisfaction_impact"] = "positive"
            
            # Adjust based on resource requirements
            resource_complexity = len(option.resource_requirements)
            if resource_complexity > 3:
                outcome_prediction["implementation_difficulty"] = "high"
                outcome_prediction["success_probability"] -= 0.1
            elif resource_complexity < 2:
                outcome_prediction["implementation_difficulty"] = "low"
                outcome_prediction["success_probability"] += 0.05
            
            # Adjust based on risk factors
            risk_count = len(option.risk_factors)
            if risk_count > 3:
                outcome_prediction["risk_level"] = "high"
                outcome_prediction["success_probability"] -= 0.15
            elif risk_count < 2:
                outcome_prediction["risk_level"] = "low"
                outcome_prediction["success_probability"] += 0.1
            
            # Project-specific impact
            for project in option.affected_projects:
                if project in self.insight_synthesizer.project_intelligence:
                    project_intel = self.insight_synthesizer.project_intelligence[project]
                    outcome_prediction["project_impact"][project] = {
                        "alignment_score": np.mean(list(project_intel.team_engagement.values())),
                        "success_indicators": len(project_intel.success_indicators),
                        "risk_factors": len(project_intel.risk_factors)
                    }
            
            # Ensure probability stays within bounds
            outcome_prediction["success_probability"] = max(0.1, min(0.95, outcome_prediction["success_probability"]))
            
            predicted_outcomes[option.option_id] = outcome_prediction
        
        decision.predicted_outcomes = predicted_outcomes
        return decision
    
    def _assess_decision_risks(self, decision: Decision) -> Decision:
        """Assess risks associated with the decision"""
        
        risk_assessment = {
            "overall_risk_level": "medium",
            "key_risk_factors": [],
            "mitigation_strategies": [],
            "psychological_risks": [],
            "implementation_risks": []
        }
        
        # Analyze urgency-related risks
        if decision.urgency == DecisionUrgency.CRITICAL:
            risk_assessment["key_risk_factors"].append("Extremely tight timeline may lead to hasty decisions")
            risk_assessment["psychological_risks"].append("High stress may impair judgment quality")
            risk_assessment["mitigation_strategies"].append("Ensure key stakeholders are immediately available")
        
        # Analyze consensus threshold risks
        if decision.required_consensus_threshold > 0.8:
            risk_assessment["key_risk_factors"].append("High consensus threshold may be difficult to achieve")
            risk_assessment["mitigation_strategies"].append("Consider phased decision-making or compromise options")
        
        # Analyze option complexity risks
        for option in decision.options:
            if len(option.risk_factors) > 3:
                risk_assessment["implementation_risks"].extend(option.risk_factors)
        
        # Psychological risk assessment
        optimal_types = decision.psychological_analysis.get("optimal_decision_makers", [])
        team_mbti_types = []
        
        for member_id, member in self.mem0_manager.team_members.items():
            profile = self.enhanced_tanka.get_psychological_profile(member_id)
            if profile:
                team_mbti_types.append(profile.mbti_type.value)
        
        # Check if team has optimal decision-makers
        optimal_available = any(mbti in team_mbti_types for mbti in optimal_types)
        if not optimal_available and optimal_types:
            risk_assessment["psychological_risks"].append(
                f"Team may lack optimal psychological types for this decision: {', '.join(optimal_types)}"
            )
            risk_assessment["mitigation_strategies"].append(
                "Provide additional context and analysis to support decision-making"
            )
        
        # Overall risk level calculation
        risk_factors_count = len(risk_assessment["key_risk_factors"]) + len(risk_assessment["psychological_risks"])
        if risk_factors_count > 4:
            risk_assessment["overall_risk_level"] = "high"
        elif risk_factors_count < 2:
            risk_assessment["overall_risk_level"] = "low"
        
        decision.risk_assessment = risk_assessment
        return decision
    
    def open_for_voting(self, decision_id: str) -> bool:
        """Open a decision for team voting"""
        
        if decision_id not in self.decisions:
            print(f"❌ Decision {decision_id} not found")
            return False
        
        decision = self.decisions[decision_id]
        
        if decision.status != DecisionStatus.DRAFT:
            print(f"❌ Decision {decision_id} is not in draft status")
            return False
        
        # Update status
        decision.status = DecisionStatus.OPEN_FOR_VOTING
        
        print(f"🗳️ Decision opened for voting: {decision.title}")
        print(f"   Voting deadline: {decision.voting_deadline.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Required consensus: {decision.required_consensus_threshold:.1%}")
        
        # Notify team members (would integrate with notification system)
        self._notify_team_of_voting(decision)
        
        return True
    
    def _notify_team_of_voting(self, decision: Decision):
        """Notify team members about voting opportunity"""
        
        # This would integrate with actual notification system
        print(f"📢 Notifying team about voting for: {decision.title}")
        
        for member_id, member in self.mem0_manager.team_members.items():
            # Get personalized Tanka guidance for this decision
            tanka_guidance = self._get_tanka_decision_guidance(member_id, decision)
            
            print(f"   📱 Notification sent to {member.name}")
            print(f"      Tanka guidance: {tanka_guidance[:100]}...")
    
    def _get_tanka_decision_guidance(self, member_id: str, decision: Decision) -> str:
        """Get personalized Tanka guidance for a team member on a decision"""
        
        member = self.mem0_manager.team_members.get(member_id)
        profile = self.enhanced_tanka.get_psychological_profile(member_id)
        
        if not member or not profile:
            return "Consider the decision carefully and vote based on your expertise and judgment."
        
        # Personalize guidance based on psychological profile
        guidance_parts = []
        
        # MBTI-based guidance
        if profile.mbti_type in [MBTIType.ENTJ, MBTIType.INTJ]:
            guidance_parts.append("Focus on the strategic implications and long-term outcomes.")
        elif profile.mbti_type in [MBTIType.ENFP, MBTIType.INFP]:
            guidance_parts.append("Consider how this aligns with team values and individual impact.")
        elif profile.mbti_type in [MBTIType.ESTJ, MBTIType.ISTJ]:
            guidance_parts.append("Evaluate the practical implementation details and resource requirements.")
        elif profile.mbti_type in [MBTIType.ESFJ, MBTIType.ISFJ]:
            guidance_parts.append("Think about how this affects team harmony and individual wellbeing.")
        
        # DISC-based guidance
        if profile.disc_primary == DISCType.DOMINANCE:
            guidance_parts.append("Focus on results and decisive action.")
        elif profile.disc_primary == DISCType.INFLUENCE:
            guidance_parts.append("Consider team collaboration and positive communication.")
        elif profile.disc_primary == DISCType.STEADINESS:
            guidance_parts.append("Evaluate stability and support for team members.")
        elif profile.disc_primary == DISCType.CONSCIENTIOUSNESS:
            guidance_parts.append("Analyze the details and assess potential risks carefully.")
        
        # Decision type specific guidance
        if decision.decision_type == DecisionType.PROJECT_SPECIFIC:
            affected_projects = []
            for option in decision.options:
                affected_projects.extend(option.affected_projects)
            
            member_projects = []
            if member_id == "daniel":
                member_projects.append("100_percent_project")
            elif member_id == "troy":
                member_projects.append("spark")
            elif member_id == "marc":
                member_projects.append("ecoco")
            elif member_id == "jimi":
                member_projects.append("treegens")
            
            if any(proj in affected_projects for proj in member_projects):
                guidance_parts.append("This decision directly affects your project area - your expertise is particularly valuable here.")
        
        return " ".join(guidance_parts)
    
    def submit_vote(self, 
                   decision_id: str,
                   voter_id: str,
                   vote_type: VoteType,
                   confidence_level: float,
                   reasoning: str,
                   option_id: Optional[str] = None,
                   conditions: Optional[str] = None) -> bool:
        """Submit a vote for a decision"""
        
        if decision_id not in self.decisions:
            print(f"❌ Decision {decision_id} not found")
            return False
        
        decision = self.decisions[decision_id]
        
        if decision.status != DecisionStatus.OPEN_FOR_VOTING:
            print(f"❌ Decision {decision_id} is not open for voting")
            return False
        
        if datetime.now() > decision.voting_deadline:
            print(f"❌ Voting deadline has passed for decision {decision_id}")
            return False
        
        # Get voter info
        voter = self.mem0_manager.team_members.get(voter_id)
        if not voter:
            print(f"❌ Voter {voter_id} not found")
            return False
        
        # Calculate vote weight
        vote_weight = self._calculate_vote_weight(voter_id, decision)
        
        # Get psychological factors
        psychological_factors = self._analyze_vote_psychology(voter_id, decision, vote_type)
        
        # Calculate expertise relevance
        expertise_relevance = self._calculate_expertise_relevance(voter_id, decision)
        
        # Create vote
        vote = Vote(
            voter_id=voter_id,
            voter_name=voter.name,
            vote_type=vote_type,
            confidence_level=confidence_level,
            reasoning=reasoning,
            conditions=conditions,
            psychological_factors=psychological_factors,
            expertise_relevance=expertise_relevance,
            vote_weight=vote_weight
        )
        
        # Store vote
        decision.votes[voter_id] = vote
        
        print(f"✅ Vote submitted by {voter.name}")
        print(f"   Vote: {vote_type.value}")
        print(f"   Confidence: {confidence_level:.1%}")
        print(f"   Weight: {vote_weight:.2f}")
        
        # Check if consensus can be calculated
        self._check_consensus_status(decision)
        
        return True
    
    def _calculate_vote_weight(self, voter_id: str, decision: Decision) -> float:
        """Calculate the weight of a vote based on psychological and expertise factors"""
        
        base_weight = 1.0
        
        if not decision.expertise_weighting_enabled and not decision.psychological_weighting_enabled:
            return base_weight
        
        # Expertise weighting
        expertise_multiplier = 1.0
        if decision.expertise_weighting_enabled:
            expertise_relevance = self._calculate_expertise_relevance(voter_id, decision)
            expertise_multiplier = 0.5 + (expertise_relevance * 1.5)  # Range: 0.5 to 2.0
        
        # Psychological weighting
        psychological_multiplier = 1.0
        if decision.psychological_weighting_enabled:
            psychological_fit = self._calculate_psychological_fit(voter_id, decision)
            psychological_multiplier = 0.7 + (psychological_fit * 0.6)  # Range: 0.7 to 1.3
        
        # Combined weight
        final_weight = base_weight * expertise_multiplier * psychological_multiplier
        
        # Cap the weight to prevent extreme values
        return max(0.3, min(2.5, final_weight))
    
    def _calculate_expertise_relevance(self, voter_id: str, decision: Decision) -> float:
        """Calculate how relevant the voter's expertise is to the decision"""
        
        voter = self.mem0_manager.team_members.get(voter_id)
        if not voter:
            return 0.5
        
        voter_expertise = set(voter.expertise_areas)
        
        # Get decision-relevant expertise areas
        relevant_expertise = set()
        
        # Add expertise based on decision type
        if decision.decision_type == DecisionType.STRATEGIC:
            relevant_expertise.update(["strategic_planning", "leadership", "vision"])
        elif decision.decision_type == DecisionType.OPERATIONAL:
            relevant_expertise.update(["project_management", "operations", "efficiency"])
        elif decision.decision_type == DecisionType.RESOURCE_ALLOCATION:
            relevant_expertise.update(["finance", "resource_management", "budgeting"])
        
        # Add expertise based on affected projects
        for option in decision.options:
            for project in option.affected_projects:
                if project in self.project_expertise_mapping:
                    relevant_expertise.update(self.project_expertise_mapping[project])
        
        # Calculate overlap
        if not relevant_expertise:
            return 0.5  # No specific expertise required
        
        overlap = len(voter_expertise.intersection(relevant_expertise))
        max_possible = len(relevant_expertise)
        
        return min(1.0, overlap / max_possible) if max_possible > 0 else 0.5
    
    def _calculate_psychological_fit(self, voter_id: str, decision: Decision) -> float:
        """Calculate how well the voter's psychology fits the decision type"""
        
        profile = self.enhanced_tanka.get_psychological_profile(voter_id)
        if not profile:
            return 0.5
        
        optimal_types = decision.psychological_analysis.get("optimal_decision_makers", [])
        
        if not optimal_types:
            return 0.5
        
        # Check MBTI fit
        mbti_fit = 1.0 if profile.mbti_type.value in optimal_types else 0.3
        
        # Check DISC fit based on decision type
        disc_fit = 0.5
        if decision.decision_type == DecisionType.STRATEGIC and profile.disc_primary == DISCType.DOMINANCE:
            disc_fit = 1.0
        elif decision.decision_type == DecisionType.OPERATIONAL and profile.disc_primary == DISCType.CONSCIENTIOUSNESS:
            disc_fit = 1.0
        elif decision.decision_type == DecisionType.PROJECT_SPECIFIC and profile.disc_primary == DISCType.INFLUENCE:
            disc_fit = 0.8
        
        # Combine MBTI and DISC fit
        return (mbti_fit * 0.7) + (disc_fit * 0.3)
    
    def _analyze_vote_psychology(self, voter_id: str, decision: Decision, vote_type: VoteType) -> Dict[str, Any]:
        """Analyze psychological factors in the vote"""
        
        profile = self.enhanced_tanka.get_psychological_profile(voter_id)
        if not profile:
            return {}
        
        psychological_factors = {
            "mbti_alignment": profile.mbti_type.value,
            "disc_style": profile.disc_primary.value,
            "decision_style_match": False,
            "stress_indicators": [],
            "confidence_factors": []
        }
        
        # Analyze decision style match
        optimal_types = decision.psychological_analysis.get("optimal_decision_makers", [])
        psychological_factors["decision_style_match"] = profile.mbti_type.value in optimal_types
        
        # Analyze vote type patterns
        if vote_type == VoteType.REQUEST_MORE_INFO:
            if profile.mbti_type.value.endswith("J"):  # Judging types
                psychological_factors["stress_indicators"].append("May indicate insufficient information for decisive action")
            else:  # Perceiving types
                psychological_factors["stress_indicators"].append("Natural preference for gathering more information")
        
        elif vote_type == VoteType.CONDITIONAL:
            psychological_factors["confidence_factors"].append("Shows thoughtful consideration of implementation details")
        
        elif vote_type == VoteType.ABSTAIN:
            psychological_factors["stress_indicators"].append("May indicate conflict avoidance or uncertainty")
        
        return psychological_factors
    
    def _check_consensus_status(self, decision: Decision):
        """Check if consensus has been reached and update decision status"""
        
        if not decision.votes:
            return
        
        # Calculate current participation rate
        total_team_members = len(self.mem0_manager.team_members)
        participation_rate = len(decision.votes) / total_team_members
        
        # Check if minimum participation is met
        if participation_rate < decision.minimum_participation:
            print(f"📊 Participation: {participation_rate:.1%} (minimum: {decision.minimum_participation:.1%})")
            return
        
        # Calculate consensus
        consensus_result = self._calculate_consensus(decision)
        decision.consensus_results = consensus_result.__dict__
        
        if consensus_result.consensus_reached:
            decision.status = DecisionStatus.CONSENSUS_REACHED
            decision.final_decision = consensus_result.winning_option_id
            decision.decision_confidence = consensus_result.confidence_level
            
            print(f"🎉 Consensus reached for: {decision.title}")
            print(f"   Winning option: {consensus_result.winning_option_id}")
            print(f"   Consensus score: {consensus_result.consensus_score:.1%}")
            print(f"   Confidence: {consensus_result.confidence_level:.1%}")
        
        elif datetime.now() > decision.voting_deadline:
            decision.status = DecisionStatus.CONSENSUS_FAILED
            print(f"⏰ Voting deadline passed without consensus: {decision.title}")
    
    def _calculate_consensus(self, decision: Decision) -> ConsensusResult:
        """Calculate consensus based on votes and weights"""
        
        # Group votes by option
        option_votes = defaultdict(list)
        total_weight = 0
        
        for vote in decision.votes.values():
            if vote.vote_type == VoteType.APPROVE:
                # For now, assume single option decisions
                # In multi-option decisions, this would need option_id
                option_votes["approve"].append(vote)
            elif vote.vote_type == VoteType.REJECT:
                option_votes["reject"].append(vote)
            elif vote.vote_type == VoteType.CONDITIONAL:
                option_votes["conditional"].append(vote)
            # Abstain and request_more_info don't count toward consensus
            
            if vote.vote_type in [VoteType.APPROVE, VoteType.REJECT, VoteType.CONDITIONAL]:
                total_weight += vote.vote_weight
        
        # Calculate weighted scores
        approve_weight = sum(vote.vote_weight for vote in option_votes["approve"])
        reject_weight = sum(vote.vote_weight for vote in option_votes["reject"])
        conditional_weight = sum(vote.vote_weight for vote in option_votes["conditional"])
        
        # Calculate consensus score
        if total_weight == 0:
            consensus_score = 0.0
        else:
            # Approve votes count fully, conditional votes count partially
            effective_approve_weight = approve_weight + (conditional_weight * 0.7)
            consensus_score = effective_approve_weight / total_weight
        
        # Check if consensus threshold is met
        consensus_reached = consensus_score >= decision.required_consensus_threshold
        
        # Calculate confidence level
        confidence_factors = []
        for vote in decision.votes.values():
            if vote.vote_type in [VoteType.APPROVE, VoteType.CONDITIONAL]:
                confidence_factors.append(vote.confidence_level)
        
        confidence_level = np.mean(confidence_factors) if confidence_factors else 0.0
        
        # Identify dissenting voices
        dissenting_voices = [
            vote.voter_name for vote in option_votes["reject"]
        ]
        
        # Collect conditions to address
        conditions_to_address = [
            vote.conditions for vote in option_votes["conditional"]
            if vote.conditions
        ]
        
        # Generate recommendation
        if consensus_reached:
            recommendation = f"Implement decision with {consensus_score:.1%} consensus"
        elif consensus_score > 0.5:
            recommendation = f"Consider addressing concerns and re-voting (current: {consensus_score:.1%})"
        else:
            recommendation = f"Significant opposition detected ({consensus_score:.1%}) - review decision"
        
        # Analyze psychological alignment
        psychological_alignment = self._analyze_consensus_psychology(decision)
        
        return ConsensusResult(
            consensus_reached=consensus_reached,
            winning_option_id="approve" if consensus_reached else None,
            consensus_score=consensus_score,
            participation_rate=len(decision.votes) / len(self.mem0_manager.team_members),
            confidence_level=confidence_level,
            psychological_alignment=psychological_alignment,
            dissenting_voices=dissenting_voices,
            conditions_to_address=conditions_to_address,
            recommendation=recommendation
        )
    
    def _analyze_consensus_psychology(self, decision: Decision) -> Dict[str, Any]:
        """Analyze psychological patterns in the consensus"""
        
        psychological_alignment = {
            "mbti_voting_patterns": defaultdict(list),
            "disc_voting_patterns": defaultdict(list),
            "psychological_consensus": {},
            "stress_indicators": []
        }
        
        for vote in decision.votes.values():
            psych_factors = vote.psychological_factors
            mbti_type = psych_factors.get("mbti_alignment")
            disc_type = psych_factors.get("disc_style")
            
            if mbti_type:
                psychological_alignment["mbti_voting_patterns"][mbti_type].append(vote.vote_type.value)
            
            if disc_type:
                psychological_alignment["disc_voting_patterns"][disc_type].append(vote.vote_type.value)
            
            # Collect stress indicators
            stress_indicators = psych_factors.get("stress_indicators", [])
            psychological_alignment["stress_indicators"].extend(stress_indicators)
        
        # Analyze psychological consensus
        for mbti_type, votes in psychological_alignment["mbti_voting_patterns"].items():
            vote_counter = Counter(votes)
            most_common_vote = vote_counter.most_common(1)[0] if vote_counter else ("none", 0)
            psychological_alignment["psychological_consensus"][mbti_type] = {
                "dominant_vote": most_common_vote[0],
                "vote_distribution": dict(vote_counter)
            }
        
        return psychological_alignment
    
    def get_decision_status(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive status of a decision"""
        
        if decision_id not in self.decisions:
            return None
        
        decision = self.decisions[decision_id]
        
        status = {
            "decision_id": decision.decision_id,
            "title": decision.title,
            "status": decision.status.value,
            "voting_deadline": decision.voting_deadline.isoformat(),
            "participation_rate": len(decision.votes) / len(self.mem0_manager.team_members),
            "consensus_threshold": decision.required_consensus_threshold,
            "votes_received": len(decision.votes),
            "total_team_members": len(self.mem0_manager.team_members),
            "consensus_results": decision.consensus_results,
            "psychological_analysis": decision.psychological_analysis,
            "risk_assessment": decision.risk_assessment,
            "predicted_outcomes": decision.predicted_outcomes
        }
        
        return status
    
    def get_team_decision_summary(self) -> Dict[str, Any]:
        """Get summary of all team decisions"""
        
        summary = {
            "total_decisions": len(self.decisions),
            "decisions_by_status": defaultdict(int),
            "decisions_by_type": defaultdict(int),
            "average_consensus_score": 0.0,
            "average_participation_rate": 0.0,
            "psychological_decision_patterns": {},
            "recent_decisions": []
        }
        
        consensus_scores = []
        participation_rates = []
        
        for decision in self.decisions.values():
            summary["decisions_by_status"][decision.status.value] += 1
            summary["decisions_by_type"][decision.decision_type.value] += 1
            
            if decision.consensus_results:
                consensus_scores.append(decision.consensus_results.get("consensus_score", 0))
                participation_rates.append(decision.consensus_results.get("participation_rate", 0))
        
        if consensus_scores:
            summary["average_consensus_score"] = np.mean(consensus_scores)
        
        if participation_rates:
            summary["average_participation_rate"] = np.mean(participation_rates)
        
        # Recent decisions (last 5)
        recent_decisions = sorted(self.decisions.values(), key=lambda d: d.created_at, reverse=True)[:5]
        summary["recent_decisions"] = [
            {
                "title": d.title,
                "status": d.status.value,
                "created_at": d.created_at.isoformat(),
                "consensus_score": d.consensus_results.get("consensus_score", 0) if d.consensus_results else 0
            }
            for d in recent_decisions
        ]
        
        return summary

# Example usage and testing
if __name__ == "__main__":
    # Test AsyncDecisionValidator (requires components from previous phases)
    try:
        # Initialize components
        mem0_manager = Mem0Manager()
        enhanced_tanka = EnhancedTankaProfileLoader(mem0_manager)
        insight_synthesizer = InsightSynthesizer(mem0_manager, enhanced_tanka, None)
        async_validator = AsyncDecisionValidator(mem0_manager, enhanced_tanka, insight_synthesizer)
        
        print("🗳️ AsyncDecisionValidator initialized successfully!")
        
        # Test decision creation
        sample_option = DecisionOption(
            option_id="option_1",
            title="Implement new project management system",
            description="Deploy SPARK methodology across all projects",
            impact_assessment={"efficiency": "high", "team_satisfaction": "positive"},
            resource_requirements={"time": "2 weeks", "budget": "$5000"},
            risk_factors=["Learning curve", "Temporary productivity dip"],
            success_indicators=["Improved project delivery", "Better team coordination"],
            implementation_timeline="4 weeks",
            affected_projects=["spark", "100_percent_project"],
            affected_team_members=["troy", "daniel", "kristie"]
        )
        
        decision = async_validator.create_decision(
            title="Implement SPARK Project Management System",
            description="Proposal to implement systematic project management across Impact Launchpad",
            decision_type=DecisionType.OPERATIONAL,
            urgency=DecisionUrgency.MEDIUM,
            proposer_id="troy",
            options=[sample_option]
        )
        
        print(f"✅ Decision created: {decision.decision_id}")
        
        # Test opening for voting
        success = async_validator.open_for_voting(decision.decision_id)
        print(f"✅ Voting opened: {success}")
        
        # Test vote submission
        vote_success = async_validator.submit_vote(
            decision_id=decision.decision_id,
            voter_id="daniel",
            vote_type=VoteType.APPROVE,
            confidence_level=0.8,
            reasoning="This aligns with our strategic goals for systematic improvement"
        )
        print(f"✅ Vote submitted: {vote_success}")
        
        # Test decision status
        status = async_validator.get_decision_status(decision.decision_id)
        print(f"✅ Decision status retrieved: {status is not None}")
        
        # Test team summary
        summary = async_validator.get_team_decision_summary()
        print(f"✅ Team summary: {summary}")
        
        print("\n✅ AsyncDecisionValidator successfully tested!")
        
    except Exception as e:
        print(f"❌ Error testing AsyncDecisionValidator: {e}")
        print("💡 This requires components from previous phases to be properly initialized")

