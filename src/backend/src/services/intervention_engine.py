"""
Targeted Intervention Generation System for Intelligence OS
Creates personalized and team-level interventions based on human needs analysis
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import structlog
from collections import defaultdict
import hashlib

from .human_needs_engine import HumanNeed, human_needs_engine
from .need_imbalance_detector import need_imbalance_detector, ImbalanceType, ImbalanceSeverity

logger = structlog.get_logger(__name__)

class InterventionType(Enum):
    """Types of interventions"""
    INDIVIDUAL = "individual"
    TEAM = "team"
    ORGANIZATIONAL = "organizational"
    PEER_TO_PEER = "peer_to_peer"
    SELF_DIRECTED = "self_directed"

class InterventionCategory(Enum):
    """Categories of interventions"""
    BEHAVIORAL = "behavioral"
    ENVIRONMENTAL = "environmental"
    STRUCTURAL = "structural"
    SOCIAL = "social"
    COGNITIVE = "cognitive"
    SKILL_BUILDING = "skill_building"

class InterventionStatus(Enum):
    """Status of interventions"""
    RECOMMENDED = "recommended"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class EffectivenessLevel(Enum):
    """Effectiveness levels for interventions"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class InterventionTemplate:
    """Template for generating interventions"""
    id: str
    name: str
    description: str
    category: InterventionCategory
    target_needs: List[HumanNeed]
    intervention_type: InterventionType
    duration_estimate: timedelta
    difficulty_level: str  # 'easy', 'moderate', 'challenging'
    required_resources: List[str]
    success_metrics: List[str]
    contraindications: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)

@dataclass
class PersonalizedIntervention:
    """Personalized intervention recommendation"""
    id: str
    template_id: str
    participant_id: str
    target_needs: List[HumanNeed]
    title: str
    description: str
    personalized_approach: str
    expected_outcomes: List[str]
    timeline: Dict[str, Any]
    resources_needed: List[str]
    success_metrics: List[str]
    privacy_level: str
    status: InterventionStatus = InterventionStatus.RECOMMENDED
    created_at: datetime = field(default_factory=datetime.utcnow)
    effectiveness_prediction: float = 0.0
    risk_assessment: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TeamIntervention:
    """Team-level intervention strategy"""
    id: str
    team_id: str
    target_needs: List[HumanNeed]
    title: str
    description: str
    team_approach: str
    individual_components: List[str]
    group_activities: List[str]
    expected_outcomes: List[str]
    timeline: Dict[str, Any]
    facilitator_requirements: List[str]
    success_metrics: List[str]
    status: InterventionStatus = InterventionStatus.RECOMMENDED
    created_at: datetime = field(default_factory=datetime.utcnow)
    participants: List[str] = field(default_factory=list)

@dataclass
class InterventionOutcome:
    """Tracks the outcome of an intervention"""
    intervention_id: str
    participant_id: str
    completion_date: datetime
    effectiveness_rating: EffectivenessLevel
    objective_measures: Dict[str, float]
    subjective_feedback: Dict[str, Any]
    lessons_learned: List[str]
    recommendations_for_future: List[str]
    privacy_protected: bool = True

