"""
Intervention Management Service
Manages organizational interventions, tracks effectiveness, and provides recommendations
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

logger = structlog.get_logger(__name__)

class InterventionType(Enum):
    """Types of organizational interventions"""
    PROCESS_IMPROVEMENT = "process_improvement"
    COMMUNICATION_ENHANCEMENT = "communication_enhancement"
    SKILL_DEVELOPMENT = "skill_development"
    CULTURE_CHANGE = "culture_change"
    TECHNOLOGY_ADOPTION = "technology_adoption"
    LEADERSHIP_DEVELOPMENT = "leadership_development"
    TEAM_BUILDING = "team_building"
    CONFLICT_RESOLUTION = "conflict_resolution"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    KNOWLEDGE_SHARING = "knowledge_sharing"

class InterventionStatus(Enum):
    """Status of interventions"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    FAILED = "failed"

class InterventionPriority(Enum):
    """Priority levels for interventions"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class EffectivenessMetric(Enum):
    """Metrics for measuring intervention effectiveness"""
    PATTERN_REDUCTION = "pattern_reduction"
    BEHAVIOR_CHANGE = "behavior_change"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    SATISFACTION_INCREASE = "satisfaction_increase"
    ENGAGEMENT_IMPROVEMENT = "engagement_improvement"
    KNOWLEDGE_TRANSFER = "knowledge_transfer"
    COLLABORATION_ENHANCEMENT = "collaboration_enhancement"
    DECISION_QUALITY = "decision_quality"

@dataclass
class InterventionPlan:
    """Detailed plan for an intervention"""
    id: str
    title: str
    description: str
    intervention_type: InterventionType
    target_patterns: List[str]  # Pattern IDs this intervention targets
    objectives: List[str]
    success_criteria: List[str]
    implementation_steps: List[Dict[str, Any]]
    timeline: Dict[str, Any]
    resource_requirements: Dict[str, Any]
    stakeholders: List[str]
    risk_assessment: Dict[str, Any]
    expected_outcomes: List[str]
    measurement_plan: Dict[str, Any]

@dataclass
class InterventionExecution:
    """Execution tracking for an intervention"""
    id: str
    plan_id: str
    status: InterventionStatus
    priority: InterventionPriority
    start_date: datetime
    expected_end_date: datetime
    actual_end_date: Optional[datetime]
    progress_percentage: float
    completed_steps: List[str]
    current_step: Optional[str]
    blockers: List[Dict[str, Any]]
    resources_used: Dict[str, Any]
    team_members: List[str]
    status_updates: List[Dict[str, Any]]

@dataclass
class EffectivenessMeasurement:
    """Measurement of intervention effectiveness"""
    id: str
    intervention_id: str
    metric_type: EffectivenessMetric
    baseline_value: float
    current_value: float
    target_value: float
    measurement_date: datetime
    measurement_method: str
    confidence_level: float
    notes: str
    data_source: str

@dataclass
class InterventionOutcome:
    """Final outcome assessment of an intervention"""
    id: str
    intervention_id: str
    overall_effectiveness_score: float
    objectives_achieved: List[str]
    objectives_missed: List[str]
    unexpected_benefits: List[str]
    lessons_learned: List[str]
    recommendations: List[str]
    sustainability_assessment: Dict[str, Any]
    cost_benefit_analysis: Dict[str, Any]
    stakeholder_feedback: List[Dict[str, Any]]
    assessment_date: datetime

@dataclass
class InterventionRecommendation:
    """AI-generated intervention recommendation"""
    id: str
    target_pattern_id: str
    recommended_intervention_type: InterventionType
    rationale: str
    expected_effectiveness: float
    implementation_complexity: str
    resource_estimate: Dict[str, Any]
    timeline_estimate: str
    success_probability: float
    alternative_approaches: List[str]
    similar_case_studies: List[str]
    confidence_score: float

class InterventionManagementService:
    """Service for managing organizational interventions"""
    
    def __init__(self):
        self.intervention_plans = {}  # plan_id -> InterventionPlan
        self.intervention_executions = {}  # execution_id -> InterventionExecution
        self.effectiveness_measurements = {}  # measurement_id -> EffectivenessMeasurement
        self.intervention_outcomes = {}  # outcome_id -> InterventionOutcome
        self.intervention_recommendations = {}  # recommendation_id -> InterventionRecommendation
        
        # Intervention templates and best practices
        self.intervention_templates = self._initialize_intervention_templates()
        self.effectiveness_benchmarks = self._initialize_effectiveness_benchmarks()
        
        # Configuration
        self.config = {
            'effectiveness_measurement_frequency_days': 7,
            'intervention_review_frequency_days': 30,
            'success_threshold': 0.7,
            'max_concurrent_interventions': 10,
            'min_confidence_for_recommendation': 0.6
        }
    
    def _initialize_intervention_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize intervention templates"""
        return {
            'communication_enhancement': {
                'title': 'Communication Enhancement Program',
                'description': 'Improve team communication patterns and effectiveness',
                'typical_duration_weeks': 8,
                'success_rate': 0.75,
                'implementation_steps': [
                    {'step': 'Assess current communication patterns', 'duration_days': 7},
                    {'step': 'Design communication training program', 'duration_days': 14},
                    {'step': 'Conduct training sessions', 'duration_days': 21},
                    {'step': 'Implement new communication protocols', 'duration_days': 14},
                    {'step': 'Monitor and adjust', 'duration_days': 14}
                ],
                'resource_requirements': {
                    'facilitator_hours': 40,
                    'participant_hours': 120,
                    'materials_cost': 500
                },
                'success_metrics': [
                    'participation_balance_improvement',
                    'interruption_rate_reduction',
                    'positive_sentiment_increase'
                ]
            },
            'process_improvement': {
                'title': 'Process Optimization Initiative',
                'description': 'Streamline and optimize organizational processes',
                'typical_duration_weeks': 12,
                'success_rate': 0.68,
                'implementation_steps': [
                    {'step': 'Process mapping and analysis', 'duration_days': 14},
                    {'step': 'Identify improvement opportunities', 'duration_days': 7},
                    {'step': 'Design improved processes', 'duration_days': 21},
                    {'step': 'Pilot new processes', 'duration_days': 28},
                    {'step': 'Full implementation and training', 'duration_days': 14}
                ],
                'resource_requirements': {
                    'analyst_hours': 80,
                    'stakeholder_hours': 160,
                    'technology_cost': 2000
                },
                'success_metrics': [
                    'process_efficiency_improvement',
                    'error_rate_reduction',
                    'stakeholder_satisfaction_increase'
                ]
            },
            'team_building': {
                'title': 'Team Cohesion Building Program',
                'description': 'Strengthen team relationships and collaboration',
                'typical_duration_weeks': 6,
                'success_rate': 0.82,
                'implementation_steps': [
                    {'step': 'Team assessment and goal setting', 'duration_days': 3},
                    {'step': 'Team building activities and workshops', 'duration_days': 14},
                    {'step': 'Collaboration skill development', 'duration_days': 14},
                    {'step': 'Implementation of team practices', 'duration_days': 7},
                    {'step': 'Follow-up and reinforcement', 'duration_days': 4}
                ],
                'resource_requirements': {
                    'facilitator_hours': 32,
                    'team_hours': 80,
                    'activity_cost': 800
                },
                'success_metrics': [
                    'team_cohesion_score_improvement',
                    'collaboration_frequency_increase',
                    'conflict_reduction'
                ]
            }
        }
    
    def _initialize_effectiveness_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Initialize effectiveness benchmarks for different intervention types"""
        return {
            'communication_enhancement': {
                'participation_balance_improvement': 0.3,  # 30% improvement expected
                'interruption_rate_reduction': 0.25,      # 25% reduction expected
                'positive_sentiment_increase': 0.2        # 20% increase expected
            },
            'process_improvement': {
                'process_efficiency_improvement': 0.4,     # 40% efficiency gain expected
                'error_rate_reduction': 0.5,              # 50% error reduction expected
                'stakeholder_satisfaction_increase': 0.3   # 30% satisfaction increase expected
            },
            'team_building': {
                'team_cohesion_score_improvement': 0.35,   # 35% cohesion improvement expected
                'collaboration_frequency_increase': 0.4,   # 40% more collaboration expected
                'conflict_reduction': 0.6                  # 60% conflict reduction expected
            }
        }
    
    async def generate_intervention_recommendations(self, 
                                                  detected_patterns: List[Dict[str, Any]]) -> List[InterventionRecommendation]:
        """Generate intervention recommendations based on detected patterns"""
        try:
            recommendations = []
            
            for pattern in detected_patterns:
                if pattern.get('severity') in ['high', 'critical']:
                    recommendation = await self._create_intervention_recommendation(pattern)
                    if recommendation.confidence_score >= self.config['min_confidence_for_recommendation']:
                        recommendations.append(recommendation)
                        self.intervention_recommendations[recommendation.id] = recommendation
            
            # Sort by expected effectiveness and success probability
            recommendations.sort(
                key=lambda x: (x.expected_effectiveness * x.success_probability), 
                reverse=True
            )
            
            logger.info("Intervention recommendations generated", 
                       recommendations_count=len(recommendations),
                       high_confidence_count=len([r for r in recommendations if r.confidence_score > 0.8]))
            
            return recommendations
            
        except Exception as e:
            logger.error("Intervention recommendation generation failed", error=str(e))
            return []
    
    async def _create_intervention_recommendation(self, pattern: Dict[str, Any]) -> InterventionRecommendation:
        """Create intervention recommendation for a specific pattern"""
        try:
            recommendation_id = str(uuid.uuid4())
            
            # Determine appropriate intervention type based on pattern
            intervention_type = self._determine_intervention_type(pattern)
            
            # Get template for this intervention type
            template = self.intervention_templates.get(intervention_type.value, {})
            
            # Calculate expected effectiveness
            expected_effectiveness = self._calculate_expected_effectiveness(pattern, intervention_type)
            
            # Estimate implementation complexity
            implementation_complexity = self._assess_implementation_complexity(pattern, intervention_type)
            
            # Generate resource estimate
            resource_estimate = self._estimate_resources(intervention_type, pattern)
            
            # Calculate success probability
            success_probability = template.get('success_rate', 0.5)
            
            # Adjust success probability based on pattern characteristics
            success_probability = self._adjust_success_probability(success_probability, pattern)
            
            # Generate rationale
            rationale = self._generate_intervention_rationale(pattern, intervention_type)
            
            # Find similar case studies
            similar_cases = self._find_similar_case_studies(pattern, intervention_type)
            
            # Calculate confidence score
            confidence_score = self._calculate_recommendation_confidence(
                pattern, intervention_type, expected_effectiveness, success_probability
            )
            
            return InterventionRecommendation(
                id=recommendation_id,
                target_pattern_id=pattern.get('id', ''),
                recommended_intervention_type=intervention_type,
                rationale=rationale,
                expected_effectiveness=expected_effectiveness,
                implementation_complexity=implementation_complexity,
                resource_estimate=resource_estimate,
                timeline_estimate=f"{template.get('typical_duration_weeks', 8)} weeks",
                success_probability=success_probability,
                alternative_approaches=self._generate_alternative_approaches(pattern, intervention_type),
                similar_case_studies=similar_cases,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error("Intervention recommendation creation failed", error=str(e))
            # Return minimal recommendation
            return InterventionRecommendation(
                id=str(uuid.uuid4()),
                target_pattern_id=pattern.get('id', ''),
                recommended_intervention_type=InterventionType.PROCESS_IMPROVEMENT,
                rationale="Unable to generate detailed recommendation",
                expected_effectiveness=0.5,
                implementation_complexity="medium",
                resource_estimate={'hours': 40, 'cost': 1000},
                timeline_estimate="8 weeks",
                success_probability=0.5,
                alternative_approaches=[],
                similar_case_studies=[],
                confidence_score=0.3
            )
    
    def _determine_intervention_type(self, pattern: Dict[str, Any]) -> InterventionType:
        """Determine appropriate intervention type for a pattern"""
        pattern_type = pattern.get('pattern_type', '').lower()
        pattern_title = pattern.get('title', '').lower()
        
        # Communication-related patterns
        if any(keyword in pattern_title for keyword in ['communication', 'interruption', 'participation']):
            return InterventionType.COMMUNICATION_ENHANCEMENT
        
        # Process-related patterns
        if any(keyword in pattern_title for keyword in ['process', 'workflow', 'efficiency']):
            return InterventionType.PROCESS_IMPROVEMENT
        
        # Team-related patterns
        if any(keyword in pattern_title for keyword in ['team', 'collaboration', 'conflict']):
            return InterventionType.TEAM_BUILDING
        
        # Skill-related patterns
        if any(keyword in pattern_title for keyword in ['skill', 'knowledge', 'learning']):
            return InterventionType.SKILL_DEVELOPMENT
        
        # Leadership-related patterns
        if any(keyword in pattern_title for keyword in ['leadership', 'decision', 'authority']):
            return InterventionType.LEADERSHIP_DEVELOPMENT
        
        # Default to process improvement
        return InterventionType.PROCESS_IMPROVEMENT
    
    def _calculate_expected_effectiveness(self, pattern: Dict[str, Any], 
                                        intervention_type: InterventionType) -> float:
        """Calculate expected effectiveness of intervention for pattern"""
        try:
            # Base effectiveness from template
            template = self.intervention_templates.get(intervention_type.value, {})
            base_effectiveness = template.get('success_rate', 0.5)
            
            # Adjust based on pattern characteristics
            severity_multiplier = {
                'critical': 1.2,
                'high': 1.1,
                'medium': 1.0,
                'low': 0.9
            }.get(pattern.get('severity', 'medium'), 1.0)
            
            # Adjust based on pattern frequency (more frequent = easier to address)
            frequency = pattern.get('frequency', 1)
            frequency_multiplier = min(1.0 + (frequency - 1) * 0.1, 1.5)
            
            # Adjust based on confidence in pattern detection
            confidence_multiplier = pattern.get('confidence_score', 0.5)
            
            expected_effectiveness = base_effectiveness * severity_multiplier * frequency_multiplier * confidence_multiplier
            
            return min(expected_effectiveness, 1.0)
            
        except Exception as e:
            logger.error("Expected effectiveness calculation failed", error=str(e))
            return 0.5
    
    def _assess_implementation_complexity(self, pattern: Dict[str, Any], 
                                        intervention_type: InterventionType) -> str:
        """Assess implementation complexity for intervention"""
        try:
            # Base complexity from intervention type
            complexity_map = {
                InterventionType.COMMUNICATION_ENHANCEMENT: 'medium',
                InterventionType.PROCESS_IMPROVEMENT: 'high',
                InterventionType.SKILL_DEVELOPMENT: 'medium',
                InterventionType.CULTURE_CHANGE: 'very_high',
                InterventionType.TECHNOLOGY_ADOPTION: 'high',
                InterventionType.LEADERSHIP_DEVELOPMENT: 'high',
                InterventionType.TEAM_BUILDING: 'low',
                InterventionType.CONFLICT_RESOLUTION: 'medium',
                InterventionType.PERFORMANCE_OPTIMIZATION: 'medium',
                InterventionType.KNOWLEDGE_SHARING: 'low'
            }
            
            base_complexity = complexity_map.get(intervention_type, 'medium')
            
            # Adjust based on pattern characteristics
            affected_participants = len(pattern.get('affected_participants', []))
            if affected_participants > 10:
                complexity_levels = ['low', 'medium', 'high', 'very_high']
                current_index = complexity_levels.index(base_complexity)
                if current_index < len(complexity_levels) - 1:
                    base_complexity = complexity_levels[current_index + 1]
            
            return base_complexity
            
        except Exception as e:
            logger.error("Implementation complexity assessment failed", error=str(e))
            return 'medium'
    
    async def create_intervention_plan(self, recommendation: InterventionRecommendation,
                                     customizations: Optional[Dict[str, Any]] = None) -> InterventionPlan:
        """Create detailed intervention plan from recommendation"""
        try:
            plan_id = str(uuid.uuid4())
            
            # Get template for intervention type
            template = self.intervention_templates.get(recommendation.recommended_intervention_type.value, {})
            
            # Apply customizations if provided
            if customizations:
                template = {**template, **customizations}
            
            # Create implementation steps
            implementation_steps = []
            for step_template in template.get('implementation_steps', []):
                step = {
                    'id': str(uuid.uuid4()),
                    'title': step_template['step'],
                    'description': f"Execute {step_template['step'].lower()}",
                    'duration_days': step_template.get('duration_days', 7),
                    'dependencies': [],
                    'resources_needed': [],
                    'success_criteria': [],
                    'status': 'planned'
                }
                implementation_steps.append(step)
            
            # Create timeline
            total_duration = sum(step.get('duration_days', 7) for step in implementation_steps)
            start_date = datetime.utcnow() + timedelta(days=7)  # Start in a week
            end_date = start_date + timedelta(days=total_duration)
            
            timeline = {
                'planned_start': start_date.isoformat(),
                'planned_end': end_date.isoformat(),
                'total_duration_days': total_duration,
                'milestones': self._generate_milestones(implementation_steps)
            }
            
            # Create measurement plan
            measurement_plan = {
                'baseline_measurement_date': start_date.isoformat(),
                'measurement_frequency_days': self.config['effectiveness_measurement_frequency_days'],
                'success_metrics': template.get('success_metrics', []),
                'measurement_methods': self._define_measurement_methods(template.get('success_metrics', []))
            }
            
            plan = InterventionPlan(
                id=plan_id,
                title=template.get('title', f"{recommendation.recommended_intervention_type.value.replace('_', ' ').title()} Plan"),
                description=template.get('description', recommendation.rationale),
                intervention_type=recommendation.recommended_intervention_type,
                target_patterns=[recommendation.target_pattern_id],
                objectives=self._generate_objectives(recommendation),
                success_criteria=self._generate_success_criteria(recommendation, template),
                implementation_steps=implementation_steps,
                timeline=timeline,
                resource_requirements=recommendation.resource_estimate,
                stakeholders=self._identify_stakeholders(recommendation),
                risk_assessment=self._assess_risks(recommendation),
                expected_outcomes=self._define_expected_outcomes(recommendation),
                measurement_plan=measurement_plan
            )
            
            self.intervention_plans[plan_id] = plan
            
            logger.info("Intervention plan created", 
                       plan_id=plan_id,
                       intervention_type=recommendation.recommended_intervention_type.value,
                       duration_days=total_duration)
            
            return plan
            
        except Exception as e:
            logger.error("Intervention plan creation failed", error=str(e))
            raise
    
    async def track_intervention_effectiveness(self, intervention_id: str) -> Dict[str, Any]:
        """Track and analyze intervention effectiveness"""
        try:
            # Get intervention execution
            execution = self.intervention_executions.get(intervention_id)
            if not execution:
                raise ValueError(f"Intervention execution {intervention_id} not found")
            
            # Get all effectiveness measurements for this intervention
            measurements = [
                m for m in self.effectiveness_measurements.values()
                if m.intervention_id == intervention_id
            ]
            
            if not measurements:
                return {
                    'intervention_id': intervention_id,
                    'status': 'no_measurements',
                    'message': 'No effectiveness measurements available yet'
                }
            
            # Analyze effectiveness trends
            effectiveness_trends = self._analyze_effectiveness_trends(measurements)
            
            # Calculate overall effectiveness score
            overall_score = self._calculate_overall_effectiveness(measurements)
            
            # Assess progress toward objectives
            objective_progress = self._assess_objective_progress(execution, measurements)
            
            # Generate insights and recommendations
            insights = self._generate_effectiveness_insights(measurements, effectiveness_trends)
            recommendations = self._generate_effectiveness_recommendations(measurements, overall_score)
            
            return {
                'intervention_id': intervention_id,
                'overall_effectiveness_score': overall_score,
                'effectiveness_trends': effectiveness_trends,
                'objective_progress': objective_progress,
                'insights': insights,
                'recommendations': recommendations,
                'measurement_count': len(measurements),
                'last_measurement_date': max(m.measurement_date for m in measurements).isoformat(),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Intervention effectiveness tracking failed", error=str(e))
            raise

# Global service instance
intervention_management_service = InterventionManagementService()