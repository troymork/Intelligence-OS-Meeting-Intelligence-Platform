"""
Strategic Recommendation and Impact Assessment Engine for Intelligence OS
Generates strategic recommendations and assesses potential impact
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import structlog
from collections import defaultdict
import numpy as np

from .strategic_framework_analyzer import strategic_framework_analyzer, FrameworkType, AlignmentLevel

logger = structlog.get_logger(__name__)

class RecommendationType(Enum):
    """Types of strategic recommendations"""
    IMMEDIATE_ACTION = "immediate_action"
    STRATEGIC_INITIATIVE = "strategic_initiative"
    CAPABILITY_BUILDING = "capability_building"
    PARTNERSHIP = "partnership"
    INNOVATION = "innovation"
    PROCESS_IMPROVEMENT = "process_improvement"
    CULTURAL_CHANGE = "cultural_change"

class ImpactDimension(Enum):
    """Dimensions of strategic impact"""
    FINANCIAL = "financial"
    SOCIAL = "social"
    ENVIRONMENTAL = "environmental"
    OPERATIONAL = "operational"
    REPUTATIONAL = "reputational"
    STRATEGIC = "strategic"

class ImpactTimeframe(Enum):
    """Timeframes for impact assessment"""
    SHORT_TERM = "short_term"  # 0-6 months
    MEDIUM_TERM = "medium_term"  # 6-18 months
    LONG_TERM = "long_term"  # 18+ months

class ImplementationComplexity(Enum):
    """Complexity levels for implementation"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class ImpactProjection:
    """Projection of potential impact from a strategic initiative"""
    dimension: ImpactDimension
    timeframe: ImpactTimeframe
    magnitude: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    description: str
    metrics: List[str]
    assumptions: List[str]

@dataclass
class StrategicRecommendation:
    """Comprehensive strategic recommendation"""
    id: str
    title: str
    description: str
    recommendation_type: RecommendationType
    priority: str  # 'critical', 'high', 'medium', 'low'
    target_frameworks: List[FrameworkType]
    expected_outcomes: List[str]
    impact_projections: List[ImpactProjection]
    implementation_complexity: ImplementationComplexity
    resource_requirements: Dict[str, Any]
    timeline: Dict[str, Any]
    success_metrics: List[str]
    risks: List[str]
    mitigation_strategies: List[str]
    dependencies: List[str]
    stakeholders: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class StrategicOpportunity:
    """Strategic opportunity identification"""
    id: str
    title: str
    description: str
    opportunity_type: str
    exponential_potential: float  # 0.0 to 1.0
    market_size: Optional[str]
    competitive_advantage: List[str]
    required_capabilities: List[str]
    time_sensitivity: str
    alignment_score: float
    frameworks_supported: List[FrameworkType]

@dataclass
class ActionPlan:
    """Strategic action plan with concrete steps"""
    id: str
    title: str
    objective: str
    target_frameworks: List[FrameworkType]
    phases: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    resource_allocation: Dict[str, Any]
    governance_structure: Dict[str, Any]
    risk_management: Dict[str, Any]
    success_criteria: List[str]
    monitoring_framework: Dict[str, Any]

