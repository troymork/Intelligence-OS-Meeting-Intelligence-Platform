"""
Oracle Intelligence System - DebriefCollector Engine
Orchestrates strategic post-meeting debriefs with psychological intelligence

This module conducts personalized strategic debriefs with each team member
using their psychological profiles (MBTI, DISC, Big Five) to:
- Generate psychologically-informed strategic questions
- Adapt debrief flow based on stress and engagement levels
- Collect and validate meaningful responses
- Store insights in Mem0 with psychological metadata
- Identify patterns and discrepancies across team members
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

from Mem0Manager import Mem0Manager, DebriefEntry
from EnhancedTankaProfileLoader import (
    EnhancedTankaProfileLoader, 
    AdaptiveTankaSession, 
    PsychologicalProfile,
    MBTIType,
    DISCType
)

class DebriefStatus(Enum):
    """Status of debrief collection process"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class ResponseQuality(Enum):
    """Quality assessment of debrief responses"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ADEQUATE = "adequate"
    POOR = "poor"
    INCOMPLETE = "incomplete"

@dataclass
class MeetingContext:
    """Context information about the meeting for debrief generation"""
    meeting_id: str
    title: str
    date: str
    participants: List[str]
    duration_minutes: int
    meeting_type: str
    key_decisions: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    discussion_topics: List[str] = field(default_factory=list)
    transcript_summary: Optional[str] = None
    strategic_themes: List[str] = field(default_factory=list)

@dataclass
class DebriefResult:
    """Result of individual team member debrief"""
    user_id: str
    user_name: str
    session_id: str
    status: DebriefStatus
    questions: List[str]
    responses: Dict[str, str]
    psychological_insights: Dict[str, Any]
    stress_level: float
    engagement_level: float
    response_quality: ResponseQuality
    completion_time: Optional[datetime] = None
    additional_insights: List[str] = field(default_factory=list)
    decision_feedback: Dict[str, str] = field(default_factory=list)  # approve/reject/concern
    missed_highlights: List[str] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)

@dataclass
class CollectiveDebriefSummary:
    """Summary of all team member debriefs"""
    meeting_id: str
    total_participants: int
    completed_debriefs: int
    average_stress_level: float
    average_engagement_level: float
    collective_insights: List[str]
    decision_consensus: Dict[str, Dict[str, int]]  # decision -> {approve: count, reject: count, concern: count}
    psychological_patterns: Dict[str, Any]
    discrepancies: List[Dict[str, Any]]
    recommended_actions: List[str]
    created_at: datetime = field(default_factory=datetime.now)

class DebriefCollector:
    """
    Orchestrates strategic post-meeting debriefs with psychological intelligence
    
    Conducts personalized debriefs with each team member using their psychological
    profiles to generate strategic insights, validate decisions, and identify
    patterns and discrepancies across the team.
    """
    
    def __init__(self, mem0_manager: Mem0Manager, enhanced_tanka: EnhancedTankaProfileLoader):
        """Initialize DebriefCollector with Mem0 and Enhanced Tanka integration"""
        self.mem0_manager = mem0_manager
        self.enhanced_tanka = enhanced_tanka
        
        # Active debrief sessions
        self.active_sessions: Dict[str, AdaptiveTankaSession] = {}
        self.debrief_results: Dict[str, DebriefResult] = {}
        
        # Configuration
        self.default_timeout_minutes = 30
        self.min_response_length = 20
        self.max_questions_per_debrief = 7
        
        print("🎯 DebriefCollector initialized with psychological intelligence")
    
    def create_meeting_context(self, meeting_data: Dict[str, Any]) -> MeetingContext:
        """Create meeting context from meeting data"""
        context = MeetingContext(
            meeting_id=meeting_data.get("meeting_id", str(uuid.uuid4())),
            title=meeting_data.get("title", "Team Meeting"),
            date=meeting_data.get("date", datetime.now().isoformat()),
            participants=meeting_data.get("participants", []),
            duration_minutes=meeting_data.get("duration_minutes", 60),
            meeting_type=meeting_data.get("meeting_type", "strategic"),
            key_decisions=meeting_data.get("key_decisions", []),
            action_items=meeting_data.get("action_items", []),
            discussion_topics=meeting_data.get("discussion_topics", []),
            transcript_summary=meeting_data.get("transcript_summary"),
            strategic_themes=meeting_data.get("strategic_themes", [])
        )
        
        print(f"📋 Created meeting context for '{context.title}' with {len(context.participants)} participants")
        return context
    
    def initiate_team_debrief(self, meeting_context: MeetingContext) -> Dict[str, AdaptiveTankaSession]:
        """Initiate strategic debriefs for all meeting participants"""
        sessions = {}
        
        print(f"🚀 Initiating team debrief for meeting: {meeting_context.title}")
        
        for participant_id in meeting_context.participants:
            if participant_id in self.mem0_manager.team_members:
                try:
                    # Create adaptive session with psychological profile
                    session = self.enhanced_tanka.create_adaptive_session(
                        user_id=participant_id,
                        session_type="post_meeting_debrief",
                        meeting_id=meeting_context.meeting_id
                    )
                    
                    # Generate psychologically-informed questions
                    questions = self._generate_contextual_questions(
                        participant_id, 
                        meeting_context,
                        session.psychological_profile
                    )
                    session.questions = questions
                    
                    # Store session
                    sessions[participant_id] = session
                    self.active_sessions[session.session_id] = session
                    
                    print(f"✅ Initiated debrief for {session.user_name} ({session.psychological_profile.mbti_type.value}/{session.psychological_profile.disc_primary.value})")
                    
                except Exception as e:
                    print(f"❌ Failed to initiate debrief for {participant_id}: {e}")
            else:
                print(f"⚠️ Participant {participant_id} not found in team members")
        
        print(f"🎯 Team debrief initiated: {len(sessions)} sessions created")
        return sessions
    
    def _generate_contextual_questions(self, user_id: str, meeting_context: MeetingContext, profile: PsychologicalProfile) -> List[str]:
        """Generate contextual questions based on meeting content and psychological profile"""
        member = self.mem0_manager.team_members[user_id]
        
        # Base context for question generation
        context_summary = self._create_context_summary(meeting_context, member)
        
        # Determine question complexity based on meeting type and profile
        if meeting_context.meeting_type in ["strategic", "planning"]:
            base_questions = 6
        elif meeting_context.meeting_type in ["operational", "status"]:
            base_questions = 4
        else:
            base_questions = 5
        
        # Adjust based on psychological profile
        if profile.big_five.conscientiousness > 0.8:
            base_questions += 1  # Detail-oriented people appreciate more thorough debriefs
        if profile.big_five.neuroticism > 0.6:
            base_questions -= 1  # Reduce cognitive load for higher stress individuals
        
        question_count = min(max(base_questions, 3), self.max_questions_per_debrief)
        
        # Generate questions using Enhanced Tanka
        try:
            questions = self.enhanced_tanka.generate_psychologically_informed_questions(
                user_id=user_id,
                meeting_context=context_summary,
                stress_level=0.0  # Initial stress level
            )
            
            # Ensure we have the right number of questions
            if len(questions) < question_count:
                # Add context-specific questions
                additional_questions = self._generate_context_specific_questions(
                    member, profile, meeting_context, question_count - len(questions)
                )
                questions.extend(additional_questions)
            
            return questions[:question_count]
            
        except Exception as e:
            print(f"⚠️ Error generating contextual questions for {member.name}: {e}")
            # Fallback to context-specific questions
            return self._generate_context_specific_questions(member, profile, meeting_context, question_count)
    
    def _create_context_summary(self, meeting_context: MeetingContext, member) -> str:
        """Create context summary for question generation"""
        summary_parts = [
            f"Meeting: {meeting_context.title}",
            f"Type: {meeting_context.meeting_type}",
            f"Duration: {meeting_context.duration_minutes} minutes"
        ]
        
        if meeting_context.key_decisions:
            summary_parts.append(f"Key Decisions: {'; '.join(meeting_context.key_decisions[:3])}")
        
        if meeting_context.action_items:
            summary_parts.append(f"Action Items: {'; '.join(meeting_context.action_items[:3])}")
        
        if meeting_context.strategic_themes:
            summary_parts.append(f"Strategic Themes: {'; '.join(meeting_context.strategic_themes)}")
        
        # Add member-specific context
        summary_parts.append(f"Participant Role: {member.role}")
        summary_parts.append(f"Expertise Areas: {', '.join(member.expertise_areas)}")
        
        return " | ".join(summary_parts)
    
    def _generate_context_specific_questions(self, member, profile: PsychologicalProfile, meeting_context: MeetingContext, count: int) -> List[str]:
        """Generate context-specific fallback questions"""
        questions = []
        
        # Decision validation questions
        if meeting_context.key_decisions:
            if profile.mbti_type.value[2] == "T":  # Thinking types
                questions.append(f"From a logical analysis perspective, which of our key decisions ({', '.join(meeting_context.key_decisions[:2])}) do you have the highest confidence in?")
            else:  # Feeling types
                questions.append(f"How do you feel about the impact of our key decisions ({', '.join(meeting_context.key_decisions[:2])}) on the team and stakeholders?")
        
        # Action item feasibility
        if meeting_context.action_items:
            if profile.disc_primary == DISCType.CONSCIENTIOUSNESS:
                questions.append("What quality standards or processes should we establish to ensure successful completion of our action items?")
            elif profile.disc_primary == DISCType.DOMINANCE:
                questions.append("What potential obstacles or challenges do you foresee in executing our action items?")
            else:
                questions.append("What support or resources will be needed to successfully complete our action items?")
        
        # Strategic insights based on expertise
        if member.expertise_areas:
            expertise_focus = member.expertise_areas[0]
            questions.append(f"From your {expertise_focus} expertise, what strategic opportunities or risks did you notice that we might not have fully explored?")
        
        # Psychological profile-based questions
        if profile.big_five.openness > 0.7:
            questions.append("What innovative ideas or creative solutions emerged in your mind during or after our discussion?")
        
        if profile.big_five.agreeableness > 0.7:
            questions.append("How can we ensure that all team members feel heard and valued in implementing these decisions?")
        
        # Meeting type-specific questions
        if meeting_context.meeting_type == "strategic":
            questions.append("What long-term implications of our decisions should we be monitoring over the next quarter?")
        elif meeting_context.meeting_type == "operational":
            questions.append("What operational details or implementation concerns should we address before moving forward?")
        
        # General reflection question
        questions.append(f"What additional thoughts or concerns have emerged since the meeting that you'd like the team to consider?")
        
        return questions[:count]
    
    def collect_debrief_response(self, session_id: str, question_index: int, response: str) -> bool:
        """Collect individual response to a debrief question"""
        if session_id not in self.active_sessions:
            print(f"❌ Session {session_id} not found")
            return False
        
        session = self.active_sessions[session_id]
        
        # Validate response quality
        if len(response.strip()) < self.min_response_length:
            print(f"⚠️ Response too short for {session.user_name} (question {question_index + 1})")
            return False
        
        # Store response
        question_key = f"q{question_index + 1}"
        session.responses[question_key] = response.strip()
        
        # Update stress and engagement levels based on response
        stress_level, engagement_level = self.enhanced_tanka.detect_stress_and_engagement({question_key: response})
        session.stress_level_detected = max(session.stress_level_detected, stress_level)
        session.engagement_level = (session.engagement_level + engagement_level) / 2  # Running average
        
        print(f"✅ Collected response from {session.user_name} (Q{question_index + 1}): stress={stress_level:.1f}, engagement={engagement_level:.1f}")
        
        # Check if debrief is complete
        if len(session.responses) >= len(session.questions):
            self._complete_individual_debrief(session)
        
        return True
    
    def _complete_individual_debrief(self, session: AdaptiveTankaSession) -> DebriefResult:
        """Complete individual debrief and generate insights"""
        print(f"🎯 Completing debrief for {session.user_name}")
        
        # Assess response quality
        response_quality = self._assess_response_quality(session.responses)
        
        # Extract psychological insights
        psychological_insights = self._extract_psychological_insights(session)
        
        # Generate additional insights and follow-up questions
        additional_insights = self._generate_additional_insights(session)
        follow_up_questions = self._generate_follow_up_questions(session)
        
        # Create debrief result
        result = DebriefResult(
            user_id=session.user_id,
            user_name=session.user_name,
            session_id=session.session_id,
            status=DebriefStatus.COMPLETED,
            questions=session.questions,
            responses=session.responses,
            psychological_insights=psychological_insights,
            stress_level=session.stress_level_detected,
            engagement_level=session.engagement_level,
            response_quality=response_quality,
            completion_time=datetime.now(),
            additional_insights=additional_insights,
            follow_up_questions=follow_up_questions
        )
        
        # Store in Mem0
        self._store_debrief_in_mem0(result, session)
        
        # Store result
        self.debrief_results[session.session_id] = result
        
        # Update session status
        session.status = "completed"
        
        print(f"✅ Debrief completed for {session.user_name}: {response_quality.value} quality, {len(additional_insights)} insights")
        return result
    
    def _assess_response_quality(self, responses: Dict[str, str]) -> ResponseQuality:
        """Assess the quality of debrief responses"""
        if not responses:
            return ResponseQuality.INCOMPLETE
        
        total_length = sum(len(response) for response in responses.values())
        avg_length = total_length / len(responses)
        
        # Simple quality assessment based on response length and completeness
        if avg_length > 100 and len(responses) >= 4:
            return ResponseQuality.EXCELLENT
        elif avg_length > 60 and len(responses) >= 3:
            return ResponseQuality.GOOD
        elif avg_length > 30 and len(responses) >= 2:
            return ResponseQuality.ADEQUATE
        elif len(responses) > 0:
            return ResponseQuality.POOR
        else:
            return ResponseQuality.INCOMPLETE
    
    def _extract_psychological_insights(self, session: AdaptiveTankaSession) -> Dict[str, Any]:
        """Extract psychological insights from debrief responses"""
        profile = session.psychological_profile
        responses_text = " ".join(session.responses.values()).lower()
        
        insights = {
            "mbti_alignment": self._assess_mbti_alignment(profile.mbti_type, responses_text),
            "disc_communication_style": self._assess_disc_alignment(profile.disc_primary, responses_text),
            "big_five_indicators": self._assess_big_five_indicators(profile.big_five, responses_text),
            "stress_patterns": self._identify_stress_patterns(profile, responses_text),
            "engagement_patterns": self._identify_engagement_patterns(profile, responses_text),
            "decision_making_style": self._assess_decision_making_style(profile, responses_text)
        }
        
        return insights
    
    def _assess_mbti_alignment(self, mbti_type: MBTIType, responses_text: str) -> Dict[str, Any]:
        """Assess how responses align with MBTI type"""
        mbti_str = mbti_type.value
        
        alignment = {
            "type": mbti_str,
            "energy_alignment": 0.5,
            "information_alignment": 0.5,
            "decision_alignment": 0.5,
            "lifestyle_alignment": 0.5
        }
        
        # Energy (E/I)
        if mbti_str[0] == "E":
            if any(word in responses_text for word in ["team", "discuss", "collaborate", "share"]):
                alignment["energy_alignment"] = 0.8
        else:  # I
            if any(word in responses_text for word in ["reflect", "consider", "think", "analyze"]):
                alignment["energy_alignment"] = 0.8
        
        # Information (S/N)
        if mbti_str[1] == "S":
            if any(word in responses_text for word in ["specific", "detail", "concrete", "practical"]):
                alignment["information_alignment"] = 0.8
        else:  # N
            if any(word in responses_text for word in ["possibility", "future", "potential", "innovative"]):
                alignment["information_alignment"] = 0.8
        
        # Decision (T/F)
        if mbti_str[2] == "T":
            if any(word in responses_text for word in ["logical", "analysis", "objective", "efficient"]):
                alignment["decision_alignment"] = 0.8
        else:  # F
            if any(word in responses_text for word in ["people", "values", "impact", "harmony"]):
                alignment["decision_alignment"] = 0.8
        
        return alignment
    
    def _assess_disc_alignment(self, disc_type: DISCType, responses_text: str) -> Dict[str, Any]:
        """Assess how responses align with DISC type"""
        alignment = {"type": disc_type.value, "alignment_score": 0.5}
        
        if disc_type == DISCType.DOMINANCE:
            if any(word in responses_text for word in ["results", "challenge", "control", "direct"]):
                alignment["alignment_score"] = 0.8
        elif disc_type == DISCType.INFLUENCE:
            if any(word in responses_text for word in ["enthusiasm", "people", "optimistic", "social"]):
                alignment["alignment_score"] = 0.8
        elif disc_type == DISCType.STEADINESS:
            if any(word in responses_text for word in ["stable", "support", "team", "gradual"]):
                alignment["alignment_score"] = 0.8
        elif disc_type == DISCType.CONSCIENTIOUSNESS:
            if any(word in responses_text for word in ["quality", "accurate", "systematic", "detail"]):
                alignment["alignment_score"] = 0.8
        
        return alignment
    
    def _assess_big_five_indicators(self, big_five, responses_text: str) -> Dict[str, float]:
        """Assess Big Five trait indicators in responses"""
        indicators = {
            "openness_indicators": 0.5,
            "conscientiousness_indicators": 0.5,
            "extraversion_indicators": 0.5,
            "agreeableness_indicators": 0.5,
            "neuroticism_indicators": 0.5
        }
        
        # Openness
        if any(word in responses_text for word in ["creative", "innovative", "new", "different", "explore"]):
            indicators["openness_indicators"] = 0.8
        
        # Conscientiousness
        if any(word in responses_text for word in ["organized", "plan", "systematic", "thorough", "quality"]):
            indicators["conscientiousness_indicators"] = 0.8
        
        # Extraversion
        if any(word in responses_text for word in ["team", "collaborate", "discuss", "energy", "social"]):
            indicators["extraversion_indicators"] = 0.8
        
        # Agreeableness
        if any(word in responses_text for word in ["harmony", "consensus", "support", "cooperation", "help"]):
            indicators["agreeableness_indicators"] = 0.8
        
        # Neuroticism (stress indicators)
        if any(word in responses_text for word in ["worried", "concerned", "stressed", "anxious", "pressure"]):
            indicators["neuroticism_indicators"] = 0.8
        
        return indicators
    
    def _identify_stress_patterns(self, profile: PsychologicalProfile, responses_text: str) -> List[str]:
        """Identify stress patterns in responses"""
        patterns = []
        
        for stress_indicator in profile.stress_indicators:
            if stress_indicator.replace("_", " ") in responses_text:
                patterns.append(f"Detected {stress_indicator.replace('_', ' ')} stress pattern")
        
        # General stress indicators
        stress_words = ["overwhelmed", "pressure", "difficult", "challenging", "concerned", "worried"]
        detected_stress = [word for word in stress_words if word in responses_text]
        
        if detected_stress:
            patterns.append(f"General stress indicators: {', '.join(detected_stress)}")
        
        return patterns
    
    def _identify_engagement_patterns(self, profile: PsychologicalProfile, responses_text: str) -> List[str]:
        """Identify engagement patterns in responses"""
        patterns = []
        
        # Motivation-based engagement
        for motivation in profile.motivation_drivers:
            if motivation.replace("_", " ") in responses_text:
                patterns.append(f"High engagement with {motivation.replace('_', ' ')}")
        
        # General engagement indicators
        engagement_words = ["excited", "interested", "opportunity", "potential", "innovative", "creative"]
        detected_engagement = [word for word in engagement_words if word in responses_text]
        
        if detected_engagement:
            patterns.append(f"Positive engagement indicators: {', '.join(detected_engagement)}")
        
        return patterns
    
    def _assess_decision_making_style(self, profile: PsychologicalProfile, responses_text: str) -> Dict[str, Any]:
        """Assess decision-making style from responses"""
        style = {
            "primary_style": "balanced",
            "confidence_level": 0.5,
            "decision_factors": []
        }
        
        # MBTI-based decision style
        mbti_str = profile.mbti_type.value
        if mbti_str[2] == "T":
            if any(word in responses_text for word in ["logical", "analysis", "data", "objective"]):
                style["primary_style"] = "analytical"
                style["confidence_level"] = 0.8
        else:  # F
            if any(word in responses_text for word in ["people", "values", "impact", "feelings"]):
                style["primary_style"] = "values_based"
                style["confidence_level"] = 0.8
        
        # DISC-based decision factors
        if profile.disc_primary == DISCType.DOMINANCE:
            style["decision_factors"].append("results_oriented")
        elif profile.disc_primary == DISCType.INFLUENCE:
            style["decision_factors"].append("people_impact")
        elif profile.disc_primary == DISCType.STEADINESS:
            style["decision_factors"].append("stability_focused")
        elif profile.disc_primary == DISCType.CONSCIENTIOUSNESS:
            style["decision_factors"].append("quality_focused")
        
        return style
    
    def _generate_additional_insights(self, session: AdaptiveTankaSession) -> List[str]:
        """Generate additional insights from debrief responses"""
        insights = []
        responses_text = " ".join(session.responses.values())
        
        # Extract key themes
        if "opportunity" in responses_text.lower():
            insights.append("Identified new opportunities for exploration")
        
        if "concern" in responses_text.lower() or "risk" in responses_text.lower():
            insights.append("Raised important concerns or risks")
        
        if "team" in responses_text.lower() and "collaboration" in responses_text.lower():
            insights.append("Emphasized team collaboration and dynamics")
        
        # Role-specific insights
        member = self.mem0_manager.team_members[session.user_id]
        for expertise in member.expertise_areas:
            if expertise.lower() in responses_text.lower():
                insights.append(f"Provided {expertise}-specific insights")
        
        return insights
    
    def _generate_follow_up_questions(self, session: AdaptiveTankaSession) -> List[str]:
        """Generate follow-up questions based on responses"""
        follow_ups = []
        responses_text = " ".join(session.responses.values()).lower()
        
        # Generate follow-ups based on response content
        if "concern" in responses_text or "worried" in responses_text:
            follow_ups.append("What specific steps could we take to address your concerns?")
        
        if "opportunity" in responses_text or "potential" in responses_text:
            follow_ups.append("How could we best capitalize on the opportunities you've identified?")
        
        if "team" in responses_text:
            follow_ups.append("What would help the team work more effectively together on this?")
        
        # Psychological profile-based follow-ups
        profile = session.psychological_profile
        if profile.big_five.openness > 0.7 and "creative" in responses_text:
            follow_ups.append("What innovative approaches should we consider exploring further?")
        
        if profile.disc_primary == DISCType.CONSCIENTIOUSNESS and "quality" in responses_text:
            follow_ups.append("What quality standards should we establish to ensure success?")
        
        return follow_ups[:3]  # Limit to 3 follow-up questions
    
    def _store_debrief_in_mem0(self, result: DebriefResult, session: AdaptiveTankaSession):
        """Store debrief result in Mem0 with psychological metadata"""
        # Create comprehensive debrief entry
        debrief_data = {
            "responses": result.responses,
            "psychological_insights": result.psychological_insights,
            "stress_level": result.stress_level,
            "engagement_level": result.engagement_level,
            "response_quality": result.response_quality.value,
            "additional_insights": result.additional_insights,
            "follow_up_questions": result.follow_up_questions
        }
        
        # Store in Mem0
        memory_id = self.mem0_manager.add_debrief(
            user_id=result.user_id,
            meeting_id=session.meeting_id,
            responses=debrief_data
        )
        
        print(f"💾 Stored debrief for {result.user_name} in Mem0: {memory_id}")
        return memory_id
    
    def generate_collective_summary(self, meeting_id: str) -> CollectiveDebriefSummary:
        """Generate collective summary of all debriefs for a meeting"""
        # Get all debrief results for this meeting
        meeting_results = [
            result for result in self.debrief_results.values()
            if result.session_id in self.active_sessions and 
            self.active_sessions[result.session_id].meeting_id == meeting_id
        ]
        
        if not meeting_results:
            print(f"⚠️ No debrief results found for meeting {meeting_id}")
            return None
        
        # Calculate averages
        total_participants = len(meeting_results)
        completed_debriefs = len([r for r in meeting_results if r.status == DebriefStatus.COMPLETED])
        avg_stress = sum(r.stress_level for r in meeting_results) / total_participants
        avg_engagement = sum(r.engagement_level for r in meeting_results) / total_participants
        
        # Collect insights
        all_insights = []
        for result in meeting_results:
            all_insights.extend(result.additional_insights)
        
        # Analyze psychological patterns
        psychological_patterns = self._analyze_team_psychological_patterns(meeting_results)
        
        # Identify discrepancies
        discrepancies = self._identify_team_discrepancies(meeting_results)
        
        # Generate recommendations
        recommendations = self._generate_team_recommendations(meeting_results, psychological_patterns)
        
        summary = CollectiveDebriefSummary(
            meeting_id=meeting_id,
            total_participants=total_participants,
            completed_debriefs=completed_debriefs,
            average_stress_level=avg_stress,
            average_engagement_level=avg_engagement,
            collective_insights=all_insights,
            decision_consensus={},  # Would be populated with actual decision feedback
            psychological_patterns=psychological_patterns,
            discrepancies=discrepancies,
            recommended_actions=recommendations
        )
        
        print(f"📊 Generated collective summary for meeting {meeting_id}: {completed_debriefs}/{total_participants} debriefs completed")
        return summary
    
    def _analyze_team_psychological_patterns(self, results: List[DebriefResult]) -> Dict[str, Any]:
        """Analyze psychological patterns across team debriefs"""
        patterns = {
            "stress_distribution": {},
            "engagement_distribution": {},
            "mbti_response_patterns": {},
            "disc_communication_patterns": {},
            "decision_making_styles": {}
        }
        
        for result in results:
            # Stress distribution
            stress_category = "high" if result.stress_level > 0.6 else "medium" if result.stress_level > 0.3 else "low"
            patterns["stress_distribution"][stress_category] = patterns["stress_distribution"].get(stress_category, 0) + 1
            
            # Engagement distribution
            engagement_category = "high" if result.engagement_level > 0.7 else "medium" if result.engagement_level > 0.4 else "low"
            patterns["engagement_distribution"][engagement_category] = patterns["engagement_distribution"].get(engagement_category, 0) + 1
            
            # MBTI patterns
            if "mbti_alignment" in result.psychological_insights:
                mbti_type = result.psychological_insights["mbti_alignment"]["type"]
                patterns["mbti_response_patterns"][mbti_type] = patterns["mbti_response_patterns"].get(mbti_type, [])
                patterns["mbti_response_patterns"][mbti_type].append({
                    "user": result.user_name,
                    "alignment": result.psychological_insights["mbti_alignment"]
                })
        
        return patterns
    
    def _identify_team_discrepancies(self, results: List[DebriefResult]) -> List[Dict[str, Any]]:
        """Identify discrepancies in team member responses"""
        discrepancies = []
        
        # Stress level discrepancies
        stress_levels = [r.stress_level for r in results]
        if max(stress_levels) - min(stress_levels) > 0.5:
            high_stress = [r.user_name for r in results if r.stress_level > 0.6]
            low_stress = [r.user_name for r in results if r.stress_level < 0.3]
            
            if high_stress and low_stress:
                discrepancies.append({
                    "type": "stress_level_variance",
                    "description": f"Significant stress level differences: {', '.join(high_stress)} (high) vs {', '.join(low_stress)} (low)",
                    "severity": "medium",
                    "recommendation": "Check in with high-stress team members individually"
                })
        
        # Engagement level discrepancies
        engagement_levels = [r.engagement_level for r in results]
        if max(engagement_levels) - min(engagement_levels) > 0.4:
            high_engagement = [r.user_name for r in results if r.engagement_level > 0.7]
            low_engagement = [r.user_name for r in results if r.engagement_level < 0.4]
            
            if high_engagement and low_engagement:
                discrepancies.append({
                    "type": "engagement_variance",
                    "description": f"Engagement level differences: {', '.join(high_engagement)} (high) vs {', '.join(low_engagement)} (low)",
                    "severity": "medium",
                    "recommendation": "Explore ways to increase engagement for less engaged members"
                })
        
        return discrepancies
    
    def _generate_team_recommendations(self, results: List[DebriefResult], patterns: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on team debrief analysis"""
        recommendations = []
        
        # Stress-based recommendations
        high_stress_count = patterns["stress_distribution"].get("high", 0)
        if high_stress_count > len(results) * 0.3:  # More than 30% high stress
            recommendations.append("Consider reducing meeting frequency or duration to manage team stress levels")
        
        # Engagement-based recommendations
        low_engagement_count = patterns["engagement_distribution"].get("low", 0)
        if low_engagement_count > len(results) * 0.3:  # More than 30% low engagement
            recommendations.append("Explore ways to increase meeting relevance and participation for all team members")
        
        # Quality-based recommendations
        poor_quality_count = len([r for r in results if r.response_quality in [ResponseQuality.POOR, ResponseQuality.INCOMPLETE]])
        if poor_quality_count > 0:
            recommendations.append("Follow up individually with team members who provided limited debrief responses")
        
        # Psychological diversity recommendations
        if len(patterns["mbti_response_patterns"]) > 6:  # High MBTI diversity
            recommendations.append("Leverage the team's psychological diversity by ensuring multiple perspectives are heard in decision-making")
        
        return recommendations
    
    def get_debrief_status(self, meeting_id: str) -> Dict[str, Any]:
        """Get status of all debriefs for a meeting"""
        meeting_sessions = [
            session for session in self.active_sessions.values()
            if session.meeting_id == meeting_id
        ]
        
        status = {
            "meeting_id": meeting_id,
            "total_sessions": len(meeting_sessions),
            "completed": len([s for s in meeting_sessions if s.status == "completed"]),
            "in_progress": len([s for s in meeting_sessions if s.status == "active"]),
            "session_details": []
        }
        
        for session in meeting_sessions:
            session_detail = {
                "user_name": session.user_name,
                "status": session.status,
                "questions_answered": len(session.responses),
                "total_questions": len(session.questions),
                "stress_level": session.stress_level_detected,
                "engagement_level": session.engagement_level
            }
            status["session_details"].append(session_detail)
        
        return status

