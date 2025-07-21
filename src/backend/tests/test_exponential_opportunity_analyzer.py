"""
Tests for Exponential Opportunity Analyzer
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.services.exponential_opportunity_analyzer import (
    ExponentialOpportunityAnalyzer,
    ExponentialDomain,
    OpportunityType,
    ReadinessLevel,
    exponential_opportunity_analyzer
)

class TestExponentialOpportunityAnalyzer:
    """Test cases for ExponentialOpportunityAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing"""
        return ExponentialOpportunityAnalyzer()
    
    @pytest.fixture
    def sample_content(self):
        """Sample content for analysis"""
        return """
        Our organization is looking to leverage artificial intelligence and machine learning
        to automate our business processes and create predictive analytics capabilities.
        We want to build a platform that connects customers with service providers,
        creating network effects and ecosystem value. We're also interested in IoT
        sensors for smart monitoring and blockchain for secure transactions.
        """
    
    @pytest.fixture
    def sample_org_context(self):
        """Sample organization context"""
        return {
            'size': 'large',
            'industry': 'technology',
            'digital_maturity': 'high',
            'innovation_culture': 'medium',
            'resource_availability': 'high',
            'technology_expertise': 'high',
            'change_agility': 'medium'
        }
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization"""
        assert analyzer is not None
        assert len(analyzer.exponential_technologies) > 0
        assert len(analyzer.opportunity_patterns) > 0
        assert len(analyzer.transformation_templates) > 0
        assert analyzer.impact_threshold == 0.7
    
    def test_technology_initialization(self, analyzer):
        """Test technology definitions are properly initialized"""
        # Check AI/ML technology
        ai_tech = analyzer.exponential_technologies.get('ai_ml')
        assert ai_tech is not None
        assert ai_tech.name == 'Artificial Intelligence & Machine Learning'
        assert ai_tech.domain == ExponentialDomain.DIGITAL
        assert ai_tech.disruption_potential == 0.9
        assert 'artificial intelligence' in ai_tech.keywords
        
        # Check IoT technology
        iot_tech = analyzer.exponential_technologies.get('iot')
        assert iot_tech is not None
        assert iot_tech.domain == ExponentialDomain.NETWORK
        assert 'IoT' in iot_tech.keywords
    
    def test_opportunity_patterns_initialization(self, analyzer):
        """Test opportunity patterns are properly initialized"""
        # Check platform model pattern
        platform_pattern = analyzer.opportunity_patterns.get('platform_model')
        assert platform_pattern is not None
        assert platform_pattern['type'] == OpportunityType.BUSINESS_MODEL
        assert platform_pattern['transformation_potential'] == 0.9
        assert 'ai_ml' in platform_pattern['related_technologies']
        
        # Check AI automation pattern
        ai_pattern = analyzer.opportunity_patterns.get('ai_automation')
        assert ai_pattern is not None
        assert ai_pattern['type'] == OpportunityType.TECHNOLOGY_ADOPTION
        assert 'ai_ml' in ai_pattern['related_technologies']
    
    @pytest.mark.asyncio
    async def test_analyze_exponential_opportunities(self, analyzer, sample_content, sample_org_context):
        """Test main analysis method"""
        result = await analyzer.analyze_exponential_opportunities(
            content=sample_content,
            organization_context=sample_org_context,
            focus_domains=[ExponentialDomain.DIGITAL, ExponentialDomain.NETWORK]
        )
        
        # Check result structure
        assert 'analysis_id' in result
        assert 'exponential_potential' in result
        assert 'relevant_technologies' in result
        assert 'opportunity_assessments' in result
        assert 'readiness_assessment' in result
        assert 'transformation_roadmap' in result
        assert 'timestamp' in result
        
        # Check exponential potential is reasonable
        assert 0.0 <= result['exponential_potential'] <= 1.0
        
        # Check technologies were identified
        assert len(result['relevant_technologies']) > 0
        
        # Check opportunities were identified
        assert len(result['opportunity_assessments']) > 0
        
        # Check readiness assessment
        readiness = result['readiness_assessment']
        assert 'overall_readiness' in readiness
        assert 'readiness_score' in readiness
        assert readiness['overall_readiness'] in ['unprepared', 'aware', 'developing', 'prepared', 'leading']
    
    @pytest.mark.asyncio
    async def test_identify_relevant_technologies(self, analyzer, sample_content):
        """Test technology identification"""
        focus_domains = [ExponentialDomain.DIGITAL, ExponentialDomain.NETWORK]
        technologies = await analyzer._identify_relevant_technologies(sample_content, focus_domains)
        
        assert len(technologies) > 0
        
        # Should identify AI/ML technology
        ai_tech = next((tech for tech in technologies if tech.id == 'ai_ml'), None)
        assert ai_tech is not None
        
        # Should identify IoT technology
        iot_tech = next((tech for tech in technologies if tech.id == 'iot'), None)
        assert iot_tech is not None
        
        # Should not include technologies from excluded domains
        for tech in technologies:
            assert tech.domain in focus_domains
    
    @pytest.mark.asyncio
    async def test_identify_opportunity_patterns(self, analyzer, sample_content):
        """Test opportunity pattern identification"""
        # First get relevant technologies
        technologies = await analyzer._identify_relevant_technologies(
            sample_content, 
            [ExponentialDomain.DIGITAL, ExponentialDomain.NETWORK]
        )
        
        patterns = await analyzer._identify_opportunity_patterns(sample_content, technologies)
        
        assert len(patterns) > 0
        
        # Should identify platform pattern due to "platform" and "network effects" mentions
        platform_pattern = next((p for p in patterns if p['pattern_id'] == 'platform_model'), None)
        assert platform_pattern is not None
        assert platform_pattern['confidence'] > 0.5
        
        # Should identify AI automation pattern due to AI mentions
        ai_pattern = next((p for p in patterns if p['pattern_id'] == 'ai_automation'), None)
        assert ai_pattern is not None
    
    @pytest.mark.asyncio
    async def test_generate_opportunity_assessments(self, analyzer, sample_content, sample_org_context):
        """Test opportunity assessment generation"""
        # Get prerequisites
        technologies = await analyzer._identify_relevant_technologies(
            sample_content, 
            [ExponentialDomain.DIGITAL, ExponentialDomain.NETWORK]
        )
        patterns = await analyzer._identify_opportunity_patterns(sample_content, technologies)
        
        assessments = await analyzer._generate_opportunity_assessments(
            sample_content, technologies, patterns, sample_org_context
        )
        
        assert len(assessments) > 0
        
        for assessment in assessments:
            # Check required fields
            assert assessment.id is not None
            assert assessment.name is not None
            assert assessment.opportunity_type is not None
            assert assessment.description is not None
            
            # Check score ranges
            assert 0.0 <= assessment.potential_impact <= 1.0
            assert 0.0 <= assessment.implementation_complexity <= 1.0
            assert 0.0 <= assessment.confidence_score <= 1.0
            
            # Check time to value
            assert assessment.time_to_value in ['short-term', 'medium-term', 'long-term']
            
            # Check readiness level
            assert isinstance(assessment.readiness_level, ReadinessLevel)
            
            # Check lists are not empty
            assert len(assessment.key_capabilities_required) > 0
            assert len(assessment.potential_barriers) > 0
    
    def test_calculate_potential_impact(self, analyzer, sample_org_context):
        """Test potential impact calculation"""
        # Mock pattern and technologies
        pattern = {
            'transformation_potential': 0.8,
            'related_technologies': ['ai_ml']
        }
        
        technologies = [analyzer.exponential_technologies['ai_ml']]
        
        impact = analyzer._calculate_potential_impact(pattern, technologies, sample_org_context)
        
        assert 0.0 <= impact <= 1.0
        assert impact > 0.8  # Should be higher than base due to multipliers
    
    def test_assess_readiness_level(self, analyzer, sample_org_context):
        """Test readiness level assessment"""
        pattern = {'type': OpportunityType.TECHNOLOGY_ADOPTION}
        
        readiness = analyzer._assess_readiness_level(pattern, sample_org_context)
        
        assert isinstance(readiness, ReadinessLevel)
        # With high digital maturity and tech expertise, should be prepared or leading
        assert readiness in [ReadinessLevel.PREPARED, ReadinessLevel.LEADING]
    
    def test_assess_readiness_level_no_context(self, analyzer):
        """Test readiness level assessment without context"""
        pattern = {'type': OpportunityType.TECHNOLOGY_ADOPTION}
        
        readiness = analyzer._assess_readiness_level(pattern, {})
        
        assert readiness == ReadinessLevel.AWARE
    
    @pytest.mark.asyncio
    async def test_assess_organizational_readiness(self, analyzer, sample_org_context):
        """Test organizational readiness assessment"""
        # Mock opportunities
        mock_opportunities = []
        
        readiness = await analyzer._assess_organizational_readiness(mock_opportunities, sample_org_context)
        
        assert 'overall_readiness' in readiness
        assert 'readiness_score' in readiness
        assert 'capability_gaps' in readiness
        assert 'readiness_factors' in readiness
        assert 'recommendations' in readiness
        
        # Check readiness score
        assert 0.0 <= readiness['readiness_score'] <= 1.0
        
        # With high context values, should have good readiness
        assert readiness['overall_readiness'] in ['prepared', 'leading']
    
    def test_calculate_exponential_potential(self, analyzer):
        """Test exponential potential calculation"""
        # Mock opportunities with varying impacts
        mock_opportunities = [
            Mock(potential_impact=0.9, opportunity_type=OpportunityType.PLATFORM_CREATION),
            Mock(potential_impact=0.7, opportunity_type=OpportunityType.TECHNOLOGY_ADOPTION),
            Mock(potential_impact=0.8, opportunity_type=OpportunityType.BUSINESS_MODEL)
        ]
        
        readiness_assessment = {'readiness_score': 0.8}
        
        potential = analyzer._calculate_exponential_potential(mock_opportunities, readiness_assessment)
        
        assert 0.0 <= potential <= 1.0
        assert potential > 0.7  # Should be high with good opportunities and readiness
    
    def test_calculate_exponential_potential_no_opportunities(self, analyzer):
        """Test exponential potential with no opportunities"""
        potential = analyzer._calculate_exponential_potential([], {'readiness_score': 0.8})
        
        assert potential == 0.5  # Default value
    
    def test_prioritize_opportunities(self, analyzer):
        """Test opportunity prioritization"""
        # Mock opportunities with different characteristics
        mock_opportunities = [
            Mock(
                potential_impact=0.6,
                implementation_complexity=0.8,
                confidence_score=0.7
            ),
            Mock(
                potential_impact=0.9,
                implementation_complexity=0.4,
                confidence_score=0.8
            ),
            Mock(
                potential_impact=0.7,
                implementation_complexity=0.6,
                confidence_score=0.6
            )
        ]
        
        readiness_assessment = {'readiness_score': 0.7}
        
        prioritized = analyzer._prioritize_opportunities(mock_opportunities, readiness_assessment)
        
        assert len(prioritized) == 3
        # Second opportunity should be first (high impact, low complexity)
        assert prioritized[0].potential_impact == 0.9
        assert prioritized[0].implementation_complexity == 0.4
    
    def test_serialization_methods(self, analyzer):
        """Test serialization methods"""
        # Test technology serialization
        tech = analyzer.exponential_technologies['ai_ml']
        serialized_techs = analyzer._serialize_technologies([tech])
        
        assert len(serialized_techs) == 1
        assert serialized_techs[0]['id'] == 'ai_ml'
        assert serialized_techs[0]['domain'] == 'digital'
        
        # Test opportunity serialization
        mock_opp = Mock(
            id='test_opp',
            name='Test Opportunity',
            opportunity_type=OpportunityType.TECHNOLOGY_ADOPTION,
            related_technologies=['ai_ml'],
            domains=[ExponentialDomain.DIGITAL],
            description='Test description',
            potential_impact=0.8,
            implementation_complexity=0.5,
            time_to_value='medium-term',
            readiness_level=ReadinessLevel.PREPARED,
            key_capabilities_required=['test_capability'],
            potential_barriers=['test_barrier'],
            success_examples=['test_example'],
            confidence_score=0.7
        )
        
        serialized_opps = analyzer._serialize_opportunities([mock_opp])
        
        assert len(serialized_opps) == 1
        assert serialized_opps[0]['id'] == 'test_opp'
        assert serialized_opps[0]['opportunity_type'] == 'technology_adoption'
        assert serialized_opps[0]['readiness_level'] == 'prepared'
    
    @pytest.mark.asyncio
    async def test_error_handling(self, analyzer):
        """Test error handling in analysis"""
        # Test with invalid content
        result = await analyzer.analyze_exponential_opportunities(
            content=None,
            organization_context=None
        )
        
        # Should return error result but not crash
        assert 'error' in result
        assert result['exponential_potential'] == 0.5  # Default value
    
    def test_global_instance(self):
        """Test global analyzer instance"""
        assert exponential_opportunity_analyzer is not None
        assert isinstance(exponential_opportunity_analyzer, ExponentialOpportunityAnalyzer)

if __name__ == '__main__':
    pytest.main([__file__])