class InterventionEngine:
    """Comprehensive intervention generation and tracking system"""
    
    def __init__(self):
        self.intervention_templates = self._initialize_intervention_templates()
        self.active_interventions: Dict[str, PersonalizedIntervention] = {}
        self.team_interventions: Dict[str, TeamIntervention] = {}
        self.intervention_outcomes: List[InterventionOutcome] = []
        self.effectiveness_database: Dict[str, List[float]] = defaultdict(list)
        
        # Privacy settings
        self.privacy_levels = ['public', 'team', 'manager', 'private', 'anonymous']
        self.anonymization_threshold = 5  # Minimum group size for anonymized data
        
        # Personalization factors
        self.personalization_weights = {
            'personality_type': 0.3,
            'work_style': 0.2,
            'past_effectiveness': 0.25,
            'current_context': 0.15,
            'preferences': 0.1
        }
    
    def _initialize_intervention_templates(self) -> Dict[str, InterventionTemplate]:
        """Initialize intervention templates for different needs and situations"""
        templates = {}
        
        # Certainty-focused interventions
        templates['certainty_structure'] = InterventionTemplate(
            id='certainty_structure',
            name='Structured Planning Framework',
            description='Implement systematic planning and tracking processes',
            category=InterventionCategory.STRUCTURAL,
            target_needs=[HumanNeed.CERTAINTY],
            intervention_type=InterventionType.INDIVIDUAL,
            duration_estimate=timedelta(weeks=2),
            difficulty_level='easy',
            required_resources=['Planning tools', 'Time management system'],
            success_metrics=['Reduced anxiety levels', 'Improved task completion', 'Better time management'],
            prerequisites=['Basic organizational skills']
        )
        
        templates['certainty_communication'] = InterventionTemplate(
            id='certainty_communication',
            name='Clear Communication Protocols',
            description='Establish regular check-ins and transparent communication',
            category=InterventionCategory.SOCIAL,
            target_needs=[HumanNeed.CERTAINTY],
            intervention_type=InterventionType.TEAM,
            duration_estimate=timedelta(weeks=4),
            difficulty_level='moderate',
            required_resources=['Meeting schedule', 'Communication platform'],
            success_metrics=['Improved information flow', 'Reduced uncertainty', 'Better team alignment']
        )
        
        # Variety-focused interventions
        templates['variety_rotation'] = InterventionTemplate(
            id='variety_rotation',
            name='Role and Task Rotation',
            description='Introduce variety through rotating responsibilities',
            category=InterventionCategory.STRUCTURAL,
            target_needs=[HumanNeed.VARIETY],
            intervention_type=InterventionType.ORGANIZATIONAL,
            duration_estimate=timedelta(weeks=8),
            difficulty_level='moderate',
            required_resources=['Cross-training time', 'Skill development support'],
            success_metrics=['Increased engagement', 'Skill diversification', 'Reduced boredom']
        )
        
        templates['variety_innovation'] = InterventionTemplate(
            id='variety_innovation',
            name='Innovation Time and Challenges',
            description='Dedicated time for creative projects and innovation',
            category=InterventionCategory.BEHAVIORAL,
            target_needs=[HumanNeed.VARIETY, HumanNeed.GROWTH],
            intervention_type=InterventionType.INDIVIDUAL,
            duration_estimate=timedelta(weeks=6),
            difficulty_level='easy',
            required_resources=['Protected time', 'Innovation resources'],
            success_metrics=['Creative output', 'Problem-solving improvement', 'Job satisfaction']
        )
        
        # Significance-focused interventions
        templates['significance_recognition'] = InterventionTemplate(
            id='significance_recognition',
            name='Recognition and Appreciation Program',
            description='Systematic recognition of contributions and achievements',
            category=InterventionCategory.SOCIAL,
            target_needs=[HumanNeed.SIGNIFICANCE],
            intervention_type=InterventionType.TEAM,
            duration_estimate=timedelta(weeks=12),
            difficulty_level='easy',
            required_resources=['Recognition platform', 'Manager training'],
            success_metrics=['Increased motivation', 'Better performance', 'Higher retention']
        )
        
        templates['significance_expertise'] = InterventionTemplate(
            id='significance_expertise',
            name='Expertise Sharing and Mentoring',
            description='Opportunities to share knowledge and mentor others',
            category=InterventionCategory.SKILL_BUILDING,
            target_needs=[HumanNeed.SIGNIFICANCE, HumanNeed.CONTRIBUTION],
            intervention_type=InterventionType.PEER_TO_PEER,
            duration_estimate=timedelta(weeks=16),
            difficulty_level='moderate',
            required_resources=['Mentoring program', 'Knowledge sharing platform'],
            success_metrics=['Knowledge transfer', 'Leadership development', 'Sense of value']
        )
        
        # Connection-focused interventions
        templates['connection_team_building'] = InterventionTemplate(
            id='connection_team_building',
            name='Team Building and Social Connection',
            description='Activities to strengthen team bonds and relationships',
            category=InterventionCategory.SOCIAL,
            target_needs=[HumanNeed.CONNECTION],
            intervention_type=InterventionType.TEAM,
            duration_estimate=timedelta(weeks=8),
            difficulty_level='easy',
            required_resources=['Activity budget', 'Facilitation support'],
            success_metrics=['Team cohesion', 'Communication quality', 'Collaboration effectiveness']
        )
        
        templates['connection_mentoring'] = InterventionTemplate(
            id='connection_mentoring',
            name='Buddy System and Mentoring',
            description='Pair individuals for mutual support and connection',
            category=InterventionCategory.SOCIAL,
            target_needs=[HumanNeed.CONNECTION, HumanNeed.GROWTH],
            intervention_type=InterventionType.PEER_TO_PEER,
            duration_estimate=timedelta(weeks=12),
            difficulty_level='moderate',
            required_resources=['Matching system', 'Training materials'],
            success_metrics=['Relationship quality', 'Support network strength', 'Knowledge sharing']
        )
        
        # Growth-focused interventions
        templates['growth_learning'] = InterventionTemplate(
            id='growth_learning',
            name='Personalized Learning and Development',
            description='Tailored learning opportunities and skill development',
            category=InterventionCategory.SKILL_BUILDING,
            target_needs=[HumanNeed.GROWTH],
            intervention_type=InterventionType.INDIVIDUAL,
            duration_estimate=timedelta(weeks=12),
            difficulty_level='moderate',
            required_resources=['Learning budget', 'Time allocation', 'Learning platforms'],
            success_metrics=['Skill acquisition', 'Performance improvement', 'Career advancement']
        )
        
        templates['growth_challenges'] = InterventionTemplate(
            id='growth_challenges',
            name='Stretch Assignments and Challenges',
            description='Challenging projects that promote growth and learning',
            category=InterventionCategory.BEHAVIORAL,
            target_needs=[HumanNeed.GROWTH, HumanNeed.SIGNIFICANCE],
            intervention_type=InterventionType.INDIVIDUAL,
            duration_estimate=timedelta(weeks=8),
            difficulty_level='challenging',
            required_resources=['Project opportunities', 'Support and coaching'],
            success_metrics=['Capability expansion', 'Confidence building', 'Achievement recognition']
        )
        
        # Contribution-focused interventions
        templates['contribution_purpose'] = InterventionTemplate(
            id='contribution_purpose',
            name='Purpose Connection and Impact Visibility',
            description='Connect work to larger purpose and show impact',
            category=InterventionCategory.COGNITIVE,
            target_needs=[HumanNeed.CONTRIBUTION],
            intervention_type=InterventionType.INDIVIDUAL,
            duration_estimate=timedelta(weeks=4),
            difficulty_level='easy',
            required_resources=['Impact measurement', 'Communication materials'],
            success_metrics=['Purpose clarity', 'Motivation increase', 'Engagement improvement']
        )
        
        templates['contribution_service'] = InterventionTemplate(
            id='contribution_service',
            name='Community Service and Volunteering',
            description='Opportunities for community service and giving back',
            category=InterventionCategory.SOCIAL,
            target_needs=[HumanNeed.CONTRIBUTION],
            intervention_type=InterventionType.ORGANIZATIONAL,
            duration_estimate=timedelta(weeks=16),
            difficulty_level='easy',
            required_resources=['Volunteer time', 'Community partnerships'],
            success_metrics=['Community impact', 'Personal fulfillment', 'Team bonding']
        )
        
        return templates
    
    async def generate_personalized_interventions(self, participant_id: str, 
                                                needs_assessment: Dict[str, Any],
                                                context: Dict[str, Any] = None) -> List[PersonalizedIntervention]:
        """Generate personalized intervention recommendations"""
        try:
            interventions = []
            need_assessments = needs_assessment.get('need_assessments', {})
            participant_context = context or {}
            
            # Identify needs requiring intervention
            intervention_needs = []
            for need_name, need_data in need_assessments.items():
                imbalance_type = need_data.get('imbalance_type')
                score = need_data.get('score', 0.5)
                
                if imbalance_type or score < 0.4 or score > 0.8:
                    intervention_needs.append((HumanNeed(need_name), need_data))
            
            # Generate interventions for each need
            for need, need_data in intervention_needs:
                suitable_templates = self._find_suitable_templates(need, need_data, participant_context)
                
                for template in suitable_templates[:3]:  # Top 3 templates per need
                    personalized_intervention = await self._personalize_intervention(
                        template, participant_id, need, need_data, participant_context
                    )
                    interventions.append(personalized_intervention)
            
            # Rank interventions by predicted effectiveness
            interventions.sort(key=lambda x: x.effectiveness_prediction, reverse=True)
            
            return interventions[:10]  # Return top 10 interventions
            
        except Exception as e:
            logger.error("Personalized intervention generation failed", 
                        participant=participant_id, error=str(e))
            return []
    
    async def generate_team_interventions(self, team_id: str, 
                                        team_assessment: Dict[str, Any],
                                        individual_assessments: Dict[str, Any] = None,
                                        context: Dict[str, Any] = None) -> List[TeamIntervention]:
        """Generate team-level intervention strategies"""
        try:
            team_interventions = []
            collective_assessments = team_assessment.get('collective_assessments', {})
            team_dynamics = team_assessment.get('team_dynamics', {})
            
            # Identify team-level needs requiring intervention
            team_needs = []
            for need_name, need_data in collective_assessments.items():
                score = need_data.get('score', 0.5)
                imbalance_type = need_data.get('imbalance_type')
                
                if imbalance_type or score < 0.4:
                    team_needs.append((HumanNeed(need_name), need_data))
            
            # Address team dynamics issues
            if team_dynamics.get('collaboration_level', 0.5) < 0.4:
                team_needs.append((HumanNeed.CONNECTION, {'score': 0.3, 'imbalance_type': 'lacking'}))
            
            if team_dynamics.get('innovation_capacity', 0.5) < 0.4:
                team_needs.append((HumanNeed.VARIETY, {'score': 0.3, 'imbalance_type': 'lacking'}))
            
            # Generate team interventions
            for need, need_data in team_needs:
                team_templates = self._find_team_templates(need, need_data, team_dynamics)
                
                for template in team_templates[:2]:  # Top 2 templates per need
                    team_intervention = await self._create_team_intervention(
                        template, team_id, need, need_data, individual_assessments, context
                    )
                    team_interventions.append(team_intervention)
            
            return team_interventions
            
        except Exception as e:
            logger.error("Team intervention generation failed", team_id=team_id, error=str(e))
            return []
    
    def _find_suitable_templates(self, need: HumanNeed, need_data: Dict[str, Any], 
                               context: Dict[str, Any]) -> List[InterventionTemplate]:
        """Find suitable intervention templates for a specific need"""
        try:
            suitable_templates = []
            
            for template in self.intervention_templates.values():
                if need in template.target_needs:
                    # Check if template is suitable for the context
                    suitability_score = self._calculate_template_suitability(
                        template, need_data, context
                    )
                    
                    if suitability_score > 0.5:
                        suitable_templates.append((template, suitability_score))
            
            # Sort by suitability score
            suitable_templates.sort(key=lambda x: x[1], reverse=True)
            
            return [template for template, _ in suitable_templates]
            
        except Exception as e:
            logger.error("Template finding failed", error=str(e))
            return []
    
    def _find_team_templates(self, need: HumanNeed, need_data: Dict[str, Any], 
                           team_dynamics: Dict[str, Any]) -> List[InterventionTemplate]:
        """Find suitable team intervention templates"""
        try:
            team_templates = []
            
            for template in self.intervention_templates.values():
                if (need in template.target_needs and 
                    template.intervention_type in [InterventionType.TEAM, InterventionType.ORGANIZATIONAL]):
                    
                    suitability_score = self._calculate_team_template_suitability(
                        template, need_data, team_dynamics
                    )
                    
                    if suitability_score > 0.5:
                        team_templates.append((template, suitability_score))
            
            # Sort by suitability score
            team_templates.sort(key=lambda x: x[1], reverse=True)
            
            return [template for template, _ in team_templates]
            
        except Exception as e:
            logger.error("Team template finding failed", error=str(e))
            return []
    
    def _calculate_template_suitability(self, template: InterventionTemplate, 
                                      need_data: Dict[str, Any], 
                                      context: Dict[str, Any]) -> float:
        """Calculate how suitable a template is for the specific situation"""
        try:
            suitability_score = 0.5  # Base score
            
            # Adjust based on need severity
            score = need_data.get('score', 0.5)
            if score < 0.3:  # Severe need
                if template.difficulty_level == 'easy':
                    suitability_score += 0.2
                elif template.difficulty_level == 'challenging':
                    suitability_score -= 0.1
            
            # Adjust based on available resources
            available_resources = context.get('available_resources', [])
            required_resources = template.required_resources
            
            if all(resource in available_resources for resource in required_resources):
                suitability_score += 0.2
            elif any(resource in available_resources for resource in required_resources):
                suitability_score += 0.1
            
            # Adjust based on past effectiveness
            template_effectiveness = self.effectiveness_database.get(template.id, [])
            if template_effectiveness:
                avg_effectiveness = sum(template_effectiveness) / len(template_effectiveness)
                suitability_score += (avg_effectiveness - 0.5) * 0.3
            
            # Adjust based on time constraints
            available_time = context.get('available_time_weeks', 12)
            required_weeks = template.duration_estimate.days / 7
            
            if required_weeks <= available_time:
                suitability_score += 0.1
            else:
                suitability_score -= 0.2
            
            return max(0.0, min(1.0, suitability_score))
            
        except Exception as e:
            logger.error("Template suitability calculation failed", error=str(e))
            return 0.5
    
    def _calculate_team_template_suitability(self, template: InterventionTemplate, 
                                           need_data: Dict[str, Any], 
                                           team_dynamics: Dict[str, Any]) -> float:
        """Calculate suitability for team templates"""
        try:
            suitability_score = 0.5
            
            # Adjust based on team dynamics
            if template.category == InterventionCategory.SOCIAL:
                collaboration_level = team_dynamics.get('collaboration_level', 0.5)
                if collaboration_level < 0.4:
                    suitability_score += 0.3  # High need for social interventions
            
            # Adjust based on team size (from context if available)
            # This would be enhanced with actual team size data
            
            return max(0.0, min(1.0, suitability_score))
            
        except Exception as e:
            logger.error("Team template suitability calculation failed", error=str(e))
            return 0.5 
   
    async def _personalize_intervention(self, template: InterventionTemplate, 
                                      participant_id: str, need: HumanNeed, 
                                      need_data: Dict[str, Any], 
                                      context: Dict[str, Any]) -> PersonalizedIntervention:
        """Create a personalized intervention from a template"""
        try:
            intervention_id = str(uuid.uuid4())
            
            # Personalize the approach based on context
            personalized_approach = await self._create_personalized_approach(
                template, participant_id, need_data, context
            )
            
            # Calculate effectiveness prediction
            effectiveness_prediction = await self._predict_effectiveness(
                template, participant_id, need_data, context
            )
            
            # Determine privacy level
            privacy_level = self._determine_privacy_level(participant_id, need, context)
            
            # Create timeline
            timeline = self._create_intervention_timeline(template, context)
            
            # Assess risks
            risk_assessment = await self._assess_intervention_risks(template, need_data, context)
            
            return PersonalizedIntervention(
                id=intervention_id,
                template_id=template.id,
                participant_id=participant_id,
                target_needs=[need],
                title=f"Personalized {template.name}",
                description=template.description,
                personalized_approach=personalized_approach,
                expected_outcomes=self._generate_expected_outcomes(template, need_data),
                timeline=timeline,
                resources_needed=template.required_resources,
                success_metrics=template.success_metrics,
                privacy_level=privacy_level,
                effectiveness_prediction=effectiveness_prediction,
                risk_assessment=risk_assessment
            )
            
        except Exception as e:
            logger.error("Intervention personalization failed", error=str(e))
            # Return basic intervention
            return PersonalizedIntervention(
                id=str(uuid.uuid4()),
                template_id=template.id,
                participant_id=participant_id,
                target_needs=[need],
                title=template.name,
                description=template.description,
                personalized_approach="Standard approach",
                expected_outcomes=[],
                timeline={},
                resources_needed=[],
                success_metrics=[],
                privacy_level='private'
            )
    
    async def _create_team_intervention(self, template: InterventionTemplate, 
                                     team_id: str, need: HumanNeed, 
                                     need_data: Dict[str, Any],
                                     individual_assessments: Dict[str, Any] = None,
                                     context: Dict[str, Any] = None) -> TeamIntervention:
        """Create a team intervention from a template"""
        try:
            intervention_id = str(uuid.uuid4())
            
            # Create team-specific approach
            team_approach = await self._create_team_approach(
                template, team_id, need_data, individual_assessments, context
            )
            
            # Identify individual components
            individual_components = self._identify_individual_components(
                template, individual_assessments
            )
            
            # Create group activities
            group_activities = self._create_group_activities(template, need_data, context)
            
            # Determine participants
            participants = list(individual_assessments.keys()) if individual_assessments else []
            
            return TeamIntervention(
                id=intervention_id,
                team_id=team_id,
                target_needs=[need],
                title=f"Team {template.name}",
                description=template.description,
                team_approach=team_approach,
                individual_components=individual_components,
                group_activities=group_activities,
                expected_outcomes=self._generate_team_expected_outcomes(template, need_data),
                timeline=self._create_intervention_timeline(template, context),
                facilitator_requirements=self._determine_facilitator_requirements(template),
                success_metrics=template.success_metrics,
                participants=participants
            )
            
        except Exception as e:
            logger.error("Team intervention creation failed", error=str(e))
            return TeamIntervention(
                id=str(uuid.uuid4()),
                team_id=team_id,
                target_needs=[need],
                title=template.name,
                description=template.description,
                team_approach="Standard team approach",
                individual_components=[],
                group_activities=[],
                expected_outcomes=[],
                timeline={},
                facilitator_requirements=[],
                success_metrics=[]
            )
    
    async def _create_personalized_approach(self, template: InterventionTemplate, 
                                          participant_id: str, need_data: Dict[str, Any], 
                                          context: Dict[str, Any]) -> str:
        """Create a personalized approach description"""
        try:
            base_approach = template.description
            
            # Personalize based on need severity
            score = need_data.get('score', 0.5)
            if score < 0.3:
                intensity = "intensive"
            elif score < 0.5:
                intensity = "moderate"
            else:
                intensity = "light"
            
            # Personalize based on context
            work_style = context.get('work_style', 'collaborative')
            personality = context.get('personality_type', 'balanced')
            
            personalized_approach = f"""
            {base_approach}
            
            Personalized for you:
            - Intensity level: {intensity} approach based on current need level
            - Adapted for {work_style} work style
            - Tailored for {personality} personality type
            - Focus on evidence-based practices with measurable outcomes
            """
            
            return personalized_approach.strip()
            
        except Exception as e:
            logger.error("Personalized approach creation failed", error=str(e))
            return template.description
    
    async def _create_team_approach(self, template: InterventionTemplate, 
                                  team_id: str, need_data: Dict[str, Any],
                                  individual_assessments: Dict[str, Any] = None,
                                  context: Dict[str, Any] = None) -> str:
        """Create a team-specific approach description"""
        try:
            base_approach = template.description
            
            # Analyze team composition
            team_size = len(individual_assessments) if individual_assessments else 5
            
            # Customize based on team characteristics
            team_approach = f"""
            {base_approach}
            
            Team-specific approach:
            - Designed for team of {team_size} members
            - Combines individual and group components
            - Includes peer support and accountability
            - Focuses on collective improvement while respecting individual differences
            """
            
            return team_approach.strip()
            
        except Exception as e:
            logger.error("Team approach creation failed", error=str(e))
            return template.description
    
    async def _predict_effectiveness(self, template: InterventionTemplate, 
                                   participant_id: str, need_data: Dict[str, Any], 
                                   context: Dict[str, Any]) -> float:
        """Predict the effectiveness of an intervention for a specific person"""
        try:
            base_effectiveness = 0.6  # Default prediction
            
            # Adjust based on historical data
            template_history = self.effectiveness_database.get(template.id, [])
            if template_history:
                historical_avg = sum(template_history) / len(template_history)
                base_effectiveness = (base_effectiveness + historical_avg) / 2
            
            # Adjust based on need severity (more severe needs may respond better)
            score = need_data.get('score', 0.5)
            if score < 0.3:
                base_effectiveness += 0.1  # Severe needs often respond well
            
            # Adjust based on confidence in assessment
            confidence = need_data.get('confidence', 0.5)
            base_effectiveness *= confidence
            
            # Adjust based on available resources
            available_resources = context.get('available_resources', [])
            required_resources = template.required_resources
            resource_availability = len([r for r in required_resources if r in available_resources]) / len(required_resources) if required_resources else 1.0
            base_effectiveness *= (0.5 + 0.5 * resource_availability)
            
            return max(0.1, min(1.0, base_effectiveness))
            
        except Exception as e:
            logger.error("Effectiveness prediction failed", error=str(e))
            return 0.5
    
    def _determine_privacy_level(self, participant_id: str, need: HumanNeed, 
                               context: Dict[str, Any]) -> str:
        """Determine appropriate privacy level for intervention"""
        try:
            # Default privacy levels based on need sensitivity
            sensitive_needs = [HumanNeed.SIGNIFICANCE, HumanNeed.CONNECTION]
            
            if need in sensitive_needs:
                return 'private'
            else:
                return context.get('preferred_privacy_level', 'team')
                
        except Exception as e:
            logger.error("Privacy level determination failed", error=str(e))
            return 'private'
    
    def _create_intervention_timeline(self, template: InterventionTemplate, 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a timeline for the intervention"""
        try:
            duration_weeks = template.duration_estimate.days / 7
            
            timeline = {
                'total_duration_weeks': duration_weeks,
                'phases': []
            }
            
            # Create phases based on intervention type
            if duration_weeks <= 2:
                timeline['phases'] = [
                    {'phase': 'Implementation', 'weeks': duration_weeks, 'activities': ['Execute intervention']}
                ]
            elif duration_weeks <= 8:
                timeline['phases'] = [
                    {'phase': 'Setup', 'weeks': 1, 'activities': ['Prepare resources', 'Set expectations']},
                    {'phase': 'Implementation', 'weeks': duration_weeks - 2, 'activities': ['Execute intervention', 'Monitor progress']},
                    {'phase': 'Review', 'weeks': 1, 'activities': ['Evaluate outcomes', 'Plan next steps']}
                ]
            else:
                timeline['phases'] = [
                    {'phase': 'Setup', 'weeks': 1, 'activities': ['Prepare resources', 'Set expectations']},
                    {'phase': 'Initial Implementation', 'weeks': duration_weeks * 0.4, 'activities': ['Begin intervention', 'Early monitoring']},
                    {'phase': 'Full Implementation', 'weeks': duration_weeks * 0.4, 'activities': ['Continue intervention', 'Adjust as needed']},
                    {'phase': 'Consolidation', 'weeks': duration_weeks * 0.15, 'activities': ['Reinforce changes', 'Prepare for sustainability']},
                    {'phase': 'Review', 'weeks': duration_weeks * 0.05, 'activities': ['Evaluate outcomes', 'Plan maintenance']}
                ]
            
            return timeline
            
        except Exception as e:
            logger.error("Timeline creation failed", error=str(e))
            return {'total_duration_weeks': 4, 'phases': []}
    
    async def _assess_intervention_risks(self, template: InterventionTemplate, 
                                       need_data: Dict[str, Any], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks associated with an intervention"""
        try:
            risks = {
                'overall_risk_level': 'low',
                'specific_risks': [],
                'mitigation_strategies': []
            }
            
            # Check contraindications
            if template.contraindications:
                for contraindication in template.contraindications:
                    if contraindication in context.get('current_conditions', []):
                        risks['specific_risks'].append(f"Contraindication: {contraindication}")
                        risks['overall_risk_level'] = 'high'
            
            # Assess based on difficulty level
            if template.difficulty_level == 'challenging':
                risks['specific_risks'].append("High difficulty may lead to frustration or abandonment")
                risks['mitigation_strategies'].append("Provide additional support and break into smaller steps")
            
            # Assess based on need severity
            score = need_data.get('score', 0.5)
            if score < 0.2:
                risks['specific_risks'].append("Severe need imbalance may require professional support")
                risks['mitigation_strategies'].append("Consider involving mental health or coaching professionals")
            
            # Determine overall risk level
            if len(risks['specific_risks']) == 0:
                risks['overall_risk_level'] = 'low'
            elif len(risks['specific_risks']) <= 2:
                risks['overall_risk_level'] = 'moderate'
            else:
                risks['overall_risk_level'] = 'high'
            
            return risks
            
        except Exception as e:
            logger.error("Risk assessment failed", error=str(e))
            return {'overall_risk_level': 'unknown', 'specific_risks': [], 'mitigation_strategies': []}
    
    def _generate_expected_outcomes(self, template: InterventionTemplate, 
                                  need_data: Dict[str, Any]) -> List[str]:
        """Generate expected outcomes for an intervention"""
        try:
            outcomes = []
            
            # Base outcomes from template
            for metric in template.success_metrics:
                outcomes.append(f"Improvement in {metric.lower()}")
            
            # Add need-specific outcomes
            target_needs = template.target_needs
            for need in target_needs:
                if need == HumanNeed.CERTAINTY:
                    outcomes.extend(["Reduced anxiety and stress", "Improved planning and organization"])
                elif need == HumanNeed.VARIETY:
                    outcomes.extend(["Increased engagement and creativity", "Reduced boredom and monotony"])
                elif need == HumanNeed.SIGNIFICANCE:
                    outcomes.extend(["Enhanced sense of value and importance", "Increased motivation"])
                elif need == HumanNeed.CONNECTION:
                    outcomes.extend(["Stronger relationships and bonds", "Improved collaboration"])
                elif need == HumanNeed.GROWTH:
                    outcomes.extend(["New skills and capabilities", "Increased confidence"])
                elif need == HumanNeed.CONTRIBUTION:
                    outcomes.extend(["Greater sense of purpose", "Increased fulfillment"])
            
            return list(set(outcomes))  # Remove duplicates
            
        except Exception as e:
            logger.error("Expected outcomes generation failed", error=str(e))
            return ["General improvement in well-being"]
    
    def _generate_team_expected_outcomes(self, template: InterventionTemplate, 
                                       need_data: Dict[str, Any]) -> List[str]:
        """Generate expected outcomes for team interventions"""
        try:
            outcomes = self._generate_expected_outcomes(template, need_data)
            
            # Add team-specific outcomes
            team_outcomes = [
                "Improved team cohesion and collaboration",
                "Better communication and understanding",
                "Enhanced collective performance",
                "Stronger team culture and identity"
            ]
            
            outcomes.extend(team_outcomes)
            return list(set(outcomes))
            
        except Exception as e:
            logger.error("Team expected outcomes generation failed", error=str(e))
            return ["Improved team dynamics"]
    
    def _identify_individual_components(self, template: InterventionTemplate, 
                                      individual_assessments: Dict[str, Any] = None) -> List[str]:
        """Identify individual components of a team intervention"""
        try:
            components = []
            
            if template.intervention_type == InterventionType.TEAM:
                components = [
                    "Personal reflection and goal setting",
                    "Individual skill practice and development",
                    "Self-monitoring and progress tracking",
                    "Personal action planning"
                ]
            
            return components
            
        except Exception as e:
            logger.error("Individual components identification failed", error=str(e))
            return []
    
    def _create_group_activities(self, template: InterventionTemplate, 
                               need_data: Dict[str, Any], 
                               context: Dict[str, Any] = None) -> List[str]:
        """Create group activities for team interventions"""
        try:
            activities = []
            
            for need in template.target_needs:
                if need == HumanNeed.CONNECTION:
                    activities.extend([
                        "Team building exercises and games",
                        "Group discussions and sharing sessions",
                        "Collaborative problem-solving activities"
                    ])
                elif need == HumanNeed.GROWTH:
                    activities.extend([
                        "Group learning sessions and workshops",
                        "Peer mentoring and knowledge sharing",
                        "Team challenges and skill-building exercises"
                    ])
                elif need == HumanNeed.CONTRIBUTION:
                    activities.extend([
                        "Team volunteer projects",
                        "Collective impact measurement sessions",
                        "Purpose alignment workshops"
                    ])
            
            return list(set(activities))
            
        except Exception as e:
            logger.error("Group activities creation failed", error=str(e))
            return ["Team meetings and discussions"]
    
    def _determine_facilitator_requirements(self, template: InterventionTemplate) -> List[str]:
        """Determine facilitator requirements for team interventions"""
        try:
            requirements = ["Basic facilitation skills"]
            
            if template.category == InterventionCategory.SOCIAL:
                requirements.append("Group dynamics expertise")
            
            if template.difficulty_level == 'challenging':
                requirements.append("Advanced coaching or counseling skills")
            
            if any(need in [HumanNeed.GROWTH, HumanNeed.SIGNIFICANCE] for need in template.target_needs):
                requirements.append("Development and motivation expertise")
            
            return requirements
            
        except Exception as e:
            logger.error("Facilitator requirements determination failed", error=str(e))
            return ["Basic facilitation skills"]
    
    async def track_intervention_progress(self, intervention_id: str, 
                                        progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track progress of an ongoing intervention"""
        try:
            # Find the intervention
            intervention = self.active_interventions.get(intervention_id)
            if not intervention:
                return {'error': 'Intervention not found'}
            
            # Update status if provided
            if 'status' in progress_data:
                intervention.status = InterventionStatus(progress_data['status'])
            
            # Store progress data (privacy-protected)
            protected_data = self._protect_privacy(progress_data, intervention.privacy_level)
            
            # Calculate progress metrics
            progress_metrics = await self._calculate_progress_metrics(intervention, protected_data)
            
            return {
                'intervention_id': intervention_id,
                'current_status': intervention.status.value,
                'progress_metrics': progress_metrics,
                'recommendations': await self._generate_progress_recommendations(intervention, protected_data),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Intervention progress tracking failed", 
                        intervention_id=intervention_id, error=str(e))
            return {'error': str(e)}
    
    async def record_intervention_outcome(self, intervention_id: str, 
                                        outcome_data: Dict[str, Any]) -> str:
        """Record the outcome of a completed intervention"""
        try:
            # Find the intervention
            intervention = self.active_interventions.get(intervention_id)
            if not intervention:
                return "Intervention not found"
            
            # Create outcome record
            outcome = InterventionOutcome(
                intervention_id=intervention_id,
                participant_id=intervention.participant_id,
                completion_date=datetime.utcnow(),
                effectiveness_rating=EffectivenessLevel(outcome_data.get('effectiveness_rating', 'moderate')),
                objective_measures=outcome_data.get('objective_measures', {}),
                subjective_feedback=self._protect_privacy(
                    outcome_data.get('subjective_feedback', {}), 
                    intervention.privacy_level
                ),
                lessons_learned=outcome_data.get('lessons_learned', []),
                recommendations_for_future=outcome_data.get('recommendations_for_future', [])
            )
            
            # Store outcome
            self.intervention_outcomes.append(outcome)
            
            # Update effectiveness database
            effectiveness_score = self._convert_effectiveness_to_score(outcome.effectiveness_rating)
            self.effectiveness_database[intervention.template_id].append(effectiveness_score)
            
            # Update intervention status
            intervention.status = InterventionStatus.COMPLETED
            
            # Move from active to completed
            del self.active_interventions[intervention_id]
            
            logger.info("Intervention outcome recorded", 
                       intervention_id=intervention_id,
                       effectiveness=outcome.effectiveness_rating.value)
            
            return "Outcome recorded successfully"
            
        except Exception as e:
            logger.error("Intervention outcome recording failed", 
                        intervention_id=intervention_id, error=str(e))
            return f"Error recording outcome: {str(e)}"
    
    def _protect_privacy(self, data: Dict[str, Any], privacy_level: str) -> Dict[str, Any]:
        """Protect privacy of sensitive data based on privacy level"""
        try:
            if privacy_level == 'anonymous':
                # Remove all identifying information
                protected_data = {}
                for key, value in data.items():
                    if key not in ['participant_id', 'name', 'email', 'personal_details']:
                        if isinstance(value, str) and len(value) > 50:
                            # Hash long text to preserve patterns while removing content
                            protected_data[key] = hashlib.sha256(value.encode()).hexdigest()[:16]
                        else:
                            protected_data[key] = value
                return protected_data
            
            elif privacy_level == 'private':
                # Keep data but mark as private
                protected_data = data.copy()
                protected_data['_privacy_level'] = 'private'
                return protected_data
            
            else:
                # Standard protection
                return data
                
        except Exception as e:
            logger.error("Privacy protection failed", error=str(e))
            return data
    
    async def _calculate_progress_metrics(self, intervention: PersonalizedIntervention, 
                                        progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate progress metrics for an intervention"""
        try:
            metrics = {
                'completion_percentage': 0.0,
                'engagement_level': 'unknown',
                'effectiveness_indicators': []
            }
            
            # Calculate completion percentage
            if 'completed_activities' in progress_data and 'total_activities' in progress_data:
                completed = progress_data['completed_activities']
                total = progress_data['total_activities']
                metrics['completion_percentage'] = (completed / total) * 100 if total > 0 else 0
            
            # Assess engagement level
            engagement_indicators = progress_data.get('engagement_indicators', {})
            if engagement_indicators:
                avg_engagement = sum(engagement_indicators.values()) / len(engagement_indicators)
                if avg_engagement > 0.8:
                    metrics['engagement_level'] = 'high'
                elif avg_engagement > 0.6:
                    metrics['engagement_level'] = 'moderate'
                else:
                    metrics['engagement_level'] = 'low'
            
            # Check effectiveness indicators
            for metric in intervention.success_metrics:
                if metric.lower().replace(' ', '_') in progress_data:
                    metrics['effectiveness_indicators'].append({
                        'metric': metric,
                        'current_value': progress_data[metric.lower().replace(' ', '_')],
                        'trend': 'improving'  # Would be calculated based on historical data
                    })
            
            return metrics
            
        except Exception as e:
            logger.error("Progress metrics calculation failed", error=str(e))
            return {'completion_percentage': 0.0, 'engagement_level': 'unknown', 'effectiveness_indicators': []}
    
    async def _generate_progress_recommendations(self, intervention: PersonalizedIntervention, 
                                               progress_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on intervention progress"""
        try:
            recommendations = []
            
            # Check completion rate
            completion_rate = progress_data.get('completion_percentage', 0)
            if completion_rate < 50:
                recommendations.append("Consider breaking activities into smaller, more manageable steps")
                recommendations.append("Review and address any barriers to participation")
            
            # Check engagement
            engagement_level = progress_data.get('engagement_level', 'unknown')
            if engagement_level == 'low':
                recommendations.append("Explore ways to increase engagement and motivation")
                recommendations.append("Consider adjusting the intervention approach")
            
            # Check for specific issues
            if 'challenges' in progress_data:
                challenges = progress_data['challenges']
                if 'time_constraints' in challenges:
                    recommendations.append("Explore more flexible scheduling options")
                if 'resource_limitations' in challenges:
                    recommendations.append("Identify alternative resources or support")
            
            return recommendations
            
        except Exception as e:
            logger.error("Progress recommendations generation failed", error=str(e))
            return ["Continue with current approach and monitor progress"]
    
    def _convert_effectiveness_to_score(self, effectiveness_rating: EffectivenessLevel) -> float:
        """Convert effectiveness rating to numerical score"""
        conversion_map = {
            EffectivenessLevel.VERY_LOW: 0.1,
            EffectivenessLevel.LOW: 0.3,
            EffectivenessLevel.MODERATE: 0.5,
            EffectivenessLevel.HIGH: 0.7,
            EffectivenessLevel.VERY_HIGH: 0.9
        }
        return conversion_map.get(effectiveness_rating, 0.5)
    
    async def get_intervention_analytics(self, anonymized: bool = True) -> Dict[str, Any]:
        """Get analytics on intervention effectiveness while protecting privacy"""
        try:
            analytics = {
                'total_interventions': len(self.intervention_outcomes),
                'effectiveness_distribution': {},
                'template_effectiveness': {},
                'need_improvement_rates': {},
                'privacy_protected': anonymized
            }
            
            if not self.intervention_outcomes:
                return analytics
            
            # Calculate effectiveness distribution
            effectiveness_counts = {}
            for outcome in self.intervention_outcomes:
                rating = outcome.effectiveness_rating.value
                effectiveness_counts[rating] = effectiveness_counts.get(rating, 0) + 1
            
            total_outcomes = len(self.intervention_outcomes)
            analytics['effectiveness_distribution'] = {
                rating: count / total_outcomes 
                for rating, count in effectiveness_counts.items()
            }
            
            # Calculate template effectiveness (anonymized)
            if anonymized and total_outcomes >= self.anonymization_threshold:
                template_scores = defaultdict(list)
                for outcome in self.intervention_outcomes:
                    # Find template from intervention (would need to store this relationship)
                    template_scores['aggregated'].append(
                        self._convert_effectiveness_to_score(outcome.effectiveness_rating)
                    )
                
                analytics['template_effectiveness'] = {
                    'aggregated_average': sum(template_scores['aggregated']) / len(template_scores['aggregated'])
                }
            
            return analytics
            
        except Exception as e:
            logger.error("Intervention analytics generation failed", error=str(e))
            return {'error': str(e), 'privacy_protected': anonymized}

# Global intervention engine instance
intervention_engine = InterventionEngine()