class StrategicRecommendationEngine:
    """Engine for generating strategic recommendations and impact assessments"""
    
    def __init__(self):
        self.recommendation_templates = self._initialize_recommendation_templates()
        self.impact_models = self._initialize_impact_models()
        self.opportunity_patterns = self._initialize_opportunity_patterns()
        
        # Historical data for impact modeling
        self.historical_outcomes = defaultdict(list)
        self.benchmark_data = {}
        
        # Configuration
        self.exponential_threshold = 0.7
        self.high_impact_threshold = 0.6
        self.complexity_factors = {
            'organizational_change': 0.8,
            'technology_adoption': 0.6,
            'partnership_development': 0.7,
            'cultural_transformation': 0.9,
            'process_redesign': 0.5
        }
    
    def _initialize_recommendation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize recommendation templates for different scenarios"""
        return {
            'sdg_alignment_low': {
                'type': RecommendationType.STRATEGIC_INITIATIVE,
                'title_template': 'Develop {framework} Integration Strategy',
                'description_template': 'Create comprehensive strategy to align with {framework} goals and targets',
                'complexity': ImplementationComplexity.HIGH,
                'timeframe': 'medium_term',
                'resource_intensity': 'high'
            },
            'doughnut_social_gap': {
                'type': RecommendationType.CAPABILITY_BUILDING,
                'title_template': 'Strengthen Social Foundation in {area}',
                'description_template': 'Build capabilities to better address social foundation requirements in {area}',
                'complexity': ImplementationComplexity.MEDIUM,
                'timeframe': 'medium_term',
                'resource_intensity': 'medium'
            },
            'agreement_economy_governance': {
                'type': RecommendationType.PROCESS_IMPROVEMENT,
                'title_template': 'Implement Collaborative Governance Framework',
                'description_template': 'Establish participatory decision-making processes and transparent accountability',
                'complexity': ImplementationComplexity.HIGH,
                'timeframe': 'long_term',
                'resource_intensity': 'medium'
            },
            'cross_framework_synergy': {
                'type': RecommendationType.INNOVATION,
                'title_template': 'Leverage {framework1}-{framework2} Synergy',
                'description_template': 'Develop integrated approach that maximizes alignment across multiple frameworks',
                'complexity': ImplementationComplexity.MEDIUM,
                'timeframe': 'medium_term',
                'resource_intensity': 'medium'
            }
        }
    
    def _initialize_impact_models(self) -> Dict[ImpactDimension, Dict[str, Any]]:
        """Initialize impact projection models"""
        return {
            ImpactDimension.FINANCIAL: {
                'factors': ['cost_reduction', 'revenue_growth', 'efficiency_gains', 'risk_mitigation'],
                'multipliers': {'sdg': 1.2, 'doughnut_economy': 1.1, 'agreement_economy': 1.15},
                'baseline_impact': 0.1
            },
            ImpactDimension.SOCIAL: {
                'factors': ['stakeholder_satisfaction', 'community_impact', 'employee_engagement', 'social_value'],
                'multipliers': {'sdg': 1.5, 'doughnut_economy': 1.4, 'agreement_economy': 1.3},
                'baseline_impact': 0.2
            },
            ImpactDimension.ENVIRONMENTAL: {
                'factors': ['carbon_reduction', 'resource_efficiency', 'waste_reduction', 'biodiversity_impact'],
                'multipliers': {'sdg': 1.3, 'doughnut_economy': 1.6, 'agreement_economy': 1.2},
                'baseline_impact': 0.15
            },
            ImpactDimension.OPERATIONAL: {
                'factors': ['process_efficiency', 'quality_improvement', 'innovation_capacity', 'agility'],
                'multipliers': {'sdg': 1.1, 'doughnut_economy': 1.2, 'agreement_economy': 1.4},
                'baseline_impact': 0.25
            },
            ImpactDimension.REPUTATIONAL: {
                'factors': ['brand_value', 'stakeholder_trust', 'market_position', 'thought_leadership'],
                'multipliers': {'sdg': 1.4, 'doughnut_economy': 1.3, 'agreement_economy': 1.2},
                'baseline_impact': 0.2
            },
            ImpactDimension.STRATEGIC: {
                'factors': ['competitive_advantage', 'market_access', 'partnership_opportunities', 'future_readiness'],
                'multipliers': {'sdg': 1.3, 'doughnut_economy': 1.2, 'agreement_economy': 1.5},
                'baseline_impact': 0.3
            }
        }
    
    def _initialize_opportunity_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for identifying strategic opportunities"""
        return {
            'sustainability_leadership': {
                'indicators': ['environmental_focus', 'social_impact', 'governance_strength'],
                'exponential_potential': 0.8,
                'market_trends': ['esg_investing', 'sustainable_products', 'circular_economy'],
                'frameworks': [FrameworkType.SDG, FrameworkType.DOUGHNUT_ECONOMY]
            },
            'collaborative_innovation': {
                'indicators': ['partnership_strength', 'innovation_capacity', 'collective_intelligence'],
                'exponential_potential': 0.9,
                'market_trends': ['open_innovation', 'ecosystem_collaboration', 'shared_value'],
                'frameworks': [FrameworkType.AGREEMENT_ECONOMY, FrameworkType.SDG]
            },
            'regenerative_business': {
                'indicators': ['regenerative_practices', 'system_thinking', 'stakeholder_value'],
                'exponential_potential': 0.85,
                'market_trends': ['regenerative_economy', 'stakeholder_capitalism', 'purpose_driven'],
                'frameworks': [FrameworkType.DOUGHNUT_ECONOMY, FrameworkType.AGREEMENT_ECONOMY]
            }
        }
    
    async def generate_strategic_recommendations(self, framework_analysis: Dict[str, Any],
                                               organization_context: Dict[str, Any] = None) -> List[StrategicRecommendation]:
        """Generate comprehensive strategic recommendations"""
        try:
            recommendations = []
            
            # Extract framework analyses
            framework_analyses = framework_analysis.get('framework_analyses', {})
            synthesis = framework_analysis.get('cross_framework_synthesis', {})
            
            # Generate framework-specific recommendations
            for framework_name, analysis in framework_analyses.items():
                framework_recs = await self._generate_framework_recommendations(
                    framework_name, analysis, organization_context
                )
                recommendations.extend(framework_recs)
            
            # Generate cross-framework recommendations
            if synthesis:
                cross_recs = await self._generate_cross_framework_recommendations(
                    synthesis, organization_context
                )
                recommendations.extend(cross_recs)
            
            # Generate opportunity-based recommendations
            opportunities = await self.identify_strategic_opportunities(
                framework_analysis, organization_context
            )
            for opportunity in opportunities:
                opp_recs = await self._generate_opportunity_recommendations(
                    opportunity, organization_context
                )
                recommendations.extend(opp_recs)
            
            # Prioritize and filter recommendations
            prioritized_recommendations = await self._prioritize_recommendations(
                recommendations, organization_context
            )
            
            return prioritized_recommendations[:15]  # Top 15 recommendations
            
        except Exception as e:
            logger.error("Strategic recommendations generation failed", error=str(e))
            return []
    
    async def assess_impact_projections(self, recommendation: StrategicRecommendation,
                                      organization_context: Dict[str, Any] = None) -> List[ImpactProjection]:
        """Assess potential impact projections for a recommendation"""
        try:
            projections = []
            
            # Generate projections for each impact dimension
            for dimension in ImpactDimension:
                projection = await self._project_impact(
                    recommendation, dimension, organization_context
                )
                if projection:
                    projections.append(projection)
            
            return projections
            
        except Exception as e:
            logger.error("Impact projections assessment failed", error=str(e))
            return []
    
    async def identify_strategic_opportunities(self, framework_analysis: Dict[str, Any],
                                            organization_context: Dict[str, Any] = None) -> List[StrategicOpportunity]:
        """Identify strategic opportunities with exponential potential"""
        try:
            opportunities = []
            
            # Analyze framework alignment for opportunity patterns
            framework_analyses = framework_analysis.get('framework_analyses', {})
            synthesis = framework_analysis.get('cross_framework_synthesis', {})
            
            # Check each opportunity pattern
            for pattern_name, pattern_config in self.opportunity_patterns.items():
                opportunity = await self._evaluate_opportunity_pattern(
                    pattern_name, pattern_config, framework_analyses, organization_context
                )
                if opportunity:
                    opportunities.append(opportunity)
            
            # Identify synergy-based opportunities
            synergies = synthesis.get('synergies', [])
            for synergy in synergies:
                if synergy.get('strength', 0) > 0.7:
                    synergy_opportunity = await self._create_synergy_opportunity(
                        synergy, organization_context
                    )
                    if synergy_opportunity:
                        opportunities.append(synergy_opportunity)
            
            # Sort by exponential potential
            opportunities.sort(key=lambda x: x.exponential_potential, reverse=True)
            
            return opportunities[:10]  # Top 10 opportunities
            
        except Exception as e:
            logger.error("Strategic opportunities identification failed", error=str(e))
            return []
    
    async def generate_action_plan(self, recommendations: List[StrategicRecommendation],
                                 organization_context: Dict[str, Any] = None) -> ActionPlan:
        """Generate comprehensive strategic action plan"""
        try:
            # Group recommendations by priority and type
            high_priority_recs = [r for r in recommendations if r.priority in ['critical', 'high']]
            
            # Create action plan phases
            phases = await self._create_action_plan_phases(high_priority_recs, organization_context)
            
            # Define milestones
            milestones = await self._define_action_plan_milestones(phases, high_priority_recs)
            
            # Calculate resource allocation
            resource_allocation = await self._calculate_resource_allocation(high_priority_recs)
            
            # Define governance structure
            governance_structure = await self._define_governance_structure(organization_context)
            
            # Create risk management framework
            risk_management = await self._create_risk_management_framework(high_priority_recs)
            
            # Define success criteria
            success_criteria = await self._define_success_criteria(high_priority_recs)
            
            # Create monitoring framework
            monitoring_framework = await self._create_monitoring_framework(high_priority_recs)
            
            # Determine target frameworks
            target_frameworks = list(set([
                framework for rec in high_priority_recs 
                for framework in rec.target_frameworks
            ]))
            
            action_plan = ActionPlan(
                id=f"action_plan_{datetime.utcnow().timestamp()}",
                title="Strategic Framework Alignment Action Plan",
                objective="Achieve comprehensive alignment with strategic frameworks through coordinated initiatives",
                target_frameworks=target_frameworks,
                phases=phases,
                milestones=milestones,
                resource_allocation=resource_allocation,
                governance_structure=governance_structure,
                risk_management=risk_management,
                success_criteria=success_criteria,
                monitoring_framework=monitoring_framework
            )
            
            return action_plan
            
        except Exception as e:
            logger.error("Action plan generation failed", error=str(e))
            return ActionPlan(
                id="error_plan",
                title="Error in Action Plan Generation",
                objective="Unable to generate action plan",
                target_frameworks=[],
                phases=[],
                milestones=[],
                resource_allocation={},
                governance_structure={},
                risk_management={},
                success_criteria=[],
                monitoring_framework={}
            )

