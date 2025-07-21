"""
Oracle 9.1 Protocol Output Generation System
Generates comprehensive structured outputs from AI analysis results
"""

import os
import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import structlog
from collections import defaultdict
import numpy as np

logger = structlog.get_logger(__name__)

class OutputSection(Enum):
    """Oracle 9.1 Protocol output sections"""
    EXECUTIVE_SUMMARY = "executive_summary"
    DECISIONS_AGREEMENTS = "decisions_agreements"
    ACTION_REGISTER = "action_register"
    STRATEGIC_IMPLICATIONS = "strategic_implications"
    DISCUSSION_DYNAMICS = "discussion_dynamics"
    HUMAN_NEEDS_INTELLIGENCE = "human_needs_intelligence"
    PATTERN_RECOGNITION = "pattern_recognition"
    COMMUNICATION_HIGHLIGHTS = "communication_highlights"
    NARRATIVE_DEVELOPMENT = "narrative_development"
    SOLUTION_PORTFOLIO = "solution_portfolio"
    HUMAN_NEEDS_FULFILLMENT = "human_needs_fulfillment"
    INTEGRITY_ALIGNMENT_CHECK = "integrity_alignment_check"

class PriorityLevel(Enum):
    """Priority levels for decisions and actions"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DecisionStatus(Enum):
    """Decision implementation status"""
    PROPOSED = "proposed"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"

class ActionStatus(Enum):
    """Action item status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class ExecutiveSummary:
    """Executive summary structure"""
    meeting_overview: str
    key_outcomes: List[str]
    critical_decisions: List[str]
    priority_actions: List[str]
    strategic_alignment: Dict[str, float]
    risk_factors: List[str]
    success_indicators: List[str]
    next_steps: List[str]
    confidence_score: float
    generated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Decision:
    """Decision structure"""
    id: str
    title: str
    description: str
    decision_maker: str
    stakeholders: List[str]
    priority: PriorityLevel
    status: DecisionStatus
    rationale: str
    implementation_plan: str
    success_criteria: List[str]
    risk_assessment: str
    impact_analysis: str
    timeline: Dict[str, Any]
    dependencies: List[str]
    resources_required: List[str]
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ActionItem:
    """Action item structure"""
    id: str
    title: str
    description: str
    owner: str
    assignees: List[str]
    priority: PriorityLevel
    status: ActionStatus
    due_date: Optional[datetime]
    estimated_effort: Optional[str]
    velocity_estimate: float
    exponential_potential: float
    dependencies: List[str]
    success_criteria: List[str]
    progress_indicators: List[str]
    resources_needed: List[str]
    risk_factors: List[str]
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class StrategicImplication:
    """Strategic implication structure"""
    id: str
    title: str
    description: str
    framework_alignment: Dict[str, float]  # SDG, Doughnut, Agreement scores
    impact_assessment: str
    opportunity_analysis: str
    risk_evaluation: str
    action_recommendations: List[str]
    timeline_considerations: str
    resource_implications: str
    success_metrics: List[str]
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class OracleOutput:
    """Complete Oracle 9.1 Protocol output"""
    id: str
    meeting_id: str
    analysis_id: str
    executive_summary: ExecutiveSummary
    decisions: List[Decision]
    actions: List[ActionItem]
    strategic_implications: List[StrategicImplication]
    discussion_dynamics: Optional['DiscussionDynamics'] = None
    human_needs_intelligence: Optional['HumanNeedsAnalysis'] = None
    narrative_development: Optional[NarrativeDevelopment] = None
    solution_portfolio: Optional[SolutionPortfolio] = None
    human_needs_fulfillment: Optional[HumanNeedsFulfillmentPlan] = None
    integrity_alignment_check: Optional[IntegrityAlignmentCheck] = None
    metadata: Dict[str, Any]
    generated_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "9.1"

