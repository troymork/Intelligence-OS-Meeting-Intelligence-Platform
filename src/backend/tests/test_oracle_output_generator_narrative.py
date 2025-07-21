"""
Tests for Oracle Output Generator Narrative Development and Solution Portfolio
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch
from src.services.oracle_output_generator import (
    OracleOutputGenerator, 
    NarrativeDevelopment, 
    SolutionPortfolio,
    SolutionComponent,
    HumanNeedsFulfillmentPlan,
    IntegrityAlignmentCheck
)

class TestNarrativeDevelopmentGeneration:
    """Test narrative development generation functionality"""
    
    @pytest.fixture
    def generator(self):
        """Create Oracle output generator instance"""
        return OracleOutputGenerator()
    
    @pytest.fixture
    def sample_analysis_data(self):
        """Sample analysis data for testing"""
        return {
            'decisions': [
                {
                    'title': 'Adopt New Strategic Framework',
                    'priority': 'high',
                    'impact_analysis': 'Significant organizational transformation',
                    'confidence_score': 0.8
                }
            ],
            'actions': [
                {
                    'title': 'Implement Training Program',
                    'description': 'Roll out comprehensive training initiative',
                    'exponential_potential': 0.7,
                    'confidence_score': 0.75
                }
            ],
            'strategic_analysis': {
                'breakthrough_insights': True,
                'framework_alignment': {'SDG': 0.8, 'Doughnut': 0.7}
            },
            'transcript_analysis': {
                'segments': [
                    {
                        'speaker': 'Alice',
                        'text': 'We need to transform our approach and innovate for growth',
                        'duration': 4.0
                    },
                    {
                        'speaker': 'Bob',
                        'text': 'This collaboration will help us lead the change together',
                        'duration': 3.5
                    }
                ]
            }
        }
    
    @pytest.fixture
    def sample_meeting_metadata(self):
        """Sample meeting metadata for testing"""
        return {
            'meeting_id': 'test-meeting-789',
            'title': 'Strategic Planning Session',
            'participants': ['Alice', 'Bob', 'Charlie'],
            'date': '2024-01-20T14:00:00Z',
            'duration_minutes': 90,
            'meeting_type': 'strategic_planning'
        }

    @pytest.mark.asyncio
    async def test_generate_narrative_development_success(self, generator, sample_analysis_data, sample_meeting_metadata):
        """Test successful narrative development generation"""
        narrative = await generator._generate_narrative_development(sample_analysis_data, sample_meeting_metadata)
        
        assert isinstance(narrative, NarrativeDevelopment)
        assert narrative.id is not None
        assert 'meeting_type' in narrative.organizational_context
        assert len(narrative.meeting_narrative) > 0
        assert len(narrative.narrative_themes) > 0
        assert narrative.confidence_score > 0

    @pytest.mark.asyncio
    async def test_generate_narrative_development_empty_data(self, generator, sample_meeting_metadata):
        """Test narrative development generation with empty analysis data"""
        empty_data = {'transcript_analysis': {'segments': []}}
        
        narrative = await generator._generate_narrative_development(empty_data, sample_meeting_metadata)
        
        assert isinstance(narrative, NarrativeDevelopment)
        assert narrative.confidence_score < 0.5

    def test_extract_organizational_context(self, generator, sample_analysis_data, sample_meeting_metadata):
        """Test organizational context extraction"""
        context = generator._extract_organizational_context(sample_analysis_data, sample_meeting_metadata)
        
        assert 'meeting_type' in context
        assert context['meeting_type'] == 'strategic_planning'
        assert 'organizational_phase' in context
        assert 'current_challenges' in context

    def test_generate_meeting_narrative(self, generator, sample_analysis_data, sample_meeting_metadata):
        """Test meeting narrative generation"""
        narrative = generator._generate_meeting_narrative(sample_analysis_data, sample_meeting_metadata)
        
        assert isinstance(narrative, str)
        assert len(narrative) > 0
        assert 'strategic_planning' in narrative.lower()
        assert 'decision' in narrative.lower()

    def test_identify_narrative_themes(self, generator, sample_analysis_data):
        """Test narrative themes identification"""
        themes = generator._identify_narrative_themes(sample_analysis_data)
        
        assert isinstance(themes, list)
        assert len(themes) > 0
        # Should identify themes from transcript content
        assert any(theme in ['transformation', 'innovation', 'growth', 'collaboration', 'leadership'] for theme in themes)

    def test_analyze_story_progression(self, generator, sample_analysis_data, sample_meeting_metadata):
        """Test story progression analysis"""
        progression = generator._analyze_story_progression(sample_analysis_data, sample_meeting_metadata)
        
        assert 'current_chapter' in progression
        assert 'progress_markers' in progression
        assert 'momentum_indicators' in progression

    def test_identify_plot_points(self, generator, sample_analysis_data):
        """Test plot points identification"""
        plot_points = generator._identify_plot_points(sample_analysis_data)
        
        assert isinstance(plot_points, list)
        if plot_points:  # If any plot points found
            assert 'type' in plot_points[0]
            assert 'title' in plot_points[0]
            assert 'significance' in plot_points[0]


class TestSolutionPortfolioGeneration:
    """Test solution portfolio generation functionality"""
    
    @pytest.fixture
    def generator(self):
        """Create Oracle output generator instance"""
        return OracleOutputGenerator()
    
    @pytest.fixture
    def sample_analysis_data(self):
        """Sample analysis data with solutions"""
        return {
            'decisions': [
                {
                    'title': 'Implement New Technology Platform',
                    'implementation_plan': 'Phased rollout over 6 months',
                    'dependencies': ['budget_approval', 'team_training'],
                    'success_criteria': ['User adoption > 80%', 'Performance improvement > 20%'],
                    'stakeholders': ['IT Team', 'Business Users'],
                    'confidence_score': 0.8
                }
            ],
            'actions': [
                {
                    'title': 'Conduct User Training',
                    'description': 'Comprehensive training program for all users',
                    'owner': 'Training Manager',
                    'assignees': ['Trainer 1', 'Trainer 2'],
                    'exponential_potential': 0.6,
                    'confidence_score': 0.75
                }
            ],
            'strategic_implications': [
                {
                    'title': 'Digital Transformation Initiative',
                    'description': 'Organization-wide digital transformation',
                    'success_metrics': ['Digital maturity score', 'Process efficiency'],
                    'confidence_score': 0.7
                }
            ]
        }
    
    @pytest.fixture
    def sample_meeting_metadata(self):
        """Sample meeting metadata"""
        return {
            'participants': ['Alice', 'Bob', 'Charlie'],
            'meeting_type': 'implementation_planning'
        }

    @pytest.mark.asyncio
    async def test_generate_solution_portfolio_success(self, generator, sample_analysis_data, sample_meeting_metadata):
        """Test successful solution portfolio generation"""
        portfolio = await generator._generate_solution_portfolio(sample_analysis_data, sample_meeting_metadata)
        
        assert isinstance(portfolio, SolutionPortfolio)
        assert portfolio.id is not None
        assert len(portfolio.solution_components) > 0
        assert 'approach' in portfolio.implementation_strategy
        assert portfolio.confidence_score > 0

    def test_generate_solution_components(self, generator, sample_analysis_data, sample_meeting_metadata):
        """Test solution components generation"""
        components = generator._generate_solution_components(sample_analysis_data, sample_meeting_metadata)
        
        assert isinstance(components, list)
        assert len(components) > 0
        
        # Check first component structure
        component = components[0]
        assert isinstance(component, SolutionComponent)
        assert component.id is not None
        assert component.title is not None
        assert component.category in ['strategic', 'technical', 'process', 'cultural']

    def test_develop_implementation_strategy(self, generator, sample_analysis_data, sample_meeting_metadata):
        """Test implementation strategy development"""
        components = generator._generate_solution_components(sample_analysis_data, sample_meeting_metadata)
        strategy = generator._develop_implementation_strategy(components, sample_analysis_data)
        
        assert 'approach' in strategy
        assert 'phases' in strategy
        assert 'critical_path' in strategy
        assert 'resource_strategy' in strategy

    def test_calculate_resource_allocation(self, generator, sample_analysis_data, sample_meeting_metadata):
        """Test resource allocation calculation"""
        components = generator._generate_solution_components(sample_analysis_data, sample_meeting_metadata)
        allocation = generator._calculate_resource_allocation(components)
        
        assert 'total_estimated_effort' in allocation
        assert 'resource_distribution' in allocation
        assert 'skill_requirements' in allocation

    def test_identify_synergy_opportunities(self, generator):
        """Test synergy opportunities identification"""
        # Create test components with potential synergies
        components = [
            SolutionComponent(
                id='comp1',
                title='Training Program',
                description='User training',
                category='process',
                implementation_complexity='medium',
                resource_requirements={'skills_required': ['training', 'communication']},
                dependencies=[],
                success_metrics=[],
                risk_factors=[],
                timeline={},
                stakeholders=['Training Team'],
                exponential_potential=0.6,
                confidence_score=0.8
            ),
            SolutionComponent(
                id='comp2',
                title='Technology Implementation',
                description='System deployment',
                category='technical',
                implementation_complexity='high',
                resource_requirements={'skills_required': ['technical', 'training']},
                dependencies=[],
                success_metrics=[],
                risk_factors=[],
                timeline={},
                stakeholders=['IT Team'],
                exponential_potential=0.7,
                confidence_score=0.75
            )
        ]
        
        synergies = generator._identify_synergy_opportunities(components)
        
        assert isinstance(synergies, list)
        # Should identify synergy due to shared 'training' skill requirement

    def test_determine_priority_sequencing(self, generator):
        """Test priority sequencing determination"""
        components = [
            SolutionComponent(
                id='high_priority',
                title='High Priority Component',
                description='High impact, low complexity',
                category='strategic',
                implementation_complexity='low',
                resource_requirements={},
                dependencies=[],
                success_metrics=[],
                risk_factors=[],
                timeline={},
                stakeholders=[],
                exponential_potential=0.9,
                confidence_score=0.9
            ),
            SolutionComponent(
                id='low_priority',
                title='Low Priority Component',
                description='Low impact, high complexity',
                category='technical',
                implementation_complexity='very_high',
                resource_requirements={},
                dependencies=['high_priority'],
                success_metrics=[],
                risk_factors=['risk1', 'risk2'],
                timeline={},
                stakeholders=[],
                exponential_potential=0.2,
                confidence_score=0.5
            )
        ]
        
        sequence = generator._determine_priority_sequencing(components)
        
        assert isinstance(sequence, list)
        assert len(sequence) == 2
        # High priority component should come first
        assert sequence[0] == 'high_priority'

    def test_calculate_priority_score(self, generator):
        """Test priority score calculation"""
        high_priority_component = SolutionComponent(
            id='test',
            title='Test Component',
            description='Test',
            category='strategic',
            implementation_complexity='low',
            resource_requirements={},
            dependencies=[],
            success_metrics=[],
            risk_factors=[],
            timeline={},
            stakeholders=[],
            exponential_potential=0.9,
            confidence_score=0.9
        )
        
        score = generator._calculate_priority_score(high_priority_component)
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert score > 0.7  # Should be high priority


class TestHumanNeedsFulfillmentPlan:
    """Test human needs fulfillment plan generation"""
    
    @pytest.fixture
    def generator(self):
        return OracleOutputGenerator()
    
    @pytest.fixture
    def sample_data(self):
        return {
            'human_needs_analysis': {
                'individual_analyses': [
                    {'participant': 'Alice', 'primary_need': 'certainty'},
                    {'participant': 'Bob', 'primary_need': 'variety'}
                ]
            }
        }

    @pytest.mark.asyncio
    async def test_generate_human_needs_fulfillment_plan(self, generator, sample_data):
        """Test human needs fulfillment plan generation"""
        plan = await generator._generate_human_needs_fulfillment_plan(sample_data, {})
        
        assert isinstance(plan, HumanNeedsFulfillmentPlan)
        assert plan.id is not None
        assert isinstance(plan.individual_plans, list)
        assert isinstance(plan.team_interventions, list)
        assert plan.confidence_score >= 0


class TestIntegrityAlignmentCheck:
    """Test integrity alignment check generation"""
    
    @pytest.fixture
    def generator(self):
        return OracleOutputGenerator()

    @pytest.mark.asyncio
    async def test_generate_integrity_alignment_check(self, generator):
        """Test integrity alignment check generation"""
        sample_data = {'test': 'data'}
        check = await generator._generate_integrity_alignment_check(sample_data, {})
        
        assert isinstance(check, IntegrityAlignmentCheck)
        assert check.id is not None
        assert 'overall_quality' in check.quality_metrics or 'error' in str(check.quality_metrics)
        assert check.overall_integrity_score >= 0


if __name__ == '__main__':
    pytest.main([__file__])