# Global strategic recommendation engine instance
strategic_recommendation_engine = StrategicRecommendationEngine()  
  
    async def _generate_framework_recommendations(self, framework_name: str, analysis: Dict[str, Any],
                                                organization_context: Dict[str, Any] = None) -> List[StrategicRecommendation]:
        """Generate recommendations for a specific framework"""
        try:
            recommendations = []
            
            overall_score = analysis.get('overall_score', 0.5)
            alignment_level = analysis.get('alignment_level', 'partially_aligned')
            
            # Generate recommendations based on alignment level
            if alignment_level == 'misaligned' or overall_score < 0.4:
                # Critical alignment needed
                rec = await self._create_alignment_recommendation(
                    framework_name, 'critical', analysis, organization_context
                )
                recommendations.append(rec)
                
            elif alignment_level == 'partially_aligned' or overall_score < 0.7:
                # Enhancement needed
                rec = await self._create_enhancement_recommendation(
                    framework_name, 'high', analysis, organization_context
                )
                recommendations.append(rec)
            
            # Generate gap-specific recommendations
            gaps = analysis.get('primary_gaps', [])
            for gap in gaps[:3]:  # Top 3 gaps
                gap_rec = await self._create_gap_recommendation(
                    framework_name, gap, analysis, organization_context
                )
                if gap_rec:
                    recommendations.append(gap_rec)
            
            # Generate opportunity-specific recommendations
            opportunities = analysis.get('strategic_opportunities', [])
            for opportunity in opportunities[:2]:  # Top 2 opportunities
                opp_rec = await self._create_opportunity_recommendation(
                    framework_name, opportunity, analysis, organization_context
                )
                if opp_rec:
                    recommendations.append(opp_rec)
            
            return recommendations
            
        except Exception as e:
            logger.error("Framework recommendations generation failed", 
                        framework=framework_name, error=str(e))
            return []
    
    async def _create_alignment_recommendation(self, framework_name: str, priority: str,
                                            analysis: Dict[str, Any], 
                                            organization_context: Dict[str, Any] = None) -> StrategicRecommendation:
        """Create alignment recommendation for a framework"""
        try:
            framework_type = FrameworkType(framework_name)
            
            # Generate impact projections
            impact_projections = []
            
            # Strategic impact
            strategic_impact = ImpactProjection(
                dimension=ImpactDimension.STRATEGIC,
                timeframe=ImpactTimeframe.LONG_TERM,
                magnitude=0.8,
                confidence=0.7,
                description=f"Significant improvement in {framework_name} strategic alignment",
                metrics=[f"{framework_name} alignment score", "Strategic coherence index"],
                assumptions=["Organizational commitment to strategic alignment", "Resource availability"]
            )
            impact_projections.append(strategic_impact)
            
            # Reputational impact
            reputational_impact = ImpactProjection(
                dimension=ImpactDimension.REPUTATIONAL,
                timeframe=ImpactTimeframe.MEDIUM_TERM,
                magnitude=0.6,
                confidence=0.6,
                description=f"Enhanced reputation through {framework_name} leadership",
                metrics=["Brand perception score", "Stakeholder trust index"],
                assumptions=["Effective communication of alignment efforts", "Authentic implementation"]
            )
            impact_projections.append(reputational_impact)
            
            recommendation = StrategicRecommendation(
                id=f"align_{framework_name}_{datetime.utcnow().timestamp()}",
                title=f"Develop Comprehensive {framework_name.upper()} Integration Strategy",
                description=f"Create and implement a comprehensive strategy to align organizational activities with {framework_name} principles and goals",
                recommendation_type=RecommendationType.STRATEGIC_INITIATIVE,
                priority=priority,
                target_frameworks=[framework_type],
                expected_outcomes=[
                    f"Improved {framework_name} alignment score",
                    "Enhanced strategic coherence",
                    "Stronger stakeholder confidence",
                    "Better risk management"
                ],
                impact_projections=impact_projections,
                implementation_complexity=ImplementationComplexity.HIGH,
                resource_requirements={
                    'human_resources': 'Dedicated strategy team (3-5 FTE)',
                    'financial_investment': 'Medium to high investment required',
                    'time_commitment': '12-18 months for full implementation',
                    'expertise_needed': f'{framework_name} expertise, change management'
                },
                timeline={
                    'phase_1': '0-3 months: Assessment and strategy development',
                    'phase_2': '3-9 months: Implementation of core initiatives',
                    'phase_3': '9-18 months: Integration and optimization'
                },
                success_metrics=[
                    f"{framework_name} alignment score improvement",
                    "Strategic initiative completion rate",
                    "Stakeholder satisfaction scores",
                    "Performance indicator improvements"
                ],
                risks=[
                    "Organizational resistance to change",
                    "Resource constraints",
                    "Competing priorities",
                    "Implementation complexity"
                ],
                mitigation_strategies=[
                    "Strong leadership commitment and communication",
                    "Phased implementation approach",
                    "Change management support",
                    "Regular progress monitoring and adjustment"
                ],
                dependencies=[
                    "Leadership commitment",
                    "Resource allocation",
                    "Organizational readiness",
                    "Stakeholder buy-in"
                ],
                stakeholders=[
                    "Executive leadership",
                    "Strategy team",
                    "Department heads",
                    "Key stakeholders"
                ]
            )
            
            return recommendation
            
        except Exception as e:
            logger.error("Alignment recommendation creation failed", error=str(e))
            return self._create_fallback_recommendation(framework_name, priority)
    
    async def _project_impact(self, recommendation: StrategicRecommendation, 
                            dimension: ImpactDimension,
                            organization_context: Dict[str, Any] = None) -> Optional[ImpactProjection]:
        """Project impact for a specific dimension"""
        try:
            impact_model = self.impact_models.get(dimension)
            if not impact_model:
                return None
            
            # Calculate base impact
            base_impact = impact_model['baseline_impact']
            
            # Apply framework multipliers
            framework_multiplier = 1.0
            for framework in recommendation.target_frameworks:
                multiplier = impact_model['multipliers'].get(framework.value, 1.0)
                framework_multiplier *= multiplier
            
            # Adjust for recommendation type
            type_multipliers = {
                RecommendationType.STRATEGIC_INITIATIVE: 1.2,
                RecommendationType.INNOVATION: 1.4,
                RecommendationType.CAPABILITY_BUILDING: 1.1,
                RecommendationType.PARTNERSHIP: 1.3,
                RecommendationType.PROCESS_IMPROVEMENT: 1.0,
                RecommendationType.CULTURAL_CHANGE: 1.5,
                RecommendationType.IMMEDIATE_ACTION: 0.8
            }
            type_multiplier = type_multipliers.get(recommendation.recommendation_type, 1.0)
            
            # Calculate final magnitude
            magnitude = min(1.0, base_impact * framework_multiplier * type_multiplier)
            
            # Determine timeframe based on complexity
            if recommendation.implementation_complexity == ImplementationComplexity.LOW:
                timeframe = ImpactTimeframe.SHORT_TERM
            elif recommendation.implementation_complexity == ImplementationComplexity.MEDIUM:
                timeframe = ImpactTimeframe.MEDIUM_TERM
            else:
                timeframe = ImpactTimeframe.LONG_TERM
            
            # Calculate confidence based on various factors
            confidence = 0.7  # Base confidence
            if organization_context:
                # Adjust based on organizational maturity
                maturity = organization_context.get('strategic_maturity', 'medium')
                if maturity == 'high':
                    confidence += 0.1
                elif maturity == 'low':
                    confidence -= 0.1
            
            # Generate description and metrics
            description = self._generate_impact_description(dimension, magnitude, timeframe)
            metrics = impact_model['factors'][:3]  # Top 3 relevant metrics
            
            # Generate assumptions
            assumptions = [
                "Successful implementation of recommendation",
                "Organizational commitment and resources",
                "Market conditions remain stable"
            ]
            
            return ImpactProjection(
                dimension=dimension,
                timeframe=timeframe,
                magnitude=magnitude,
                confidence=confidence,
                description=description,
                metrics=metrics,
                assumptions=assumptions
            )
            
        except Exception as e:
            logger.error("Impact projection failed", dimension=dimension.value, error=str(e))
            return None
    
    def _generate_impact_description(self, dimension: ImpactDimension, 
                                   magnitude: float, timeframe: ImpactTimeframe) -> str:
        """Generate impact description"""
        try:
            magnitude_desc = "significant" if magnitude > 0.7 else "moderate" if magnitude > 0.4 else "limited"
            timeframe_desc = {
                ImpactTimeframe.SHORT_TERM: "within 6 months",
                ImpactTimeframe.MEDIUM_TERM: "within 6-18 months", 
                ImpactTimeframe.LONG_TERM: "over 18+ months"
            }[timeframe]
            
            dimension_focus = {
                ImpactDimension.FINANCIAL: "financial performance and cost efficiency",
                ImpactDimension.SOCIAL: "social value creation and stakeholder satisfaction",
                ImpactDimension.ENVIRONMENTAL: "environmental sustainability and resource efficiency",
                ImpactDimension.OPERATIONAL: "operational efficiency and process optimization",
                ImpactDimension.REPUTATIONAL: "brand reputation and stakeholder trust",
                ImpactDimension.STRATEGIC: "strategic positioning and competitive advantage"
            }[dimension]
            
            return f"Expected {magnitude_desc} positive impact on {dimension_focus} {timeframe_desc}"
            
        except Exception as e:
            logger.error("Impact description generation failed", error=str(e))
            return f"Expected impact on {dimension.value}"
    
    async def _evaluate_opportunity_pattern(self, pattern_name: str, pattern_config: Dict[str, Any],
                                          framework_analyses: Dict[str, Any],
                                          organization_context: Dict[str, Any] = None) -> Optional[StrategicOpportunity]:
        """Evaluate a strategic opportunity pattern"""
        try:
            indicators = pattern_config['indicators']
            frameworks = pattern_config['frameworks']
            
            # Calculate alignment score for this opportunity
            alignment_scores = []
            for framework in frameworks:
                framework_analysis = framework_analyses.get(framework.value, {})
                score = framework_analysis.get('overall_score', 0.5)
                alignment_scores.append(score)
            
            avg_alignment = np.mean(alignment_scores) if alignment_scores else 0.5
            
            # Only consider opportunities with reasonable alignment potential
            if avg_alignment < 0.3:
                return None
            
            # Calculate exponential potential
            base_potential = pattern_config['exponential_potential']
            context_multiplier = 1.0
            
            if organization_context:
                # Adjust based on organizational capabilities
                innovation_capacity = organization_context.get('innovation_capacity', 'medium')
                if innovation_capacity == 'high':
                    context_multiplier += 0.2
                elif innovation_capacity == 'low':
                    context_multiplier -= 0.2
            
            exponential_potential = min(1.0, base_potential * context_multiplier)
            
            # Only include high-potential opportunities
            if exponential_potential < self.exponential_threshold:
                return None
            
            opportunity = StrategicOpportunity(
                id=f"opp_{pattern_name}_{datetime.utcnow().timestamp()}",
                title=f"{pattern_name.replace('_', ' ').title()} Opportunity",
                description=f"Strategic opportunity to leverage {pattern_name.replace('_', ' ')} for exponential impact",
                opportunity_type=pattern_name,
                exponential_potential=exponential_potential,
                market_size=self._estimate_market_size(pattern_name, organization_context),
                competitive_advantage=self._identify_competitive_advantages(pattern_name, organization_context),
                required_capabilities=indicators,
                time_sensitivity="Medium",
                alignment_score=avg_alignment,
                frameworks_supported=frameworks
            )
            
            return opportunity
            
        except Exception as e:
            logger.error("Opportunity pattern evaluation failed", pattern=pattern_name, error=str(e))
            return None
    
    def _estimate_market_size(self, pattern_name: str, organization_context: Dict[str, Any] = None) -> str:
        """Estimate market size for opportunity"""
        try:
            # Simplified market size estimation
            market_sizes = {
                'sustainability_leadership': 'Large and growing ($2T+ ESG market)',
                'collaborative_innovation': 'Medium to large (Platform economy)',
                'regenerative_business': 'Emerging but high-growth (Regenerative economy)'
            }
            
            return market_sizes.get(pattern_name, 'Medium')
            
        except Exception as e:
            logger.error("Market size estimation failed", error=str(e))
            return "Unknown"
    
    def _identify_competitive_advantages(self, pattern_name: str, 
                                       organization_context: Dict[str, Any] = None) -> List[str]:
        """Identify competitive advantages for opportunity"""
        try:
            advantages = {
                'sustainability_leadership': [
                    'First-mover advantage in sustainable practices',
                    'Enhanced brand reputation and trust',
                    'Access to ESG-focused investment and partnerships'
                ],
                'collaborative_innovation': [
                    'Accelerated innovation through partnerships',
                    'Reduced R&D costs through collaboration',
                    'Access to diverse expertise and markets'
                ],
                'regenerative_business': [
                    'Differentiation through regenerative impact',
                    'Resilient business model design',
                    'Stakeholder loyalty and engagement'
                ]
            }
            
            return advantages.get(pattern_name, ['Strategic differentiation', 'Market positioning'])
            
        except Exception as e:
            logger.error("Competitive advantages identification failed", error=str(e))
            return []
    
    async def _prioritize_recommendations(self, recommendations: List[StrategicRecommendation],
                                        organization_context: Dict[str, Any] = None) -> List[StrategicRecommendation]:
        """Prioritize recommendations based on impact and feasibility"""
        try:
            # Calculate priority scores
            for rec in recommendations:
                priority_score = await self._calculate_priority_score(rec, organization_context)
                rec.metadata = {'priority_score': priority_score}
            
            # Sort by priority score
            recommendations.sort(key=lambda x: x.metadata.get('priority_score', 0), reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error("Recommendations prioritization failed", error=str(e))
            return recommendations
    
    async def _calculate_priority_score(self, recommendation: StrategicRecommendation,
                                      organization_context: Dict[str, Any] = None) -> float:
        """Calculate priority score for a recommendation"""
        try:
            score = 0.0
            
            # Priority weight
            priority_weights = {'critical': 1.0, 'high': 0.8, 'medium': 0.6, 'low': 0.4}
            score += priority_weights.get(recommendation.priority, 0.5) * 0.3
            
            # Impact weight
            if recommendation.impact_projections:
                avg_impact = np.mean([proj.magnitude for proj in recommendation.impact_projections])
                score += avg_impact * 0.4
            
            # Feasibility weight (inverse of complexity)
            complexity_weights = {
                ImplementationComplexity.LOW: 1.0,
                ImplementationComplexity.MEDIUM: 0.7,
                ImplementationComplexity.HIGH: 0.4,
                ImplementationComplexity.VERY_HIGH: 0.2
            }
            score += complexity_weights.get(recommendation.implementation_complexity, 0.5) * 0.3
            
            return score
            
        except Exception as e:
            logger.error("Priority score calculation failed", error=str(e))
            return 0.5
    
    def _create_fallback_recommendation(self, framework_name: str, priority: str) -> StrategicRecommendation:
        """Create fallback recommendation when detailed generation fails"""
        return StrategicRecommendation(
            id=f"fallback_{framework_name}_{datetime.utcnow().timestamp()}",
            title=f"Improve {framework_name.upper()} Alignment",
            description=f"General recommendation to improve alignment with {framework_name} framework",
            recommendation_type=RecommendationType.STRATEGIC_INITIATIVE,
            priority=priority,
            target_frameworks=[FrameworkType(framework_name)],
            expected_outcomes=[f"Better {framework_name} alignment"],
            impact_projections=[],
            implementation_complexity=ImplementationComplexity.MEDIUM,
            resource_requirements={},
            timeline={},
            success_metrics=[],
            risks=[],
            mitigation_strategies=[],
            dependencies=[],
            stakeholders=[]
        )