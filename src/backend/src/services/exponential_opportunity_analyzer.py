"""
Exponential Opportunity Analyzer for Intelligence OS
Identifies non-linear growth opportunities and exponential transformation paths
"""

import os
import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import structlog
from collections import defaultdict
import numpy as np

logger = structlog.get_logger(__name__)

class ExponentialDomain(Enum):
    """Domains of exponential technologies and opportunities"""
    DIGITAL = "digital"
    BIOLOGICAL = "biological"
    PHYSICAL = "physical"
    NETWORK = "network"
    COGNITIVE = "cognitive"
    ORGANIZATIONAL = "organizational"

class OpportunityType(Enum):
    """Types of exponential opportunities"""
    TECHNOLOGY_ADOPTION = "technology_adoption"
    BUSINESS_MODEL = "business_model"
    PLATFORM_CREATION = "platform_creation"
    NETWORK_EFFECT = "network_effect"
    ECOSYSTEM_DEVELOPMENT = "ecosystem_development"
    CAPABILITY_BUILDING = "capability_building"

class TransformationPhase(Enum):
    """Phases of exponential transformation"""
    DIGITIZATION = "digitization"
    DECEPTION = "deception"
    DISRUPTION = "disruption"
    DEMONETIZATION = "demonetization"
    DEMATERIALIZATION = "dematerialization"
    DEMOCRATIZATION = "democratization"

class ReadinessLevel(Enum):
    """Organizational readiness levels for exponential opportunities"""
    UNPREPARED = "unprepared"
    AWARE = "aware"
    DEVELOPING = "developing"
    PREPARED = "prepared"
    LEADING = "leading"

@dataclass
class ExponentialTechnology:
    """Exponential technology definition"""
    id: str
    name: str
    domain: ExponentialDomain
    description: str
    maturity_level: str  # 'emerging', 'growing', 'mature'
    growth_rate: float  # Annual growth rate
    adoption_timeline: str  # e.g., '1-3 years', '3-5 years', '5-10 years'
    keywords: List[str]
    use_cases: List[str]
    disruption_potential: float  # 0.0 to 1.0

@dataclass
class OpportunityAssessment:
    """Assessment of an exponential opportunity"""
    id: str
    name: str
    opportunity_type: OpportunityType
    related_technologies: List[str]
    domains: List[ExponentialDomain]
    description: str
    potential_impact: float  # 0.0 to 1.0
    implementation_complexity: float  # 0.0 to 1.0
    time_to_value: str  # e.g., 'short-term', 'medium-term', 'long-term'
    readiness_level: ReadinessLevel
    key_capabilities_required: List[str]
    potential_barriers: List[str]
    success_examples: List[str]
    confidence_score: float

@dataclass
class TransformationRoadmap:
    """Roadmap for exponential transformation"""
    id: str
    title: str
    description: str
    target_opportunities: List[str]  # IDs of opportunities
    phases: List[Dict[str, Any]]
    key_milestones: List[Dict[str, Any]]
    capability_development: List[Dict[str, Any]]
    resource_requirements: Dict[str, Any]
    risk_mitigation: List[Dict[str, Any]]
    success_metrics: List[Dict[str, Any]]
    timeline: Dict[str, Any]