class OracleOutputGenerator:
    """Generator for Oracle 9.1 Protocol structured outputs"""
    
    def __init__(self):
        # Template configurations
        self.summary_templates = self._initialize_summary_templates()
        self.decision_templates = self._initialize_decision_templates()
        self.action_templates = self._initialize_action_templates()
        self.strategic_templates = self._initialize_strategic_templates()
        
        # Analysis processors
        self.processors = {
            OutputSection.EXECUTIVE_SUMMARY: self._generate_executive_summary,
            OutputSection.DECISIONS_AGREEMENTS: self._generate_decisions_agreements,
            OutputSection.ACTION_REGISTER: self._generate_action_register,
            OutputSection.STRATEGIC_IMPLICATIONS: self._generate_strategic_implications
        }
        
        # Quality thresholds
        self.confidence_thresholds = {
            'executive_summary': 0.7,
            'decisions': 0.8,
            'actions': 0.75,
            'strategic_implications': 0.7
        }
        
        # Generated outputs cache
        self.generated_outputs = {}
    
    def _initialize_summary_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize executive summary templates"""
        return {
            'standard': {
                'structure': [
                    'meeting_overview',
                    'key_outcomes',
                    'critical_decisions',
                    'priority_actions',
                    'strategic_alignment',
                    'risk_factors',
                    'success_indicators',
                    'next_steps'
                ],
                'overview_template': "This {meeting_type} meeting involved {participant_count} participants and focused on {primary_topics}. The session lasted {duration} minutes and achieved {completion_rate}% of planned objectives.",
                'outcomes_patterns': [
                    "Key decisions made regarding {topic}",
                    "Strategic alignment achieved on {framework}",
                    "Action items identified for {area}",
                    "Risk mitigation strategies developed for {risk_area}"
                ],
                'confidence_factors': [
                    'transcript_quality',
                    'participant_engagement',
                    'decision_clarity',
                    'action_specificity'
                ]
            },
            'strategic': {
                'structure': [
                    'strategic_context',
                    'alignment_assessment',
                    'transformation_opportunities',
                    'implementation_roadmap',
                    'success_framework'
                ],
                'context_template': "This strategic session addressed {strategic_focus} with emphasis on {framework_alignment}. The discussion centered on {transformation_themes} and identified {opportunity_count} exponential opportunities.",
                'alignment_patterns': [
                    "SDG alignment score: {sdg_score}",
                    "Doughnut Economy indicators: {doughnut_score}",
                    "Agreement Economy metrics: {agreement_score}"
                ]
            },
            'operational': {
                'structure': [
                    'operational_focus',
                    'process_improvements',
                    'resource_optimization',
                    'performance_metrics',
                    'implementation_timeline'
                ],
                'focus_template': "This operational meeting addressed {operational_areas} with {improvement_count} process improvements identified and {optimization_opportunities} resource optimization opportunities."
            }
        }
    
    def _initialize_decision_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize decision tracking templates"""
        return {
            'strategic_decision': {
                'title_patterns': [
                    "Strategic Decision: {topic}",
                    "Framework Adoption: {framework}",
                    "Transformation Initiative: {initiative}"
                ],
                'rationale_template': "This decision was made based on {analysis_factors} with consideration of {stakeholder_input} and alignment with {strategic_frameworks}.",
                'implementation_template': "Implementation will proceed through {phases} phases over {timeline} with {resource_allocation} resource allocation and {success_metrics} success metrics.",
                'required_fields': [
                    'strategic_alignment',
                    'transformation_impact',
                    'resource_implications',
                    'timeline_considerations'
                ]
            },
            'operational_decision': {
                'title_patterns': [
                    "Operational Decision: {topic}",
                    "Process Change: {process}",
                    "Resource Allocation: {resource}"
                ],
                'rationale_template': "This operational decision addresses {operational_need} with expected {efficiency_gain} efficiency improvements and {cost_impact} cost implications.",
                'implementation_template': "Implementation requires {implementation_steps} with {timeline} timeline and {resource_requirements} resource requirements."
            },
            'tactical_decision': {
                'title_patterns': [
                    "Tactical Decision: {topic}",
                    "Immediate Action: {action}",
                    "Quick Resolution: {resolution}"
                ],
                'rationale_template': "This tactical decision provides immediate resolution for {immediate_need} with {quick_impact} expected impact.",
                'implementation_template': "Immediate implementation through {quick_steps} with {short_timeline} completion target."
            }
        }
    
    def _initialize_action_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize action item templates"""
        return {
            'strategic_action': {
                'title_patterns': [
                    "Strategic Action: {objective}",
                    "Framework Implementation: {framework}",
                    "Transformation Task: {transformation}"
                ],
                'description_template': "This strategic action advances {strategic_objective} through {implementation_approach} with {expected_outcomes} expected outcomes.",
                'velocity_factors': [
                    'strategic_alignment',
                    'resource_availability',
                    'stakeholder_support',
                    'complexity_level'
                ],
                'exponential_indicators': [
                    'network_effects',
                    'scalability_potential',
                    'transformation_impact',
                    'innovation_factor'
                ]
            },
            'operational_action': {
                'title_patterns': [
                    "Operational Action: {task}",
                    "Process Improvement: {process}",
                    "Efficiency Initiative: {initiative}"
                ],
                'description_template': "This operational action improves {operational_area} through {improvement_method} with {efficiency_target} efficiency target.",
                'velocity_factors': [
                    'process_complexity',
                    'resource_requirements',
                    'stakeholder_impact',
                    'implementation_risk'
                ]
            },
            'tactical_action': {
                'title_patterns': [
                    "Tactical Action: {task}",
                    "Immediate Task: {immediate}",
                    "Quick Win: {win}"
                ],
                'description_template': "This tactical action delivers {immediate_value} through {quick_implementation} with {short_term_impact} impact.",
                'velocity_factors': [
                    'task_clarity',
                    'resource_availability',
                    'implementation_simplicity'
                ]
            }
        }
    
    def _initialize_strategic_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize strategic implications templates"""
        return {
            'transformation_opportunity': {
                'title_patterns': [
                    "Transformation Opportunity: {opportunity}",
                    "Strategic Shift: {shift}",
                    "Innovation Potential: {innovation}"
                ],
                'description_template': "This transformation opportunity enables {transformation_outcome} through {strategic_approach} with {exponential_potential} exponential potential.",
                'framework_analysis': [
                    'sdg_alignment_assessment',
                    'doughnut_economy_impact',
                    'agreement_economy_benefits'
                ],
                'action_categories': [
                    'immediate_actions',
                    'medium_term_initiatives',
                    'long_term_transformations'
                ]
            },
            'risk_mitigation': {
                'title_patterns': [
                    "Risk Mitigation: {risk}",
                    "Strategic Risk: {strategic_risk}",
                    "Systemic Challenge: {challenge}"
                ],
                'description_template': "This strategic risk requires {mitigation_approach} with {prevention_measures} prevention measures and {contingency_plans} contingency planning.",
                'assessment_framework': [
                    'probability_analysis',
                    'impact_assessment',
                    'mitigation_strategies',
                    'monitoring_systems'
                ]
            },
            'alignment_enhancement': {
                'title_patterns': [
                    "Alignment Enhancement: {area}",
                    "Framework Integration: {framework}",
                    "Strategic Coherence: {coherence}"
                ],
                'description_template': "This alignment enhancement strengthens {strategic_coherence} through {integration_approach} with {synergy_benefits} synergy benefits."
            }
        }
    
    async def generate_oracle_output(self, analysis_data: Dict[str, Any], 
                                   meeting_metadata: Dict[str, Any]) -> OracleOutput:
        """
        Generate complete Oracle 9.1 Protocol output from analysis data
        """
        try:
            output_id = str(uuid.uuid4())
            meeting_id = meeting_metadata.get('meeting_id', str(uuid.uuid4()))
            analysis_id = analysis_data.get('analysis_id', str(uuid.uuid4()))
            
            logger.info("Generating Oracle 9.1 Protocol output", 
                       output_id=output_id, meeting_id=meeting_id)
            
            # Generate executive summary
            executive_summary = await self._generate_executive_summary(analysis_data, meeting_metadata)
            
            # Generate decisions and agreements
            decisions = await self._generate_decisions_agreements(analysis_data, meeting_metadata)
            
            # Generate action register
            actions = await self._generate_action_register(analysis_data, meeting_metadata)
            
            # Generate strategic implications
            strategic_implications = await self._generate_strategic_implications(analysis_data, meeting_metadata)
            
            # Generate narrative development
            narrative_development = await self._generate_narrative_development(analysis_data, meeting_metadata)
            
            # Generate solution portfolio
            solution_portfolio = await self._generate_solution_portfolio(analysis_data, meeting_metadata)
            
            # Generate human needs fulfillment plan
            human_needs_fulfillment = await self._generate_human_needs_fulfillment_plan(analysis_data, meeting_metadata)
            
            # Generate integrity alignment check
            integrity_alignment_check = await self._generate_integrity_alignment_check(analysis_data, meeting_metadata)
            
            # Create complete output
            oracle_output = OracleOutput(
                id=output_id,
                meeting_id=meeting_id,
                analysis_id=analysis_id,
                executive_summary=executive_summary,
                decisions=decisions,
                actions=actions,
                strategic_implications=strategic_implications,
                narrative_development=narrative_development,
                solution_portfolio=solution_portfolio,
                human_needs_fulfillment=human_needs_fulfillment,
                integrity_alignment_check=integrity_alignment_check,
                metadata={
                    'meeting_title': meeting_metadata.get('title', 'Untitled Meeting'),
                    'meeting_date': meeting_metadata.get('date', datetime.utcnow().isoformat()),
                    'participants': meeting_metadata.get('participants', []),
                    'duration_minutes': meeting_metadata.get('duration_minutes', 0),
                    'meeting_type': meeting_metadata.get('meeting_type', 'general'),
                    'analysis_confidence': self._calculate_overall_confidence(
                        executive_summary, decisions, actions, strategic_implications
                    ),
                    'generation_timestamp': datetime.utcnow().isoformat(),
                    'oracle_version': "9.1"
                }
            )
            
            # Cache the output
            self.generated_outputs[output_id] = oracle_output
            
            logger.info("Oracle 9.1 Protocol output generated successfully", 
                       output_id=output_id,
                       decisions_count=len(decisions),
                       actions_count=len(actions),
                       strategic_implications_count=len(strategic_implications))
            
            return oracle_output
            
        except Exception as e:
            logger.error("Oracle output generation failed", error=str(e))
            raise
    
    async def _generate_executive_summary(self, analysis_data: Dict[str, Any], 
                                        meeting_metadata: Dict[str, Any]) -> ExecutiveSummary:
        """Generate executive summary section"""
        try:
            # Determine meeting type and select appropriate template
            meeting_type = meeting_metadata.get('meeting_type', 'standard')
            template_key = 'strategic' if 'strategic' in meeting_type.lower() else 'standard'
            template = self.summary_templates[template_key]
            
            # Extract key information from analysis
            key_topics = analysis_data.get('key_topics', [])
            decisions_data = analysis_data.get('decisions', [])
            actions_data = analysis_data.get('actions', [])
            strategic_data = analysis_data.get('strategic_analysis', {})
            risks_data = analysis_data.get('risks', [])
            
            # Generate meeting overview
            meeting_overview = self._generate_meeting_overview(
                meeting_metadata, key_topics, template['overview_template']
            )
            
            # Extract key outcomes
            key_outcomes = self._extract_key_outcomes(
                analysis_data, template['outcomes_patterns']
            )
            
            # Identify critical decisions
            critical_decisions = self._identify_critical_decisions(decisions_data)
            
            # Identify priority actions
            priority_actions = self._identify_priority_actions(actions_data)
            
            # Calculate strategic alignment
            strategic_alignment = self._calculate_strategic_alignment(strategic_data)
            
            # Identify risk factors
            risk_factors = self._extract_risk_factors(risks_data, analysis_data)
            
            # Generate success indicators
            success_indicators = self._generate_success_indicators(
                decisions_data, actions_data, strategic_data
            )
            
            # Generate next steps
            next_steps = self._generate_next_steps(
                critical_decisions, priority_actions, risk_factors
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_summary_confidence(
                analysis_data, meeting_metadata, template['confidence_factors']
            )
            
            return ExecutiveSummary(
                meeting_overview=meeting_overview,
                key_outcomes=key_outcomes,
                critical_decisions=critical_decisions,
                priority_actions=priority_actions,
                strategic_alignment=strategic_alignment,
                risk_factors=risk_factors,
                success_indicators=success_indicators,
                next_steps=next_steps,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error("Executive summary generation failed", error=str(e))
            raise
    
    def _generate_meeting_overview(self, meeting_metadata: Dict[str, Any], 
                                 key_topics: List[str], template: str) -> str:
        """Generate meeting overview text"""
        try:
            participants = meeting_metadata.get('participants', [])
            duration = meeting_metadata.get('duration_minutes', 0)
            meeting_type = meeting_metadata.get('meeting_type', 'meeting')
            
            # Calculate completion rate based on objectives vs outcomes
            planned_objectives = meeting_metadata.get('planned_objectives', [])
            completion_rate = 85 if planned_objectives else 75  # Default estimate
            
            # Format primary topics
            primary_topics = ', '.join(key_topics[:3]) if key_topics else 'general discussion'
            
            overview = template.format(
                meeting_type=meeting_type,
                participant_count=len(participants),
                primary_topics=primary_topics,
                duration=duration,
                completion_rate=completion_rate
            )
            
            return overview
            
        except Exception as e:
            logger.error("Meeting overview generation failed", error=str(e))
            return "Meeting overview could not be generated due to insufficient data."
    
    def _extract_key_outcomes(self, analysis_data: Dict[str, Any], 
                            patterns: List[str]) -> List[str]:
        """Extract key outcomes from analysis data"""
        try:
            outcomes = []
            
            # Extract from decisions
            decisions = analysis_data.get('decisions', [])
            for decision in decisions[:3]:  # Top 3 decisions
                topic = decision.get('topic', decision.get('title', 'decision'))
                outcomes.append(f"Key decision made regarding {topic}")
            
            # Extract from strategic analysis
            strategic = analysis_data.get('strategic_analysis', {})
            if strategic:
                frameworks = strategic.get('framework_alignment', {})
                for framework, score in frameworks.items():
                    if score > 0.7:
                        outcomes.append(f"Strategic alignment achieved on {framework}")
            
            # Extract from actions
            actions = analysis_data.get('actions', [])
            if actions:
                action_areas = set()
                for action in actions:
                    area = action.get('category', action.get('area', 'operations'))
                    action_areas.add(area)
                
                for area in list(action_areas)[:2]:  # Top 2 areas
                    outcomes.append(f"Action items identified for {area}")
            
            # Extract from risks
            risks = analysis_data.get('risks', [])
            for risk in risks[:2]:  # Top 2 risks
                risk_area = risk.get('area', risk.get('category', 'operations'))
                outcomes.append(f"Risk mitigation strategies developed for {risk_area}")
            
            return outcomes[:6]  # Maximum 6 outcomes
            
        except Exception as e:
            logger.error("Key outcomes extraction failed", error=str(e))
            return ["Key outcomes could not be extracted from analysis data."]
    
    def _identify_critical_decisions(self, decisions_data: List[Dict[str, Any]]) -> List[str]:
        """Identify critical decisions from analysis"""
        try:
            critical_decisions = []
            
            for decision in decisions_data:
                # Check if decision is critical based on various factors
                priority = decision.get('priority', 'medium')
                impact = decision.get('impact_score', 0.5)
                urgency = decision.get('urgency', 'medium')
                
                if (priority in ['critical', 'high'] or 
                    impact > 0.7 or 
                    urgency in ['urgent', 'high']):
                    
                    title = decision.get('title', decision.get('topic', 'Untitled Decision'))
                    status = decision.get('status', 'proposed')
                    
                    critical_decisions.append(f"{title} (Status: {status})")
            
            # If no critical decisions found, include top decisions by impact
            if not critical_decisions and decisions_data:
                sorted_decisions = sorted(
                    decisions_data, 
                    key=lambda x: x.get('impact_score', 0), 
                    reverse=True
                )
                
                for decision in sorted_decisions[:3]:
                    title = decision.get('title', decision.get('topic', 'Untitled Decision'))
                    critical_decisions.append(title)
            
            return critical_decisions[:5]  # Maximum 5 critical decisions
            
        except Exception as e:
            logger.error("Critical decisions identification failed", error=str(e))
            return ["Critical decisions could not be identified from analysis data."]
    
    def _identify_priority_actions(self, actions_data: List[Dict[str, Any]]) -> List[str]:
        """Identify priority actions from analysis"""
        try:
            priority_actions = []
            
            for action in actions_data:
                # Check if action is priority based on various factors
                priority = action.get('priority', 'medium')
                urgency = action.get('urgency', 'medium')
                impact = action.get('impact_score', 0.5)
                exponential_potential = action.get('exponential_potential', 0.0)
                
                if (priority in ['critical', 'high', 'urgent'] or 
                    impact > 0.7 or 
                    exponential_potential > 0.6):
                    
                    title = action.get('title', action.get('task', 'Untitled Action'))
                    owner = action.get('owner', 'Unassigned')
                    due_date = action.get('due_date', 'TBD')
                    
                    priority_actions.append(f"{title} (Owner: {owner}, Due: {due_date})")
            
            # If no priority actions found, include top actions by impact
            if not priority_actions and actions_data:
                sorted_actions = sorted(
                    actions_data,
                    key=lambda x: x.get('impact_score', 0) + x.get('exponential_potential', 0),
                    reverse=True
                )
                
                for action in sorted_actions[:3]:
                    title = action.get('title', action.get('task', 'Untitled Action'))
                    priority_actions.append(title)
            
            return priority_actions[:5]  # Maximum 5 priority actions
            
        except Exception as e:
            logger.error("Priority actions identification failed", error=str(e))
            return ["Priority actions could not be identified from analysis data."]

    def _calculate_strategic_alignment(self, strategic_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate strategic alignment scores"""
        try:
            alignment = {}
            
            # SDG alignment
            sdg_data = strategic_data.get('sdg_alignment', {})
            if isinstance(sdg_data, dict):
                alignment['SDG'] = sdg_data.get('overall_score', 0.0)
            else:
                alignment['SDG'] = 0.0
            
            # Doughnut Economy alignment
            doughnut_data = strategic_data.get('doughnut_economy', {})
            if isinstance(doughnut_data, dict):
                regenerative = doughnut_data.get('regenerative_score', 0.0)
                distributive = doughnut_data.get('distributive_score', 0.0)
                alignment['Doughnut Economy'] = (regenerative + distributive) / 2
            else:
                alignment['Doughnut Economy'] = 0.0
            
            # Agreement Economy alignment
            agreement_data = strategic_data.get('agreement_economy', {})
            if isinstance(agreement_data, dict):
                collaboration = agreement_data.get('collaboration_score', 0.0)
                value_sharing = agreement_data.get('value_sharing_score', 0.0)
                alignment['Agreement Economy'] = (collaboration + value_sharing) / 2
            else:
                alignment['Agreement Economy'] = 0.0
            
            # Overall strategic coherence
            if alignment:
                alignment['Overall'] = sum(alignment.values()) / len(alignment)
            else:
                alignment['Overall'] = 0.0
            
            return alignment
            
        except Exception as e:
            logger.error("Strategic alignment calculation failed", error=str(e))
            return {'SDG': 0.0, 'Doughnut Economy': 0.0, 'Agreement Economy': 0.0, 'Overall': 0.0}
    
    def _extract_risk_factors(self, risks_data: List[Dict[str, Any]], 
                            analysis_data: Dict[str, Any]) -> List[str]:
        """Extract risk factors from analysis"""
        try:
            risk_factors = []
            
            # Extract from explicit risks
            for risk in risks_data:
                risk_description = risk.get('description', risk.get('title', 'Unspecified risk'))
                probability = risk.get('probability', 'medium')
                impact = risk.get('impact', 'medium')
                
                if probability in ['high', 'critical'] or impact in ['high', 'critical']:
                    risk_factors.append(f"{risk_description} (Probability: {probability}, Impact: {impact})")
            
            # Extract from decision risks
            decisions = analysis_data.get('decisions', [])
            for decision in decisions:
                decision_risks = decision.get('risks', [])
                for risk in decision_risks[:2]:  # Top 2 risks per decision
                    risk_factors.append(f"Decision risk: {risk}")
            
            # Extract from action risks
            actions = analysis_data.get('actions', [])
            for action in actions:
                action_risks = action.get('risks', [])
                for risk in action_risks[:1]:  # Top risk per action
                    risk_factors.append(f"Implementation risk: {risk}")
            
            # Extract from strategic risks
            strategic = analysis_data.get('strategic_analysis', {})
            strategic_risks = strategic.get('risks', [])
            for risk in strategic_risks[:2]:
                risk_factors.append(f"Strategic risk: {risk}")
            
            return risk_factors[:6]  # Maximum 6 risk factors
            
        except Exception as e:
            logger.error("Risk factors extraction failed", error=str(e))
            return ["Risk factors could not be extracted from analysis data."]
    
    def _generate_success_indicators(self, decisions_data: List[Dict[str, Any]], 
                                   actions_data: List[Dict[str, Any]], 
                                   strategic_data: Dict[str, Any]) -> List[str]:
        """Generate success indicators"""
        try:
            indicators = []
            
            # Decision success indicators
            for decision in decisions_data[:3]:
                success_criteria = decision.get('success_criteria', [])
                for criterion in success_criteria[:2]:
                    indicators.append(f"Decision success: {criterion}")
            
            # Action success indicators
            for action in actions_data[:3]:
                success_criteria = action.get('success_criteria', [])
                for criterion in success_criteria[:1]:
                    indicators.append(f"Action success: {criterion}")
            
            # Strategic success indicators
            strategic_metrics = strategic_data.get('success_metrics', [])
            for metric in strategic_metrics[:2]:
                indicators.append(f"Strategic success: {metric}")
            
            # General success indicators
            if not indicators:
                indicators = [
                    "All critical decisions implemented successfully",
                    "Priority actions completed on schedule",
                    "Strategic alignment maintained above 70%",
                    "Risk mitigation measures effective"
                ]
            
            return indicators[:5]  # Maximum 5 success indicators
            
        except Exception as e:
            logger.error("Success indicators generation failed", error=str(e))
            return ["Success indicators could not be generated from analysis data."]
    
    def _generate_next_steps(self, critical_decisions: List[str], 
                           priority_actions: List[str], 
                           risk_factors: List[str]) -> List[str]:
        """Generate next steps"""
        try:
            next_steps = []
            
            # Decision-based next steps
            if critical_decisions:
                next_steps.append(f"Finalize implementation plans for {len(critical_decisions)} critical decisions")
            
            # Action-based next steps
            if priority_actions:
                next_steps.append(f"Begin execution of {len(priority_actions)} priority actions")
            
            # Risk-based next steps
            if risk_factors:
                next_steps.append(f"Implement mitigation strategies for {len(risk_factors)} identified risks")
            
            # Standard next steps
            next_steps.extend([
                "Schedule follow-up meeting to review progress",
                "Communicate outcomes to relevant stakeholders",
                "Update project tracking systems with new actions"
            ])
            
            return next_steps[:5]  # Maximum 5 next steps
            
        except Exception as e:
            logger.error("Next steps generation failed", error=str(e))
            return ["Next steps could not be generated from analysis data."]
    
    def _calculate_summary_confidence(self, analysis_data: Dict[str, Any], 
                                    meeting_metadata: Dict[str, Any], 
                                    confidence_factors: List[str]) -> float:
        """Calculate executive summary confidence score"""
        try:
            confidence_scores = []
            
            # Transcript quality factor
            transcript_quality = analysis_data.get('transcript_quality', 0.7)
            confidence_scores.append(transcript_quality)
            
            # Participant engagement factor
            participants = meeting_metadata.get('participants', [])
            engagement_score = min(len(participants) / 10, 1.0)  # Normalize to 1.0
            confidence_scores.append(engagement_score)
            
            # Decision clarity factor
            decisions = analysis_data.get('decisions', [])
            decision_clarity = sum(d.get('confidence', 0.5) for d in decisions) / max(len(decisions), 1)
            confidence_scores.append(decision_clarity)
            
            # Action specificity factor
            actions = analysis_data.get('actions', [])
            action_specificity = sum(a.get('specificity_score', 0.5) for a in actions) / max(len(actions), 1)
            confidence_scores.append(action_specificity)
            
            # Overall confidence
            overall_confidence = sum(confidence_scores) / len(confidence_scores)
            
            return min(max(overall_confidence, 0.0), 1.0)  # Clamp between 0 and 1
            
        except Exception as e:
            logger.error("Summary confidence calculation failed", error=str(e))
            return 0.7  # Default confidence
    
    async def _generate_decisions_agreements(self, analysis_data: Dict[str, Any], 
                                           meeting_metadata: Dict[str, Any]) -> List[Decision]:
        """Generate decisions and agreements section"""
        try:
            decisions = []
            decisions_data = analysis_data.get('decisions', [])
            
            for i, decision_data in enumerate(decisions_data):
                # Determine decision type and template
                decision_type = self._classify_decision_type(decision_data)
                template = self.decision_templates.get(decision_type, self.decision_templates['operational_decision'])
                
                # Generate decision ID
                decision_id = decision_data.get('id', f"decision_{i+1}")
                
                # Generate title
                title = self._generate_decision_title(decision_data, template)
                
                # Extract basic information
                description = decision_data.get('description', decision_data.get('summary', ''))
                decision_maker = decision_data.get('decision_maker', decision_data.get('owner', 'TBD'))
                stakeholders = decision_data.get('stakeholders', decision_data.get('affected_parties', []))
                
                # Determine priority
                priority = self._determine_decision_priority(decision_data)
                
                # Determine status
                status = self._determine_decision_status(decision_data)
                
                # Generate rationale
                rationale = self._generate_decision_rationale(decision_data, template)
                
                # Generate implementation plan
                implementation_plan = self._generate_implementation_plan(decision_data, template)
                
                # Extract success criteria
                success_criteria = decision_data.get('success_criteria', [])
                if not success_criteria:
                    success_criteria = self._generate_success_criteria(decision_data)
                
                # Generate risk assessment
                risk_assessment = self._generate_risk_assessment(decision_data)
                
                # Generate impact analysis
                impact_analysis = self._generate_impact_analysis(decision_data)
                
                # Generate timeline
                timeline = self._generate_decision_timeline(decision_data)
                
                # Extract dependencies and resources
                dependencies = decision_data.get('dependencies', [])
                resources_required = decision_data.get('resources_required', decision_data.get('resources', []))
                
                # Calculate confidence score
                confidence_score = decision_data.get('confidence', 0.8)
                
                decision = Decision(
                    id=decision_id,
                    title=title,
                    description=description,
                    decision_maker=decision_maker,
                    stakeholders=stakeholders,
                    priority=priority,
                    status=status,
                    rationale=rationale,
                    implementation_plan=implementation_plan,
                    success_criteria=success_criteria,
                    risk_assessment=risk_assessment,
                    impact_analysis=impact_analysis,
                    timeline=timeline,
                    dependencies=dependencies,
                    resources_required=resources_required,
                    confidence_score=confidence_score
                )
                
                decisions.append(decision)
            
            return decisions
            
        except Exception as e:
            logger.error("Decisions generation failed", error=str(e))
            return []
    
    def _classify_decision_type(self, decision_data: Dict[str, Any]) -> str:
        """Classify decision type for template selection"""
        try:
            # Check for strategic indicators
            strategic_keywords = ['strategic', 'framework', 'transformation', 'vision', 'mission']
            decision_text = f"{decision_data.get('title', '')} {decision_data.get('description', '')}".lower()
            
            if any(keyword in decision_text for keyword in strategic_keywords):
                return 'strategic_decision'
            
            # Check for tactical indicators
            tactical_keywords = ['immediate', 'quick', 'urgent', 'now', 'today']
            if any(keyword in decision_text for keyword in tactical_keywords):
                return 'tactical_decision'
            
            # Default to operational
            return 'operational_decision'
            
        except Exception as e:
            logger.error("Decision type classification failed", error=str(e))
            return 'operational_decision'
    
    def _generate_decision_title(self, decision_data: Dict[str, Any], 
                               template: Dict[str, Any]) -> str:
        """Generate decision title using template"""
        try:
            existing_title = decision_data.get('title', decision_data.get('topic'))
            if existing_title:
                return existing_title
            
            # Use template patterns
            patterns = template.get('title_patterns', [])
            if patterns:
                pattern = patterns[0]  # Use first pattern
                topic = decision_data.get('topic', decision_data.get('area', 'General'))
                return pattern.format(topic=topic)
            
            return "Decision: TBD"
            
        except Exception as e:
            logger.error("Decision title generation failed", error=str(e))
            return "Decision: TBD"
    
    def _determine_decision_priority(self, decision_data: Dict[str, Any]) -> PriorityLevel:
        """Determine decision priority level"""
        try:
            # Check explicit priority
            priority_str = decision_data.get('priority', '').lower()
            if priority_str in ['critical', 'urgent']:
                return PriorityLevel.CRITICAL
            elif priority_str in ['high', 'important']:
                return PriorityLevel.HIGH
            elif priority_str in ['medium', 'moderate']:
                return PriorityLevel.MEDIUM
            elif priority_str in ['low', 'minor']:
                return PriorityLevel.LOW
            
            # Determine from impact and urgency
            impact = decision_data.get('impact_score', 0.5)
            urgency = decision_data.get('urgency_score', 0.5)
            
            combined_score = (impact + urgency) / 2
            
            if combined_score >= 0.8:
                return PriorityLevel.CRITICAL
            elif combined_score >= 0.6:
                return PriorityLevel.HIGH
            elif combined_score >= 0.4:
                return PriorityLevel.MEDIUM
            else:
                return PriorityLevel.LOW
                
        except Exception as e:
            logger.error("Decision priority determination failed", error=str(e))
            return PriorityLevel.MEDIUM
    
    def _determine_decision_status(self, decision_data: Dict[str, Any]) -> DecisionStatus:
        """Determine decision status"""
        try:
            status_str = decision_data.get('status', '').lower()
            
            status_mapping = {
                'proposed': DecisionStatus.PROPOSED,
                'approved': DecisionStatus.APPROVED,
                'in_progress': DecisionStatus.IN_PROGRESS,
                'in progress': DecisionStatus.IN_PROGRESS,
                'implemented': DecisionStatus.IMPLEMENTED,
                'complete': DecisionStatus.IMPLEMENTED,
                'completed': DecisionStatus.IMPLEMENTED,
                'rejected': DecisionStatus.REJECTED,
                'on_hold': DecisionStatus.ON_HOLD,
                'on hold': DecisionStatus.ON_HOLD,
                'paused': DecisionStatus.ON_HOLD
            }
            
            return status_mapping.get(status_str, DecisionStatus.PROPOSED)
            
        except Exception as e:
            logger.error("Decision status determination failed", error=str(e))
            return DecisionStatus.PROPOSED
    
    def _generate_decision_rationale(self, decision_data: Dict[str, Any], 
                                   template: Dict[str, Any]) -> str:
        """Generate decision rationale"""
        try:
            existing_rationale = decision_data.get('rationale', decision_data.get('reasoning'))
            if existing_rationale:
                return existing_rationale
            
            # Use template
            rationale_template = template.get('rationale_template', '')
            if rationale_template:
                analysis_factors = decision_data.get('analysis_factors', ['data analysis', 'stakeholder input'])
                stakeholder_input = decision_data.get('stakeholder_input', 'team discussion')
                strategic_frameworks = decision_data.get('strategic_frameworks', ['organizational goals'])
                
                return rationale_template.format(
                    analysis_factors=', '.join(analysis_factors),
                    stakeholder_input=stakeholder_input,
                    strategic_frameworks=', '.join(strategic_frameworks)
                )
            
            return "Rationale to be documented."
            
        except Exception as e:
            logger.error("Decision rationale generation failed", error=str(e))
            return "Rationale to be documented."
    
    def _generate_implementation_plan(self, decision_data: Dict[str, Any], 
                                    template: Dict[str, Any]) -> str:
        """Generate implementation plan"""
        try:
            existing_plan = decision_data.get('implementation_plan', decision_data.get('plan'))
            if existing_plan:
                return existing_plan
            
            # Use template
            implementation_template = template.get('implementation_template', '')
            if implementation_template:
                phases = decision_data.get('phases', ['planning', 'execution', 'review'])
                timeline = decision_data.get('timeline', 'TBD')
                resource_allocation = decision_data.get('resource_allocation', 'standard')
                success_metrics = decision_data.get('success_metrics', ['completion', 'quality'])
                
                return implementation_template.format(
                    phases=', '.join(phases),
                    timeline=timeline,
                    resource_allocation=resource_allocation,
                    success_metrics=', '.join(success_metrics)
                )
            
            return "Implementation plan to be developed."
            
        except Exception as e:
            logger.error("Implementation plan generation failed", error=str(e))
            return "Implementation plan to be developed."
    
    def _generate_success_criteria(self, decision_data: Dict[str, Any]) -> List[str]:
        """Generate success criteria for decision"""
        try:
            criteria = []
            
            # Add objective-based criteria
            objectives = decision_data.get('objectives', [])
            for objective in objectives:
                criteria.append(f"Achievement of {objective}")
            
            # Add metric-based criteria
            metrics = decision_data.get('metrics', [])
            for metric in metrics:
                criteria.append(f"Improvement in {metric}")
            
            # Add default criteria if none found
            if not criteria:
                criteria = [
                    "Decision implemented successfully",
                    "Stakeholder acceptance achieved",
                    "Expected outcomes realized"
                ]
            
            return criteria[:5]  # Maximum 5 criteria
            
        except Exception as e:
            logger.error("Success criteria generation failed", error=str(e))
            return ["Success criteria to be defined."]
    
    def _generate_risk_assessment(self, decision_data: Dict[str, Any]) -> str:
        """Generate risk assessment for decision"""
        try:
            risks = decision_data.get('risks', [])
            if risks:
                risk_descriptions = []
                for risk in risks:
                    if isinstance(risk, dict):
                        desc = risk.get('description', str(risk))
                        probability = risk.get('probability', 'medium')
                        impact = risk.get('impact', 'medium')
                        risk_descriptions.append(f"{desc} (Probability: {probability}, Impact: {impact})")
                    else:
                        risk_descriptions.append(str(risk))
                
                return "Key risks identified: " + "; ".join(risk_descriptions)
            
            # Generate generic risk assessment
            return "Standard implementation risks apply. Mitigation strategies to be developed."
            
        except Exception as e:
            logger.error("Risk assessment generation failed", error=str(e))
            return "Risk assessment to be completed."
    
    def _generate_impact_analysis(self, decision_data: Dict[str, Any]) -> str:
        """Generate impact analysis for decision"""
        try:
            impact_data = decision_data.get('impact_analysis', {})
            if impact_data:
                analysis_parts = []
                
                for area, impact in impact_data.items():
                    if isinstance(impact, dict):
                        level = impact.get('level', 'medium')
                        description = impact.get('description', '')
                        analysis_parts.append(f"{area}: {level} impact - {description}")
                    else:
                        analysis_parts.append(f"{area}: {impact}")
                
                return "Impact analysis: " + "; ".join(analysis_parts)
            
            # Generate basic impact analysis
            impact_score = decision_data.get('impact_score', 0.5)
            if impact_score > 0.7:
                return "High impact decision with significant organizational implications."
            elif impact_score > 0.4:
                return "Medium impact decision with moderate organizational effects."
            else:
                return "Low impact decision with limited organizational effects."
                
        except Exception as e:
            logger.error("Impact analysis generation failed", error=str(e))
            return "Impact analysis to be completed."
    
    def _generate_decision_timeline(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate decision timeline"""
        try:
            timeline = decision_data.get('timeline', {})
            if timeline:
                return timeline
            
            # Generate basic timeline
            return {
                'decision_date': datetime.utcnow().isoformat(),
                'implementation_start': (datetime.utcnow() + timedelta(days=7)).isoformat(),
                'target_completion': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                'review_date': (datetime.utcnow() + timedelta(days=45)).isoformat()
            }
            
        except Exception as e:
            logger.error("Decision timeline generation failed", error=str(e))
            return {'status': 'Timeline to be determined'}
    
    def _calculate_overall_confidence(self, executive_summary: ExecutiveSummary,
                                    decisions: List[Decision],
                                    actions: List[ActionItem],
                                    strategic_implications: List[StrategicImplication]) -> float:
        """Calculate overall confidence score for the output"""
        try:
            confidence_scores = [executive_summary.confidence_score]
            
            # Add decision confidences
            if decisions:
                decision_confidence = sum(d.confidence_score for d in decisions) / len(decisions)
                confidence_scores.append(decision_confidence)
            
            # Add action confidences
            if actions:
                action_confidence = sum(a.confidence_score for a in actions) / len(actions)
                confidence_scores.append(action_confidence)
            
            # Add strategic confidences
            if strategic_implications:
                strategic_confidence = sum(s.confidence_score for s in strategic_implications) / len(strategic_implications)
                confidence_scores.append(strategic_confidence)
            
            return sum(confidence_scores) / len(confidence_scores)
            
        except Exception as e:
            logger.error("Overall confidence calculation failed", error=str(e))
            return 0.7

    async def _generate_action_register(self, analysis_data: Dict[str, Any], 
                                      meeting_metadata: Dict[str, Any]) -> List[ActionItem]:
        """Generate action register section"""
        try:
            actions = []
            actions_data = analysis_data.get('actions', [])
            
            for i, action_data in enumerate(actions_data):
                # Determine action type and template
                action_type = self._classify_action_type(action_data)
                template = self.action_templates.get(action_type, self.action_templates['operational_action'])
                
                # Generate action ID
                action_id = action_data.get('id', f"action_{i+1}")
                
                # Generate title
                title = self._generate_action_title(action_data, template)
                
                # Generate description
                description = self._generate_action_description(action_data, template)
                
                # Extract ownership information
                owner = action_data.get('owner', action_data.get('assignee', 'TBD'))
                assignees = action_data.get('assignees', action_data.get('team', []))
                if isinstance(assignees, str):
                    assignees = [assignees]
                
                # Determine priority
                priority = self._determine_action_priority(action_data)
                
                # Determine status
                status = self._determine_action_status(action_data)
                
                # Extract timing information
                due_date = self._parse_due_date(action_data.get('due_date'))
                estimated_effort = action_data.get('estimated_effort', action_data.get('effort'))
                
                # Calculate velocity estimate
                velocity_estimate = self._calculate_velocity_estimate(action_data, template)
                
                # Calculate exponential potential
                exponential_potential = self._calculate_exponential_potential(action_data, template)
                
                # Extract dependencies and criteria
                dependencies = action_data.get('dependencies', [])
                success_criteria = action_data.get('success_criteria', [])
                if not success_criteria:
                    success_criteria = self._generate_action_success_criteria(action_data)
                
                # Generate progress indicators
                progress_indicators = self._generate_progress_indicators(action_data)
                
                # Extract resources and risks
                resources_needed = action_data.get('resources_needed', action_data.get('resources', []))
                risk_factors = action_data.get('risk_factors', action_data.get('risks', []))
                
                # Calculate confidence score
                confidence_score = action_data.get('confidence', 0.75)
                
                action = ActionItem(
                    id=action_id,
                    title=title,
                    description=description,
                    owner=owner,
                    assignees=assignees,
                    priority=priority,
                    status=status,
                    due_date=due_date,
                    estimated_effort=estimated_effort,
                    velocity_estimate=velocity_estimate,
                    exponential_potential=exponential_potential,
                    dependencies=dependencies,
                    success_criteria=success_criteria,
                    progress_indicators=progress_indicators,
                    resources_needed=resources_needed,
                    risk_factors=risk_factors,
                    confidence_score=confidence_score
                )
                
                actions.append(action)
            
            return actions
            
        except Exception as e:
            logger.error("Action register generation failed", error=str(e))
            return []
    
    def _classify_action_type(self, action_data: Dict[str, Any]) -> str:
        """Classify action type for template selection"""
        try:
            # Check for strategic indicators
            strategic_keywords = ['strategic', 'framework', 'transformation', 'long-term', 'vision']
            action_text = f"{action_data.get('title', '')} {action_data.get('description', '')}".lower()
            
            if any(keyword in action_text for keyword in strategic_keywords):
                return 'strategic_action'
            
            # Check for tactical indicators
            tactical_keywords = ['immediate', 'quick', 'urgent', 'today', 'asap']
            if any(keyword in action_text for keyword in tactical_keywords):
                return 'tactical_action'
            
            # Default to operational
            return 'operational_action'
            
        except Exception as e:
            logger.error("Action type classification failed", error=str(e))
            return 'operational_action'
    
    def _generate_action_title(self, action_data: Dict[str, Any], 
                             template: Dict[str, Any]) -> str:
        """Generate action title using template"""
        try:
            existing_title = action_data.get('title', action_data.get('task'))
            if existing_title:
                return existing_title
            
            # Use template patterns
            patterns = template.get('title_patterns', [])
            if patterns:
                pattern = patterns[0]  # Use first pattern
                objective = action_data.get('objective', action_data.get('goal', 'TBD'))
                return pattern.format(objective=objective)
            
            return "Action: TBD"
            
        except Exception as e:
            logger.error("Action title generation failed", error=str(e))
            return "Action: TBD"
    
    def _generate_action_description(self, action_data: Dict[str, Any], 
                                   template: Dict[str, Any]) -> str:
        """Generate action description using template"""
        try:
            existing_description = action_data.get('description', action_data.get('details'))
            if existing_description:
                return existing_description
            
            # Use template
            description_template = template.get('description_template', '')
            if description_template:
                objective = action_data.get('objective', 'specified objective')
                approach = action_data.get('approach', 'defined approach')
                outcomes = action_data.get('expected_outcomes', ['positive results'])
                
                return description_template.format(
                    strategic_objective=objective,
                    implementation_approach=approach,
                    expected_outcomes=', '.join(outcomes) if isinstance(outcomes, list) else outcomes
                )
            
            return "Action description to be provided."
            
        except Exception as e:
            logger.error("Action description generation failed", error=str(e))
            return "Action description to be provided."
    
    def _determine_action_priority(self, action_data: Dict[str, Any]) -> PriorityLevel:
        """Determine action priority level"""
        try:
            # Check explicit priority
            priority_str = action_data.get('priority', '').lower()
            if priority_str in ['critical', 'urgent']:
                return PriorityLevel.CRITICAL
            elif priority_str in ['high', 'important']:
                return PriorityLevel.HIGH
            elif priority_str in ['medium', 'moderate']:
                return PriorityLevel.MEDIUM
            elif priority_str in ['low', 'minor']:
                return PriorityLevel.LOW
            
            # Determine from impact and urgency
            impact = action_data.get('impact_score', 0.5)
            urgency = action_data.get('urgency_score', 0.5)
            exponential_potential = action_data.get('exponential_potential', 0.0)
            
            combined_score = (impact + urgency + exponential_potential) / 3
            
            if combined_score >= 0.8:
                return PriorityLevel.CRITICAL
            elif combined_score >= 0.6:
                return PriorityLevel.HIGH
            elif combined_score >= 0.4:
                return PriorityLevel.MEDIUM
            else:
                return PriorityLevel.LOW
                
        except Exception as e:
            logger.error("Action priority determination failed", error=str(e))
            return PriorityLevel.MEDIUM
    
    def _determine_action_status(self, action_data: Dict[str, Any]) -> ActionStatus:
        """Determine action status"""
        try:
            status_str = action_data.get('status', '').lower()
            
            status_mapping = {
                'not_started': ActionStatus.NOT_STARTED,
                'not started': ActionStatus.NOT_STARTED,
                'new': ActionStatus.NOT_STARTED,
                'in_progress': ActionStatus.IN_PROGRESS,
                'in progress': ActionStatus.IN_PROGRESS,
                'active': ActionStatus.IN_PROGRESS,
                'working': ActionStatus.IN_PROGRESS,
                'blocked': ActionStatus.BLOCKED,
                'stuck': ActionStatus.BLOCKED,
                'waiting': ActionStatus.BLOCKED,
                'completed': ActionStatus.COMPLETED,
                'complete': ActionStatus.COMPLETED,
                'done': ActionStatus.COMPLETED,
                'finished': ActionStatus.COMPLETED,
                'cancelled': ActionStatus.CANCELLED,
                'canceled': ActionStatus.CANCELLED,
                'dropped': ActionStatus.CANCELLED
            }
            
            return status_mapping.get(status_str, ActionStatus.NOT_STARTED)
            
        except Exception as e:
            logger.error("Action status determination failed", error=str(e))
            return ActionStatus.NOT_STARTED
    
    def _parse_due_date(self, due_date_str: Any) -> Optional[datetime]:
        """Parse due date from various formats"""
        try:
            if not due_date_str:
                return None
            
            if isinstance(due_date_str, datetime):
                return due_date_str
            
            if isinstance(due_date_str, str):
                # Try common date formats
                formats = [
                    '%Y-%m-%d',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d %H:%M:%S',
                    '%m/%d/%Y',
                    '%d/%m/%Y'
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(due_date_str, fmt)
                    except ValueError:
                        continue
            
            return None
            
        except Exception as e:
            logger.error("Due date parsing failed", error=str(e))
            return None
    
    def _calculate_velocity_estimate(self, action_data: Dict[str, Any], 
                                   template: Dict[str, Any]) -> float:
        """Calculate velocity estimate for action"""
        try:
            # Check for explicit velocity
            explicit_velocity = action_data.get('velocity_estimate', action_data.get('velocity'))
            if explicit_velocity is not None:
                return float(explicit_velocity)
            
            # Calculate based on factors
            velocity_factors = template.get('velocity_factors', [])
            factor_scores = []
            
            for factor in velocity_factors:
                if factor == 'strategic_alignment':
                    score = action_data.get('strategic_alignment', 0.5)
                elif factor == 'resource_availability':
                    score = action_data.get('resource_availability', 0.7)
                elif factor == 'stakeholder_support':
                    score = action_data.get('stakeholder_support', 0.6)
                elif factor == 'complexity_level':
                    complexity = action_data.get('complexity', 0.5)
                    score = 1.0 - complexity  # Invert complexity
                elif factor == 'process_complexity':
                    complexity = action_data.get('process_complexity', 0.5)
                    score = 1.0 - complexity
                elif factor == 'task_clarity':
                    score = action_data.get('task_clarity', 0.7)
                elif factor == 'implementation_simplicity':
                    score = action_data.get('implementation_simplicity', 0.6)
                else:
                    score = 0.6  # Default score
                
                factor_scores.append(score)
            
            # Calculate weighted average
            if factor_scores:
                velocity = sum(factor_scores) / len(factor_scores)
            else:
                velocity = 0.6  # Default velocity
            
            return min(max(velocity, 0.0), 1.0)  # Clamp between 0 and 1
            
        except Exception as e:
            logger.error("Velocity estimate calculation failed", error=str(e))
            return 0.6  # Default velocity
    
    def _calculate_exponential_potential(self, action_data: Dict[str, Any], 
                                       template: Dict[str, Any]) -> float:
        """Calculate exponential potential for action"""
        try:
            # Check for explicit exponential potential
            explicit_potential = action_data.get('exponential_potential')
            if explicit_potential is not None:
                return float(explicit_potential)
            
            # Calculate based on exponential indicators
            exponential_indicators = template.get('exponential_indicators', [])
            indicator_scores = []
            
            for indicator in exponential_indicators:
                if indicator == 'network_effects':
                    score = action_data.get('network_effects', 0.3)
                elif indicator == 'scalability_potential':
                    score = action_data.get('scalability_potential', 0.4)
                elif indicator == 'transformation_impact':
                    score = action_data.get('transformation_impact', 0.3)
                elif indicator == 'innovation_factor':
                    score = action_data.get('innovation_factor', 0.2)
                else:
                    score = 0.3  # Default score
                
                indicator_scores.append(score)
            
            # Calculate weighted average
            if indicator_scores:
                potential = sum(indicator_scores) / len(indicator_scores)
            else:
                # Estimate based on other factors
                impact = action_data.get('impact_score', 0.5)
                innovation = action_data.get('innovation_level', 0.3)
                scalability = action_data.get('scalability', 0.4)
                potential = (impact + innovation + scalability) / 3
            
            return min(max(potential, 0.0), 1.0)  # Clamp between 0 and 1
            
        except Exception as e:
            logger.error("Exponential potential calculation failed", error=str(e))
            return 0.3  # Default potential
    
    def _generate_action_success_criteria(self, action_data: Dict[str, Any]) -> List[str]:
        """Generate success criteria for action"""
        try:
            criteria = []
            
            # Add objective-based criteria
            objectives = action_data.get('objectives', [])
            for objective in objectives:
                criteria.append(f"Achievement of {objective}")
            
            # Add deliverable-based criteria
            deliverables = action_data.get('deliverables', [])
            for deliverable in deliverables:
                criteria.append(f"Completion of {deliverable}")
            
            # Add metric-based criteria
            metrics = action_data.get('success_metrics', [])
            for metric in metrics:
                criteria.append(f"Target achieved for {metric}")
            
            # Add default criteria if none found
            if not criteria:
                criteria = [
                    "Action completed on time",
                    "Quality standards met",
                    "Stakeholder satisfaction achieved"
                ]
            
            return criteria[:5]  # Maximum 5 criteria
            
        except Exception as e:
            logger.error("Action success criteria generation failed", error=str(e))
            return ["Success criteria to be defined."]
    
    def _generate_progress_indicators(self, action_data: Dict[str, Any]) -> List[str]:
        """Generate progress indicators for action"""
        try:
            indicators = []
            
            # Add milestone-based indicators
            milestones = action_data.get('milestones', [])
            for milestone in milestones:
                indicators.append(f"Milestone: {milestone}")
            
            # Add deliverable-based indicators
            deliverables = action_data.get('deliverables', [])
            for deliverable in deliverables:
                indicators.append(f"Deliverable: {deliverable}")
            
            # Add default indicators if none found
            if not indicators:
                indicators = [
                    "Planning phase completed",
                    "Implementation started",
                    "Progress review conducted",
                    "Final deliverable completed"
                ]
            
            return indicators[:6]  # Maximum 6 indicators
            
        except Exception as e:
            logger.error("Progress indicators generation failed", error=str(e))
            return ["Progress indicators to be defined."]
    
    async def _generate_strategic_implications(self, analysis_data: Dict[str, Any], 
                                             meeting_metadata: Dict[str, Any]) -> List[StrategicImplication]:
        """Generate strategic implications section"""
        try:
            implications = []
            strategic_data = analysis_data.get('strategic_analysis', {})
            
            # Generate transformation opportunities
            opportunities = strategic_data.get('opportunities', [])
            for i, opportunity in enumerate(opportunities):
                implication = await self._create_strategic_implication(
                    opportunity, 'transformation_opportunity', f"strategic_opp_{i+1}"
                )
                implications.append(implication)
            
            # Generate risk implications
            risks = strategic_data.get('strategic_risks', [])
            for i, risk in enumerate(risks):
                implication = await self._create_strategic_implication(
                    risk, 'risk_mitigation', f"strategic_risk_{i+1}"
                )
                implications.append(implication)
            
            # Generate alignment implications
            alignment_data = strategic_data.get('alignment_analysis', {})
            if alignment_data:
                implication = await self._create_alignment_implication(alignment_data)
                implications.append(implication)
            
            return implications
            
        except Exception as e:
            logger.error("Strategic implications generation failed", error=str(e))
            return []
    
    async def _create_strategic_implication(self, data: Dict[str, Any], 
                                         implication_type: str, 
                                         implication_id: str) -> StrategicImplication:
        """Create a strategic implication from data"""
        try:
            template = self.strategic_templates.get(implication_type, {})
            
            # Generate title
            title = self._generate_strategic_title(data, template)
            
            # Generate description
            description = self._generate_strategic_description(data, template)
            
            # Calculate framework alignment
            framework_alignment = self._calculate_framework_alignment(data)
            
            # Generate assessments
            impact_assessment = self._generate_impact_assessment(data)
            opportunity_analysis = self._generate_opportunity_analysis(data)
            risk_evaluation = self._generate_risk_evaluation(data)
            
            # Generate recommendations
            action_recommendations = self._generate_action_recommendations(data, template)
            
            # Generate considerations
            timeline_considerations = self._generate_timeline_considerations(data)
            resource_implications = self._generate_resource_implications(data)
            
            # Generate success metrics
            success_metrics = self._generate_strategic_success_metrics(data)
            
            # Calculate confidence
            confidence_score = data.get('confidence', 0.7)
            
            return StrategicImplication(
                id=implication_id,
                title=title,
                description=description,
                framework_alignment=framework_alignment,
                impact_assessment=impact_assessment,
                opportunity_analysis=opportunity_analysis,
                risk_evaluation=risk_evaluation,
                action_recommendations=action_recommendations,
                timeline_considerations=timeline_considerations,
                resource_implications=resource_implications,
                success_metrics=success_metrics,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error("Strategic implication creation failed", error=str(e))
            return StrategicImplication(
                id=implication_id,
                title="Strategic Implication",
                description="Strategic implication details to be determined.",
                framework_alignment={},
                impact_assessment="Impact assessment pending.",
                opportunity_analysis="Opportunity analysis pending.",
                risk_evaluation="Risk evaluation pending.",
                action_recommendations=[],
                timeline_considerations="Timeline to be determined.",
                resource_implications="Resource implications to be assessed.",
                success_metrics=[],
                confidence_score=0.5
            )
    
    async def _create_alignment_implication(self, alignment_data: Dict[str, Any]) -> StrategicImplication:
        """Create strategic implication for alignment enhancement"""
        try:
            return StrategicImplication(
                id="alignment_enhancement",
                title="Strategic Alignment Enhancement",
                description="Opportunities to strengthen strategic coherence across frameworks.",
                framework_alignment=alignment_data.get('current_alignment', {}),
                impact_assessment="Enhanced alignment will improve strategic coherence and execution effectiveness.",
                opportunity_analysis="Integration opportunities identified across SDG, Doughnut Economy, and Agreement Economy frameworks.",
                risk_evaluation="Misalignment risks mitigated through systematic integration approach.",
                action_recommendations=[
                    "Develop integrated framework dashboard",
                    "Establish cross-framework success metrics",
                    "Create alignment monitoring system"
                ],
                timeline_considerations="Alignment enhancement can be achieved over 3-6 months with proper coordination.",
                resource_implications="Requires dedicated strategic coordination resources and framework expertise.",
                success_metrics=[
                    "Framework alignment scores above 80%",
                    "Strategic coherence index improvement",
                    "Cross-framework synergy realization"
                ],
                confidence_score=0.8
            )
            
        except Exception as e:
            logger.error("Alignment implication creation failed", error=str(e))
            return StrategicImplication(
                id="alignment_enhancement",
                title="Strategic Alignment Enhancement",
                description="Alignment enhancement details to be determined.",
                framework_alignment={},
                impact_assessment="Impact assessment pending.",
                opportunity_analysis="Opportunity analysis pending.",
                risk_evaluation="Risk evaluation pending.",
                action_recommendations=[],
                timeline_considerations="Timeline to be determined.",
                resource_implications="Resource implications to be assessed.",
                success_metrics=[],
                confidence_score=0.5
            )
    
    def _generate_strategic_title(self, data: Dict[str, Any], template: Dict[str, Any]) -> str:
        """Generate strategic implication title"""
        try:
            existing_title = data.get('title', data.get('name'))
            if existing_title:
                return existing_title
            
            patterns = template.get('title_patterns', [])
            if patterns:
                pattern = patterns[0]
                opportunity = data.get('opportunity', data.get('topic', 'Strategic Initiative'))
                return pattern.format(opportunity=opportunity)
            
            return "Strategic Implication"
            
        except Exception as e:
            logger.error("Strategic title generation failed", error=str(e))
            return "Strategic Implication"
    
    def _generate_strategic_description(self, data: Dict[str, Any], template: Dict[str, Any]) -> str:
        """Generate strategic implication description"""
        try:
            existing_description = data.get('description', data.get('summary'))
            if existing_description:
                return existing_description
            
            description_template = template.get('description_template', '')
            if description_template:
                outcome = data.get('transformation_outcome', 'strategic transformation')
                approach = data.get('strategic_approach', 'systematic approach')
                potential = data.get('exponential_potential', 'significant potential')
                
                return description_template.format(
                    transformation_outcome=outcome,
                    strategic_approach=approach,
                    exponential_potential=potential
                )
            
            return "Strategic implication details to be determined."
            
        except Exception as e:
            logger.error("Strategic description generation failed", error=str(e))
            return "Strategic implication details to be determined."
    
    def _calculate_framework_alignment(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate framework alignment scores"""
        try:
            alignment = {}
            
            # Extract alignment scores
            alignment['SDG'] = data.get('sdg_alignment', data.get('sdg_score', 0.6))
            alignment['Doughnut Economy'] = data.get('doughnut_alignment', data.get('doughnut_score', 0.6))
            alignment['Agreement Economy'] = data.get('agreement_alignment', data.get('agreement_score', 0.6))
            
            # Ensure all scores are floats between 0 and 1
            for key, value in alignment.items():
                if isinstance(value, (int, float)):
                    alignment[key] = min(max(float(value), 0.0), 1.0)
                else:
                    alignment[key] = 0.6  # Default value
            
            return alignment
            
        except Exception as e:
            logger.error("Framework alignment calculation failed", error=str(e))
            return {'SDG': 0.6, 'Doughnut Economy': 0.6, 'Agreement Economy': 0.6}
    
    # Additional helper methods for strategic implications
    def _generate_impact_assessment(self, data: Dict[str, Any]) -> str:
        """Generate impact assessment"""
        impact_score = data.get('impact_score', 0.5)
        if impact_score > 0.8:
            return "High strategic impact with transformational potential for organizational capabilities and market position."
        elif impact_score > 0.6:
            return "Significant strategic impact with substantial improvements to organizational effectiveness."
        elif impact_score > 0.4:
            return "Moderate strategic impact with measurable improvements to specific operational areas."
        else:
            return "Limited strategic impact with focused improvements to targeted processes."
    
    def _generate_opportunity_analysis(self, data: Dict[str, Any]) -> str:
        """Generate opportunity analysis"""
        opportunities = data.get('opportunities', [])
        if opportunities:
            return f"Key opportunities identified: {', '.join(opportunities[:3])}. Strategic positioning enables competitive advantage through systematic capability development."
        return "Opportunity analysis reveals potential for strategic advancement through focused initiative implementation."
    
    def _generate_risk_evaluation(self, data: Dict[str, Any]) -> str:
        """Generate risk evaluation"""
        risks = data.get('risks', [])
        if risks:
            return f"Primary risks include: {', '.join(risks[:3])}. Mitigation strategies focus on proactive risk management and contingency planning."
        return "Risk evaluation indicates manageable implementation risks with standard mitigation approaches applicable."
    
    def _generate_action_recommendations(self, data: Dict[str, Any], template: Dict[str, Any]) -> List[str]:
        """Generate action recommendations"""
        recommendations = data.get('recommendations', data.get('actions', []))
        if recommendations:
            return recommendations[:5]
        
        # Generate default recommendations based on template
        action_categories = template.get('action_categories', [])
        if action_categories:
            return [
                "Develop immediate implementation plan",
                "Establish medium-term capability building initiatives",
                "Create long-term transformation roadmap"
            ]
        
        return ["Action recommendations to be developed based on strategic analysis."]
    
    def _generate_timeline_considerations(self, data: Dict[str, Any]) -> str:
        """Generate timeline considerations"""
        timeline = data.get('timeline', data.get('timeframe'))
        if timeline:
            return f"Implementation timeline: {timeline}. Phased approach recommended for optimal resource utilization and risk management."
        return "Timeline considerations require detailed planning with phased implementation approach over 6-12 month horizon."
    
    def _generate_resource_implications(self, data: Dict[str, Any]) -> str:
        """Generate resource implications"""
        resources = data.get('resources', data.get('resource_requirements'))
        if resources:
            if isinstance(resources, list):
                return f"Resource requirements include: {', '.join(resources)}. Strategic resource allocation necessary for successful implementation."
            else:
                return f"Resource implications: {resources}"
        return "Resource implications require assessment of capability requirements, budget allocation, and organizational capacity."
    
    def _generate_strategic_success_metrics(self, data: Dict[str, Any]) -> List[str]:
        """Generate strategic success metrics"""
        metrics = data.get('success_metrics', data.get('metrics', []))
        if metrics:
            return metrics[:5]
        
        return [
            "Strategic objective achievement rate",
            "Framework alignment improvement",
            "Organizational capability enhancement",
            "Stakeholder satisfaction index",
            "Implementation timeline adherence"
        ]# 
Additional imports for discussion dynamics and human needs
from collections import Counter

class CommunicationStyle(Enum):
    """Communication style classifications"""
    ASSERTIVE = "assertive"
    COLLABORATIVE = "collaborative"
    ANALYTICAL = "analytical"
    SUPPORTIVE = "supportive"
    DIRECTIVE = "directive"
    PASSIVE = "passive"
    AGGRESSIVE = "aggressive"

class EngagementLevel(Enum):
    """Participant engagement levels"""
    HIGHLY_ENGAGED = "highly_engaged"
    ENGAGED = "engaged"
    MODERATELY_ENGAGED = "moderately_engaged"
    DISENGAGED = "disengaged"
    WITHDRAWN = "withdrawn"

class HumanNeed(Enum):
    """Six fundamental human needs"""
    CERTAINTY = "certainty"
    VARIETY = "variety"
    SIGNIFICANCE = "significance"
    CONNECTION = "connection"
    GROWTH = "growth"
    CONTRIBUTION = "contribution"

class InterventionType(Enum):
    """Types of interventions"""
    INDIVIDUAL = "individual"
    TEAM = "team"
    PROCESS = "process"
    CULTURAL = "cultural"
    STRUCTURAL = "structural"

@dataclass
class ParticipantProfile:
    """Individual participant analysis profile"""
    name: str
    communication_style: CommunicationStyle
    engagement_level: EngagementLevel
    speaking_time_percentage: float
    interaction_count: int
    influence_score: float
    collaboration_score: float
    human_needs_profile: Dict[HumanNeed, float]
    behavioral_patterns: List[str]
    communication_effectiveness: float
    confidence_score: float

@dataclass
class DiscussionDynamics:
    """Discussion dynamics analysis"""
    id: str
    meeting_id: str
    participant_profiles: List[ParticipantProfile]
    overall_engagement: float
    communication_balance: float
    collaboration_index: float
    conflict_indicators: List[str]
    power_dynamics: Dict[str, Any]
    information_flow: Dict[str, Any]
    decision_making_patterns: List[str]
    group_cohesion_score: float
    communication_effectiveness: float
    improvement_recommendations: List[str]
    confidence_score: float
    generated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class HumanNeedsAnalysis:
    """Human needs and emotional intelligence analysis"""
    id: str
    meeting_id: str
    individual_needs_profiles: List[Dict[str, Any]]
    team_needs_balance: Dict[HumanNeed, float]
    need_fulfillment_gaps: List[Dict[str, Any]]
    emotional_climate: Dict[str, float]
    stress_indicators: List[str]
    motivation_factors: List[str]
    intervention_recommendations: List[Dict[str, Any]]
    team_cohesion_factors: List[str]
    psychological_safety_score: float
    collective_wellbeing_score: float
    confidence_score: float
    generated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PatternRecognition:
    """Pattern recognition analysis"""
    id: str
    meeting_id: str
    recurring_themes: List[Dict[str, Any]]
    behavioral_patterns: List[Dict[str, Any]]
    communication_patterns: List[Dict[str, Any]]
    decision_patterns: List[Dict[str, Any]]
    problem_patterns: List[Dict[str, Any]]
    success_patterns: List[Dict[str, Any]]
    intervention_protocols: List[Dict[str, Any]]
    pattern_confidence_scores: Dict[str, float]
    trend_analysis: Dict[str, Any]
    predictive_insights: List[str]
    confidence_score: float
    generated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CommunicationHighlights:
    """Communication highlights and insights"""
    id: str
    meeting_id: str
    key_insights: List[Dict[str, Any]]
    communication_strengths: List[str]
    communication_challenges: List[str]
    breakthrough_moments: List[Dict[str, Any]]
    missed_opportunities: List[Dict[str, Any]]
    influence_networks: Dict[str, Any]
    information_quality: Dict[str, float]
    dialogue_effectiveness: float
    listening_quality_score: float
    clarity_and_precision_score: float
    improvement_recommendations: List[Dict[str, Any]]
    confidence_score: float
    generated_at: datetime = field(default_factory=datetime.utcnow)

# Extend the OracleOutput dataclass
@dataclass
class ExtendedOracleOutput(OracleOutput):
    """Extended Oracle 9.1 Protocol output with discussion dynamics and human needs"""
    discussion_dynamics: Optional[DiscussionDynamics] = None
    human_needs_analysis: Optional[HumanNeedsAnalysis] = None
    pattern_recognition: Optional[PatternRecognition] = None
    communication_highlights: Optional[CommunicationHighlights] = None

# Add new methods to OracleOutputGenerator class
class OracleOutputGenerator:
    """Extended Oracle Output Generator with discussion dynamics and human needs analysis"""
    
    def __init__(self):
        # Initialize existing components
        self.summary_templates = self._initialize_summary_templates()
        self.decision_templates = self._initialize_decision_templates()
        self.action_templates = self._initialize_action_templates()
        self.strategic_templates = self._initialize_strategic_templates()
        
        # Initialize new components for discussion dynamics and human needs
        self.discussion_templates = self._initialize_discussion_templates()
        self.human_needs_templates = self._initialize_human_needs_templates()
        self.pattern_templates = self._initialize_pattern_templates()
        self.communication_templates = self._initialize_communication_templates()
        
        # Extended processors
        self.processors = {
            OutputSection.EXECUTIVE_SUMMARY: self._generate_executive_summary,
            OutputSection.DECISIONS_AGREEMENTS: self._generate_decisions_agreements,
            OutputSection.ACTION_REGISTER: self._generate_action_register,
            OutputSection.STRATEGIC_IMPLICATIONS: self._generate_strategic_implications,
            OutputSection.DISCUSSION_DYNAMICS: self._generate_discussion_dynamics,
            OutputSection.HUMAN_NEEDS_INTELLIGENCE: self._generate_human_needs_analysis,
            OutputSection.PATTERN_RECOGNITION: self._generate_pattern_recognition,
            OutputSection.COMMUNICATION_HIGHLIGHTS: self._generate_communication_highlights
        }
        
        # Quality thresholds
        self.confidence_thresholds = {
            'executive_summary': 0.7,
            'decisions': 0.8,
            'actions': 0.75,
            'strategic_implications': 0.7,
            'discussion_dynamics': 0.75,
            'human_needs': 0.8,
            'pattern_recognition': 0.7,
            'communication_highlights': 0.75
        }
        
        # Generated outputs cache
        self.generated_outputs = {}
        
        # Human needs analysis configuration
        self.human_needs_weights = {
            HumanNeed.CERTAINTY: 0.18,
            HumanNeed.VARIETY: 0.16,
            HumanNeed.SIGNIFICANCE: 0.17,
            HumanNeed.CONNECTION: 0.16,
            HumanNeed.GROWTH: 0.16,
            HumanNeed.CONTRIBUTION: 0.17
        }
    
    def _initialize_discussion_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize discussion dynamics templates"""
        return {
            'engagement_analysis': {
                'high_engagement_indicators': [
                    'frequent_contributions',
                    'active_questioning',
                    'building_on_ideas',
                    'collaborative_language'
                ],
                'low_engagement_indicators': [
                    'minimal_participation',
                    'passive_responses',
                    'distraction_signs',
                    'withdrawal_behaviors'
                ],
                'balance_metrics': [
                    'speaking_time_distribution',
                    'interaction_frequency',
                    'idea_contribution_rate',
                    'question_asking_frequency'
                ]
            },
            'communication_styles': {
                'assertive_patterns': [
                    'clear_position_statements',
                    'confident_language',
                    'direct_communication',
                    'respectful_disagreement'
                ],
                'collaborative_patterns': [
                    'building_on_others_ideas',
                    'seeking_consensus',
                    'inclusive_language',
                    'shared_problem_solving'
                ],
                'analytical_patterns': [
                    'data_driven_arguments',
                    'logical_reasoning',
                    'systematic_approach',
                    'evidence_based_conclusions'
                ]
            },
            'power_dynamics': {
                'influence_indicators': [
                    'idea_adoption_rate',
                    'speaking_time_allocation',
                    'interruption_patterns',
                    'decision_influence'
                ],
                'hierarchy_patterns': [
                    'deference_behaviors',
                    'authority_recognition',
                    'formal_vs_informal_power',
                    'decision_making_flow'
                ]
            }
        }
    
    def _initialize_human_needs_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize human needs analysis templates"""
        return {
            'certainty_indicators': {
                'high_certainty': [
                    'seeks_clear_expectations',
                    'prefers_structured_approach',
                    'values_predictability',
                    'emphasizes_security'
                ],
                'low_certainty': [
                    'comfortable_with_ambiguity',
                    'embraces_uncertainty',
                    'flexible_approach',
                    'adaptable_mindset'
                ]
            },
            'variety_indicators': {
                'high_variety': [
                    'seeks_new_experiences',
                    'enjoys_change',
                    'creative_contributions',
                    'diverse_perspectives'
                ],
                'low_variety': [
                    'prefers_routine',
                    'consistent_approach',
                    'stability_focused',
                    'traditional_methods'
                ]
            },
            'significance_indicators': {
                'high_significance': [
                    'seeks_recognition',
                    'emphasizes_importance',
                    'status_conscious',
                    'achievement_oriented'
                ],
                'low_significance': [
                    'humble_approach',
                    'team_focused',
                    'behind_scenes_contribution',
                    'service_oriented'
                ]
            },
            'connection_indicators': {
                'high_connection': [
                    'relationship_building',
                    'collaborative_language',
                    'team_bonding',
                    'emotional_expression'
                ],
                'low_connection': [
                    'task_focused',
                    'independent_work',
                    'minimal_social_interaction',
                    'professional_boundaries'
                ]
            },
            'growth_indicators': {
                'high_growth': [
                    'learning_orientation',
                    'skill_development',
                    'challenge_seeking',
                    'improvement_focus'
                ],
                'low_growth': [
                    'comfort_zone_preference',
                    'established_expertise',
                    'stability_seeking',
                    'proven_methods'
                ]
            },
            'contribution_indicators': {
                'high_contribution': [
                    'service_to_others',
                    'meaningful_impact',
                    'legacy_building',
                    'purpose_driven'
                ],
                'low_contribution': [
                    'personal_benefit_focus',
                    'individual_achievement',
                    'self_interest',
                    'immediate_rewards'
                ]
            },
            'intervention_strategies': {
                'certainty_interventions': [
                    'provide_clear_structure',
                    'establish_expectations',
                    'create_predictable_processes',
                    'offer_security_assurances'
                ],
                'variety_interventions': [
                    'introduce_new_approaches',
                    'encourage_experimentation',
                    'provide_diverse_options',
                    'stimulate_creativity'
                ],
                'significance_interventions': [
                    'recognize_contributions',
                    'highlight_importance',
                    'provide_status_opportunities',
                    'celebrate_achievements'
                ],
                'connection_interventions': [
                    'facilitate_relationship_building',
                    'encourage_collaboration',
                    'create_bonding_opportunities',
                    'foster_emotional_safety'
                ],
                'growth_interventions': [
                    'provide_learning_opportunities',
                    'offer_challenges',
                    'support_skill_development',
                    'encourage_experimentation'
                ],
                'contribution_interventions': [
                    'connect_to_purpose',
                    'highlight_impact',
                    'create_service_opportunities',
                    'emphasize_legacy_building'
                ]
            }
        }
    
    def _initialize_pattern_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize pattern recognition templates"""
        return {
            'recurring_themes': {
                'theme_categories': [
                    'strategic_themes',
                    'operational_themes',
                    'cultural_themes',
                    'technical_themes',
                    'relationship_themes'
                ],
                'pattern_strength_indicators': [
                    'frequency_of_occurrence',
                    'consistency_across_meetings',
                    'participant_agreement',
                    'outcome_correlation'
                ]
            },
            'behavioral_patterns': {
                'positive_patterns': [
                    'collaborative_problem_solving',
                    'constructive_feedback',
                    'active_listening',
                    'inclusive_participation'
                ],
                'negative_patterns': [
                    'recurring_conflicts',
                    'communication_breakdowns',
                    'decision_paralysis',
                    'disengagement_cycles'
                ],
                'intervention_triggers': [
                    'pattern_frequency_threshold',
                    'impact_severity_level',
                    'participant_feedback',
                    'outcome_degradation'
                ]
            },
            'success_patterns': {
                'high_performance_indicators': [
                    'efficient_decision_making',
                    'effective_collaboration',
                    'clear_communication',
                    'goal_achievement'
                ],
                'replication_strategies': [
                    'process_documentation',
                    'best_practice_sharing',
                    'template_creation',
                    'training_development'
                ]
            }
        }
    
    def _initialize_communication_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize communication highlights templates"""
        return {
            'insight_categories': {
                'breakthrough_insights': [
                    'novel_solutions',
                    'paradigm_shifts',
                    'creative_connections',
                    'strategic_revelations'
                ],
                'process_insights': [
                    'workflow_improvements',
                    'efficiency_opportunities',
                    'bottleneck_identification',
                    'optimization_potential'
                ],
                'relationship_insights': [
                    'team_dynamics',
                    'collaboration_patterns',
                    'trust_building',
                    'conflict_resolution'
                ]
            },
            'communication_quality': {
                'clarity_indicators': [
                    'precise_language',
                    'clear_explanations',
                    'structured_presentation',
                    'logical_flow'
                ],
                'listening_indicators': [
                    'active_acknowledgment',
                    'building_on_ideas',
                    'clarifying_questions',
                    'empathetic_responses'
                ],
                'effectiveness_metrics': [
                    'message_comprehension',
                    'action_clarity',
                    'decision_quality',
                    'outcome_achievement'
                ]
            }
        }
    
    async def generate_extended_oracle_output(self, analysis_data: Dict[str, Any], 
                                            meeting_metadata: Dict[str, Any]) -> ExtendedOracleOutput:
        """
        Generate extended Oracle 9.1 Protocol output with discussion dynamics and human needs
        """
        try:
            # Generate base Oracle output
            base_output = await self.generate_oracle_output(analysis_data, meeting_metadata)
            
            # Generate discussion dynamics
            discussion_dynamics = await self._generate_discussion_dynamics(analysis_data, meeting_metadata)
            
            # Generate human needs analysis
            human_needs_analysis = await self._generate_human_needs_analysis(analysis_data, meeting_metadata)
            
            # Generate pattern recognition
            pattern_recognition = await self._generate_pattern_recognition(analysis_data, meeting_metadata)
            
            # Generate communication highlights
            communication_highlights = await self._generate_communication_highlights(analysis_data, meeting_metadata)
            
            # Create extended output
            extended_output = ExtendedOracleOutput(
                id=base_output.id,
                meeting_id=base_output.meeting_id,
                analysis_id=base_output.analysis_id,
                executive_summary=base_output.executive_summary,
                decisions=base_output.decisions,
                actions=base_output.actions,
                strategic_implications=base_output.strategic_implications,
                discussion_dynamics=discussion_dynamics,
                human_needs_analysis=human_needs_analysis,
                pattern_recognition=pattern_recognition,
                communication_highlights=communication_highlights,
                metadata={
                    **base_output.metadata,
                    'extended_analysis': True,
                    'discussion_confidence': discussion_dynamics.confidence_score,
                    'human_needs_confidence': human_needs_analysis.confidence_score,
                    'pattern_confidence': pattern_recognition.confidence_score,
                    'communication_confidence': communication_highlights.confidence_score
                }
            )
            
            logger.info("Extended Oracle 9.1 Protocol output generated successfully", 
                       output_id=extended_output.id,
                       participants_analyzed=len(discussion_dynamics.participant_profiles),
                       patterns_identified=len(pattern_recognition.recurring_themes))
            
            return extended_output
            
        except Exception as e:
            logger.error("Extended Oracle output generation failed", error=str(e))
            raise
    
    async def _generate_discussion_dynamics(self, analysis_data: Dict[str, Any], 
                                          meeting_metadata: Dict[str, Any]) -> DiscussionDynamics:
        """Generate discussion dynamics analysis"""
        try:
            discussion_id = str(uuid.uuid4())
            meeting_id = meeting_metadata.get('meeting_id', str(uuid.uuid4()))
            
            # Extract participant data
            participants_data = analysis_data.get('participants', [])
            transcript_data = analysis_data.get('transcript_analysis', {})
            
            # Generate participant profiles
            participant_profiles = await self._generate_participant_profiles(
                participants_data, transcript_data, meeting_metadata
            )
            
            # Calculate overall engagement
            overall_engagement = self._calculate_overall_engagement(participant_profiles)
            
            # Calculate communication balance
            communication_balance = self._calculate_communication_balance(participant_profiles)
            
            # Calculate collaboration index
            collaboration_index = self._calculate_collaboration_index(participant_profiles, transcript_data)
            
            # Identify conflict indicators
            conflict_indicators = self._identify_conflict_indicators(transcript_data, participant_profiles)
            
            # Analyze power dynamics
            power_dynamics = self._analyze_power_dynamics(participant_profiles, transcript_data)
            
            # Analyze information flow
            information_flow = self._analyze_information_flow(transcript_data, participant_profiles)
            
            # Identify decision-making patterns
            decision_making_patterns = self._identify_decision_making_patterns(transcript_data)
            
            # Calculate group cohesion score
            group_cohesion_score = self._calculate_group_cohesion(participant_profiles, transcript_data)
            
            # Calculate communication effectiveness
            communication_effectiveness = self._calculate_communication_effectiveness(transcript_data, participant_profiles)
            
            # Generate improvement recommendations
            improvement_recommendations = self._generate_discussion_improvements(
                participant_profiles, conflict_indicators, communication_effectiveness
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_discussion_confidence(
                participant_profiles, transcript_data, meeting_metadata
            )
            
            return DiscussionDynamics(
                id=discussion_id,
                meeting_id=meeting_id,
                participant_profiles=participant_profiles,
                overall_engagement=overall_engagement,
                communication_balance=communication_balance,
                collaboration_index=collaboration_index,
                conflict_indicators=conflict_indicators,
                power_dynamics=power_dynamics,
                information_flow=information_flow,
                decision_making_patterns=decision_making_patterns,
                group_cohesion_score=group_cohesion_score,
                communication_effectiveness=communication_effectiveness,
                improvement_recommendations=improvement_recommendations,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error("Discussion dynamics generation failed", error=str(e))
            raise
    
    async def _generate_participant_profiles(self, participants_data: List[Dict[str, Any]], 
                                           transcript_data: Dict[str, Any],
                                           meeting_metadata: Dict[str, Any]) -> List[ParticipantProfile]:
        """Generate individual participant profiles"""
        try:
            profiles = []
            total_speaking_time = transcript_data.get('total_speaking_time', 100)
            
            for participant_data in participants_data:
                name = participant_data.get('name', 'Unknown Participant')
                
                # Analyze communication style
                communication_style = self._analyze_communication_style(participant_data)
                
                # Determine engagement level
                engagement_level = self._determine_engagement_level(participant_data)
                
                # Calculate speaking time percentage
                speaking_time = participant_data.get('speaking_time', 0)
                speaking_time_percentage = (speaking_time / max(total_speaking_time, 1)) * 100
                
                # Count interactions
                interaction_count = participant_data.get('interaction_count', 0)
                
                # Calculate influence score
                influence_score = self._calculate_influence_score(participant_data, transcript_data)
                
                # Calculate collaboration score
                collaboration_score = self._calculate_collaboration_score(participant_data)
                
                # Analyze human needs profile
                human_needs_profile = self._analyze_individual_human_needs(participant_data)
                
                # Identify behavioral patterns
                behavioral_patterns = self._identify_behavioral_patterns(participant_data)
                
                # Calculate communication effectiveness
                communication_effectiveness = self._calculate_individual_communication_effectiveness(participant_data)
                
                # Calculate confidence score
                confidence_score = participant_data.get('analysis_confidence', 0.75)
                
                profile = ParticipantProfile(
                    name=name,
                    communication_style=communication_style,
                    engagement_level=engagement_level,
                    speaking_time_percentage=speaking_time_percentage,
                    interaction_count=interaction_count,
                    influence_score=influence_score,
                    collaboration_score=collaboration_score,
                    human_needs_profile=human_needs_profile,
                    behavioral_patterns=behavioral_patterns,
                    communication_effectiveness=communication_effectiveness,
                    confidence_score=confidence_score
                )
                
                profiles.append(profile)
            
            return profiles
            
        except Exception as e:
            logger.error("Participant profiles generation failed", error=str(e))
            return []
    
    def _analyze_communication_style(self, participant_data: Dict[str, Any]) -> CommunicationStyle:
        """Analyze participant's communication style"""
        try:
            # Extract communication indicators
            assertive_score = participant_data.get('assertive_indicators', 0)
            collaborative_score = participant_data.get('collaborative_indicators', 0)
            analytical_score = participant_data.get('analytical_indicators', 0)
            supportive_score = participant_data.get('supportive_indicators', 0)
            directive_score = participant_data.get('directive_indicators', 0)
            
            # Find dominant style
            style_scores = {
                CommunicationStyle.ASSERTIVE: assertive_score,
                CommunicationStyle.COLLABORATIVE: collaborative_score,
                CommunicationStyle.ANALYTICAL: analytical_score,
                CommunicationStyle.SUPPORTIVE: supportive_score,
                CommunicationStyle.DIRECTIVE: directive_score
            }
            
            dominant_style = max(style_scores, key=style_scores.get)
            
            # Check for passive or aggressive patterns
            if participant_data.get('passive_indicators', 0) > 0.7:
                return CommunicationStyle.PASSIVE
            elif participant_data.get('aggressive_indicators', 0) > 0.7:
                return CommunicationStyle.AGGRESSIVE
            
            return dominant_style
            
        except Exception as e:
            logger.error("Communication style analysis failed", error=str(e))
            return CommunicationStyle.COLLABORATIVE  # Default
    
    def _determine_engagement_level(self, participant_data: Dict[str, Any]) -> EngagementLevel:
        """Determine participant's engagement level"""
        try:
            engagement_score = participant_data.get('engagement_score', 0.5)
            
            if engagement_score >= 0.9:
                return EngagementLevel.HIGHLY_ENGAGED
            elif engagement_score >= 0.7:
                return EngagementLevel.ENGAGED
            elif engagement_score >= 0.5:
                return EngagementLevel.MODERATELY_ENGAGED
            elif engagement_score >= 0.3:
                return EngagementLevel.DISENGAGED
            else:
                return EngagementLevel.WITHDRAWN
                
        except Exception as e:
            logger.error("Engagement level determination failed", error=str(e))
            return EngagementLevel.MODERATELY_ENGAGED  # Default    

    def _calculate_influence_score(self, participant_data: Dict[str, Any], 
                                 transcript_data: Dict[str, Any]) -> float:
        """Calculate participant's influence score"""
        try:
            # Factors contributing to influence
            speaking_time_factor = participant_data.get('speaking_time_ratio', 0.2)
            idea_adoption_rate = participant_data.get('idea_adoption_rate', 0.5)
            interruption_ratio = participant_data.get('interruption_ratio', 0.1)
            decision_influence = participant_data.get('decision_influence', 0.5)
            
            # Calculate weighted influence score
            influence_score = (
                speaking_time_factor * 0.2 +
                idea_adoption_rate * 0.4 +
                (1 - interruption_ratio) * 0.2 +  # Being interrupted less = more influence
                decision_influence * 0.2
            )
            
            return min(max(influence_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error("Influence score calculation failed", error=str(e))
            return 0.5  # Default
    
    def _calculate_collaboration_score(self, participant_data: Dict[str, Any]) -> float:
        """Calculate participant's collaboration score"""
        try:
            # Collaboration indicators
            building_on_ideas = participant_data.get('building_on_ideas', 0.5)
            asking_questions = participant_data.get('asking_questions', 0.5)
            inclusive_language = participant_data.get('inclusive_language', 0.5)
            supporting_others = participant_data.get('supporting_others', 0.5)
            
            collaboration_score = (
                building_on_ideas * 0.3 +
                asking_questions * 0.2 +
                inclusive_language * 0.25 +
                supporting_others * 0.25
            )
            
            return min(max(collaboration_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error("Collaboration score calculation failed", error=str(e))
            return 0.5  # Default
    
    def _analyze_individual_human_needs(self, participant_data: Dict[str, Any]) -> Dict[HumanNeed, float]:
        """Analyze individual participant's human needs profile"""
        try:
            needs_profile = {}
            
            # Certainty need analysis
            certainty_indicators = participant_data.get('certainty_indicators', {})
            needs_profile[HumanNeed.CERTAINTY] = self._calculate_need_score(
                certainty_indicators, self.human_needs_templates['certainty_indicators']
            )
            
            # Variety need analysis
            variety_indicators = participant_data.get('variety_indicators', {})
            needs_profile[HumanNeed.VARIETY] = self._calculate_need_score(
                variety_indicators, self.human_needs_templates['variety_indicators']
            )
            
            # Significance need analysis
            significance_indicators = participant_data.get('significance_indicators', {})
            needs_profile[HumanNeed.SIGNIFICANCE] = self._calculate_need_score(
                significance_indicators, self.human_needs_templates['significance_indicators']
            )
            
            # Connection need analysis
            connection_indicators = participant_data.get('connection_indicators', {})
            needs_profile[HumanNeed.CONNECTION] = self._calculate_need_score(
                connection_indicators, self.human_needs_templates['connection_indicators']
            )
            
            # Growth need analysis
            growth_indicators = participant_data.get('growth_indicators', {})
            needs_profile[HumanNeed.GROWTH] = self._calculate_need_score(
                growth_indicators, self.human_needs_templates['growth_indicators']
            )
            
            # Contribution need analysis
            contribution_indicators = participant_data.get('contribution_indicators', {})
            needs_profile[HumanNeed.CONTRIBUTION] = self._calculate_need_score(
                contribution_indicators, self.human_needs_templates['contribution_indicators']
            )
            
            return needs_profile
            
        except Exception as e:
            logger.error("Individual human needs analysis failed", error=str(e))
            return {need: 0.5 for need in HumanNeed}  # Default balanced profile
    
    def _calculate_need_score(self, indicators: Dict[str, Any], 
                            template: Dict[str, List[str]]) -> float:
        """Calculate score for a specific human need"""
        try:
            high_indicators = template.get('high_' + list(template.keys())[0].split('_')[1], [])
            low_indicators = template.get('low_' + list(template.keys())[0].split('_')[1], [])
            
            high_score = sum(indicators.get(indicator, 0) for indicator in high_indicators)
            low_score = sum(indicators.get(indicator, 0) for indicator in low_indicators)
            
            # Normalize and calculate final score
            total_possible = len(high_indicators) + len(low_indicators)
            if total_possible > 0:
                normalized_score = (high_score - low_score + total_possible) / (2 * total_possible)
                return min(max(normalized_score, 0.0), 1.0)
            
            return 0.5  # Default if no indicators
            
        except Exception as e:
            logger.error("Need score calculation failed", error=str(e))
            return 0.5
    
    def _identify_behavioral_patterns(self, participant_data: Dict[str, Any]) -> List[str]:
        """Identify behavioral patterns for participant"""
        try:
            patterns = []
            
            # Check for specific behavioral indicators
            if participant_data.get('interrupts_frequently', False):
                patterns.append("Tends to interrupt others during discussions")
            
            if participant_data.get('builds_on_ideas', 0) > 0.7:
                patterns.append("Consistently builds on others' ideas")
            
            if participant_data.get('asks_clarifying_questions', 0) > 0.6:
                patterns.append("Frequently asks clarifying questions")
            
            if participant_data.get('provides_examples', 0) > 0.6:
                patterns.append("Uses examples to illustrate points")
            
            if participant_data.get('summarizes_discussions', 0) > 0.5:
                patterns.append("Often summarizes key discussion points")
            
            if participant_data.get('challenges_assumptions', 0) > 0.6:
                patterns.append("Challenges assumptions and conventional thinking")
            
            if participant_data.get('seeks_consensus', 0) > 0.7:
                patterns.append("Actively seeks consensus and agreement")
            
            return patterns[:5]  # Return top 5 patterns
            
        except Exception as e:
            logger.error("Behavioral patterns identification failed", error=str(e))
            return ["Behavioral patterns could not be identified"]
    
    def _calculate_individual_communication_effectiveness(self, participant_data: Dict[str, Any]) -> float:
        """Calculate individual communication effectiveness"""
        try:
            clarity_score = participant_data.get('clarity_score', 0.7)
            listening_score = participant_data.get('listening_score', 0.7)
            responsiveness_score = participant_data.get('responsiveness_score', 0.7)
            influence_score = participant_data.get('influence_score', 0.5)
            
            effectiveness = (
                clarity_score * 0.3 +
                listening_score * 0.3 +
                responsiveness_score * 0.2 +
                influence_score * 0.2
            )
            
            return min(max(effectiveness, 0.0), 1.0)
            
        except Exception as e:
            logger.error("Individual communication effectiveness calculation failed", error=str(e))
            return 0.7  # Default
    
    def _calculate_overall_engagement(self, participant_profiles: List[ParticipantProfile]) -> float:
        """Calculate overall meeting engagement"""
        try:
            if not participant_profiles:
                return 0.5
            
            engagement_scores = []
            for profile in participant_profiles:
                if profile.engagement_level == EngagementLevel.HIGHLY_ENGAGED:
                    engagement_scores.append(1.0)
                elif profile.engagement_level == EngagementLevel.ENGAGED:
                    engagement_scores.append(0.8)
                elif profile.engagement_level == EngagementLevel.MODERATELY_ENGAGED:
                    engagement_scores.append(0.6)
                elif profile.engagement_level == EngagementLevel.DISENGAGED:
                    engagement_scores.append(0.3)
                else:  # WITHDRAWN
                    engagement_scores.append(0.1)
            
            return sum(engagement_scores) / len(engagement_scores)
            
        except Exception as e:
            logger.error("Overall engagement calculation failed", error=str(e))
            return 0.6  # Default
    
    def _calculate_communication_balance(self, participant_profiles: List[ParticipantProfile]) -> float:
        """Calculate communication balance across participants"""
        try:
            if not participant_profiles:
                return 0.5
            
            speaking_times = [profile.speaking_time_percentage for profile in participant_profiles]
            
            # Calculate coefficient of variation (lower = more balanced)
            if len(speaking_times) > 1:
                mean_time = sum(speaking_times) / len(speaking_times)
                variance = sum((time - mean_time) ** 2 for time in speaking_times) / len(speaking_times)
                std_dev = variance ** 0.5
                
                if mean_time > 0:
                    cv = std_dev / mean_time
                    # Convert to balance score (1 = perfectly balanced, 0 = completely unbalanced)
                    balance_score = max(0, 1 - cv)
                    return min(balance_score, 1.0)
            
            return 0.5  # Default for single participant or no variation
            
        except Exception as e:
            logger.error("Communication balance calculation failed", error=str(e))
            return 0.5
    
    def _calculate_collaboration_index(self, participant_profiles: List[ParticipantProfile], 
                                     transcript_data: Dict[str, Any]) -> float:
        """Calculate collaboration index"""
        try:
            if not participant_profiles:
                return 0.5
            
            # Average collaboration scores
            collaboration_scores = [profile.collaboration_score for profile in participant_profiles]
            avg_collaboration = sum(collaboration_scores) / len(collaboration_scores)
            
            # Factor in group collaboration indicators
            group_collaboration_indicators = transcript_data.get('group_collaboration', {})
            shared_problem_solving = group_collaboration_indicators.get('shared_problem_solving', 0.5)
            consensus_building = group_collaboration_indicators.get('consensus_building', 0.5)
            idea_building = group_collaboration_indicators.get('idea_building', 0.5)
            
            group_factor = (shared_problem_solving + consensus_building + idea_building) / 3
            
            # Combine individual and group factors
            collaboration_index = (avg_collaboration * 0.7 + group_factor * 0.3)
            
            return min(max(collaboration_index, 0.0), 1.0)
            
        except Exception as e:
            logger.error("Collaboration index calculation failed", error=str(e))
            return 0.6  # Default
    
    def _identify_conflict_indicators(self, transcript_data: Dict[str, Any], 
                                    participant_profiles: List[ParticipantProfile]) -> List[str]:
        """Identify conflict indicators in the discussion"""
        try:
            indicators = []
            
            # Check transcript-level conflict indicators
            conflict_data = transcript_data.get('conflict_analysis', {})
            
            if conflict_data.get('interruption_frequency', 0) > 0.3:
                indicators.append("High frequency of interruptions detected")
            
            if conflict_data.get('disagreement_intensity', 0) > 0.6:
                indicators.append("Intense disagreements observed")
            
            if conflict_data.get('emotional_tension', 0) > 0.5:
                indicators.append("Elevated emotional tension in discussions")
            
            if conflict_data.get('defensive_language', 0) > 0.4:
                indicators.append("Defensive language patterns identified")
            
            # Check participant-level indicators
            high_influence_participants = [p for p in participant_profiles if p.influence_score > 0.8]
            if len(high_influence_participants) > len(participant_profiles) * 0.3:
                indicators.append("Power imbalance with multiple high-influence participants")
            
            low_engagement_count = sum(1 for p in participant_profiles 
                                     if p.engagement_level in [EngagementLevel.DISENGAGED, EngagementLevel.WITHDRAWN])
            if low_engagement_count > len(participant_profiles) * 0.3:
                indicators.append("Significant participant disengagement observed")
            
            return indicators[:6]  # Return top 6 indicators
            
        except Exception as e:
            logger.error("Conflict indicators identification failed", error=str(e))
            return ["Conflict analysis could not be completed"]
    
    def _analyze_power_dynamics(self, participant_profiles: List[ParticipantProfile], 
                              transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze power dynamics in the meeting"""
        try:
            power_analysis = {}
            
            # Identify high-influence participants
            high_influence = [p for p in participant_profiles if p.influence_score > 0.7]
            power_analysis['high_influence_participants'] = [p.name for p in high_influence]
            
            # Calculate influence distribution
            influence_scores = [p.influence_score for p in participant_profiles]
            power_analysis['influence_distribution'] = {
                'mean': sum(influence_scores) / len(influence_scores) if influence_scores else 0,
                'max': max(influence_scores) if influence_scores else 0,
                'min': min(influence_scores) if influence_scores else 0
            }
            
            # Analyze speaking time concentration
            speaking_times = [p.speaking_time_percentage for p in participant_profiles]
            top_speaker_time = max(speaking_times) if speaking_times else 0
            power_analysis['speaking_concentration'] = top_speaker_time
            
            # Identify power imbalances
            power_analysis['imbalance_indicators'] = []
            if top_speaker_time > 50:
                power_analysis['imbalance_indicators'].append("Single participant dominates speaking time")
            
            if len(high_influence) == 1 and len(participant_profiles) > 3:
                power_analysis['imbalance_indicators'].append("Single high-influence participant in group setting")
            
            return power_analysis
            
        except Exception as e:
            logger.error("Power dynamics analysis failed", error=str(e))
            return {'analysis_error': 'Power dynamics could not be analyzed'}
    
    def _analyze_information_flow(self, transcript_data: Dict[str, Any], 
                                participant_profiles: List[ParticipantProfile]) -> Dict[str, Any]:
        """Analyze information flow patterns"""
        try:
            flow_analysis = {}
            
            # Information sharing patterns
            info_flow_data = transcript_data.get('information_flow', {})
            flow_analysis['information_density'] = info_flow_data.get('information_density', 0.5)
            flow_analysis['knowledge_sharing_rate'] = info_flow_data.get('knowledge_sharing_rate', 0.5)
            flow_analysis['question_to_answer_ratio'] = info_flow_data.get('question_answer_ratio', 0.5)
            
            # Identify information hubs (participants who share most information)
            info_sharers = []
            for profile in participant_profiles:
                if profile.speaking_time_percentage > 20 and profile.collaboration_score > 0.6:
                    info_sharers.append(profile.name)
            
            flow_analysis['information_hubs'] = info_sharers
            
            # Information quality indicators
            flow_analysis['information_quality'] = {
                'clarity': info_flow_data.get('clarity_score', 0.7),
                'relevance': info_flow_data.get('relevance_score', 0.7),
                'completeness': info_flow_data.get('completeness_score', 0.6)
            }
            
            return flow_analysis
            
        except Exception as e:
            logger.error("Information flow analysis failed", error=str(e))
            return {'analysis_error': 'Information flow could not be analyzed'}
    
    def _identify_decision_making_patterns(self, transcript_data: Dict[str, Any]) -> List[str]:
        """Identify decision-making patterns"""
        try:
            patterns = []
            
            decision_data = transcript_data.get('decision_analysis', {})
            
            # Decision-making style
            if decision_data.get('consensus_seeking', 0) > 0.7:
                patterns.append("Consensus-driven decision making")
            elif decision_data.get('authoritative_decisions', 0) > 0.7:
                patterns.append("Authoritative decision making")
            elif decision_data.get('collaborative_decisions', 0) > 0.7:
                patterns.append("Collaborative decision making")
            
            # Decision quality indicators
            if decision_data.get('evidence_based', 0) > 0.6:
                patterns.append("Evidence-based decision approach")
            
            if decision_data.get('stakeholder_consideration', 0) > 0.6:
                patterns.append("Strong stakeholder consideration in decisions")
            
            if decision_data.get('risk_assessment', 0) > 0.5:
                patterns.append("Risk assessment integrated in decision process")
            
            return patterns[:5]  # Return top 5 patterns
            
        except Exception as e:
            logger.error("Decision-making patterns identification failed", error=str(e))
            return ["Decision-making patterns could not be identified"]
    
    def _calculate_group_cohesion(self, participant_profiles: List[ParticipantProfile], 
                                transcript_data: Dict[str, Any]) -> float:
        """Calculate group cohesion score"""
        try:
            # Average collaboration scores
            collaboration_scores = [p.collaboration_score for p in participant_profiles]
            avg_collaboration = sum(collaboration_scores) / len(collaboration_scores) if collaboration_scores else 0.5
            
            # Communication balance factor
            communication_balance = self._calculate_communication_balance(participant_profiles)
            
            # Group harmony indicators
            harmony_data = transcript_data.get('group_harmony', {})
            shared_understanding = harmony_data.get('shared_understanding', 0.6)
            mutual_support = harmony_data.get('mutual_support', 0.6)
            conflict_resolution = harmony_data.get('conflict_resolution', 0.5)
            
            # Calculate overall cohesion
            cohesion_score = (
                avg_collaboration * 0.3 +
                communication_balance * 0.2 +
                shared_understanding * 0.2 +
                mutual_support * 0.2 +
                conflict_resolution * 0.1
            )
            
            return min(max(cohesion_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error("Group cohesion calculation failed", error=str(e))
            return 0.6  # Default
    
    def _calculate_communication_effectiveness(self, transcript_data: Dict[str, Any], 
                                            participant_profiles: List[ParticipantProfile]) -> float:
        """Calculate overall communication effectiveness"""
        try:
            # Individual effectiveness average
            individual_scores = [p.communication_effectiveness for p in participant_profiles]
            avg_individual = sum(individual_scores) / len(individual_scores) if individual_scores else 0.7
            
            # Group communication factors
            comm_data = transcript_data.get('communication_analysis', {})
            message_clarity = comm_data.get('message_clarity', 0.7)
            active_listening = comm_data.get('active_listening', 0.6)
            feedback_quality = comm_data.get('feedback_quality', 0.6)
            
            # Calculate overall effectiveness
            effectiveness = (
                avg_individual * 0.4 +
                message_clarity * 0.25 +
                active_listening * 0.2 +
                feedback_quality * 0.15
            )
            
            return min(max(effectiveness, 0.0), 1.0)
            
        except Exception as e:
            logger.error("Communication effectiveness calculation failed", error=str(e))
            return 0.7  # Default
    
    def _generate_discussion_improvements(self, participant_profiles: List[ParticipantProfile], 
                                        conflict_indicators: List[str],
                                        communication_effectiveness: float) -> List[str]:
        """Generate discussion improvement recommendations"""
        try:
            recommendations = []
            
            # Communication balance recommendations
            speaking_times = [p.speaking_time_percentage for p in participant_profiles]
            if max(speaking_times) > 50:
                recommendations.append("Encourage more balanced participation by actively inviting quieter members to contribute")
            
            # Engagement recommendations
            low_engagement_count = sum(1 for p in participant_profiles 
                                     if p.engagement_level in [EngagementLevel.DISENGAGED, EngagementLevel.WITHDRAWN])
            if low_engagement_count > 0:
                recommendations.append("Implement engagement strategies for disengaged participants through direct questions and involvement")
            
            # Conflict resolution recommendations
            if conflict_indicators:
                recommendations.append("Address identified conflict indicators through structured dialogue and mediation techniques")
            
            # Communication effectiveness recommendations
            if communication_effectiveness < 0.7:
                recommendations.append("Improve communication effectiveness through active listening training and clear communication protocols")
            
            # Collaboration enhancement
            low_collaboration_count = sum(1 for p in participant_profiles if p.collaboration_score < 0.5)
            if low_collaboration_count > len(participant_profiles) * 0.3:
                recommendations.append("Foster collaboration through team-building activities and collaborative problem-solving exercises")
            
            return recommendations[:6]  # Return top 6 recommendations
            
        except Exception as e:
            logger.error("Discussion improvements generation failed", error=str(e))
            return ["Discussion improvement recommendations could not be generated"]
    
    def _calculate_discussion_confidence(self, participant_profiles: List[ParticipantProfile], 
                                       transcript_data: Dict[str, Any],
                                       meeting_metadata: Dict[str, Any]) -> float:
        """Calculate confidence score for discussion dynamics analysis"""
        try:
            confidence_factors = []
            
            # Participant analysis confidence
            if participant_profiles:
                participant_confidences = [p.confidence_score for p in participant_profiles]
                avg_participant_confidence = sum(participant_confidences) / len(participant_confidences)
                confidence_factors.append(avg_participant_confidence)
            
            # Transcript quality factor
            transcript_quality = transcript_data.get('quality_score', 0.7)
            confidence_factors.append(transcript_quality)
            
            # Meeting metadata completeness
            metadata_completeness = 0.5
            if meeting_metadata.get('participants'):
                metadata_completeness += 0.2
            if meeting_metadata.get('duration_minutes'):
                metadata_completeness += 0.15
            if meeting_metadata.get('meeting_type'):
                metadata_completeness += 0.15
            
            confidence_factors.append(metadata_completeness)
            
            # Calculate overall confidence
            overall_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.7
            
            return min(max(overall_confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error("Discussion confidence calculation failed", error=str(e))
            return 0.7  # Default    
                'decision_making_flow',
                    'consensus_building_patterns'
                ],
                'flow_patterns': [
                    "Sequential discussion with clear topic progression",
                    "Parallel conversations with multiple threads",
                    "Circular discussion returning to key themes",
                    "Fragmented discussion with frequent topic shifts"
                ],
                'transition_quality': [
                    "Smooth transitions between topics",
                    "Abrupt topic changes",
                    "Natural evolution of discussion",
                    "Forced topic redirections"
                ]
            },
            'psychological_safety': {
                'indicators': [
                    'open_disagreement_comfort',
                    'idea_sharing_frequency',
                    'mistake_acknowledgment',
                    'help_seeking_behavior',
                    'diverse_perspective_inclusion'
                ],
                'safety_levels': {
                    'high': "High psychological safety evidenced by open disagreement, frequent idea sharing, and comfortable mistake acknowledgment",
                    'moderate': "Moderate psychological safety with some hesitation in challenging ideas or admitting uncertainties",
                    'low': "Limited psychological safety indicated by minimal disagreement, cautious participation, and defensive responses"
                }
            }
        }

    def _initialize_needs_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize human needs intelligence templates"""
        return {
            'six_human_needs': {
                'certainty': {
                    'indicators': ['structure_seeking', 'clarity_requests', 'confirmation_seeking', 'risk_aversion'],
                    'fulfillment_strategies': [
                        'Provide clear timelines and milestones',
                        'Establish regular check-in processes',
                        'Create detailed documentation',
                        'Implement structured decision-making frameworks'
                    ]
                },
                'variety': {
                    'indicators': ['novelty_seeking', 'challenge_embracing', 'creative_solutions', 'change_advocacy'],
                    'fulfillment_strategies': [
                        'Introduce new approaches and methodologies',
                        'Rotate responsibilities and roles',
                        'Encourage experimental initiatives',
                        'Provide diverse learning opportunities'
                    ]
                },
                'significance': {
                    'indicators': ['recognition_seeking', 'expertise_demonstration', 'leadership_taking', 'achievement_focus'],
                    'fulfillment_strategies': [
                        'Acknowledge individual contributions publicly',
                        'Provide opportunities for expertise sharing',
                        'Create leadership development paths',
                        'Establish achievement recognition systems'
                    ]
                },
                'connection': {
                    'indicators': ['relationship_building', 'team_cohesion_focus', 'empathy_expression', 'collaboration_seeking'],
                    'fulfillment_strategies': [
                        'Foster team building activities',
                        'Create collaborative work structures',
                        'Encourage peer mentoring',
                        'Establish regular social interactions'
                    ]
                },
                'growth': {
                    'indicators': ['learning_orientation', 'skill_development_focus', 'feedback_seeking', 'improvement_mindset'],
                    'fulfillment_strategies': [
                        'Provide continuous learning opportunities',
                        'Implement regular feedback mechanisms',
                        'Support skill development initiatives',
                        'Create stretch assignments and challenges'
                    ]
                },
                'contribution': {
                    'indicators': ['purpose_seeking', 'impact_focus', 'service_orientation', 'legacy_building'],
                    'fulfillment_strategies': [
                        'Connect work to larger organizational purpose',
                        'Highlight impact and outcomes',
                        'Create mentoring and teaching opportunities',
                        'Establish community service initiatives'
                    ]
                }
            },
            'assessment_framework': {
                'individual_analysis': [
                    'primary_need_identification',
                    'secondary_need_patterns',
                    'need_fulfillment_level',
                    'imbalance_indicators',
                    'intervention_recommendations'
                ],
                'team_analysis': [
                    'collective_need_patterns',
                    'need_complementarity',
                    'team_imbalances',
                    'synergy_opportunities',
                    'collective_interventions'
                ]
            }
        }    asyn
c def _generate_discussion_dynamics(self, analysis_data: Dict[str, Any], 
                                          meeting_metadata: Dict[str, Any]) -> DiscussionDynamics:
        """Generate discussion dynamics analysis"""
        try:
            dynamics_id = str(uuid.uuid4())
            
            # Extract participant data
            participants = meeting_metadata.get('participants', [])
            transcript_data = analysis_data.get('transcript_analysis', {})
            
            # Analyze participation patterns
            participation_analysis = self._analyze_participation_patterns(transcript_data, participants)
            
            # Analyze communication patterns
            communication_patterns = self._analyze_communication_patterns(transcript_data)
            
            # Perform sentiment analysis
            sentiment_analysis = self._analyze_discussion_sentiment(transcript_data)
            
            # Analyze power dynamics
            power_dynamics = self._analyze_power_dynamics(transcript_data, participants)
            
            # Calculate collaboration metrics
            collaboration_metrics = self._calculate_collaboration_metrics(transcript_data)
            
            # Analyze decision-making process
            decision_making_process = self._analyze_decision_making_process(transcript_data)
            
            # Identify conflict patterns
            conflict_patterns = self._analyze_conflict_patterns(transcript_data)
            
            # Assess psychological safety
            psychological_safety = self._assess_psychological_safety(transcript_data)
            
            # Calculate engagement levels
            engagement_levels = self._calculate_engagement_levels(transcript_data, participants)
            
            # Generate key insights
            key_insights = self._generate_dynamics_insights(
                participation_analysis, communication_patterns, sentiment_analysis,
                power_dynamics, collaboration_metrics
            )
            
            # Generate recommendations
            recommendations = self._generate_dynamics_recommendations(
                participation_analysis, psychological_safety, collaboration_metrics
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_dynamics_confidence(
                transcript_data, participants, participation_analysis
            )
            
            return DiscussionDynamics(
                id=dynamics_id,
                participation_analysis=participation_analysis,
                communication_patterns=communication_patterns,
                sentiment_analysis=sentiment_analysis,
                power_dynamics=power_dynamics,
                collaboration_metrics=collaboration_metrics,
                decision_making_process=decision_making_process,
                conflict_patterns=conflict_patterns,
                psychological_safety=psychological_safety,
                engagement_levels=engagement_levels,
                key_insights=key_insights,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error("Discussion dynamics generation failed", error=str(e))
            # Return minimal dynamics structure
            return DiscussionDynamics(
                id=str(uuid.uuid4()),
                participation_analysis={'error': 'Analysis failed'},
                communication_patterns={'error': 'Analysis failed'},
                sentiment_analysis={'error': 'Analysis failed'},
                power_dynamics={'error': 'Analysis failed'},
                collaboration_metrics={'error': 'Analysis failed'},
                decision_making_process="Unable to analyze decision-making process",
                conflict_patterns={'error': 'Analysis failed'},
                psychological_safety={'error': 'Analysis failed'},
                engagement_levels={},
                key_insights=["Discussion dynamics analysis encountered errors"],
                recommendations=["Review transcript quality and participant identification"],
                confidence_score=0.1
            )

    async def _generate_human_needs_intelligence(self, analysis_data: Dict[str, Any], 
                                               meeting_metadata: Dict[str, Any]) -> HumanNeedsIntelligence:
        """Generate human needs intelligence analysis"""
        try:
            needs_id = str(uuid.uuid4())
            
            # Extract participant and conversation data
            participants = meeting_metadata.get('participants', [])
            transcript_data = analysis_data.get('transcript_analysis', {})
            
            # Analyze individual needs
            individual_analyses = self._analyze_individual_needs(transcript_data, participants)
            
            # Analyze team-level needs
            team_analysis = self._analyze_team_needs(individual_analyses, transcript_data)
            
            # Assess each of the six human needs
            certainty_assessment = self._assess_certainty_needs(transcript_data, individual_analyses)
            variety_assessment = self._assess_variety_needs(transcript_data, individual_analyses)
            significance_assessment = self._assess_significance_needs(transcript_data, individual_analyses)
            connection_assessment = self._assess_connection_needs(transcript_data, individual_analyses)
            growth_assessment = self._assess_growth_needs(transcript_data, individual_analyses)
            contribution_assessment = self._assess_contribution_needs(transcript_data, individual_analyses)
            
            # Identify need imbalances
            need_imbalances = self._identify_need_imbalances(individual_analyses, team_analysis)
            
            # Generate intervention recommendations
            intervention_recommendations = self._generate_need_interventions(
                need_imbalances, individual_analyses, team_analysis
            )
            
            # Create fulfillment strategies
            fulfillment_strategies = self._create_fulfillment_strategies(
                certainty_assessment, variety_assessment, significance_assessment,
                connection_assessment, growth_assessment, contribution_assessment
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_needs_confidence(
                transcript_data, participants, individual_analyses
            )
            
            return HumanNeedsIntelligence(
                id=needs_id,
                individual_analyses=individual_analyses,
                team_analysis=team_analysis,
                certainty_assessment=certainty_assessment,
                variety_assessment=variety_assessment,
                significance_assessment=significance_assessment,
                connection_assessment=connection_assessment,
                growth_assessment=growth_assessment,
                contribution_assessment=contribution_assessment,
                need_imbalances=need_imbalances,
                intervention_recommendations=intervention_recommendations,
                fulfillment_strategies=fulfillment_strategies,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error("Human needs intelligence generation failed", error=str(e))
            # Return minimal needs structure
            return HumanNeedsIntelligence(
                id=str(uuid.uuid4()),
                individual_analyses=[],
                team_analysis={'error': 'Analysis failed'},
                certainty_assessment={'error': 'Analysis failed'},
                variety_assessment={'error': 'Analysis failed'},
                significance_assessment={'error': 'Analysis failed'},
                connection_assessment={'error': 'Analysis failed'},
                growth_assessment={'error': 'Analysis failed'},
                contribution_assessment={'error': 'Analysis failed'},
                need_imbalances=[],
                intervention_recommendations=[],
                fulfillment_strategies={},
                confidence_score=0.1
            )    def _
analyze_participation_patterns(self, transcript_data: Dict[str, Any], 
                                      participants: List[str]) -> Dict[str, Any]:
        """Analyze participation patterns from transcript data"""
        try:
            # Extract speaking segments
            segments = transcript_data.get('segments', [])
            if not segments:
                return {'error': 'No transcript segments available'}
            
            # Calculate speaking time per participant
            speaking_times = defaultdict(float)
            turn_counts = defaultdict(int)
            
            for segment in segments:
                speaker = segment.get('speaker', 'Unknown')
                duration = segment.get('duration', 0)
                speaking_times[speaker] += duration
                turn_counts[speaker] += 1
            
            total_time = sum(speaking_times.values())
            
            # Calculate participation distribution
            participation_distribution = {}
            for speaker, time in speaking_times.items():
                participation_distribution[speaker] = {
                    'speaking_time_seconds': time,
                    'speaking_time_percentage': (time / total_time * 100) if total_time > 0 else 0,
                    'turn_count': turn_counts[speaker],
                    'average_turn_duration': time / turn_counts[speaker] if turn_counts[speaker] > 0 else 0
                }
            
            # Identify participation patterns
            sorted_participants = sorted(participation_distribution.items(), 
                                       key=lambda x: x[1]['speaking_time_percentage'], reverse=True)
            
            dominant_speakers = [p for p, data in sorted_participants 
                               if data['speaking_time_percentage'] > 25]
            moderate_speakers = [p for p, data in sorted_participants 
                               if 10 <= data['speaking_time_percentage'] <= 25]
            minimal_speakers = [p for p, data in sorted_participants 
                              if data['speaking_time_percentage'] < 10]
            
            return {
                'participation_distribution': participation_distribution,
                'total_speaking_time': total_time,
                'dominant_speakers': dominant_speakers,
                'moderate_speakers': moderate_speakers,
                'minimal_speakers': minimal_speakers,
                'participation_balance': self._calculate_participation_balance(participation_distribution),
                'turn_taking_patterns': self._analyze_turn_taking(segments)
            }
            
        except Exception as e:
            logger.error("Participation pattern analysis failed", error=str(e))
            return {'error': f'Analysis failed: {str(e)}'}

    def _analyze_communication_patterns(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze communication flow and patterns"""
        try:
            segments = transcript_data.get('segments', [])
            if not segments:
                return {'error': 'No transcript segments available'}
            
            # Analyze conversation flow
            conversation_flow = self._analyze_conversation_flow(segments)
            
            # Analyze topic transitions
            topic_transitions = self._analyze_topic_transitions(segments)
            
            # Analyze interruption patterns
            interruption_patterns = self._analyze_interruptions(segments)
            
            # Analyze question-response patterns
            qa_patterns = self._analyze_question_response_patterns(segments)
            
            return {
                'conversation_flow': conversation_flow,
                'topic_transitions': topic_transitions,
                'interruption_patterns': interruption_patterns,
                'question_response_patterns': qa_patterns,
                'communication_style': self._identify_communication_style(segments),
                'information_flow': self._analyze_information_flow(segments)
            }
            
        except Exception as e:
            logger.error("Communication pattern analysis failed", error=str(e))
            return {'error': f'Analysis failed: {str(e)}'}

    def _analyze_discussion_sentiment(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment and emotional tone of discussion"""
        try:
            segments = transcript_data.get('segments', [])
            if not segments:
                return {'error': 'No transcript segments available'}
            
            # Simple sentiment analysis based on keywords
            positive_keywords = ['agree', 'excellent', 'great', 'good', 'yes', 'perfect', 'love', 'like']
            negative_keywords = ['disagree', 'no', 'bad', 'wrong', 'problem', 'issue', 'concern', 'worry']
            neutral_keywords = ['maybe', 'perhaps', 'consider', 'think', 'believe', 'suggest']
            
            sentiment_scores = defaultdict(list)
            overall_sentiment = {'positive': 0, 'negative': 0, 'neutral': 0}
            
            for segment in segments:
                text = segment.get('text', '').lower()
                speaker = segment.get('speaker', 'Unknown')
                
                pos_count = sum(1 for word in positive_keywords if word in text)
                neg_count = sum(1 for word in negative_keywords if word in text)
                neu_count = sum(1 for word in neutral_keywords if word in text)
                
                if pos_count > neg_count and pos_count > neu_count:
                    sentiment = 'positive'
                elif neg_count > pos_count and neg_count > neu_count:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
                
                sentiment_scores[speaker].append(sentiment)
                overall_sentiment[sentiment] += 1
            
            # Calculate sentiment distribution
            total_segments = len(segments)
            sentiment_distribution = {
                'positive_percentage': (overall_sentiment['positive'] / total_segments * 100) if total_segments > 0 else 0,
                'negative_percentage': (overall_sentiment['negative'] / total_segments * 100) if total_segments > 0 else 0,
                'neutral_percentage': (overall_sentiment['neutral'] / total_segments * 100) if total_segments > 0 else 0
            }
            
            return {
                'overall_sentiment': sentiment_distribution,
                'speaker_sentiment': dict(sentiment_scores),
                'emotional_tone': self._determine_emotional_tone(sentiment_distribution),
                'sentiment_trends': self._analyze_sentiment_trends(segments)
            }
            
        except Exception as e:
            logger.error("Sentiment analysis failed", error=str(e))
            return {'error': f'Analysis failed: {str(e)}'}

    def _analyze_power_dynamics(self, transcript_data: Dict[str, Any], 
                              participants: List[str]) -> Dict[str, Any]:
        """Analyze power and influence patterns"""
        try:
            segments = transcript_data.get('segments', [])
            if not segments:
                return {'error': 'No transcript segments available'}
            
            # Identify influence indicators
            influence_indicators = {
                'decision_making': ['decide', 'will do', 'let\'s', 'we should', 'I think we need'],
                'direction_setting': ['next', 'move forward', 'focus on', 'priority', 'important'],
                'question_asking': ['?', 'what', 'how', 'why', 'when', 'where'],
                'interrupting': ['but', 'however', 'actually', 'wait'],
                'summarizing': ['so', 'in summary', 'to recap', 'overall']
            }
            
            speaker_influence = defaultdict(lambda: defaultdict(int))
            
            for segment in segments:
                text = segment.get('text', '').lower()
                speaker = segment.get('speaker', 'Unknown')
                
                for indicator_type, keywords in influence_indicators.items():
                    count = sum(1 for keyword in keywords if keyword in text)
                    speaker_influence[speaker][indicator_type] += count
            
            # Calculate influence scores
            influence_scores = {}
            for speaker, indicators in speaker_influence.items():
                total_score = sum(indicators.values())
                influence_scores[speaker] = {
                    'total_influence_score': total_score,
                    'decision_making_score': indicators['decision_making'],
                    'direction_setting_score': indicators['direction_setting'],
                    'question_asking_score': indicators['question_asking'],
                    'interrupting_score': indicators['interrupting'],
                    'summarizing_score': indicators['summarizing']
                }
            
            # Identify power patterns
            sorted_influence = sorted(influence_scores.items(), 
                                    key=lambda x: x[1]['total_influence_score'], reverse=True)
            
            return {
                'influence_scores': influence_scores,
                'influence_ranking': [speaker for speaker, _ in sorted_influence],
                'power_distribution': self._categorize_power_distribution(influence_scores),
                'leadership_patterns': self._identify_leadership_patterns(influence_scores)
            }
            
        except Exception as e:
            logger.error("Power dynamics analysis failed", error=str(e))
            return {'error': f'Analysis failed: {str(e)}'}  
  def _analyze_individual_needs(self, transcript_data: Dict[str, Any], 
                                participants: List[str]) -> List[Dict[str, Any]]:
        """Analyze individual human needs from transcript data"""
        try:
            segments = transcript_data.get('segments', [])
            if not segments:
                return []
            
            individual_analyses = []
            
            for participant in participants:
                # Get participant's segments
                participant_segments = [s for s in segments if s.get('speaker') == participant]
                if not participant_segments:
                    continue
                
                # Analyze needs indicators
                needs_analysis = {
                    'participant': participant,
                    'certainty_indicators': self._identify_certainty_indicators(participant_segments),
                    'variety_indicators': self._identify_variety_indicators(participant_segments),
                    'significance_indicators': self._identify_significance_indicators(participant_segments),
                    'connection_indicators': self._identify_connection_indicators(participant_segments),
                    'growth_indicators': self._identify_growth_indicators(participant_segments),
                    'contribution_indicators': self._identify_contribution_indicators(participant_segments)
                }
                
                # Calculate need scores
                needs_analysis['need_scores'] = self._calculate_individual_need_scores(needs_analysis)
                
                # Identify primary and secondary needs
                sorted_needs = sorted(needs_analysis['need_scores'].items(), 
                                    key=lambda x: x[1], reverse=True)
                needs_analysis['primary_need'] = sorted_needs[0][0] if sorted_needs else 'unknown'
                needs_analysis['secondary_need'] = sorted_needs[1][0] if len(sorted_needs) > 1 else 'unknown'
                
                individual_analyses.append(needs_analysis)
            
            return individual_analyses
            
        except Exception as e:
            logger.error("Individual needs analysis failed", error=str(e))
            return []

    def _identify_certainty_indicators(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify certainty need indicators in speech patterns"""
        certainty_keywords = [
            'sure', 'certain', 'confirm', 'clarify', 'understand', 'clear',
            'plan', 'schedule', 'timeline', 'deadline', 'structure', 'process',
            'guarantee', 'promise', 'commit', 'reliable', 'stable', 'consistent'
        ]
        
        question_patterns = ['what if', 'are you sure', 'can we confirm', 'is it certain']
        
        indicators = {
            'keyword_count': 0,
            'question_count': 0,
            'structure_seeking': 0,
            'confirmation_requests': 0
        }
        
        for segment in segments:
            text = segment.get('text', '').lower()
            
            # Count certainty keywords
            indicators['keyword_count'] += sum(1 for word in certainty_keywords if word in text)
            
            # Count certainty-seeking questions
            indicators['question_count'] += sum(1 for pattern in question_patterns if pattern in text)
            
            # Identify structure-seeking language
            if any(word in text for word in ['plan', 'schedule', 'timeline', 'process']):
                indicators['structure_seeking'] += 1
            
            # Identify confirmation requests
            if any(word in text for word in ['confirm', 'sure', 'certain', 'right']):
                indicators['confirmation_requests'] += 1
        
        return indicators

    def _identify_variety_indicators(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify variety need indicators in speech patterns"""
        variety_keywords = [
            'new', 'different', 'change', 'alternative', 'creative', 'innovative',
            'experiment', 'try', 'explore', 'adventure', 'challenge', 'exciting',
            'fresh', 'novel', 'unique', 'diverse', 'mix', 'variety'
        ]
        
        indicators = {
            'keyword_count': 0,
            'change_advocacy': 0,
            'creative_suggestions': 0,
            'challenge_seeking': 0
        }
        
        for segment in segments:
            text = segment.get('text', '').lower()
            
            # Count variety keywords
            indicators['keyword_count'] += sum(1 for word in variety_keywords if word in text)
            
            # Identify change advocacy
            if any(word in text for word in ['change', 'different', 'new approach']):
                indicators['change_advocacy'] += 1
            
            # Identify creative suggestions
            if any(word in text for word in ['creative', 'innovative', 'idea', 'what if']):
                indicators['creative_suggestions'] += 1
            
            # Identify challenge seeking
            if any(word in text for word in ['challenge', 'difficult', 'complex']):
                indicators['challenge_seeking'] += 1
        
        return indicators

    def _identify_significance_indicators(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify significance need indicators in speech patterns"""
        significance_keywords = [
            'important', 'significant', 'matter', 'impact', 'influence', 'recognition',
            'achievement', 'success', 'accomplish', 'expert', 'experience', 'knowledge',
            'lead', 'responsible', 'authority', 'respect', 'reputation', 'status'
        ]
        
        indicators = {
            'keyword_count': 0,
            'expertise_demonstration': 0,
            'leadership_taking': 0,
            'recognition_seeking': 0
        }
        
        for segment in segments:
            text = segment.get('text', '').lower()
            
            # Count significance keywords
            indicators['keyword_count'] += sum(1 for word in significance_keywords if word in text)
            
            # Identify expertise demonstration
            if any(phrase in text for phrase in ['in my experience', 'i know', 'i\'ve seen', 'i\'ve done']):
                indicators['expertise_demonstration'] += 1
            
            # Identify leadership taking
            if any(word in text for word in ['i will', 'i\'ll handle', 'let me', 'i can lead']):
                indicators['leadership_taking'] += 1
            
            # Identify recognition seeking
            if any(word in text for word in ['recognize', 'acknowledge', 'credit', 'appreciate']):
                indicators['recognition_seeking'] += 1
        
        return indicators

    def _calculate_individual_need_scores(self, needs_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate need scores for an individual"""
        scores = {}
        
        # Calculate certainty score
        certainty = needs_analysis['certainty_indicators']
        scores['certainty'] = (
            certainty['keyword_count'] * 0.3 +
            certainty['question_count'] * 0.4 +
            certainty['structure_seeking'] * 0.2 +
            certainty['confirmation_requests'] * 0.1
        )
        
        # Calculate variety score
        variety = needs_analysis['variety_indicators']
        scores['variety'] = (
            variety['keyword_count'] * 0.3 +
            variety['change_advocacy'] * 0.3 +
            variety['creative_suggestions'] * 0.2 +
            variety['challenge_seeking'] * 0.2
        )
        
        # Calculate significance score
        significance = needs_analysis['significance_indicators']
        scores['significance'] = (
            significance['keyword_count'] * 0.3 +
            significance['expertise_demonstration'] * 0.3 +
            significance['leadership_taking'] * 0.2 +
            significance['recognition_seeking'] * 0.2
        )
        
        # Add connection, growth, and contribution scores (simplified for now)
        connection = needs_analysis.get('connection_indicators', {})
        scores['connection'] = sum(connection.values()) * 0.25 if connection else 0
        
        growth = needs_analysis.get('growth_indicators', {})
        scores['growth'] = sum(growth.values()) * 0.25 if growth
 else 0
        
        contribution = needs_analysis.get('contribution_indicators', {})
        scores['contribution'] = sum(contribution.values()) * 0.25 if contribution else 0
        
        return scores

    def _analyze_team_needs(self, individual_analyses: List[Dict[str, Any]], 
                          transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze team-level human needs patterns"""
        try:
            if not individual_analyses:
                return {'error': 'No individual analyses available'}
            
            # Aggregate individual need scores
            team_need_totals = defaultdict(float)
            need_counts = defaultdict(int)
            
            for analysis in individual_analyses:
                need_scores = analysis.get('need_scores', {})
                for need, score in need_scores.items():
                    team_need_totals[need] += score
                    need_counts[need] += 1
            
            # Calculate team averages
            team_need_averages = {}
            for need, total in team_need_totals.items():
                team_need_averages[need] = total / need_counts[need] if need_counts[need] > 0 else 0
            
            # Identify team patterns
            dominant_needs = sorted(team_need_averages.items(), key=lambda x: x[1], reverse=True)[:2]
            underserved_needs = sorted(team_need_averages.items(), key=lambda x: x[1])[:2]
            
            # Analyze need complementarity
            need_complementarity = self._analyze_need_complementarity(individual_analyses)
            
            return {
                'team_need_averages': team_need_averages,
                'dominant_team_needs': [need for need, _ in dominant_needs],
                'underserved_team_needs': [need for need, _ in underserved_needs],
                'need_complementarity': need_complementarity,
                'team_balance_score': self._calculate_team_balance_score(team_need_averages),
                'collective_patterns': self._identify_collective_patterns(individual_analyses)
            }
            
        except Exception as e:
            logger.error("Team needs analysis failed", error=str(e))
            return {'error': f'Analysis failed: {str(e)}'}

    def _generate_dynamics_insights(self, participation_analysis: Dict[str, Any],
                                  communication_patterns: Dict[str, Any],
                                  sentiment_analysis: Dict[str, Any],
                                  power_dynamics: Dict[str, Any],
                                  collaboration_metrics: Dict[str, Any]) -> List[str]:
        """Generate key insights about discussion dynamics"""
        insights = []
        
        try:
            # Participation insights
            if 'dominant_speakers' in participation_analysis:
                dominant_count = len(participation_analysis['dominant_speakers'])
                if dominant_count == 1:
                    insights.append("Discussion was dominated by a single participant, potentially limiting diverse input")
                elif dominant_count > 3:
                    insights.append("Well-distributed participation with multiple active contributors")
            
            # Sentiment insights
            if 'overall_sentiment' in sentiment_analysis:
                sentiment = sentiment_analysis['overall_sentiment']
                if sentiment.get('positive_percentage', 0) > 60:
                    insights.append("Predominantly positive discussion tone supporting collaborative decision-making")
                elif sentiment.get('negative_percentage', 0) > 40:
                    insights.append("Significant negative sentiment detected, indicating potential concerns or conflicts")
            
            # Power dynamics insights
            if 'influence_ranking' in power_dynamics:
                ranking = power_dynamics['influence_ranking']
                if len(ranking) > 0:
                    insights.append(f"Clear influence hierarchy with {ranking[0]} demonstrating primary leadership")
            
            # Communication flow insights
            if 'conversation_flow' in communication_patterns:
                flow = communication_patterns['conversation_flow']
                if flow.get('interruption_rate', 0) > 0.3:
                    insights.append("High interruption rate may indicate engagement but could limit thorough discussion")
            
            # Default insight if none generated
            if not insights:
                insights.append("Discussion dynamics analysis completed with standard patterns observed")
            
        except Exception as e:
            logger.error("Dynamics insights generation failed", error=str(e))
            insights.append("Unable to generate detailed dynamics insights due to analysis limitations")
        
        return insights[:5]  # Limit to 5 key insights

    def _generate_dynamics_recommendations(self, participation_analysis: Dict[str, Any],
                                         psychological_safety: Dict[str, Any],
                                         collaboration_metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving discussion dynamics"""
        recommendations = []
        
        try:
            # Participation recommendations
            if 'minimal_speakers' in participation_analysis:
                minimal_count = len(participation_analysis['minimal_speakers'])
                if minimal_count > 0:
                    recommendations.append("Implement structured turn-taking to encourage participation from quieter members")
            
            # Psychological safety recommendations
            if psychological_safety.get('safety_level') == 'low':
                recommendations.append("Focus on building psychological safety through active listening and non-judgmental responses")
            
            # Collaboration recommendations
            if collaboration_metrics.get('collaboration_score', 0) < 0.6:
                recommendations.append("Introduce collaborative decision-making frameworks to improve team synergy")
            
            # General recommendations
            recommendations.extend([
                "Consider rotating meeting facilitation to distribute leadership opportunities",
                "Implement regular check-ins to ensure all voices are heard",
                "Use structured brainstorming techniques to maximize creative input"
            ])
            
        except Exception as e:
            logger.error("Dynamics recommendations generation failed", error=str(e))
            recommendations.append("Review meeting structure and facilitation approaches for optimization")
        
        return recommendations[:5]  # Limit to 5 recommendations

    def _calculate_dynamics_confidence(self, transcript_data: Dict[str, Any],
                                     participants: List[str],
                                     participation_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for dynamics analysis"""
        try:
            confidence_factors = []
            
            # Transcript quality factor
            segments = transcript_data.get('segments', [])
            if segments:
                confidence_factors.append(min(len(segments) / 50, 1.0))  # More segments = higher confidence
            else:
                confidence_factors.append(0.1)
            
            # Participant identification factor
            identified_speakers = len(participation_analysis.get('participation_distribution', {}))
            expected_speakers = len(participants)
            if expected_speakers > 0:
                confidence_factors.append(identified_speakers / expected_speakers)
            else:
                confidence_factors.append(0.5)
            
            # Data completeness factor
            if participation_analysis.get('error'):
                confidence_factors.append(0.2)
            else:
                confidence_factors.append(0.8)
            
            return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.3
            
        except Exception as e:
            logger.error("Dynamics confidence calculation failed", error=str(e))
            return 0.3

    def _calculate_needs_confidence(self, transcript_data: Dict[str, Any],
                                  participants: List[str],
                                  individual_analyses: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for needs analysis"""
        try:
            confidence_factors = []
            
            # Analysis completeness factor
            if individual_analyses:
                confidence_factors.append(len(individual_analyses) / max(len(participants), 1))
            else:
                confidence_factors.append(0.1)
            
            # Data quality factor
            segments = transcript_data.get('segments', [])
            if segments:
                confidence_factors.append(min(len(segments) / 30, 1.0))
            else:
                confidence_factors.append(0.1)
            
            # Analysis depth factor
            if individual_analyses and all('need_scores' in analysis for analysis in individual_analyses):
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.4)
            
            return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.3
            
        except Exception as e:
            logger.error("Needs confidence calculation failed", error=str(e))
            return 0.3 
   # Helper methods for analysis
    def _calculate_participation_balance(self, participation_distribution: Dict[str, Any]) -> float:
        """Calculate how balanced participation is across speakers"""
        if not participation_distribution:
            return 0.0
        
        percentages = [data['speaking_time_percentage'] for data in participation_distribution.values()]
        if not percentages:
            return 0.0
        
        # Calculate standard deviation - lower is more balanced
        mean_percentage = sum(percentages) / len(percentages)
        variance = sum((p - mean_percentage) ** 2 for p in percentages) / len(percentages)
        std_dev = variance ** 0.5
        
        # Convert to balance score (0-1, where 1 is perfectly balanced)
        max_possible_std = mean_percentage  # Maximum when one person speaks 100%
        balance_score = 1 - (std_dev / max_possible_std) if max_possible_std > 0 else 1
        
        return max(0, min(1, balance_score))

    def _analyze_turn_taking(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze turn-taking patterns in conversation"""
        if not segments:
            return {'error': 'No segments available'}
        
        # Track speaker transitions
        transitions = []
        interruptions = 0
        
        for i in range(1, len(segments)):
            prev_speaker = segments[i-1].get('speaker')
            curr_speaker = segments[i].get('speaker')
            
            if prev_speaker != curr_speaker:
                transitions.append((prev_speaker, curr_speaker))
                
                # Simple interruption detection (very short previous segment)
                prev_duration = segments[i-1].get('duration', 0)
                if prev_duration < 2:  # Less than 2 seconds might indicate interruption
                    interruptions += 1
        
        return {
            'total_transitions': len(transitions),
            'interruption_count': interruptions,
            'interruption_rate': interruptions / len(transitions) if transitions else 0,
            'average_turn_length': sum(s.get('duration', 0) for s in segments) / len(segments)
        }

    def _analyze_conversation_flow(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall conversation flow patterns"""
        if not segments:
            return {'error': 'No segments available'}
        
        # Analyze pacing
        durations = [s.get('duration', 0) for s in segments]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Analyze speaker distribution
        speakers = [s.get('speaker') for s in segments]
        unique_speakers = set(speakers)
        
        return {
            'total_segments': len(segments),
            'unique_speakers': len(unique_speakers),
            'average_segment_duration': avg_duration,
            'conversation_pace': 'fast' if avg_duration < 5 else 'moderate' if avg_duration < 15 else 'slow',
            'speaker_diversity': len(unique_speakers) / len(segments) if segments else 0
        }

    def _determine_emotional_tone(self, sentiment_distribution: Dict[str, float]) -> str:
        """Determine overall emotional tone of discussion"""
        positive = sentiment_distribution.get('positive_percentage', 0)
        negative = sentiment_distribution.get('negative_percentage', 0)
        
        if positive > 60:
            return 'positive'
        elif negative > 40:
            return 'negative'
        elif positive > 40 and negative < 20:
            return 'optimistic'
        elif negative > 20 and positive < 40:
            return 'cautious'
        else:
            return 'neutral'

    def _analyze_need_complementarity(self, individual_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how individual needs complement each other in the team"""
        if not individual_analyses:
            return {'error': 'No individual analyses available'}
        
        # Count primary needs
        primary_needs = [analysis.get('primary_need') for analysis in individual_analyses]
        need_counts = defaultdict(int)
        for need in primary_needs:
            if need and need != 'unknown':
                need_counts[need] += 1
        
        # Calculate diversity
        total_people = len(individual_analyses)
        need_diversity = len(need_counts) / 6  # 6 total needs
        
        return {
            'need_distribution': dict(need_counts),
            'need_diversity_score': need_diversity,
            'complementarity_level': 'high' if need_diversity > 0.6 else 'moderate' if need_diversity > 0.3 else 'low',
            'potential_synergies': self._identify_need_synergies(need_counts)
        }

    def _identify_need_synergies(self, need_counts: Dict[str, int]) -> List[str]:
        """Identify potential synergies between different needs"""
        synergies = []
        
        # Certainty + Growth = Structured learning
        if need_counts.get('certainty', 0) > 0 and need_counts.get('growth', 0) > 0:
            synergies.append("Certainty and Growth needs can create structured learning opportunities")
        
        # Variety + Significance = Innovation leadership
        if need_counts.get('variety', 0) > 0 and need_counts.get('significance', 0) > 0:
            synergies.append("Variety and Significance needs can drive innovative leadership")
        
        # Connection + Contribution = Team service
        if need_counts.get('connection', 0) > 0 and need_counts.get('contribution', 0) > 0:
            synergies.append("Connection and Contribution needs can enhance team service orientation")
        
        return synergies

    def _calculate_team_balance_score(self, team_need_averages: Dict[str, float]) -> float:
        """Calculate how balanced the team's needs are"""
        if not team_need_averages:
            return 0.0
        
        scores = list(team_need_averages.values())
        if not scores:
            return 0.0
        
        # Calculate coefficient of variation (lower = more balanced)
        mean_score = sum(scores) / len(scores)
        if mean_score == 0:
            return 1.0  # Perfect balance if all scores are 0
        
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        std_dev = variance ** 0.5
        cv = std_dev / mean_score
        
        # Convert to balance score (0-1, where 1 is perfectly balanced)
        balance_score = 1 / (1 + cv)  # Higher CV = lower balance
        
        return max(0, min(1, balance_score))  
  async def generate_oracle_output(self, analysis_data: Dict[str, Any], 
                                   meeting_metadata: Dict[str, Any]) -> OracleOutput:
        """
        Generate complete Oracle 9.1 Protocol output from analysis data
        """
        try:
            output_id = str(uuid.uuid4())
            meeting_id = meeting_metadata.get('meeting_id', str(uuid.uuid4()))
            analysis_id = analysis_data.get('analysis_id', str(uuid.uuid4()))
            
            logger.info("Generating Oracle 9.1 Protocol output", 
                       output_id=output_id, meeting_id=meeting_id)
            
            # Generate executive summary
            executive_summary = await self._generate_executive_summary(analysis_data, meeting_metadata)
            
            # Generate decisions and agreements
            decisions = await self._generate_decisions_agreements(analysis_data, meeting_metadata)
            
            # Generate action register
            actions = await self._generate_action_register(analysis_data, meeting_metadata)
            
            # Generate strategic implications
            strategic_implications = await self._generate_strategic_implications(analysis_data, meeting_metadata)
            
            # Generate discussion dynamics
            discussion_dynamics = await self._generate_discussion_dynamics(analysis_data, meeting_metadata)
            
            # Generate human needs intelligence
            human_needs_intelligence = await self._generate_human_needs_intelligence(analysis_data, meeting_metadata)
            
            # Create complete output
            oracle_output = OracleOutput(
                id=output_id,
                meeting_id=meeting_id,
                analysis_id=analysis_id,
                executive_summary=executive_summary,
                decisions=decisions,
                actions=actions,
                strategic_implications=strategic_implications,
                discussion_dynamics=discussion_dynamics,
                human_needs_intelligence=human_needs_intelligence,
                metadata={
                    'meeting_title': meeting_metadata.get('title', 'Untitled Meeting'),
                    'meeting_date': meeting_metadata.get('date', datetime.utcnow().isoformat()),
                    'participants': meeting_metadata.get('participants', []),
                    'duration_minutes': meeting_metadata.get('duration_minutes', 0),
                    'meeting_type': meeting_metadata.get('meeting_type', 'general'),
                    'analysis_confidence': self._calculate_overall_confidence(
                        executive_summary, decisions, actions, strategic_implications
                    ),
                    'generation_timestamp': datetime.utcnow().isoformat(),
                    'oracle_version': "9.1"
                }
            )
            
            # Cache the output
            self.generated_outputs[output_id] = oracle_output
            
            logger.info("Oracle 9.1 Protocol output generated successfully", 
                       output_id=output_id,
                       decisions_count=len(decisions),
                       actions_count=len(actions),
                       strategic_implications_count=len(strategic_implications),
                       has_discussion_dynamics=discussion_dynamics is not None,
                       has_human_needs_intelligence=human_needs_intelligence is not None)
            
            return oracle_output
            
        except Exception as e:
            logger.error("Oracle output generation failed", error=str(e))
            raise

    # Placeholder methods for existing functionality (to be implemented separately)
    async def _generate_executive_summary(self, analysis_data: Dict[str, Any], 
                                        meeting_metadata: Dict[str, Any]) -> ExecutiveSummary:
        """Generate executive summary (placeholder)"""
        return ExecutiveSummary(
            meeting_overview="Executive summary generation in progress",
            key_outcomes=[],
            critical_decisions=[],
            priority_actions=[],
            strategic_alignment={},
            risk_factors=[],
            success_indicators=[],
            next_steps=[],
            confidence_score=0.5
        )

    async def _generate_decisions_agreements(self, analysis_data: Dict[str, Any], 
                                           meeting_metadata: Dict[str, Any]) -> List[Decision]:
        """Generate decisions and agreements (placeholder)"""
        return []

    async def _generate_action_register(self, analysis_data: Dict[str, Any], 
                                      meeting_metadata: Dict[str, Any]) -> List[ActionItem]:
        """Generate action register (placeholder)"""
        return []

    async def _generate_strategic_implications(self, analysis_data: Dict[str, Any], 
                                             meeting_metadata: Dict[str, Any]) -> List[StrategicImplication]:
        """Generate strategic implications (placeholder)"""
        return []

    def _calculate_overall_confidence(self, executive_summary: ExecutiveSummary,
                                    decisions: List[Decision],
                                    actions: List[ActionItem],
                                    strategic_implications: List[StrategicImplication]) -> float:
        """Calculate overall confidence score"""
        scores = [executive_summary.confidence_score]
        
        if decisions:
            scores.extend([d.confidence_score for d in decisions])
        if actions:
            scores.extend([a.confidence_score for a in actions])
        if strategic_implications:
            scores.extend([s.confidence_score for s in strategic_implications])
        
        return sum(scores) / len(scores) if scores else 0.5@dat
aclass
class NarrativeDevelopment:
    """Narrative development and organizational story integration"""
    id: str
    organizational_context: Dict[str, Any]  # Current organizational state and context
    meeting_narrative: str  # How this meeting fits into the organizational story
    story_progression: Dict[str, Any]  # Progress markers in the organizational journey
    narrative_themes: List[str]  # Key themes emerging from the discussion
    character_development: Dict[str, Any]  # How participants/roles are evolving
    plot_points: List[Dict[str, Any]]  # Significant events and turning points
    conflict_resolution: Dict[str, Any]  # How conflicts are being addressed in the story
    future_chapters: List[str]  # Anticipated future developments
    narrative_coherence: float  # How well the meeting fits the organizational story
    story_momentum: str  # Direction and energy of the organizational narrative
    cultural_evolution: Dict[str, Any]  # How organizational culture is evolving
    legacy_building: List[str]  # Long-term impact and legacy considerations
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SolutionComponent:
    """Individual solution component"""
    id: str
    title: str
    description: str
    category: str  # technical, process, cultural, strategic
    implementation_complexity: str  # low, medium, high, very_high
    resource_requirements: Dict[str, Any]  # people, time, budget, technology
    dependencies: List[str]  # Other components this depends on
    success_metrics: List[str]  # How success will be measured
    risk_factors: List[str]  # Potential risks and mitigation strategies
    timeline: Dict[str, Any]  # Implementation timeline and milestones
    stakeholders: List[str]  # Key stakeholders involved
    exponential_potential: float  # Potential for exponential impact
    confidence_score: float

@dataclass
class SolutionPortfolio:
    """Comprehensive solution portfolio with implementation plans"""
    id: str
    portfolio_overview: str  # High-level description of the solution portfolio
    solution_components: List[SolutionComponent]  # Individual solution components
    implementation_strategy: Dict[str, Any]  # Overall implementation approach
    resource_allocation: Dict[str, Any]  # Resource distribution across solutions
    timeline_coordination: Dict[str, Any]  # How components are coordinated over time
    risk_management: Dict[str, Any]  # Portfolio-level risk management
    success_framework: Dict[str, Any]  # How portfolio success will be measured
    synergy_opportunities: List[Dict[str, Any]]  # Cross-component synergies
    priority_sequencing: List[str]  # Recommended implementation sequence
    change_management: Dict[str, Any]  # Change management considerations
    governance_structure: Dict[str, Any]  # How the portfolio will be governed
    continuous_improvement: Dict[str, Any]  # Ongoing optimization approach
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class HumanNeedsFulfillmentPlan:
    """Targeted interventions and success metrics for human needs fulfillment"""
    id: str
    individual_plans: List[Dict[str, Any]]  # Individual fulfillment plans
    team_interventions: List[Dict[str, Any]]  # Team-level interventions
    organizational_initiatives: List[Dict[str, Any]]  # Organization-wide initiatives
    need_specific_strategies: Dict[str, List[str]]  # Strategies for each of the 6 needs
    implementation_timeline: Dict[str, Any]  # When interventions will be implemented
    success_metrics: Dict[str, List[str]]  # Metrics for measuring fulfillment
    monitoring_framework: Dict[str, Any]  # How progress will be monitored
    feedback_mechanisms: List[str]  # How feedback will be collected
    adjustment_protocols: List[str]  # How plans will be adjusted based on feedback
    resource_requirements: Dict[str, Any]  # Resources needed for implementation
    stakeholder_roles: Dict[str, List[str]]  # Who is responsible for what
    integration_points: List[str]  # How this integrates with other initiatives
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class IntegrityAlignmentCheck:
    """Consistency validation and quality assurance"""
    id: str
    consistency_analysis: Dict[str, Any]  # Analysis of internal consistency
    alignment_assessment: Dict[str, Any]  # How well components align with each other
    quality_metrics: Dict[str, float]  # Various quality indicators
    validation_results: Dict[str, Any]  # Results of validation checks
    discrepancy_identification: List[Dict[str, Any]]  # Identified inconsistencies
    resolution_recommendations: List[str]  # How to resolve discrepancies
    confidence_validation: Dict[str, float]  # Validation of confidence scores
    completeness_check: Dict[str, Any]  # Assessment of output completeness
    accuracy_assessment: Dict[str, Any]  # Assessment of output accuracy
    reliability_indicators: Dict[str, float]  # Reliability metrics
    improvement_suggestions: List[str]  # Suggestions for improvement
    overall_integrity_score: float  # Overall integrity and alignment score
    created_at: datetime = field(default_factory=datetime.utcnow)    a
sync def _generate_narrative_development(self, analysis_data: Dict[str, Any], 
                                            meeting_metadata: Dict[str, Any]) -> NarrativeDevelopment:
        """Generate narrative development and organizational story integration"""
        try:
            narrative_id = str(uuid.uuid4())
            
            # Extract organizational context
            organizational_context = self._extract_organizational_context(analysis_data, meeting_metadata)
            
            # Generate meeting narrative
            meeting_narrative = self._generate_meeting_narrative(analysis_data, meeting_metadata)
            
            # Analyze story progression
            story_progression = self._analyze_story_progression(analysis_data, meeting_metadata)
            
            # Identify narrative themes
            narrative_themes = self._identify_narrative_themes(analysis_data)
            
            # Analyze character development
            character_development = self._analyze_character_development(analysis_data, meeting_metadata)
            
            # Identify plot points
            plot_points = self._identify_plot_points(analysis_data)
            
            # Analyze conflict resolution
            conflict_resolution = self._analyze_conflict_resolution(analysis_data)
            
            # Generate future chapters
            future_chapters = self._generate_future_chapters(analysis_data, meeting_metadata)
            
            # Calculate narrative coherence
            narrative_coherence = self._calculate_narrative_coherence(analysis_data, meeting_metadata)
            
            # Determine story momentum
            story_momentum = self._determine_story_momentum(analysis_data)
            
            # Analyze cultural evolution
            cultural_evolution = self._analyze_cultural_evolution(analysis_data, meeting_metadata)
            
            # Identify legacy building opportunities
            legacy_building = self._identify_legacy_building(analysis_data)
            
            # Calculate confidence score
            confidence_score = self._calculate_narrative_confidence(analysis_data, meeting_metadata)
            
            return NarrativeDevelopment(
                id=narrative_id,
                organizational_context=organizational_context,
                meeting_narrative=meeting_narrative,
                story_progression=story_progression,
                narrative_themes=narrative_themes,
                character_development=character_development,
                plot_points=plot_points,
                conflict_resolution=conflict_resolution,
                future_chapters=future_chapters,
                narrative_coherence=narrative_coherence,
                story_momentum=story_momentum,
                cultural_evolution=cultural_evolution,
                legacy_building=legacy_building,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error("Narrative development generation failed", error=str(e))
            # Return minimal narrative structure
            return NarrativeDevelopment(
                id=str(uuid.uuid4()),
                organizational_context={'error': 'Analysis failed'},
                meeting_narrative="Unable to generate meeting narrative",
                story_progression={'error': 'Analysis failed'},
                narrative_themes=["Narrative analysis encountered errors"],
                character_development={'error': 'Analysis failed'},
                plot_points=[],
                conflict_resolution={'error': 'Analysis failed'},
                future_chapters=["Future narrative development needed"],
                narrative_coherence=0.1,
                story_momentum="uncertain",
                cultural_evolution={'error': 'Analysis failed'},
                legacy_building=["Legacy building opportunities to be identified"],
                confidence_score=0.1
            )

    async def _generate_solution_portfolio(self, analysis_data: Dict[str, Any], 
                                         meeting_metadata: Dict[str, Any]) -> SolutionPortfolio:
        """Generate comprehensive solution portfolio with implementation plans"""
        try:
            portfolio_id = str(uuid.uuid4())
            
            # Generate portfolio overview
            portfolio_overview = self._generate_portfolio_overview(analysis_data, meeting_metadata)
            
            # Generate solution components
            solution_components = self._generate_solution_components(analysis_data, meeting_metadata)
            
            # Develop implementation strategy
            implementation_strategy = self._develop_implementation_strategy(solution_components, analysis_data)
            
            # Calculate resource allocation
            resource_allocation = self._calculate_resource_allocation(solution_components)
            
            # Coordinate timeline
            timeline_coordination = self._coordinate_timeline(solution_components)
            
            # Develop risk management
            risk_management = self._develop_portfolio_risk_management(solution_components, analysis_data)
            
            # Create success framework
            success_framework = self._create_success_framework(solution_components, analysis_data)
            
            # Identify synergy opportunities
            synergy_opportunities = self._identify_synergy_opportunities(solution_components)
            
            # Determine priority sequencing
            priority_sequencing = self._determine_priority_sequencing(solution_components)
            
            # Develop change management
            change_management = self._develop_change_management(solution_components, meeting_metadata)
            
            # Create governance structure
            governance_structure = self._create_governance_structure(solution_components, meeting_metadata)
            
            # Plan continuous improvement
            continuous_improvement = self._plan_continuous_improvement(solution_components)
            
            # Calculate confidence score
            confidence_score = self._calculate_portfolio_confidence(solution_components, analysis_data)
            
            return SolutionPortfolio(
                id=portfolio_id,
                portfolio_overview=portfolio_overview,
                solution_components=solution_components,
                implementation_strategy=implementation_strategy,
                resource_allocation=resource_allocation,
                timeline_coordination=timeline_coordination,
                risk_management=risk_management,
                success_framework=success_framework,
                synergy_opportunities=synergy_opportunities,
                priority_sequencing=priority_sequencing,
                change_management=change_management,
                governance_structure=governance_structure,
                continuous_improvement=continuous_improvement,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error("Solution portfolio generation failed", error=str(e))
            # Return minimal portfolio structure
            return SolutionPortfolio(
                id=str(uuid.uuid4()),
                portfolio_overview="Solution portfolio generation encountered errors",
                solution_components=[],
                implementation_strategy={'error': 'Analysis failed'},
                resource_allocation={'error': 'Analysis failed'},
                timeline_coordination={'error': 'Analysis failed'},
                risk_management={'error': 'Analysis failed'},
                success_framework={'error': 'Analysis failed'},
                synergy_opportunities=[],
                priority_sequencing=[],
                change_management={'error': 'Analysis failed'},
                governance_structure={'error': 'Analysis failed'},
                continuous_improvement={'error': 'Analysis failed'},
                confidence_score=0.1
            )    def 
_extract_organizational_context(self, analysis_data: Dict[str, Any], 
                                      meeting_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract organizational context from meeting data"""
        try:
            context = {
                'meeting_type': meeting_metadata.get('meeting_type', 'general'),
                'organizational_phase': self._determine_organizational_phase(analysis_data),
                'current_challenges': self._extract_current_challenges(analysis_data),
                'strategic_focus': self._extract_strategic_focus(analysis_data),
                'team_dynamics': self._summarize_team_dynamics(analysis_data),
                'cultural_indicators': self._identify_cultural_indicators(analysis_data),
                'change_readiness': self._assess_change_readiness(analysis_data)
            }
            
            return context
            
        except Exception as e:
            logger.error("Organizational context extraction failed", error=str(e))
            return {'error': f'Context extraction failed: {str(e)}'}

    def _generate_meeting_narrative(self, analysis_data: Dict[str, Any], 
                                  meeting_metadata: Dict[str, Any]) -> str:
        """Generate narrative description of how this meeting fits into organizational story"""
        try:
            meeting_type = meeting_metadata.get('meeting_type', 'meeting')
            participants = meeting_metadata.get('participants', [])
            
            # Identify key narrative elements
            key_decisions = analysis_data.get('decisions', [])
            key_actions = analysis_data.get('actions', [])
            strategic_themes = analysis_data.get('strategic_analysis', {})
            
            # Generate narrative based on meeting content
            if key_decisions:
                decision_narrative = f"This {meeting_type} marked a pivotal moment with {len(key_decisions)} significant decisions that will shape the organization's future direction."
            else:
                decision_narrative = f"This {meeting_type} focused on exploration and alignment rather than definitive decision-making."
            
            if key_actions:
                action_narrative = f" The team committed to {len(key_actions)} concrete actions, demonstrating readiness to move from planning to execution."
            else:
                action_narrative = " The discussion remained at a strategic level, setting the foundation for future action planning."
            
            # Add participant engagement narrative
            if len(participants) > 1:
                engagement_narrative = f" With {len(participants)} participants actively engaged, the meeting reflected collaborative leadership and shared ownership of outcomes."
            else:
                engagement_narrative = " The focused discussion allowed for deep exploration of key themes and thorough consideration of options."
            
            return decision_narrative + action_narrative + engagement_narrative
            
        except Exception as e:
            logger.error("Meeting narrative generation failed", error=str(e))
            return "This meeting represents a step forward in the organization's ongoing journey, though specific narrative details could not be determined."

    def _analyze_story_progression(self, analysis_data: Dict[str, Any], 
                                 meeting_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how the organization's story is progressing"""
        try:
            progression = {
                'current_chapter': self._identify_current_chapter(analysis_data, meeting_metadata),
                'progress_markers': self._identify_progress_markers(analysis_data),
                'momentum_indicators': self._assess_momentum_indicators(analysis_data),
                'transition_points': self._identify_transition_points(analysis_data),
                'story_arc_position': self._determine_story_arc_position(analysis_data)
            }
            
            return progression
            
        except Exception as e:
            logger.error("Story progression analysis failed", error=str(e))
            return {'error': f'Story progression analysis failed: {str(e)}'}

    def _identify_narrative_themes(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Identify key narrative themes emerging from the discussion"""
        try:
            themes = []
            
            # Extract themes from transcript analysis
            transcript_data = analysis_data.get('transcript_analysis', {})
            if transcript_data:
                # Look for recurring topics and concepts
                segments = transcript_data.get('segments', [])
                theme_keywords = defaultdict(int)
                
                # Common organizational themes
                theme_patterns = {
                    'transformation': ['change', 'transform', 'evolve', 'shift', 'transition'],
                    'growth': ['grow', 'expand', 'scale', 'develop', 'progress'],
                    'innovation': ['innovate', 'creative', 'new', 'novel', 'breakthrough'],
                    'collaboration': ['together', 'team', 'collaborate', 'partnership', 'unity'],
                    'leadership': ['lead', 'guide', 'direct', 'vision', 'inspire'],
                    'resilience': ['adapt', 'overcome', 'resilient', 'challenge', 'persevere'],
                    'purpose': ['mission', 'purpose', 'meaning', 'impact', 'legacy'],
                    'excellence': ['quality', 'excellence', 'best', 'optimize', 'improve']
                }
                
                for segment in segments:
                    text = segment.get('text', '').lower()
                    for theme, keywords in theme_patterns.items():
                        count = sum(1 for keyword in keywords if keyword in text)
                        if count > 0:
                            theme_keywords[theme] += count
                
                # Select top themes
                sorted_themes = sorted(theme_keywords.items(), key=lambda x: x[1], reverse=True)
                themes = [theme for theme, count in sorted_themes[:5] if count > 0]
            
            # Add default themes if none found
            if not themes:
                themes = ['organizational_development', 'strategic_alignment', 'team_collaboration']
            
            return themes
            
        except Exception as e:
            logger.error("Narrative themes identification failed", error=str(e))
            return ['organizational_development']

    def _analyze_character_development(self, analysis_data: Dict[str, Any], 
                                     meeting_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how participants/roles are evolving"""
        try:
            participants = meeting_metadata.get('participants', [])
            character_development = {}
            
            # Analyze each participant's role and evolution
            for participant in participants:
                character_development[participant] = {
                    'role_evolution': self._assess_role_evolution(participant, analysis_data),
                    'leadership_development': self._assess_leadership_development(participant, analysis_data),
                    'skill_growth': self._assess_skill_growth(participant, analysis_data),
                    'influence_trajectory': self._assess_influence_trajectory(participant, analysis_data)
                }
            
            # Add team-level character development
            character_development['team_dynamics'] = {
                'collective_maturity': self._assess_collective_maturity(analysis_data),
                'collaboration_evolution': self._assess_collaboration_evolution(analysis_data),
                'decision_making_sophistication': self._assess_decision_making_sophistication(analysis_data)
            }
            
            return character_development
            
        except Exception as e:
            logger.error("Character development analysis failed", error=str(e))
            return {'error': f'Character development analysis failed: {str(e)}'}

    def _identify_plot_points(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify significant events and turning points"""
        try:
            plot_points = []
            
            # Major decisions as plot points
            decisions = analysis_data.get('decisions', [])
            for decision in decisions:
                if decision.get('priority') in ['critical', 'high']:
                    plot_points.append({
                        'type': 'decision',
                        'title': decision.get('title', 'Major Decision'),
                        'significance': 'high',
                        'impact': decision.get('impact_analysis', 'Significant organizational impact'),
                        'timestamp': decision.get('timestamp', 'During meeting')
                    })
            
            # Strategic breakthroughs as plot points
            strategic_data = analysis_data.get('strategic_analysis', {})
            if strategic_data.get('breakthrough_insights'):
                plot_points.append({
                    'type': 'breakthrough',
                    'title': 'Strategic Breakthrough',
                    'significance': 'high',
                    'impact': 'New strategic understanding achieved',
                    'timestamp': 'During strategic discussion'
                })
            
            # Conflict resolution as plot points
            conflicts = analysis_data.get('conflicts', [])
            for conflict in conflicts:
                if conflict.get('resolution_status') == 'resolved':
                    plot_points.append({
                        'type': 'resolution',
                        'title': f"Resolution: {conflict.get('topic', 'Conflict')}",
                        'significance': 'medium',
                        'impact': 'Team alignment improved',
                        'timestamp': conflict.get('resolution_time', 'During meeting')
                    })
            
            return plot_points[:10]  # Limit to top 10 plot points
            
        except Exception as e:
            logger.error("Plot points identification failed", error=str(e))
            return [{'type': 'meeting', 'title': 'Meeting Conducted', 'significance': 'medium', 'impact': 'Team alignment and progress', 'timestamp': 'Meeting duration'}]    def
 _generate_solution_components(self, analysis_data: Dict[str, Any], 
                                    meeting_metadata: Dict[str, Any]) -> List[SolutionComponent]:
        """Generate individual solution components from analysis"""
        try:
            components = []
            
            # Generate components from decisions
            decisions = analysis_data.get('decisions', [])
            for i, decision in enumerate(decisions):
                component = SolutionComponent(
                    id=f"decision-component-{i}",
                    title=f"Decision Implementation: {decision.get('title', 'Decision')}",
                    description=decision.get('implementation_plan', 'Implementation plan to be developed'),
                    category='strategic',
                    implementation_complexity=self._assess_implementation_complexity(decision),
                    resource_requirements=self._extract_resource_requirements(decision),
                    dependencies=decision.get('dependencies', []),
                    success_metrics=decision.get('success_criteria', []),
                    risk_factors=self._extract_risk_factors_from_decision(decision),
                    timeline=decision.get('timeline', {}),
                    stakeholders=decision.get('stakeholders', []),
                    exponential_potential=decision.get('exponential_potential', 0.5),
                    confidence_score=decision.get('confidence_score', 0.7)
                )
                components.append(component)
            
            # Generate components from actions
            actions = analysis_data.get('actions', [])
            for i, action in enumerate(actions):
                component = SolutionComponent(
                    id=f"action-component-{i}",
                    title=f"Action Implementation: {action.get('title', 'Action')}",
                    description=action.get('description', 'Action description to be provided'),
                    category=self._categorize_action_component(action),
                    implementation_complexity=self._assess_action_complexity(action),
                    resource_requirements=self._extract_action_resources(action),
                    dependencies=action.get('dependencies', []),
                    success_metrics=action.get('success_criteria', []),
                    risk_factors=action.get('risk_factors', []),
                    timeline=self._create_action_timeline(action),
                    stakeholders=[action.get('owner', 'TBD')] + action.get('assignees', []),
                    exponential_potential=action.get('exponential_potential', 0.3),
                    confidence_score=action.get('confidence_score', 0.7)
                )
                components.append(component)
            
            # Generate components from strategic implications
            strategic_implications = analysis_data.get('strategic_implications', [])
            for i, implication in enumerate(strategic_implications):
                component = SolutionComponent(
                    id=f"strategic-component-{i}",
                    title=f"Strategic Initiative: {implication.get('title', 'Initiative')}",
                    description=implication.get('description', 'Strategic initiative description'),
                    category='strategic',
                    implementation_complexity='high',
                    resource_requirements=self._extract_strategic_resources(implication),
                    dependencies=[],
                    success_metrics=implication.get('success_metrics', []),
                    risk_factors=[implication.get('risk_evaluation', 'Risk assessment needed')],
                    timeline=self._create_strategic_timeline(implication),
                    stakeholders=[],
                    exponential_potential=0.7,
                    confidence_score=implication.get('confidence_score', 0.6)
                )
                components.append(component)
            
            return components
            
        except Exception as e:
            logger.error("Solution components generation failed", error=str(e))
            return []

    def _develop_implementation_strategy(self, solution_components: List[SolutionComponent], 
                                       analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Develop overall implementation strategy for the solution portfolio"""
        try:
            strategy = {
                'approach': self._determine_implementation_approach(solution_components),
                'phases': self._create_implementation_phases(solution_components),
                'critical_path': self._identify_critical_path(solution_components),
                'resource_strategy': self._develop_resource_strategy(solution_components),
                'risk_mitigation': self._develop_risk_mitigation_strategy(solution_components),
                'success_criteria': self._define_portfolio_success_criteria(solution_components),
                'monitoring_approach': self._design_monitoring_approach(solution_components)
            }
            
            return strategy
            
        except Exception as e:
            logger.error("Implementation strategy development failed", error=str(e))
            return {'error': f'Strategy development failed: {str(e)}'}

    def _calculate_resource_allocation(self, solution_components: List[SolutionComponent]) -> Dict[str, Any]:
        """Calculate resource allocation across solution components"""
        try:
            allocation = {
                'total_estimated_effort': 0,
                'resource_distribution': {},
                'budget_allocation': {},
                'timeline_distribution': {},
                'skill_requirements': defaultdict(int),
                'capacity_planning': {}
            }
            
            for component in solution_components:
                resources = component.resource_requirements
                
                # Aggregate effort estimates
                effort = resources.get('effort_estimate', 0)
                allocation['total_estimated_effort'] += effort
                
                # Track resource distribution
                allocation['resource_distribution'][component.id] = {
                    'effort_percentage': 0,  # Will be calculated after totals
                    'complexity': component.implementation_complexity,
                    'priority': self._determine_component_priority(component)
                }
                
                # Aggregate skill requirements
                skills = resources.get('skills_required', [])
                for skill in skills:
                    allocation['skill_requirements'][skill] += 1
            
            # Calculate percentages
            total_effort = allocation['total_estimated_effort']
            if total_effort > 0:
                for component_id, dist in allocation['resource_distribution'].items():
                    component = next(c for c in solution_components if c.id == component_id)
                    effort = component.resource_requirements.get('effort_estimate', 0)
                    dist['effort_percentage'] = (effort / total_effort) * 100
            
            return allocation
            
        except Exception as e:
            logger.error("Resource allocation calculation failed", error=str(e))
            return {'error': f'Resource allocation failed: {str(e)}'}

    def _identify_synergy_opportunities(self, solution_components: List[SolutionComponent]) -> List[Dict[str, Any]]:
        """Identify synergy opportunities between solution components"""
        try:
            synergies = []
            
            # Check for components that can be combined or coordinated
            for i, component1 in enumerate(solution_components):
                for j, component2 in enumerate(solution_components[i+1:], i+1):
                    synergy_score = self._calculate_synergy_score(component1, component2)
                    
                    if synergy_score > 0.6:  # Significant synergy threshold
                        synergies.append({
                            'component_1': component1.id,
                            'component_2': component2.id,
                            'synergy_type': self._identify_synergy_type(component1, component2),
                            'synergy_score': synergy_score,
                            'benefits': self._describe_synergy_benefits(component1, component2),
                            'implementation_approach': self._suggest_synergy_implementation(component1, component2)
                        })
            
            # Sort by synergy score
            synergies.sort(key=lambda x: x['synergy_score'], reverse=True)
            
            return synergies[:10]  # Top 10 synergies
            
        except Exception as e:
            logger.error("Synergy opportunities identification failed", error=str(e))
            return []

    def _determine_priority_sequencing(self, solution_components: List[SolutionComponent]) -> List[str]:
        """Determine recommended implementation sequence"""
        try:
            # Score components based on multiple factors
            component_scores = []
            
            for component in solution_components:
                score = self._calculate_priority_score(component)
                component_scores.append((component.id, score))
            
            # Sort by priority score (highest first)
            component_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return ordered list of component IDs
            return [component_id for component_id, _ in component_scores]
            
        except Exception as e:
            logger.error("Priority sequencing determination failed", error=str(e))
            return [component.id for component in solution_components]

    def _calculate_priority_score(self, component: SolutionComponent) -> float:
        """Calculate priority score for a solution component"""
        try:
            score = 0.0
            
            # Exponential potential factor (0-1)
            score += component.exponential_potential * 0.3
            
            # Confidence factor (0-1)
            score += component.confidence_score * 0.2
            
            # Complexity factor (inverse - simpler is higher priority)
            complexity_scores = {'low': 1.0, 'medium': 0.7, 'high': 0.4, 'very_high': 0.2}
            score += complexity_scores.get(component.implementation_complexity, 0.5) * 0.2
            
            # Dependencies factor (fewer dependencies = higher priority)
            dependency_factor = max(0, 1 - (len(component.dependencies) * 0.1))
            score += dependency_factor * 0.15
            
            # Risk factor (lower risk = higher priority)
            risk_factor = max(0, 1 - (len(component.risk_factors) * 0.1))
            score += risk_factor * 0.15
            
            return min(1.0, score)  # Cap at 1.0
            
        except Exception as e:
            logger.error("Priority score calculation failed", error=str(e))
            return 0.5 
   async def _generate_human_needs_fulfillment_plan(self, analysis_data: Dict[str, Any], 
                                                   meeting_metadata: Dict[str, Any]) -> HumanNeedsFulfillmentPlan:
        """Generate targeted interventions and success metrics for human needs fulfillment"""
        try:
            plan_id = str(uuid.uuid4())
            
            # Generate individual fulfillment plans
            individual_plans = self._generate_individual_fulfillment_plans(analysis_data, meeting_metadata)
            
            # Generate team interventions
            team_interventions = self._generate_team_interventions(analysis_data, meeting_metadata)
            
            # Generate organizational initiatives
            organizational_initiatives = self._generate_organizational_initiatives(analysis_data, meeting_metadata)
            
            # Create need-specific strategies
            need_specific_strategies = self._create_need_specific_strategies(analysis_data)
            
            # Create implementation timeline
            implementation_timeline = self._create_fulfillment_timeline(individual_plans, team_interventions)
            
            # Define success metrics
            success_metrics = self._define_fulfillment_success_metrics(need_specific_strategies)
            
            # Create monitoring framework
            monitoring_framework = self._create_fulfillment_monitoring_framework(success_metrics)
            
            # Define feedback mechanisms
            feedback_mechanisms = self._define_feedback_mechanisms()
            
            # Create adjustment protocols
            adjustment_protocols = self._create_adjustment_protocols()
            
            # Calculate resource requirements
            resource_requirements = self._calculate_fulfillment_resource_requirements(
                individual_plans, team_interventions, organizational_initiatives
            )
            
            # Define stakeholder roles
            stakeholder_roles = self._define_stakeholder_roles(meeting_metadata)
            
            # Identify integration points
            integration_points = self._identify_integration_points(analysis_data)
            
            # Calculate confidence score
            confidence_score = self._calculate_fulfillment_confidence(analysis_data, individual_plans)
            
            return HumanNeedsFulfillmentPlan(
                id=plan_id,
                individual_plans=individual_plans,
                team_interventions=team_interventions,
                organizational_initiatives=organizational_initiatives,
                need_specific_strategies=need_specific_strategies,
                implementation_timeline=implementation_timeline,
                success_metrics=success_metrics,
                monitoring_framework=monitoring_framework,
                feedback_mechanisms=feedback_mechanisms,
                adjustment_protocols=adjustment_protocols,
                resource_requirements=resource_requirements,
                stakeholder_roles=stakeholder_roles,
                integration_points=integration_points,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error("Human needs fulfillment plan generation failed", error=str(e))
            # Return minimal plan structure
            return HumanNeedsFulfillmentPlan(
                id=str(uuid.uuid4()),
                individual_plans=[],
                team_interventions=[],
                organizational_initiatives=[],
                need_specific_strategies={},
                implementation_timeline={'error': 'Timeline generation failed'},
                success_metrics={},
                monitoring_framework={'error': 'Monitoring framework creation failed'},
                feedback_mechanisms=["Feedback mechanisms to be established"],
                adjustment_protocols=["Adjustment protocols to be developed"],
                resource_requirements={'error': 'Resource calculation failed'},
                stakeholder_roles={},
                integration_points=["Integration points to be identified"],
                confidence_score=0.1
            )

    async def _generate_integrity_alignment_check(self, analysis_data: Dict[str, Any], 
                                                meeting_metadata: Dict[str, Any]) -> IntegrityAlignmentCheck:
        """Generate consistency validation and quality assurance"""
        try:
            check_id = str(uuid.uuid4())
            
            # Perform consistency analysis
            consistency_analysis = self._perform_consistency_analysis(analysis_data)
            
            # Assess alignment between components
            alignment_assessment = self._assess_component_alignment(analysis_data)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(analysis_data, meeting_metadata)
            
            # Validate outputs
            validation_results = self._validate_outputs(analysis_data)
            
            # Identify discrepancies
            discrepancy_identification = self._identify_discrepancies(analysis_data)
            
            # Generate resolution recommendations
            resolution_recommendations = self._generate_resolution_recommendations(discrepancy_identification)
            
            # Validate confidence scores
            confidence_validation = self._validate_confidence_scores(analysis_data)
            
            # Check completeness
            completeness_check = self._check_completeness(analysis_data, meeting_metadata)
            
            # Assess accuracy
            accuracy_assessment = self._assess_accuracy(analysis_data, meeting_metadata)
            
            # Calculate reliability indicators
            reliability_indicators = self._calculate_reliability_indicators(analysis_data)
            
            # Generate improvement suggestions
            improvement_suggestions = self._generate_improvement_suggestions(
                quality_metrics, discrepancy_identification, completeness_check
            )
            
            # Calculate overall integrity score
            overall_integrity_score = self._calculate_overall_integrity_score(
                consistency_analysis, alignment_assessment, quality_metrics
            )
            
            return IntegrityAlignmentCheck(
                id=check_id,
                consistency_analysis=consistency_analysis,
                alignment_assessment=alignment_assessment,
                quality_metrics=quality_metrics,
                validation_results=validation_results,
                discrepancy_identification=discrepancy_identification,
                resolution_recommendations=resolution_recommendations,
                confidence_validation=confidence_validation,
                completeness_check=completeness_check,
                accuracy_assessment=accuracy_assessment,
                reliability_indicators=reliability_indicators,
                improvement_suggestions=improvement_suggestions,
                overall_integrity_score=overall_integrity_score
            )
            
        except Exception as e:
            logger.error("Integrity alignment check generation failed", error=str(e))
            # Return minimal check structure
            return IntegrityAlignmentCheck(
                id=str(uuid.uuid4()),
                consistency_analysis={'error': 'Consistency analysis failed'},
                alignment_assessment={'error': 'Alignment assessment failed'},
                quality_metrics={'overall_quality': 0.1},
                validation_results={'error': 'Validation failed'},
                discrepancy_identification=[],
                resolution_recommendations=["Review analysis inputs and methodology"],
                confidence_validation={'overall_confidence': 0.1},
                completeness_check={'error': 'Completeness check failed'},
                accuracy_assessment={'error': 'Accuracy assessment failed'},
                reliability_indicators={'overall_reliability': 0.1},
                improvement_suggestions=["Improve data quality and analysis methodology"],
                overall_integrity_score=0.1
            )