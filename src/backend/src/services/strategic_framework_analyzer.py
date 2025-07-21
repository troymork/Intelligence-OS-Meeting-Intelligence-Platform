"""
Strategic Framework Analyzer for Intelligence OS
Multi-framework strategic alignment assessment system
"""

import os
import asyncio
import logging
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

class FrameworkType(Enum):
    """Types of strategic frameworks"""
    SDG = "sdg"
    DOUGHNUT_ECONOMY = "doughnut_economy"
    AGREEMENT_ECONOMY = "agreement_economy"

class AlignmentLevel(Enum):
    """Levels of framework alignment"""
    MISALIGNED = "misaligned"
    PARTIALLY_ALIGNED = "partially_aligned"
    WELL_ALIGNED = "well_aligned"
    EXEMPLARY = "exemplary"

@dataclass
class FrameworkElement:
    """Individual element within a strategic framework"""
    id: str
    name: str
    description: str
    framework: FrameworkType
    keywords: List[str]
    indicators: List[str]
    measurement_criteria: List[str]
    weight: float = 1.0

@dataclass
class AlignmentAssessment:
    """Assessment of alignment with a framework element"""
    element_id: str
    alignment_score: float  # 0.0 to 1.0
    alignment_level: AlignmentLevel
    evidence: List[str]
    gaps: List[str]
    opportunities: List[str]
    confidence: float
    recommendations: List[str] = field(default_factory=list)

@dataclass
class FrameworkAnalysis:
    """Complete analysis of alignment with a strategic framework"""
    framework: FrameworkType
    overall_score: float
    alignment_level: AlignmentLevel
    element_assessments: List[AlignmentAssessment]
    key_strengths: List[str]
    primary_gaps: List[str]
    strategic_opportunities: List[str]
    recommendations: List[str]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CrossFrameworkSynthesis:
    """Synthesis across multiple strategic frameworks"""
    frameworks_analyzed: List[FrameworkType]
    overall_strategic_health: float
    synergies: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    optimization_opportunities: List[Dict[str, Any]]
    integrated_recommendations: List[Dict[str, Any]]
    strategic_priorities: List[str]
    implementation_roadmap: List[Dict[str, Any]]