# Example usage and testing
if __name__ == "__main__":
    # Test DebriefCollector (requires OPENAI_API_KEY)
    try:
        # Initialize components
        mem0_manager = Mem0Manager()
        enhanced_tanka = EnhancedTankaProfileLoader(mem0_manager)
        debrief_collector = DebriefCollector(mem0_manager, enhanced_tanka)
        
        # Create sample meeting context
        sample_meeting = {
            "meeting_id": "strategic_q2_2024",
            "title": "Q2 Strategic Planning Session",
            "date": "2024-07-03",
            "participants": ["daniel", "troy", "kristie", "marc"],
            "duration_minutes": 90,
            "meeting_type": "strategic",
            "key_decisions": [
                "Accelerate SPARK project timeline",
                "Increase Ecoco sustainability focus",
                "Implement new team collaboration tools"
            ],
            "action_items": [
                "Troy to update SPARK roadmap by July 15",
                "Marc to present Ecoco sustainability metrics",
                "Kristie to research collaboration platforms"
            ],
            "strategic_themes": ["Innovation", "Sustainability", "Team Efficiency"]
        }
        
        meeting_context = debrief_collector.create_meeting_context(sample_meeting)
        
        # Initiate team debrief
        sessions = debrief_collector.initiate_team_debrief(meeting_context)
        
        print(f"\n🎯 Debrief Sessions Created:")
        for user_id, session in sessions.items():
            print(f"• {session.user_name}: {len(session.questions)} questions")
            for i, question in enumerate(session.questions, 1):
                print(f"  {i}. {question}")
        
        # Simulate some responses (in real implementation, these would come from UI)
        sample_responses = {
            "daniel": [
                "I'm excited about accelerating the SPARK timeline. This aligns perfectly with our strategic vision for Q2.",
                "The sustainability focus for Ecoco is crucial - we need to ensure we're measuring the right metrics.",
                "I think the collaboration tools will help, but we need to ensure adoption across all team members."
            ],
            "troy": [
                "The SPARK timeline acceleration is ambitious but achievable with proper resource allocation.",
                "I'll need to coordinate with the development team to ensure quality isn't compromised.",
                "The collaboration tools should integrate with our existing project management systems."
            ]
        }
        
        # Collect sample responses
        for user_id, responses in sample_responses.items():
            if user_id in sessions:
                session = sessions[user_id]
                for i, response in enumerate(responses):
                    if i < len(session.questions):
                        debrief_collector.collect_debrief_response(session.session_id, i, response)
        
        # Generate collective summary
        summary = debrief_collector.generate_collective_summary(meeting_context.meeting_id)
        if summary:
            print(f"\n📊 Collective Summary:")
            print(f"Completed: {summary.completed_debriefs}/{summary.total_participants}")
            print(f"Average Stress: {summary.average_stress_level:.1f}")
            print(f"Average Engagement: {summary.average_engagement_level:.1f}")
            print(f"Recommendations: {summary.recommended_actions}")
        
        print("\n✅ DebriefCollector successfully tested!")
        
    except Exception as e:
        print(f"❌ Error testing DebriefCollector: {e}")
        print("💡 Make sure OPENAI_API_KEY is set for full functionality")