class ExponentialOpportunityAnalyzer:
    """System for identifying exponential opportunities and transformation paths"""
    
    def __init__(self):
        self.exponential_technologies = self._initialize_technologies()
        self.opportunity_patterns = self._initialize_opportunity_patterns()
        self.transformation_templates = self._initialize_transformation_templates()
        self.identified_opportunities = {}
        self.generated_roadmaps = {}
        
        # Analysis configuration
        self.impact_threshold = 0.7  # Minimum impact score for high-potential opportunities
        self.readiness_weights = {
            'technology_familiarity': 0.3,
            'capability_alignment': 0.25,
            'culture_adaptability': 0.25,
            'resource_availability': 0.2
        }
    
    def _initialize_technologies(self) -> Dict[str, ExponentialTechnology]:
        """Initialize exponential technology definitions"""
        technologies = {}
        
        # Digital Domain Technologies
        technologies['ai_ml'] = ExponentialTechnology(
            id='ai_ml',
            name='Artificial Intelligence & Machine Learning',
            domain=ExponentialDomain.DIGITAL,
            description='Systems capable of performing tasks that typically require human intelligence',
            maturity_level='growing',
            growth_rate=1.4,  # 40% annual growth
            adoption_timeline='1-3 years',
            keywords=['artificial intelligence', 'machine learning', 'deep learning', 'neural networks', 'AI'],
            use_cases=['predictive analytics', 'natural language processing', 'computer vision', 'decision support'],
            disruption_potential=0.9
        )
        
        technologies['blockchain'] = ExponentialTechnology(
            id='blockchain',
            name='Blockchain & Distributed Ledger',
            domain=ExponentialDomain.DIGITAL,
            description='Decentralized, immutable record-keeping technology',
            maturity_level='growing',
            growth_rate=1.3,  # 30% annual growth
            adoption_timeline='3-5 years',
            keywords=['blockchain', 'distributed ledger', 'smart contracts', 'cryptocurrency', 'tokens'],
            use_cases=['supply chain tracking', 'digital identity', 'secure transactions', 'smart contracts'],
            disruption_potential=0.8
        )
        
        technologies['quantum_computing'] = ExponentialTechnology(
            id='quantum_computing',
            name='Quantum Computing',
            domain=ExponentialDomain.DIGITAL,
            description='Computing using quantum-mechanical phenomena',
            maturity_level='emerging',
            growth_rate=1.5,  # 50% annual growth
            adoption_timeline='5-10 years',
            keywords=['quantum', 'qubits', 'quantum supremacy', 'quantum algorithms', 'quantum encryption'],
            use_cases=['complex optimization', 'cryptography', 'material science', 'drug discovery'],
            disruption_potential=0.95
        )
        
        # Add more technologies...
        technologies['iot'] = ExponentialTechnology(
            id='iot',
            name='Internet of Things',
            domain=ExponentialDomain.NETWORK,
            description='Network of connected physical objects with sensors and software',
            maturity_level='growing',
            growth_rate=1.35,  # 35% annual growth
            adoption_timeline='1-3 years',
            keywords=['IoT', 'connected devices', 'sensors', 'smart devices', 'M2M'],
            use_cases=['smart cities', 'industrial monitoring', 'connected health', 'smart homes'],
            disruption_potential=0.8
        )
        
        technologies['robotics'] = ExponentialTechnology(
            id='robotics',
            name='Advanced Robotics & Automation',
            domain=ExponentialDomain.PHYSICAL,
            description='Intelligent machines capable of physical tasks',
            maturity_level='growing',
            growth_rate=1.3,  # 30% annual growth
            adoption_timeline='2-5 years',
            keywords=['robotics', 'automation', 'cobots', 'autonomous systems', 'robotic process automation'],
            use_cases=['manufacturing', 'logistics', 'healthcare', 'agriculture'],
            disruption_potential=0.75
        )
        
        return technologies
    
    def _initialize_opportunity_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize opportunity pattern definitions"""
        patterns = {}
        
        # Platform Business Model Pattern
        patterns['platform_model'] = {
            'name': 'Platform Business Model',
            'type': OpportunityType.BUSINESS_MODEL,
            'description': 'Creating multi-sided platforms that connect users and providers',
            'key_elements': ['network effects', 'ecosystem', 'value exchange', 'scalability'],
            'related_technologies': ['ai_ml', 'blockchain', 'iot'],
            'example_pattern': r'\b(platform|marketplace|network effects|ecosystem|multi-sided)\b',
            'success_examples': ['Uber', 'Airbnb', 'Amazon', 'App Store'],
            'transformation_potential': 0.9
        }
        
        # AI Automation Pattern
        patterns['ai_automation'] = {
            'name': 'AI-Powered Automation',
            'type': OpportunityType.TECHNOLOGY_ADOPTION,
            'description': 'Using AI to automate complex processes and decision-making',
            'key_elements': ['process automation', 'decision support', 'predictive analytics', 'efficiency'],
            'related_technologies': ['ai_ml', 'robotics'],
            'example_pattern': r'\b(automation|AI|machine learning|predictive|intelligent)\b',
            'success_examples': ['UiPath', 'Blue Prism', 'DataRobot', 'IBM Watson'],
            'transformation_potential': 0.85
        }
        
        return patterns
    
    def _initialize_transformation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize transformation roadmap templates"""
        templates = {}
        
        # Digital Transformation Template
        templates['digital_transformation'] = {
            'title': 'Digital Transformation Roadmap',
            'description': 'Comprehensive path to digital business transformation',
            'phases': [
                {
                    'name': 'Digitization',
                    'description': 'Convert analog processes to digital',
                    'duration': '3-6 months',
                    'key_activities': [
                        'Process mapping and digitization',
                        'Basic automation implementation',
                        'Digital tool adoption',
                        'Data collection systems'
                    ]
                },
                {
                    'name': 'Intelligence',
                    'description': 'Implement AI and analytics capabilities',
                    'duration': '12-18 months',
                    'key_activities': [
                        'Analytics implementation',
                        'AI/ML model development',
                        'Decision support systems',
                        'Predictive capabilities'
                    ]
                }
            ]
        }
        
        return templates    
   
 async def analyze_exponential_opportunities(self, content: str, 
                                             organization_context: Dict[str, Any] = None,
                                             focus_domains: List[ExponentialDomain] = None) -> Dict[str, Any]:
        """Analyze content for exponential opportunities"""
        try:
            if focus_domains is None:
                focus_domains = list(ExponentialDomain)
            
            # Identify relevant technologies
            relevant_technologies = await self._identify_relevant_technologies(content, focus_domains)
            
            # Identify opportunity patterns
            opportunity_patterns = await self._identify_opportunity_patterns(content, relevant_technologies)
            
            # Generate opportunity assessments
            opportunity_assessments = await self._generate_opportunity_assessments(
                content, relevant_technologies, opportunity_patterns, organization_context
            )
            
            # Assess organizational readiness
            readiness_assessment = await self._assess_organizational_readiness(
                opportunity_assessments, organization_context
            )
            
            # Generate transformation roadmap
            transformation_roadmap = await self._generate_transformation_roadmap(
                opportunity_assessments, readiness_assessment, organization_context
            )
            
            # Calculate exponential potential score
            exponential_potential = self._calculate_exponential_potential(
                opportunity_assessments, readiness_assessment
            )
            
            # Store results for future reference
            analysis_id = str(uuid.uuid4())
            self.identified_opportunities[analysis_id] = opportunity_assessments
            self.generated_roadmaps[analysis_id] = transformation_roadmap
            
            return {
                'analysis_id': analysis_id,
                'exponential_potential': exponential_potential,
                'relevant_technologies': self._serialize_technologies(relevant_technologies),
                'opportunity_assessments': self._serialize_opportunities(opportunity_assessments),
                'readiness_assessment': readiness_assessment,
                'transformation_roadmap': self._serialize_roadmap(transformation_roadmap),
                'timestamp': datetime.utcnow().isoformat(),
                'domains_analyzed': [domain.value for domain in focus_domains]
            }
            
        except Exception as e:
            logger.error("Exponential opportunity analysis failed", error=str(e))
            return {
                'analysis_id': str(uuid.uuid4()),
                'exponential_potential': 0.5,
                'relevant_technologies': [],
                'opportunity_assessments': [],
                'readiness_assessment': {},
                'transformation_roadmap': {},
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _identify_relevant_technologies(self, content: str, 
                                           focus_domains: List[ExponentialDomain]) -> List[ExponentialTechnology]:
        """Identify relevant exponential technologies in content"""
        try:
            content_lower = content.lower()
            relevant_techs = []
            
            for tech_id, tech in self.exponential_technologies.items():
                if tech.domain not in focus_domains:
                    continue
                
                # Check for keyword matches
                keyword_matches = sum(1 for keyword in tech.keywords 
                                    if keyword.lower() in content_lower)
                
                # Check for use case mentions
                use_case_matches = sum(1 for use_case in tech.use_cases 
                                     if use_case.lower() in content_lower)
                
                # Calculate relevance score
                relevance_score = (keyword_matches * 0.6 + use_case_matches * 0.4) / max(len(tech.keywords), 1)
                
                if relevance_score > 0.2:  # Threshold for relevance
                    relevant_techs.append(tech)
            
            # Sort by disruption potential and relevance
            relevant_techs.sort(key=lambda t: t.disruption_potential, reverse=True)
            
            return relevant_techs[:10]  # Return top 10 most relevant technologies
            
        except Exception as e:
            logger.error("Technology identification failed", error=str(e))
            return []
    
    async def _identify_opportunity_patterns(self, content: str, 
                                           relevant_technologies: List[ExponentialTechnology]) -> List[Dict[str, Any]]:
        """Identify opportunity patterns in content"""
        try:
            content_lower = content.lower()
            identified_patterns = []
            
            for pattern_id, pattern in self.opportunity_patterns.items():
                # Check for pattern keywords
                pattern_match = re.search(pattern['example_pattern'], content_lower, re.IGNORECASE)
                
                # Check for related technology alignment
                tech_alignment = any(tech.id in pattern['related_technologies'] 
                                   for tech in relevant_technologies)
                
                if pattern_match or tech_alignment:
                    confidence = 0.7 if pattern_match else 0.5
                    if tech_alignment:
                        confidence += 0.2
                    
                    identified_patterns.append({
                        'pattern_id': pattern_id,
                        'pattern': pattern,
                        'confidence': min(confidence, 1.0),
                        'match_evidence': pattern_match.group() if pattern_match else None,
                        'tech_alignment': tech_alignment
                    })
            
            # Sort by confidence and transformation potential
            identified_patterns.sort(
                key=lambda p: p['confidence'] * p['pattern']['transformation_potential'], 
                reverse=True
            )
            
            return identified_patterns[:8]  # Return top 8 patterns
            
        except Exception as e:
            logger.error("Pattern identification failed", error=str(e))
            return []
    
    async def _generate_opportunity_assessments(self, content: str,
                                              relevant_technologies: List[ExponentialTechnology],
                                              opportunity_patterns: List[Dict[str, Any]],
                                              organization_context: Dict[str, Any] = None) -> List[OpportunityAssessment]:
        """Generate detailed opportunity assessments"""
        try:
            assessments = []
            org_context = organization_context or {}
            
            for i, pattern_data in enumerate(opportunity_patterns):
                pattern = pattern_data['pattern']
                pattern_id = pattern_data['pattern_id']
                
                # Generate opportunity assessment
                assessment = OpportunityAssessment(
                    id=f"opp_{pattern_id}_{i}",
                    name=f"{pattern['name']} Opportunity",
                    opportunity_type=pattern['type'],
                    related_technologies=[tech.id for tech in relevant_technologies 
                                        if tech.id in pattern['related_technologies']],
                    domains=list(set(tech.domain for tech in relevant_technologies 
                                   if tech.id in pattern['related_technologies'])),
                    description=self._generate_opportunity_description(pattern, relevant_technologies, content),
                    potential_impact=self._calculate_potential_impact(pattern, relevant_technologies, org_context),
                    implementation_complexity=self._calculate_implementation_complexity(pattern, relevant_technologies, org_context),
                    time_to_value=self._estimate_time_to_value(pattern, relevant_technologies),
                    readiness_level=self._assess_readiness_level(pattern, org_context),
                    key_capabilities_required=self._identify_required_capabilities(pattern, relevant_technologies),
                    potential_barriers=self._identify_potential_barriers(pattern, org_context),
                    success_examples=pattern['success_examples'],
                    confidence_score=pattern_data['confidence']
                )
                
                assessments.append(assessment)
            
            return assessments
            
        except Exception as e:
            logger.error("Opportunity assessment generation failed", error=str(e))
            return []
    
    def _generate_opportunity_description(self, pattern: Dict[str, Any], 
                                        technologies: List[ExponentialTechnology],
                                        content: str) -> str:
        """Generate detailed opportunity description"""
        tech_names = [tech.name for tech in technologies if tech.id in pattern['related_technologies']]
        
        description = f"{pattern['description']}. "
        
        if tech_names:
            description += f"This opportunity leverages {', '.join(tech_names[:3])} "
            description += "to create exponential value through "
            description += f"{', '.join(pattern['key_elements'][:3])}. "
        
        # Add context-specific insights
        if 'efficiency' in content.lower():
            description += "Focus on operational efficiency improvements and cost reduction. "
        if 'customer' in content.lower():
            description += "Emphasize customer experience enhancement and engagement. "
        if 'innovation' in content.lower():
            description += "Drive innovation and competitive differentiation. "
        
        return description.strip()
    
    def _calculate_potential_impact(self, pattern: Dict[str, Any], 
                                  technologies: List[ExponentialTechnology],
                                  org_context: Dict[str, Any]) -> float:
        """Calculate potential impact score"""
        base_impact = pattern['transformation_potential']
        
        # Technology multiplier
        tech_multiplier = 1.0
        for tech in technologies:
            if tech.id in pattern['related_technologies']:
                tech_multiplier += tech.disruption_potential * 0.1
        
        # Organization context adjustments
        org_multiplier = 1.0
        if org_context:
            # Size factor
            if org_context.get('size') == 'large':
                org_multiplier += 0.1
            elif org_context.get('size') == 'startup':
                org_multiplier += 0.2
            
            # Industry factor
            if org_context.get('industry') in ['technology', 'financial_services', 'healthcare']:
                org_multiplier += 0.15
        
        return min(base_impact * tech_multiplier * org_multiplier, 1.0)
    
    def _calculate_implementation_complexity(self, pattern: Dict[str, Any],
                                           technologies: List[ExponentialTechnology],
                                           org_context: Dict[str, Any]) -> float:
        """Calculate implementation complexity score"""
        base_complexity = 0.5  # Base complexity
        
        # Technology complexity
        for tech in technologies:
            if tech.id in pattern['related_technologies']:
                if tech.maturity_level == 'emerging':
                    base_complexity += 0.2
                elif tech.maturity_level == 'growing':
                    base_complexity += 0.1
        
        # Pattern complexity
        if pattern['type'] == OpportunityType.PLATFORM_CREATION:
            base_complexity += 0.2
        elif pattern['type'] == OpportunityType.ECOSYSTEM_DEVELOPMENT:
            base_complexity += 0.15
        
        # Organization context adjustments
        if org_context:
            if org_context.get('digital_maturity') == 'low':
                base_complexity += 0.2
            elif org_context.get('digital_maturity') == 'high':
                base_complexity -= 0.1
        
        return min(base_complexity, 1.0)
    
    def _estimate_time_to_value(self, pattern: Dict[str, Any],
                               technologies: List[ExponentialTechnology]) -> str:
        """Estimate time to value realization"""
        # Get average adoption timeline from related technologies
        timelines = []
        for tech in technologies:
            if tech.id in pattern['related_technologies']:
                if '1-3' in tech.adoption_timeline:
                    timelines.append(2)
                elif '3-5' in tech.adoption_timeline:
                    timelines.append(4)
                elif '5-10' in tech.adoption_timeline:
                    timelines.append(7)
                else:
                    timelines.append(5)
        
        if not timelines:
            avg_timeline = 3
        else:
            avg_timeline = sum(timelines) / len(timelines)
        
        # Adjust based on opportunity type
        if pattern['type'] == OpportunityType.TECHNOLOGY_ADOPTION:
            avg_timeline *= 0.8
        elif pattern['type'] == OpportunityType.PLATFORM_CREATION:
            avg_timeline *= 1.5
        elif pattern['type'] == OpportunityType.ECOSYSTEM_DEVELOPMENT:
            avg_timeline *= 2.0
        
        if avg_timeline <= 2:
            return 'short-term'
        elif avg_timeline <= 5:
            return 'medium-term'
        else:
            return 'long-term'    

    def _assess_readiness_level(self, pattern: Dict[str, Any],
                               org_context: Dict[str, Any]) -> ReadinessLevel:
        """Assess organizational readiness level"""
        if not org_context:
            return ReadinessLevel.AWARE
        
        readiness_score = 0.0
        
        # Digital maturity factor
        digital_maturity = org_context.get('digital_maturity', 'medium')
        if digital_maturity == 'high':
            readiness_score += 0.3
        elif digital_maturity == 'medium':
            readiness_score += 0.2
        else:
            readiness_score += 0.1
        
        # Innovation culture factor
        innovation_culture = org_context.get('innovation_culture', 'medium')
        if innovation_culture == 'high':
            readiness_score += 0.25
        elif innovation_culture == 'medium':
            readiness_score += 0.15
        else:
            readiness_score += 0.05
        
        # Resource availability factor
        resource_availability = org_context.get('resource_availability', 'medium')
        if resource_availability == 'high':
            readiness_score += 0.25
        elif resource_availability == 'medium':
            readiness_score += 0.15
        else:
            readiness_score += 0.05
        
        # Technology expertise factor
        tech_expertise = org_context.get('technology_expertise', 'medium')
        if tech_expertise == 'high':
            readiness_score += 0.2
        elif tech_expertise == 'medium':
            readiness_score += 0.1
        else:
            readiness_score += 0.05
        
        # Map score to readiness level
        if readiness_score >= 0.8:
            return ReadinessLevel.LEADING
        elif readiness_score >= 0.6:
            return ReadinessLevel.PREPARED
        elif readiness_score >= 0.4:
            return ReadinessLevel.DEVELOPING
        elif readiness_score >= 0.2:
            return ReadinessLevel.AWARE
        else:
            return ReadinessLevel.UNPREPARED
    
    def _identify_required_capabilities(self, pattern: Dict[str, Any],
                                      technologies: List[ExponentialTechnology]) -> List[str]:
        """Identify key capabilities required for opportunity"""
        capabilities = set(pattern['key_elements'])
        
        # Add technology-specific capabilities
        for tech in technologies:
            if tech.id in pattern['related_technologies']:
                if tech.domain == ExponentialDomain.DIGITAL:
                    capabilities.update(['digital literacy', 'data analytics', 'software development'])
                elif tech.domain == ExponentialDomain.NETWORK:
                    capabilities.update(['network architecture', 'connectivity', 'systems integration'])
                elif tech.domain == ExponentialDomain.PHYSICAL:
                    capabilities.update(['engineering', 'manufacturing', 'supply chain'])
        
        # Add pattern-specific capabilities
        if pattern['type'] == OpportunityType.PLATFORM_CREATION:
            capabilities.update(['platform design', 'ecosystem orchestration', 'API management'])
        elif pattern['type'] == OpportunityType.BUSINESS_MODEL:
            capabilities.update(['business model innovation', 'value proposition design', 'monetization'])
        
        return list(capabilities)[:10]  # Return top 10 capabilities
    
    def _identify_potential_barriers(self, pattern: Dict[str, Any],
                                   org_context: Dict[str, Any]) -> List[str]:
        """Identify potential implementation barriers"""
        barriers = []
        
        # Common barriers by opportunity type
        if pattern['type'] == OpportunityType.TECHNOLOGY_ADOPTION:
            barriers.extend(['technical complexity', 'skill gaps', 'integration challenges'])
        elif pattern['type'] == OpportunityType.BUSINESS_MODEL:
            barriers.extend(['market acceptance', 'revenue model validation', 'competitive response'])
        elif pattern['type'] == OpportunityType.PLATFORM_CREATION:
            barriers.extend(['network effects chicken-and-egg', 'platform governance', 'ecosystem coordination'])
        
        # Organization-specific barriers
        if org_context:
            if org_context.get('digital_maturity') == 'low':
                barriers.extend(['digital skills shortage', 'legacy system constraints'])
            if org_context.get('innovation_culture') == 'low':
                barriers.extend(['change resistance', 'risk aversion'])
            if org_context.get('resource_availability') == 'low':
                barriers.extend(['funding constraints', 'resource allocation'])
        
        # General barriers
        barriers.extend(['regulatory compliance', 'cybersecurity risks', 'scalability challenges'])
        
        return list(set(barriers))[:8]  # Return unique barriers, max 8
    
    async def _assess_organizational_readiness(self, opportunities: List[OpportunityAssessment],
                                             org_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Assess overall organizational readiness for exponential opportunities"""
        try:
            if not org_context:
                return {
                    'overall_readiness': 'aware',
                    'readiness_score': 0.5,
                    'capability_gaps': ['digital transformation', 'innovation culture', 'technology expertise'],
                    'readiness_factors': {},
                    'recommendations': ['Conduct digital maturity assessment', 'Develop innovation capabilities']
                }
            
            # Calculate readiness factors
            readiness_factors = {
                'digital_maturity': self._score_factor(org_context.get('digital_maturity', 'medium')),
                'innovation_culture': self._score_factor(org_context.get('innovation_culture', 'medium')),
                'technology_expertise': self._score_factor(org_context.get('technology_expertise', 'medium')),
                'resource_availability': self._score_factor(org_context.get('resource_availability', 'medium')),
                'change_agility': self._score_factor(org_context.get('change_agility', 'medium'))
            }
            
            # Calculate weighted readiness score
            readiness_score = sum(
                score * self.readiness_weights.get(factor, 0.2) 
                for factor, score in readiness_factors.items()
            )
            
            # Identify capability gaps
            capability_gaps = []
            for factor, score in readiness_factors.items():
                if score < 0.6:
                    capability_gaps.append(factor.replace('_', ' '))
            
            # Generate recommendations
            recommendations = self._generate_readiness_recommendations(readiness_factors, opportunities)
            
            # Determine overall readiness level
            if readiness_score >= 0.8:
                overall_readiness = 'leading'
            elif readiness_score >= 0.6:
                overall_readiness = 'prepared'
            elif readiness_score >= 0.4:
                overall_readiness = 'developing'
            elif readiness_score >= 0.2:
                overall_readiness = 'aware'
            else:
                overall_readiness = 'unprepared'
            
            return {
                'overall_readiness': overall_readiness,
                'readiness_score': readiness_score,
                'capability_gaps': capability_gaps,
                'readiness_factors': readiness_factors,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error("Readiness assessment failed", error=str(e))
            return {
                'overall_readiness': 'aware',
                'readiness_score': 0.5,
                'capability_gaps': ['assessment_error'],
                'readiness_factors': {},
                'recommendations': ['Retry readiness assessment'],
                'error': str(e)
            }
    
    def _score_factor(self, level: str) -> float:
        """Convert level to numeric score"""
        level_scores = {
            'low': 0.2,
            'medium': 0.5,
            'high': 0.8,
            'very_high': 1.0
        }
        return level_scores.get(level, 0.5)
    
    def _generate_readiness_recommendations(self, readiness_factors: Dict[str, float],
                                          opportunities: List[OpportunityAssessment]) -> List[str]:
        """Generate recommendations based on readiness assessment"""
        recommendations = []
        
        # Factor-specific recommendations
        if readiness_factors.get('digital_maturity', 0.5) < 0.6:
            recommendations.append('Invest in digital transformation initiatives and digital literacy programs')
        
        if readiness_factors.get('innovation_culture', 0.5) < 0.6:
            recommendations.append('Foster innovation culture through experimentation and risk-taking encouragement')
        
        if readiness_factors.get('technology_expertise', 0.5) < 0.6:
            recommendations.append('Build technology capabilities through training and strategic hiring')
        
        if readiness_factors.get('resource_availability', 0.5) < 0.6:
            recommendations.append('Secure dedicated resources and budget for exponential initiatives')
        
        if readiness_factors.get('change_agility', 0.5) < 0.6:
            recommendations.append('Develop organizational agility and change management capabilities')
        
        # Opportunity-specific recommendations
        high_impact_opportunities = [opp for opp in opportunities if opp.potential_impact > 0.7]
        if high_impact_opportunities:
            recommendations.append(f'Prioritize {len(high_impact_opportunities)} high-impact opportunities for immediate focus')
        
        return recommendations[:6]  # Return top 6 recommendations
    
    async def _generate_transformation_roadmap(self, opportunities: List[OpportunityAssessment],
                                             readiness_assessment: Dict[str, Any],
                                             org_context: Dict[str, Any] = None) -> TransformationRoadmap:
        """Generate transformation roadmap based on opportunities and readiness"""
        try:
            # Select appropriate template
            template_key = self._select_roadmap_template(opportunities, readiness_assessment)
            template = self.transformation_templates.get(template_key, self.transformation_templates['digital_transformation'])
            
            # Prioritize opportunities
            prioritized_opportunities = self._prioritize_opportunities(opportunities, readiness_assessment)
            
            # Generate phases with specific opportunities
            phases = self._generate_roadmap_phases(template, prioritized_opportunities, readiness_assessment)
            
            # Generate milestones
            milestones = self._generate_key_milestones(phases, prioritized_opportunities)
            
            # Generate capability development plan
            capability_development = self._generate_capability_development_plan(
                prioritized_opportunities, readiness_assessment
            )
            
            # Estimate resource requirements
            resource_requirements = self._estimate_resource_requirements(prioritized_opportunities, phases)
            
            # Generate risk mitigation plan
            risk_mitigation = self._generate_risk_mitigation_plan(prioritized_opportunities)
            
            # Define success metrics
            success_metrics = self._define_success_metrics(prioritized_opportunities, template)
            
            # Create timeline
            timeline = self._create_transformation_timeline(phases)
            
            roadmap = TransformationRoadmap(
                id=str(uuid.uuid4()),
                title=f"{template['title']} - Customized",
                description=f"{template['description']} tailored for identified exponential opportunities",
                target_opportunities=[opp.id for opp in prioritized_opportunities],
                phases=phases,
                key_milestones=milestones,
                capability_development=capability_development,
                resource_requirements=resource_requirements,
                risk_mitigation=risk_mitigation,
                success_metrics=success_metrics,
                timeline=timeline
            )
            
            return roadmap
            
        except Exception as e:
            logger.error("Roadmap generation failed", error=str(e))
            # Return basic roadmap
            return TransformationRoadmap(
                id=str(uuid.uuid4()),
                title="Basic Transformation Roadmap",
                description="Basic roadmap due to generation error",
                target_opportunities=[],
                phases=[],
                key_milestones=[],
                capability_development=[],
                resource_requirements={},
                risk_mitigation=[],
                success_metrics=[],
                timeline={}
            )
    
    def _select_roadmap_template(self, opportunities: List[OpportunityAssessment],
                                readiness_assessment: Dict[str, Any]) -> str:
        """Select appropriate roadmap template"""
        # Count opportunity types
        type_counts = {}
        for opp in opportunities:
            type_counts[opp.opportunity_type] = type_counts.get(opp.opportunity_type, 0) + 1
        
        # Select template based on dominant opportunity type
        if type_counts.get(OpportunityType.PLATFORM_CREATION, 0) > 0:
            return 'platform_business'
        elif type_counts.get(OpportunityType.TECHNOLOGY_ADOPTION, 0) > 0 and 'ai_ml' in str(opportunities):
            return 'ai_transformation'
        else:
            return 'digital_transformation'
    
    def _prioritize_opportunities(self, opportunities: List[OpportunityAssessment],
                                 readiness_assessment: Dict[str, Any]) -> List[OpportunityAssessment]:
        """Prioritize opportunities based on impact, complexity, and readiness"""
        def priority_score(opp):
            impact_score = opp.potential_impact
            complexity_penalty = opp.implementation_complexity * 0.5
            confidence_bonus = opp.confidence_score * 0.3
            readiness_bonus = readiness_assessment.get('readiness_score', 0.5) * 0.2
            
            return impact_score - complexity_penalty + confidence_bonus + readiness_bonus
        
        return sorted(opportunities, key=priority_score, reverse=True)
    
    def _calculate_exponential_potential(self, opportunities: List[OpportunityAssessment],
                                       readiness_assessment: Dict[str, Any]) -> float:
        """Calculate overall exponential potential score"""
        if not opportunities:
            return 0.5
        
        # Average opportunity impact
        avg_impact = sum(opp.potential_impact for opp in opportunities) / len(opportunities)
        
        # Readiness factor
        readiness_factor = readiness_assessment.get('readiness_score', 0.5)
        
        # Opportunity diversity bonus
        unique_types = len(set(opp.opportunity_type for opp in opportunities))
        diversity_bonus = min(unique_types * 0.1, 0.3)
        
        # High-impact opportunity bonus
        high_impact_count = sum(1 for opp in opportunities if opp.potential_impact > 0.7)
        high_impact_bonus = min(high_impact_count * 0.05, 0.2)
        
        exponential_potential = (
            avg_impact * 0.4 +
            readiness_factor * 0.3 +
            diversity_bonus +
            high_impact_bonus
        )
        
        return min(exponential_potential, 1.0)
    
    # Serialization methods
    def _serialize_technologies(self, technologies: List[ExponentialTechnology]) -> List[Dict[str, Any]]:
        """Serialize technologies for JSON response"""
        return [
            {
                'id': tech.id,
                'name': tech.name,
                'domain': tech.domain.value,
                'description': tech.description,
                'maturity_level': tech.maturity_level,
                'growth_rate': tech.growth_rate,
                'adoption_timeline': tech.adoption_timeline,
                'disruption_potential': tech.disruption_potential
            }
            for tech in technologies
        ]
    
    def _serialize_opportunities(self, opportunities: List[OpportunityAssessment]) -> List[Dict[str, Any]]:
        """Serialize opportunities for JSON response"""
        return [
            {
                'id': opp.id,
                'name': opp.name,
                'opportunity_type': opp.opportunity_type.value,
                'related_technologies': opp.related_technologies,
                'domains': [domain.value for domain in opp.domains],
                'description': opp.description,
                'potential_impact': opp.potential_impact,
                'implementation_complexity': opp.implementation_complexity,
                'time_to_value': opp.time_to_value,
                'readiness_level': opp.readiness_level.value,
                'key_capabilities_required': opp.key_capabilities_required,
                'potential_barriers': opp.potential_barriers,
                'success_examples': opp.success_examples,
                'confidence_score': opp.confidence_score
            }
            for opp in opportunities
        ]
    
    def _serialize_roadmap(self, roadmap: TransformationRoadmap) -> Dict[str, Any]:
        """Serialize roadmap for JSON response"""
        return {
            'id': roadmap.id,
            'title': roadmap.title,
            'description': roadmap.description,
            'target_opportunities': roadmap.target_opportunities,
            'phases': roadmap.phases,
            'key_milestones': roadmap.key_milestones,
            'capability_development': roadmap.capability_development,
            'resource_requirements': roadmap.resource_requirements,
            'risk_mitigation': roadmap.risk_mitigation,
            'success_metrics': roadmap.success_metrics,
            'timeline': roadmap.timeline
        }

# Global exponential opportunity analyzer instance
exponential_opportunity_analyzer = ExponentialOpportunityAnalyzer()    
    
def _generate_roadmap_phases(self, template: Dict[str, Any], 
                                opportunities: List[OpportunityAssessment],
                                readiness_assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate customized roadmap phases"""
        phases = []
        base_phases = template.get('phases', [])
        
        for i, base_phase in enumerate(base_phases):
            # Assign opportunities to phases based on complexity and readiness
            phase_opportunities = []
            for opp in opportunities:
                if i == 0 and opp.implementation_complexity < 0.5:  # Easy wins first
                    phase_opportunities.append(opp.id)
                elif i == 1 and 0.3 < opp.implementation_complexity < 0.7:  # Medium complexity
                    phase_opportunities.append(opp.id)
                elif i >= 2 and opp.implementation_complexity >= 0.6:  # Complex opportunities later
                    phase_opportunities.append(opp.id)
            
            phase = {
                'name': base_phase['name'],
                'description': base_phase['description'],
                'duration': base_phase['duration'],
                'key_activities': base_phase['key_activities'],
                'target_opportunities': phase_opportunities[:3],  # Max 3 opportunities per phase
                'success_criteria': self._generate_phase_success_criteria(base_phase, phase_opportunities),
                'dependencies': self._identify_phase_dependencies(i, base_phases)
            }
            phases.append(phase)
        
        return phases
    
    def _generate_phase_success_criteria(self, base_phase: Dict[str, Any], 
                                       opportunity_ids: List[str]) -> List[str]:
        """Generate success criteria for a phase"""
        criteria = []
        
        # Base criteria from template
        if 'digitization' in base_phase['name'].lower():
            criteria.extend([
                'Core processes digitized',
                'Basic automation implemented',
                'Data collection systems operational'
            ])
        elif 'intelligence' in base_phase['name'].lower():
            criteria.extend([
                'Analytics capabilities deployed',
                'AI models in production',
                'Decision support systems active'
            ])
        
        # Opportunity-specific criteria
        if opportunity_ids:
            criteria.append(f'{len(opportunity_ids)} exponential opportunities initiated')
        
        return criteria[:5]  # Max 5 criteria per phase
    
    def _identify_phase_dependencies(self, phase_index: int, 
                                   all_phases: List[Dict[str, Any]]) -> List[str]:
        """Identify dependencies between phases"""
        dependencies = []
        
        if phase_index > 0:
            dependencies.append(f"Completion of {all_phases[phase_index-1]['name']}")
        
        if phase_index > 1:
            dependencies.append("Organizational readiness validation")
        
        return dependencies
    
    def _generate_key_milestones(self, phases: List[Dict[str, Any]], 
                               opportunities: List[OpportunityAssessment]) -> List[Dict[str, Any]]:
        """Generate key milestones for the transformation"""
        milestones = []
        
        # Phase completion milestones
        for i, phase in enumerate(phases):
            milestone = {
                'name': f"{phase['name']} Phase Complete",
                'description': f"Successfully completed {phase['name']} phase activities",
                'target_date': f"Month {(i+1)*6}",  # Assuming 6-month phases
                'success_metrics': phase.get('success_criteria', []),
                'deliverables': [f"{phase['name']} phase deliverables"]
            }
            milestones.append(milestone)
        
        # Opportunity-specific milestones
        high_impact_opps = [opp for opp in opportunities if opp.potential_impact > 0.7]
        for opp in high_impact_opps[:3]:  # Top 3 high-impact opportunities
            milestone = {
                'name': f"{opp.name} Implementation",
                'description': f"Successful implementation of {opp.name}",
                'target_date': f"Month {12 if opp.time_to_value == 'medium-term' else 6}",
                'success_metrics': [f"Opportunity impact realized", f"Success criteria met"],
                'deliverables': [f"{opp.name} fully operational"]
            }
            milestones.append(milestone)
        
        return milestones
    
    def _generate_capability_development_plan(self, opportunities: List[OpportunityAssessment],
                                            readiness_assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate capability development plan"""
        capability_plan = []
        
        # Collect all required capabilities
        all_capabilities = set()
        for opp in opportunities:
            all_capabilities.update(opp.key_capabilities_required)
        
        # Prioritize capabilities based on frequency and readiness gaps
        capability_gaps = readiness_assessment.get('capability_gaps', [])
        
        for capability in list(all_capabilities)[:8]:  # Top 8 capabilities
            priority = 'high' if capability.replace(' ', '_') in capability_gaps else 'medium'
            
            development_item = {
                'capability': capability,
                'priority': priority,
                'development_approach': self._suggest_development_approach(capability),
                'timeline': '3-6 months' if priority == 'high' else '6-12 months',
                'resources_required': self._estimate_capability_resources(capability)
            }
            capability_plan.append(development_item)
        
        return capability_plan
    
    def _suggest_development_approach(self, capability: str) -> str:
        """Suggest development approach for capability"""
        approaches = {
            'digital literacy': 'Training programs and digital tool adoption',
            'data analytics': 'Analytics platform implementation and training',
            'platform design': 'Design thinking workshops and platform architecture training',
            'ecosystem orchestration': 'Partnership development and ecosystem strategy',
            'business model innovation': 'Innovation labs and business model canvas workshops',
            'change management': 'Change management certification and process implementation'
        }
        
        return approaches.get(capability, 'Targeted training and skill development programs')
    
    def _estimate_capability_resources(self, capability: str) -> Dict[str, Any]:
        """Estimate resources required for capability development"""
        return {
            'budget_range': '$50K-200K',
            'time_investment': '20-40 hours per person',
            'external_support': 'Recommended for specialized capabilities',
            'internal_champions': '2-3 dedicated team members'
        }
    
    def _estimate_resource_requirements(self, opportunities: List[OpportunityAssessment],
                                      phases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate overall resource requirements"""
        # Base resource estimation
        total_opportunities = len(opportunities)
        high_complexity_count = sum(1 for opp in opportunities if opp.implementation_complexity > 0.7)
        
        return {
            'budget_estimate': {
                'total_range': f'${total_opportunities * 200}K - ${total_opportunities * 500}K',
                'breakdown': {
                    'technology_investment': '40-50%',
                    'capability_development': '25-30%',
                    'change_management': '15-20%',
                    'external_consulting': '10-15%'
                }
            },
            'team_requirements': {
                'core_team_size': f'{max(3, total_opportunities // 2)} people',
                'specialized_roles': ['Digital transformation lead', 'Technology architect', 'Change manager'],
                'external_expertise': 'Recommended for complex implementations'
            },
            'timeline_estimate': f'{len(phases) * 6} months',
            'infrastructure_needs': [
                'Cloud platform capabilities',
                'Data analytics infrastructure',
                'Integration platforms',
                'Security and compliance tools'
            ]
        }
    
    def _generate_risk_mitigation_plan(self, opportunities: List[OpportunityAssessment]) -> List[Dict[str, Any]]:
        """Generate risk mitigation plan"""
        risks = []
        
        # Collect all potential barriers as risks
        all_barriers = set()
        for opp in opportunities:
            all_barriers.update(opp.potential_barriers)
        
        # Convert barriers to risks with mitigation strategies
        for barrier in list(all_barriers)[:6]:  # Top 6 risks
            risk = {
                'risk': barrier,
                'impact': 'medium',  # Default impact
                'probability': 'medium',  # Default probability
                'mitigation_strategy': self._suggest_mitigation_strategy(barrier),
                'contingency_plan': self._suggest_contingency_plan(barrier),
                'owner': 'Transformation team'
            }
            risks.append(risk)
        
        return risks
    
    def _suggest_mitigation_strategy(self, barrier: str) -> str:
        """Suggest mitigation strategy for barrier"""
        strategies = {
            'technical complexity': 'Phased implementation with proof of concepts',
            'skill gaps': 'Comprehensive training and external expertise',
            'change resistance': 'Change management program and stakeholder engagement',
            'funding constraints': 'Business case development and phased investment',
            'integration challenges': 'API-first architecture and integration testing',
            'regulatory compliance': 'Early regulatory engagement and compliance framework'
        }
        
        return strategies.get(barrier, 'Proactive planning and stakeholder engagement')
    
    def _suggest_contingency_plan(self, barrier: str) -> str:
        """Suggest contingency plan for barrier"""
        return f"Alternative approach and timeline adjustment for {barrier}"
    
    def _define_success_metrics(self, opportunities: List[OpportunityAssessment],
                               template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define success metrics for transformation"""
        metrics = []
        
        # Template-based metrics
        template_metrics = template.get('success_metrics', [])
        for metric_name in template_metrics[:3]:
            metric = {
                'name': metric_name,
                'description': f'Measure of {metric_name.lower()}',
                'target': 'TBD based on baseline',
                'measurement_frequency': 'Monthly',
                'owner': 'Transformation team'
            }
            metrics.append(metric)
        
        # Opportunity-specific metrics
        if opportunities:
            avg_impact = sum(opp.potential_impact for opp in opportunities) / len(opportunities)
            metrics.append({
                'name': 'Exponential Opportunity Realization',
                'description': 'Percentage of identified opportunities successfully implemented',
                'target': f'{int(avg_impact * 100)}% of opportunities realized',
                'measurement_frequency': 'Quarterly',
                'owner': 'Opportunity leads'
            })
        
        return metrics
    
    def _create_transformation_timeline(self, phases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create transformation timeline"""
        return {
            'total_duration': f'{len(phases) * 6} months',
            'phases': [
                {
                    'phase': phase['name'],
                    'start_month': i * 6 + 1,
                    'end_month': (i + 1) * 6,
                    'duration': phase['duration']
                }
                for i, phase in enumerate(phases)
            ],
            'key_decision_points': [
                f'Month {i * 6 + 3}: {phase["name"]} mid-point review'
                for i, phase in enumerate(phases)
            ]
        }