class StrategicFrameworkAnalyzer:
    """Comprehensive strategic framework alignment analyzer"""
    
    def __init__(self):
        self.frameworks = self._initialize_frameworks()
        self.alignment_history = defaultdict(list)
        self.cross_framework_patterns = {}
        
        # Analysis configuration
        self.alignment_thresholds = {
            AlignmentLevel.MISALIGNED: 0.3,
            AlignmentLevel.PARTIALLY_ALIGNED: 0.6,
            AlignmentLevel.WELL_ALIGNED: 0.8,
            AlignmentLevel.EXEMPLARY: 0.9
        }
    
    def _initialize_frameworks(self) -> Dict[FrameworkType, List[FrameworkElement]]:
        """Initialize strategic framework definitions"""
        frameworks = {}
        
        # SDG Framework (Sustainable Development Goals)
        frameworks[FrameworkType.SDG] = [
            FrameworkElement(
                id="sdg_1",
                name="No Poverty",
                description="End poverty in all its forms everywhere",
                framework=FrameworkType.SDG,
                keywords=["poverty", "income", "basic needs", "economic security", "social protection"],
                indicators=["poverty reduction", "income equality", "social safety nets"],
                measurement_criteria=["poverty rate reduction", "income distribution", "access to basic services"]
            ),
            FrameworkElement(
                id="sdg_2",
                name="Zero Hunger",
                description="End hunger, achieve food security and improved nutrition",
                framework=FrameworkType.SDG,
                keywords=["hunger", "food security", "nutrition", "agriculture", "sustainable farming"],
                indicators=["food access", "nutritional quality", "agricultural sustainability"],
                measurement_criteria=["food security index", "malnutrition rates", "sustainable agriculture practices"]
            ),
            FrameworkElement(
                id="sdg_3",
                name="Good Health and Well-being",
                description="Ensure healthy lives and promote well-being for all",
                framework=FrameworkType.SDG,
                keywords=["health", "well-being", "healthcare", "mental health", "disease prevention"],
                indicators=["health outcomes", "healthcare access", "wellness programs"],
                measurement_criteria=["health indicators", "healthcare coverage", "wellness metrics"]
            ),
            FrameworkElement(
                id="sdg_4",
                name="Quality Education",
                description="Ensure inclusive and equitable quality education",
                framework=FrameworkType.SDG,
                keywords=["education", "learning", "skills", "knowledge", "training", "development"],
                indicators=["educational access", "learning outcomes", "skill development"],
                measurement_criteria=["literacy rates", "educational attainment", "skill acquisition"]
            ),
            FrameworkElement(
                id="sdg_8",
                name="Decent Work and Economic Growth",
                description="Promote sustained, inclusive and sustainable economic growth",
                framework=FrameworkType.SDG,
                keywords=["employment", "economic growth", "decent work", "productivity", "innovation"],
                indicators=["job creation", "economic development", "work quality"],
                measurement_criteria=["employment rates", "GDP growth", "job quality metrics"]
            ),
            FrameworkElement(
                id="sdg_9",
                name="Industry, Innovation and Infrastructure",
                description="Build resilient infrastructure, promote inclusive industrialization",
                framework=FrameworkType.SDG,
                keywords=["innovation", "infrastructure", "technology", "research", "development"],
                indicators=["innovation capacity", "infrastructure quality", "technological advancement"],
                measurement_criteria=["R&D investment", "infrastructure index", "innovation metrics"]
            ),
            FrameworkElement(
                id="sdg_10",
                name="Reduced Inequality",
                description="Reduce inequality within and among countries",
                framework=FrameworkType.SDG,
                keywords=["equality", "inclusion", "diversity", "fairness", "social justice"],
                indicators=["income equality", "social inclusion", "equal opportunities"],
                measurement_criteria=["gini coefficient", "inclusion metrics", "equality indicators"]
            ),
            FrameworkElement(
                id="sdg_16",
                name="Peace, Justice and Strong Institutions",
                description="Promote peaceful and inclusive societies",
                framework=FrameworkType.SDG,
                keywords=["peace", "justice", "governance", "transparency", "accountability"],
                indicators=["governance quality", "transparency levels", "justice access"],
                measurement_criteria=["governance index", "transparency score", "justice metrics"]
            ),
            FrameworkElement(
                id="sdg_17",
                name="Partnerships for the Goals",
                description="Strengthen means of implementation and revitalize partnerships",
                framework=FrameworkType.SDG,
                keywords=["partnership", "collaboration", "cooperation", "alliance", "collective action"],
                indicators=["partnership quality", "collaborative outcomes", "collective impact"],
                measurement_criteria=["partnership effectiveness", "collaboration metrics", "collective results"]
            )
        ]
        
        # Doughnut Economy Framework
        frameworks[FrameworkType.DOUGHNUT_ECONOMY] = [
            # Social Foundation Elements
            FrameworkElement(
                id="de_food",
                name="Food",
                description="Access to sufficient, nutritious food",
                framework=FrameworkType.DOUGHNUT_ECONOMY,
                keywords=["food", "nutrition", "hunger", "agriculture", "food security"],
                indicators=["food access", "nutritional adequacy", "food system sustainability"],
                measurement_criteria=["food security metrics", "nutritional outcomes", "sustainable food systems"]
            ),
            FrameworkElement(
                id="de_health",
                name="Health",
                description="Access to healthcare and healthy living conditions",
                framework=FrameworkType.DOUGHNUT_ECONOMY,
                keywords=["health", "healthcare", "wellness", "medical", "well-being"],
                indicators=["health outcomes", "healthcare access", "health equity"],
                measurement_criteria=["health indicators", "healthcare coverage", "health equity metrics"]
            ),
            FrameworkElement(
                id="de_education",
                name="Education",
                description="Access to quality education and learning opportunities",
                framework=FrameworkType.DOUGHNUT_ECONOMY,
                keywords=["education", "learning", "knowledge", "skills", "training"],
                indicators=["educational access", "learning quality", "skill development"],
                measurement_criteria=["education metrics", "learning outcomes", "skill indicators"]
            ),
            FrameworkElement(
                id="de_income_work",
                name="Income & Work",
                description="Access to decent work and adequate income",
                framework=FrameworkType.DOUGHNUT_ECONOMY,
                keywords=["income", "work", "employment", "wages", "livelihood"],
                indicators=["income adequacy", "work quality", "employment security"],
                measurement_criteria=["income levels", "job quality", "employment stability"]
            ),
            FrameworkElement(
                id="de_social_equity",
                name="Social Equity",
                description="Freedom from discrimination and equal opportunities",
                framework=FrameworkType.DOUGHNUT_ECONOMY,
                keywords=["equity", "equality", "fairness", "inclusion", "diversity"],
                indicators=["social inclusion", "equal opportunities", "discrimination absence"],
                measurement_criteria=["equity metrics", "inclusion indicators", "diversity measures"]
            ),
            # Ecological Ceiling Elements
            FrameworkElement(
                id="de_climate_change",
                name="Climate Change",
                description="Staying within safe climate boundaries",
                framework=FrameworkType.DOUGHNUT_ECONOMY,
                keywords=["climate", "carbon", "emissions", "sustainability", "environment"],
                indicators=["carbon footprint", "climate impact", "environmental sustainability"],
                measurement_criteria=["carbon emissions", "climate metrics", "environmental indicators"]
            ),
            FrameworkElement(
                id="de_biodiversity",
                name="Biodiversity Loss",
                description="Protecting biodiversity and ecosystems",
                framework=FrameworkType.DOUGHNUT_ECONOMY,
                keywords=["biodiversity", "ecosystem", "species", "conservation", "nature"],
                indicators=["biodiversity protection", "ecosystem health", "conservation efforts"],
                measurement_criteria=["biodiversity index", "ecosystem metrics", "conservation indicators"]
            )
        ]
        
        # Agreement Economy Framework
        frameworks[FrameworkType.AGREEMENT_ECONOMY] = [
            FrameworkElement(
                id="ae_value_creation",
                name="Value Creation",
                description="Creating shared value for all stakeholders",
                framework=FrameworkType.AGREEMENT_ECONOMY,
                keywords=["value", "creation", "benefit", "stakeholder", "shared value"],
                indicators=["stakeholder value", "shared benefits", "value distribution"],
                measurement_criteria=["value creation metrics", "stakeholder satisfaction", "benefit sharing"]
            ),
            FrameworkElement(
                id="ae_collaborative_governance",
                name="Collaborative Governance",
                description="Participatory and inclusive decision-making processes",
                framework=FrameworkType.AGREEMENT_ECONOMY,
                keywords=["governance", "collaboration", "participation", "inclusion", "democracy"],
                indicators=["participatory governance", "inclusive decision-making", "collaborative processes"],
                measurement_criteria=["participation rates", "governance quality", "collaboration effectiveness"]
            ),
            FrameworkElement(
                id="ae_shared_resources",
                name="Shared Resources",
                description="Equitable access to and stewardship of resources",
                framework=FrameworkType.AGREEMENT_ECONOMY,
                keywords=["resources", "sharing", "commons", "stewardship", "access"],
                indicators=["resource sharing", "equitable access", "stewardship quality"],
                measurement_criteria=["resource distribution", "access equity", "stewardship metrics"]
            ),
            FrameworkElement(
                id="ae_collective_intelligence",
                name="Collective Intelligence",
                description="Harnessing collective wisdom and knowledge",
                framework=FrameworkType.AGREEMENT_ECONOMY,
                keywords=["intelligence", "collective", "wisdom", "knowledge", "learning"],
                indicators=["knowledge sharing", "collective learning", "wisdom application"],
                measurement_criteria=["knowledge metrics", "learning outcomes", "collective intelligence indicators"]
            ),
            FrameworkElement(
                id="ae_regenerative_practices",
                name="Regenerative Practices",
                description="Practices that restore and regenerate systems",
                framework=FrameworkType.AGREEMENT_ECONOMY,
                keywords=["regenerative", "restoration", "renewal", "sustainability", "healing"],
                indicators=["regenerative impact", "system restoration", "sustainability practices"],
                measurement_criteria=["regeneration metrics", "restoration indicators", "sustainability measures"]
            ),
            FrameworkElement(
                id="ae_transparent_accountability",
                name="Transparent Accountability",
                description="Open and accountable processes and outcomes",
                framework=FrameworkType.AGREEMENT_ECONOMY,
                keywords=["transparency", "accountability", "openness", "responsibility", "trust"],
                indicators=["transparency levels", "accountability measures", "trust building"],
                measurement_criteria=["transparency index", "accountability metrics", "trust indicators"]
            )
        ]
        
        return frameworks
    
    async def analyze_strategic_alignment(self, content: str, 
                                        organization_context: Dict[str, Any] = None,
                                        frameworks_to_analyze: List[FrameworkType] = None) -> Dict[str, Any]:
        """Analyze strategic alignment across multiple frameworks"""
        try:
            if frameworks_to_analyze is None:
                frameworks_to_analyze = list(FrameworkType)
            
            framework_analyses = {}
            
            # Analyze each framework
            for framework_type in frameworks_to_analyze:
                analysis = await self._analyze_single_framework(
                    content, framework_type, organization_context
                )
                framework_analyses[framework_type.value] = analysis
            
            # Perform cross-framework synthesis
            synthesis = await self._perform_cross_framework_synthesis(
                framework_analyses, content, organization_context
            )
            
            return {
                'framework_analyses': {k: self._serialize_framework_analysis(v) 
                                     for k, v in framework_analyses.items()},
                'cross_framework_synthesis': self._serialize_synthesis(synthesis),
                'overall_strategic_health': synthesis.overall_strategic_health,
                'timestamp': datetime.utcnow().isoformat(),
                'frameworks_analyzed': [f.value for f in frameworks_to_analyze]
            }
            
        except Exception as e:
            logger.error("Strategic alignment analysis failed", error=str(e))
            return {
                'framework_analyses': {},
                'cross_framework_synthesis': {},
                'overall_strategic_health': 0.5,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

# Global strategic framework analyzer instance
strategic_framework_analyzer = StrategicFrameworkAnalyzer()    
   
 async def _analyze_single_framework(self, content: str, framework_type: FrameworkType,
                                      organization_context: Dict[str, Any] = None) -> FrameworkAnalysis:
        """Analyze alignment with a single strategic framework"""
        try:
            framework_elements = self.frameworks.get(framework_type, [])
            element_assessments = []
            
            # Analyze each element in the framework
            for element in framework_elements:
                assessment = await self._assess_element_alignment(content, element, organization_context)
                element_assessments.append(assessment)
            
            # Calculate overall framework score
            if element_assessments:
                scores = [assessment.alignment_score for assessment in element_assessments]
                weights = [self.frameworks[framework_type][i].weight for i in range(len(scores))]
                overall_score = np.average(scores, weights=weights)
            else:
                overall_score = 0.5
            
            # Determine alignment level
            alignment_level = self._determine_alignment_level(overall_score)
            
            # Extract key insights
            key_strengths = self._extract_strengths(element_assessments)
            primary_gaps = self._extract_gaps(element_assessments)
            strategic_opportunities = self._extract_opportunities(element_assessments)
            recommendations = self._generate_framework_recommendations(
                framework_type, element_assessments, organization_context
            )
            
            # Calculate confidence
            confidences = [assessment.confidence for assessment in element_assessments]
            overall_confidence = np.mean(confidences) if confidences else 0.5
            
            return FrameworkAnalysis(
                framework=framework_type,
                overall_score=overall_score,
                alignment_level=alignment_level,
                element_assessments=element_assessments,
                key_strengths=key_strengths,
                primary_gaps=primary_gaps,
                strategic_opportunities=strategic_opportunities,
                recommendations=recommendations,
                confidence=overall_confidence
            )
            
        except Exception as e:
            logger.error("Single framework analysis failed", 
                        framework=framework_type.value, error=str(e))
            return FrameworkAnalysis(
                framework=framework_type,
                overall_score=0.5,
                alignment_level=AlignmentLevel.PARTIALLY_ALIGNED,
                element_assessments=[],
                key_strengths=[],
                primary_gaps=[],
                strategic_opportunities=[],
                recommendations=[],
                confidence=0.3
            )
    
    async def _assess_element_alignment(self, content: str, element: FrameworkElement,
                                      organization_context: Dict[str, Any] = None) -> AlignmentAssessment:
        """Assess alignment with a specific framework element"""
        try:
            content_lower = content.lower()
            
            # Keyword matching
            keyword_matches = 0
            evidence = []
            
            for keyword in element.keywords:
                if keyword.lower() in content_lower:
                    keyword_matches += 1
                    # Find sentences containing the keyword
                    sentences = re.findall(f"[^.!?]*{keyword}[^.!?]*[.!?]", content, re.IGNORECASE)
                    evidence.extend(sentences[:2])  # Limit evidence per keyword
            
            # Calculate base alignment score
            keyword_score = min(1.0, keyword_matches / len(element.keywords)) if element.keywords else 0.0
            
            # Indicator matching
            indicator_matches = 0
            for indicator in element.indicators:
                if any(word in content_lower for word in indicator.lower().split()):
                    indicator_matches += 1
            
            indicator_score = min(1.0, indicator_matches / len(element.indicators)) if element.indicators else 0.0
            
            # Combine scores
            alignment_score = (keyword_score * 0.6 + indicator_score * 0.4)
            
            # Adjust based on organization context
            if organization_context:
                context_adjustment = self._calculate_context_adjustment(element, organization_context)
                alignment_score = min(1.0, alignment_score * context_adjustment)
            
            # Determine alignment level
            alignment_level = self._determine_alignment_level(alignment_score)
            
            # Identify gaps and opportunities
            gaps = self._identify_element_gaps(element, alignment_score, evidence)
            opportunities = self._identify_element_opportunities(element, alignment_score, organization_context)
            
            # Generate recommendations
            recommendations = self._generate_element_recommendations(element, alignment_score, gaps, opportunities)
            
            # Calculate confidence based on evidence quality
            confidence = min(1.0, len(evidence) * 0.1 + keyword_matches * 0.05)
            confidence = max(0.3, confidence)
            
            return AlignmentAssessment(
                element_id=element.id,
                alignment_score=alignment_score,
                alignment_level=alignment_level,
                evidence=evidence[:5],  # Limit evidence
                gaps=gaps,
                opportunities=opportunities,
                confidence=confidence,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error("Element alignment assessment failed", 
                        element_id=element.id, error=str(e))
            return AlignmentAssessment(
                element_id=element.id,
                alignment_score=0.5,
                alignment_level=AlignmentLevel.PARTIALLY_ALIGNED,
                evidence=[],
                gaps=[],
                opportunities=[],
                confidence=0.3,
                recommendations=[]
            )
    
    def _determine_alignment_level(self, score: float) -> AlignmentLevel:
        """Determine alignment level based on score"""
        if score >= self.alignment_thresholds[AlignmentLevel.EXEMPLARY]:
            return AlignmentLevel.EXEMPLARY
        elif score >= self.alignment_thresholds[AlignmentLevel.WELL_ALIGNED]:
            return AlignmentLevel.WELL_ALIGNED
        elif score >= self.alignment_thresholds[AlignmentLevel.PARTIALLY_ALIGNED]:
            return AlignmentLevel.PARTIALLY_ALIGNED
        else:
            return AlignmentLevel.MISALIGNED
    
    def _calculate_context_adjustment(self, element: FrameworkElement, 
                                    organization_context: Dict[str, Any]) -> float:
        """Calculate context-based adjustment to alignment score"""
        try:
            adjustment = 1.0
            
            # Industry context
            industry = organization_context.get('industry', '').lower()
            if element.framework == FrameworkType.SDG:
                if 'technology' in industry and element.id in ['sdg_9', 'sdg_4']:
                    adjustment += 0.2  # Tech companies likely stronger on innovation and education
                elif 'healthcare' in industry and element.id == 'sdg_3':
                    adjustment += 0.3  # Healthcare companies stronger on health
            
            # Organization size
            size = organization_context.get('size', 'medium').lower()
            if size == 'large' and element.framework == FrameworkType.AGREEMENT_ECONOMY:
                adjustment += 0.1  # Larger orgs may have more collaborative structures
            
            # Mission alignment
            mission = organization_context.get('mission', '').lower()
            for keyword in element.keywords:
                if keyword.lower() in mission:
                    adjustment += 0.15
                    break
            
            return min(1.5, adjustment)  # Cap adjustment at 1.5x
            
        except Exception as e:
            logger.error("Context adjustment calculation failed", error=str(e))
            return 1.0
    
    def _extract_strengths(self, assessments: List[AlignmentAssessment]) -> List[str]:
        """Extract key strengths from element assessments"""
        try:
            strengths = []
            
            # Find well-aligned elements
            strong_elements = [a for a in assessments if a.alignment_score > 0.7]
            
            for assessment in strong_elements[:5]:  # Top 5 strengths
                element = next((e for elements in self.frameworks.values() 
                              for e in elements if e.id == assessment.element_id), None)
                if element:
                    strengths.append(f"Strong alignment with {element.name}")
            
            return strengths
            
        except Exception as e:
            logger.error("Strengths extraction failed", error=str(e))
            return []
    
    def _extract_gaps(self, assessments: List[AlignmentAssessment]) -> List[str]:
        """Extract primary gaps from element assessments"""
        try:
            gaps = []
            
            # Find poorly aligned elements
            weak_elements = [a for a in assessments if a.alignment_score < 0.4]
            
            for assessment in weak_elements[:5]:  # Top 5 gaps
                element = next((e for elements in self.frameworks.values() 
                              for e in elements if e.id == assessment.element_id), None)
                if element:
                    gaps.append(f"Limited alignment with {element.name}")
            
            return gaps
            
        except Exception as e:
            logger.error("Gaps extraction failed", error=str(e))
            return []
    
    def _extract_opportunities(self, assessments: List[AlignmentAssessment]) -> List[str]:
        """Extract strategic opportunities from assessments"""
        try:
            opportunities = []
            
            # Combine opportunities from all assessments
            for assessment in assessments:
                opportunities.extend(assessment.opportunities)
            
            # Remove duplicates and limit
            unique_opportunities = list(set(opportunities))
            return unique_opportunities[:10]
            
        except Exception as e:
            logger.error("Opportunities extraction failed", error=str(e))
            return []
    
    def _identify_element_gaps(self, element: FrameworkElement, score: float, 
                             evidence: List[str]) -> List[str]:
        """Identify gaps for a specific element"""
        try:
            gaps = []
            
            if score < 0.4:
                gaps.append(f"Minimal evidence of {element.name.lower()} focus")
                
                if not evidence:
                    gaps.append(f"No explicit mention of {element.name.lower()} priorities")
                
                # Element-specific gaps
                if element.framework == FrameworkType.SDG:
                    if element.id == 'sdg_4':
                        gaps.append("Limited focus on learning and development initiatives")
                    elif element.id == 'sdg_8':
                        gaps.append("Insufficient emphasis on decent work conditions")
                
                elif element.framework == FrameworkType.DOUGHNUT_ECONOMY:
                    if 'climate' in element.id:
                        gaps.append("Environmental sustainability not prioritized")
                    elif 'social' in element.id:
                        gaps.append("Social equity considerations underdeveloped")
                
                elif element.framework == FrameworkType.AGREEMENT_ECONOMY:
                    if 'collaborative' in element.id:
                        gaps.append("Collaborative governance structures absent")
                    elif 'transparency' in element.id:
                        gaps.append("Transparency and accountability mechanisms lacking")
            
            return gaps[:3]  # Limit to top 3 gaps
            
        except Exception as e:
            logger.error("Element gaps identification failed", error=str(e))
            return []
    
    def _identify_element_opportunities(self, element: FrameworkElement, score: float,
                                      organization_context: Dict[str, Any] = None) -> List[str]:
        """Identify opportunities for a specific element"""
        try:
            opportunities = []
            
            if score < 0.7:  # Room for improvement
                # Generic opportunities
                opportunities.append(f"Strengthen {element.name.lower()} initiatives")
                
                # Element-specific opportunities
                if element.framework == FrameworkType.SDG:
                    if element.id == 'sdg_9':
                        opportunities.append("Invest in innovation and R&D capabilities")
                    elif element.id == 'sdg_17':
                        opportunities.append("Develop strategic partnerships for greater impact")
                
                elif element.framework == FrameworkType.DOUGHNUT_ECONOMY:
                    if 'climate' in element.id:
                        opportunities.append("Implement carbon reduction and sustainability programs")
                    elif 'education' in element.id:
                        opportunities.append("Expand learning and development opportunities")
                
                elif element.framework == FrameworkType.AGREEMENT_ECONOMY:
                    if 'value_creation' in element.id:
                        opportunities.append("Develop shared value creation strategies")
                    elif 'collective_intelligence' in element.id:
                        opportunities.append("Harness collective wisdom through collaboration platforms")
            
            return opportunities[:3]  # Limit to top 3 opportunities
            
        except Exception as e:
            logger.error("Element opportunities identification failed", error=str(e))
            return []
    
    def _generate_element_recommendations(self, element: FrameworkElement, score: float,
                                        gaps: List[str], opportunities: List[str]) -> List[str]:
        """Generate recommendations for a specific element"""
        try:
            recommendations = []
            
            if score < 0.5:
                recommendations.append(f"Develop comprehensive {element.name.lower()} strategy")
                recommendations.append(f"Integrate {element.name.lower()} metrics into performance measurement")
            
            elif score < 0.8:
                recommendations.append(f"Enhance existing {element.name.lower()} initiatives")
                recommendations.append(f"Expand {element.name.lower()} impact measurement")
            
            # Add opportunity-based recommendations
            for opportunity in opportunities[:2]:
                recommendations.append(f"Consider: {opportunity}")
            
            return recommendations[:5]  # Limit to top 5 recommendations
            
        except Exception as e:
            logger.error("Element recommendations generation failed", error=str(e))
            return []
    
    def _generate_framework_recommendations(self, framework_type: FrameworkType,
                                         assessments: List[AlignmentAssessment],
                                         organization_context: Dict[str, Any] = None) -> List[str]:
        """Generate framework-level recommendations"""
        try:
            recommendations = []
            
            # Calculate average score
            avg_score = np.mean([a.alignment_score for a in assessments]) if assessments else 0.5
            
            # Framework-specific recommendations
            if framework_type == FrameworkType.SDG:
                if avg_score < 0.6:
                    recommendations.append("Develop comprehensive SDG integration strategy")
                    recommendations.append("Establish SDG measurement and reporting framework")
                recommendations.append("Align business strategy with relevant SDG targets")
                
            elif framework_type == FrameworkType.DOUGHNUT_ECONOMY:
                if avg_score < 0.6:
                    recommendations.append("Adopt regenerative business practices")
                    recommendations.append("Balance social foundation with ecological ceiling")
                recommendations.append("Implement circular economy principles")
                
            elif framework_type == FrameworkType.AGREEMENT_ECONOMY:
                if avg_score < 0.6:
                    recommendations.append("Strengthen collaborative governance structures")
                    recommendations.append("Develop shared value creation mechanisms")
                recommendations.append("Enhance transparency and accountability systems")
            
            return recommendations[:5]
            
        except Exception as e:
            logger.error("Framework recommendations generation failed", error=str(e))
            return []    

    async def _perform_cross_framework_synthesis(self, framework_analyses: Dict[str, FrameworkAnalysis],
                                               content: str, organization_context: Dict[str, Any] = None) -> CrossFrameworkSynthesis:
        """Perform synthesis across multiple strategic frameworks"""
        try:
            frameworks_analyzed = [FrameworkType(k) for k in framework_analyses.keys()]
            
            # Calculate overall strategic health
            framework_scores = [analysis.overall_score for analysis in framework_analyses.values()]
            overall_strategic_health = np.mean(framework_scores) if framework_scores else 0.5
            
            # Identify synergies between frameworks
            synergies = await self._identify_cross_framework_synergies(framework_analyses)
            
            # Identify conflicts between frameworks
            conflicts = await self._identify_cross_framework_conflicts(framework_analyses)
            
            # Find optimization opportunities
            optimization_opportunities = await self._identify_optimization_opportunities(framework_analyses)
            
            # Generate integrated recommendations
            integrated_recommendations = await self._generate_integrated_recommendations(
                framework_analyses, synergies, conflicts, organization_context
            )
            
            # Determine strategic priorities
            strategic_priorities = await self._determine_strategic_priorities(
                framework_analyses, synergies, optimization_opportunities
            )
            
            # Create implementation roadmap
            implementation_roadmap = await self._create_implementation_roadmap(
                integrated_recommendations, strategic_priorities, organization_context
            )
            
            return CrossFrameworkSynthesis(
                frameworks_analyzed=frameworks_analyzed,
                overall_strategic_health=overall_strategic_health,
                synergies=synergies,
                conflicts=conflicts,
                optimization_opportunities=optimization_opportunities,
                integrated_recommendations=integrated_recommendations,
                strategic_priorities=strategic_priorities,
                implementation_roadmap=implementation_roadmap
            )
            
        except Exception as e:
            logger.error("Cross-framework synthesis failed", error=str(e))
            return CrossFrameworkSynthesis(
                frameworks_analyzed=frameworks_analyzed,
                overall_strategic_health=0.5,
                synergies=[],
                conflicts=[],
                optimization_opportunities=[],
                integrated_recommendations=[],
                strategic_priorities=[],
                implementation_roadmap=[]
            )
    
    async def _identify_cross_framework_synergies(self, framework_analyses: Dict[str, FrameworkAnalysis]) -> List[Dict[str, Any]]:
        """Identify synergies between different frameworks"""
        try:
            synergies = []
            
            # Define known synergies between frameworks
            synergy_mappings = {
                ('sdg', 'doughnut_economy'): {
                    'elements': [('sdg_3', 'de_health'), ('sdg_4', 'de_education'), ('sdg_8', 'de_income_work')],
                    'description': 'SDGs and Doughnut Economy share common social foundation elements'
                },
                ('sdg', 'agreement_economy'): {
                    'elements': [('sdg_17', 'ae_collaborative_governance'), ('sdg_16', 'ae_transparent_accountability')],
                    'description': 'SDGs and Agreement Economy align on governance and partnership principles'
                },
                ('doughnut_economy', 'agreement_economy'): {
                    'elements': [('de_social_equity', 'ae_value_creation'), ('de_climate_change', 'ae_regenerative_practices')],
                    'description': 'Doughnut Economy and Agreement Economy share regenerative and equity focus'
                }
            }
            
            # Check for synergies based on element performance
            for (framework1, framework2), synergy_info in synergy_mappings.items():
                if framework1 in framework_analyses and framework2 in framework_analyses:
                    analysis1 = framework_analyses[framework1]
                    analysis2 = framework_analyses[framework2]
                    
                    # Calculate synergy strength based on aligned elements
                    synergy_strength = 0.0
                    aligned_elements = []
                    
                    for element1_id, element2_id in synergy_info['elements']:
                        assessment1 = next((a for a in analysis1.element_assessments if a.element_id == element1_id), None)
                        assessment2 = next((a for a in analysis2.element_assessments if a.element_id == element2_id), None)
                        
                        if assessment1 and assessment2:
                            element_synergy = min(assessment1.alignment_score, assessment2.alignment_score)
                            synergy_strength += element_synergy
                            if element_synergy > 0.6:
                                aligned_elements.append((element1_id, element2_id))
                    
                    if aligned_elements:
                        synergies.append({
                            'frameworks': [framework1, framework2],
                            'strength': synergy_strength / len(synergy_info['elements']),
                            'description': synergy_info['description'],
                            'aligned_elements': aligned_elements,
                            'opportunities': [
                                f"Leverage {framework1.upper()}-{framework2.upper()} alignment for integrated strategy",
                                f"Develop joint initiatives that advance both {framework1} and {framework2} goals"
                            ]
                        })
            
            return synergies
            
        except Exception as e:
            logger.error("Cross-framework synergies identification failed", error=str(e))
            return []
    
    async def _identify_cross_framework_conflicts(self, framework_analyses: Dict[str, FrameworkAnalysis]) -> List[Dict[str, Any]]:
        """Identify potential conflicts between frameworks"""
        try:
            conflicts = []
            
            # Define potential conflict areas
            conflict_areas = {
                ('sdg', 'doughnut_economy'): {
                    'area': 'Economic Growth vs Environmental Limits',
                    'description': 'SDG 8 (Economic Growth) may conflict with Doughnut Economy ecological ceiling'
                },
                ('agreement_economy', 'sdg'): {
                    'area': 'Collaborative vs Competitive Approaches',
                    'description': 'Agreement Economy collaboration may conflict with competitive market approaches in some SDGs'
                }
            }
            
            # Analyze for actual conflicts based on assessment data
            for (framework1, framework2), conflict_info in conflict_areas.items():
                if framework1 in framework_analyses and framework2 in framework_analyses:
                    analysis1 = framework_analyses[framework1]
                    analysis2 = framework_analyses[framework2]
                    
                    # Simple conflict detection based on score disparities
                    score_difference = abs(analysis1.overall_score - analysis2.overall_score)
                    
                    if score_difference > 0.3:  # Significant disparity
                        conflicts.append({
                            'frameworks': [framework1, framework2],
                            'severity': 'moderate' if score_difference < 0.5 else 'high',
                            'area': conflict_info['area'],
                            'description': conflict_info['description'],
                            'resolution_strategies': [
                                'Develop balanced approach that addresses both framework requirements',
                                'Prioritize based on organizational mission and stakeholder needs',
                                'Seek innovative solutions that transcend traditional trade-offs'
                            ]
                        })
            
            return conflicts
            
        except Exception as e:
            logger.error("Cross-framework conflicts identification failed", error=str(e))
            return []
    
    async def _identify_optimization_opportunities(self, framework_analyses: Dict[str, FrameworkAnalysis]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities across frameworks"""
        try:
            opportunities = []
            
            # Find common weak areas across frameworks
            all_assessments = []
            for analysis in framework_analyses.values():
                all_assessments.extend(analysis.element_assessments)
            
            # Group by similar themes
            theme_groups = {
                'governance': ['governance', 'accountability', 'transparency', 'participation'],
                'sustainability': ['climate', 'environment', 'regenerative', 'biodiversity'],
                'equity': ['equality', 'inclusion', 'equity', 'fairness'],
                'innovation': ['innovation', 'technology', 'development', 'learning'],
                'collaboration': ['partnership', 'collaboration', 'collective', 'shared']
            }
            
            for theme, keywords in theme_groups.items():
                theme_assessments = []
                for assessment in all_assessments:
                    element = next((e for elements in self.frameworks.values() 
                                  for e in elements if e.id == assessment.element_id), None)
                    if element and any(keyword in ' '.join(element.keywords).lower() for keyword in keywords):
                        theme_assessments.append(assessment)
                
                if theme_assessments:
                    avg_score = np.mean([a.alignment_score for a in theme_assessments])
                    if avg_score < 0.6:  # Opportunity for improvement
                        opportunities.append({
                            'theme': theme,
                            'current_performance': avg_score,
                            'improvement_potential': 1.0 - avg_score,
                            'affected_frameworks': list(set([
                                next((f.value for f, elements in self.frameworks.items() 
                                     for e in elements if e.id == a.element_id), 'unknown')
                                for a in theme_assessments
                            ])),
                            'optimization_strategies': [
                                f"Develop integrated {theme} strategy across all frameworks",
                                f"Establish {theme} center of excellence",
                                f"Create cross-functional {theme} working group"
                            ]
                        })
            
            return opportunities[:5]  # Top 5 opportunities
            
        except Exception as e:
            logger.error("Optimization opportunities identification failed", error=str(e))
            return []
    
    async def _generate_integrated_recommendations(self, framework_analyses: Dict[str, FrameworkAnalysis],
                                                 synergies: List[Dict[str, Any]], conflicts: List[Dict[str, Any]],
                                                 organization_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate integrated recommendations across frameworks"""
        try:
            recommendations = []
            
            # High-level strategic recommendations
            avg_scores = [analysis.overall_score for analysis in framework_analyses.values()]
            overall_avg = np.mean(avg_scores) if avg_scores else 0.5
            
            if overall_avg < 0.6:
                recommendations.append({
                    'priority': 'high',
                    'category': 'strategic_foundation',
                    'title': 'Establish Integrated Strategic Framework',
                    'description': 'Develop comprehensive strategy that aligns with multiple frameworks',
                    'expected_impact': 'high',
                    'timeframe': '6-12 months',
                    'frameworks_affected': list(framework_analyses.keys())
                })
            
            # Synergy-based recommendations
            for synergy in synergies:
                if synergy['strength'] > 0.7:
                    recommendations.append({
                        'priority': 'medium',
                        'category': 'synergy_leverage',
                        'title': f"Leverage {'-'.join(synergy['frameworks']).upper()} Synergy",
                        'description': synergy['description'],
                        'expected_impact': 'medium',
                        'timeframe': '3-6 months',
                        'frameworks_affected': synergy['frameworks']
                    })
            
            # Conflict resolution recommendations
            for conflict in conflicts:
                if conflict['severity'] == 'high':
                    recommendations.append({
                        'priority': 'high',
                        'category': 'conflict_resolution',
                        'title': f"Resolve {conflict['area']} Tension",
                        'description': f"Address conflicts between {' and '.join(conflict['frameworks'])}",
                        'expected_impact': 'high',
                        'timeframe': '3-9 months',
                        'frameworks_affected': conflict['frameworks']
                    })
            
            return recommendations[:10]  # Top 10 recommendations
            
        except Exception as e:
            logger.error("Integrated recommendations generation failed", error=str(e))
            return []
    
    async def _determine_strategic_priorities(self, framework_analyses: Dict[str, FrameworkAnalysis],
                                           synergies: List[Dict[str, Any]], 
                                           optimization_opportunities: List[Dict[str, Any]]) -> List[str]:
        """Determine strategic priorities based on analysis"""
        try:
            priorities = []
            
            # Priority 1: Address critical gaps
            critical_gaps = []
            for analysis in framework_analyses.values():
                if analysis.overall_score < 0.4:
                    critical_gaps.append(analysis.framework.value)
            
            if critical_gaps:
                priorities.append(f"Address critical gaps in {', '.join(critical_gaps)} alignment")
            
            # Priority 2: Leverage strong synergies
            strong_synergies = [s for s in synergies if s['strength'] > 0.7]
            if strong_synergies:
                priorities.append("Leverage cross-framework synergies for integrated impact")
            
            # Priority 3: Optimize common themes
            high_impact_opportunities = [o for o in optimization_opportunities if o['improvement_potential'] > 0.4]
            if high_impact_opportunities:
                top_theme = max(high_impact_opportunities, key=lambda x: x['improvement_potential'])['theme']
                priorities.append(f"Strengthen {top_theme} capabilities across all frameworks")
            
            # Priority 4: Build measurement and reporting
            priorities.append("Establish integrated measurement and reporting system")
            
            # Priority 5: Develop organizational capabilities
            priorities.append("Build organizational capabilities for multi-framework alignment")
            
            return priorities[:5]
            
        except Exception as e:
            logger.error("Strategic priorities determination failed", error=str(e))
            return []
    
    async def _create_implementation_roadmap(self, integrated_recommendations: List[Dict[str, Any]],
                                           strategic_priorities: List[str],
                                           organization_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Create implementation roadmap for strategic alignment"""
        try:
            roadmap = []
            
            # Phase 1: Foundation (0-6 months)
            roadmap.append({
                'phase': 'Foundation',
                'timeframe': '0-6 months',
                'objectives': [
                    'Establish strategic framework integration team',
                    'Conduct comprehensive baseline assessment',
                    'Develop integrated measurement system'
                ],
                'key_activities': [
                    'Form cross-functional strategic alignment team',
                    'Complete detailed framework alignment assessment',
                    'Design integrated KPI and measurement framework',
                    'Establish governance structure for strategic alignment'
                ],
                'success_metrics': [
                    'Team established and operational',
                    'Baseline assessment completed',
                    'Measurement framework designed'
                ]
            })
            
            # Phase 2: Implementation (6-18 months)
            roadmap.append({
                'phase': 'Implementation',
                'timeframe': '6-18 months',
                'objectives': [
                    'Execute high-priority recommendations',
                    'Address critical gaps and conflicts',
                    'Leverage identified synergies'
                ],
                'key_activities': [
                    'Implement priority strategic initiatives',
                    'Launch integrated programs addressing multiple frameworks',
                    'Establish cross-framework collaboration mechanisms',
                    'Begin regular monitoring and reporting'
                ],
                'success_metrics': [
                    'Priority initiatives launched',
                    'Framework alignment scores improved',
                    'Synergies actively leveraged'
                ]
            })
            
            # Phase 3: Optimization (18-36 months)
            roadmap.append({
                'phase': 'Optimization',
                'timeframe': '18-36 months',
                'objectives': [
                    'Optimize cross-framework performance',
                    'Scale successful initiatives',
                    'Achieve strategic alignment maturity'
                ],
                'key_activities': [
                    'Optimize and scale successful programs',
                    'Address remaining gaps and opportunities',
                    'Develop organizational capabilities',
                    'Share learnings and best practices'
                ],
                'success_metrics': [
                    'All frameworks well-aligned',
                    'Sustainable improvement processes',
                    'Organizational capability maturity'
                ]
            })
            
            return roadmap
            
        except Exception as e:
            logger.error("Implementation roadmap creation failed", error=str(e))
            return []
    
    def _serialize_framework_analysis(self, analysis: FrameworkAnalysis) -> Dict[str, Any]:
        """Serialize framework analysis for JSON response"""
        return {
            'framework': analysis.framework.value,
            'overall_score': analysis.overall_score,
            'alignment_level': analysis.alignment_level.value,
            'key_strengths': analysis.key_strengths,
            'primary_gaps': analysis.primary_gaps,
            'strategic_opportunities': analysis.strategic_opportunities,
            'recommendations': analysis.recommendations,
            'confidence': analysis.confidence,
            'timestamp': analysis.timestamp.isoformat(),
            'element_count': len(analysis.element_assessments)
        }
    
    def _serialize_synthesis(self, synthesis: CrossFrameworkSynthesis) -> Dict[str, Any]:
        """Serialize cross-framework synthesis for JSON response"""
        return {
            'frameworks_analyzed': [f.value for f in synthesis.frameworks_analyzed],
            'overall_strategic_health': synthesis.overall_strategic_health,
            'synergies': synthesis.synergies,
            'conflicts': synthesis.conflicts,
            'optimization_opportunities': synthesis.optimization_opportunities,
            'integrated_recommendations': synthesis.integrated_recommendations,
            'strategic_priorities': synthesis.strategic_priorities,
            'implementation_roadmap': synthesis.implementation_roadmap
        }