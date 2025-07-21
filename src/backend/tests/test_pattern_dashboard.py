"""
Tests for Pattern Dashboard and Visualization Services
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.services.pattern_visualization_service import (
    PatternVisualizationService,
    VisualizationType,
    DashboardSection,
    ChartData,
    NetworkGraphData,
    Dashboard
)
from src.services.intervention_management_service import (
    InterventionManagementService,
    InterventionType,
    InterventionRecommendation
)
from src.services.predictive_analytics_service import (
    PredictiveAnalyticsService,
    ForecastType,
    ForecastHorizon,
    ForecastResult
)

class TestPatternVisualizationService:
    """Test pattern visualization service functionality"""
    
    @pytest.fixture
    def service(self):
        """Create pattern visualization service instance"""
        return PatternVisualizationService()
    
    @pytest.fixture
    def sample_pattern_data(self):
        """Sample pattern data for testing"""
        return [
            {
                'id': 'pattern-001',
                'pattern_type': 'recurring_challenge',
                'title': 'Communication Issues',
                'instances': [
                    {'timestamp': '2024-01-15T10:00:00Z'},
                    {'timestamp': '2024-01-16T14:00:00Z'},
                    {'timestamp': '2024-01-17T09:00:00Z'}
                ]
            },
            {
                'id': 'pattern-002',
                'pattern_type': 'behavioral_pattern',
                'title': 'Meeting Delays',
                'instances': [
                    {'timestamp': '2024-01-15T11:00:00Z'},
                    {'timestamp': '2024-01-18T15:00:00Z'}
                ]
            }
        ]
    
    @pytest.fixture
    def sample_concepts(self):
        """Sample concepts for network visualization"""
        return [
            {
                'id': 'concept-001',
                'name': 'Project Management',
                'concept_type': 'process',
                'importance_score': 0.8,
                'mention_count': 5
            },
            {
                'id': 'concept-002',
                'name': 'Team Communication',
                'concept_type': 'topic',
                'importance_score': 0.7,
                'mention_count': 3
            },
            {
                'id': 'concept-003',
                'name': 'Alice',
                'concept_type': 'person',
                'importance_score': 0.6,
                'mention_count': 8
            }
        ]
    
    @pytest.fixture
    def sample_relationships(self):
        """Sample relationships for network visualization"""
        return [
            {
                'source_concept_id': 'concept-001',
                'target_concept_id': 'concept-002',
                'relationship_type': 'relates_to',
                'strength': 0.8,
                'confidence': 0.9
            },
            {
                'source_concept_id': 'concept-003',
                'target_concept_id': 'concept-001',
                'relationship_type': 'participates_in',
                'strength': 0.7,
                'confidence': 0.8
            }
        ]

    @pytest.mark.asyncio
    async def test_create_pattern_timeline_visualization(self, service, sample_pattern_data):
        """Test pattern timeline visualization creation"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        
        chart_data = await service.create_pattern_timeline_visualization(
            sample_pattern_data, (start_date, end_date)
        )
        
        assert isinstance(chart_data, ChartData)
        assert len(chart_data.labels) > 0
        assert len(chart_data.datasets) > 0
        assert chart_data.data_quality_score > 0
        
        # Check that we have overall pattern count dataset
        total_patterns_dataset = next(
            (ds for ds in chart_data.datasets if ds['label'] == 'Total Patterns'), 
            None
        )
        assert total_patterns_dataset is not None
        assert len(total_patterns_dataset['data']) == len(chart_data.labels)

    @pytest.mark.asyncio
    async def test_create_concept_network_visualization(self, service, sample_concepts, sample_relationships):
        """Test concept network visualization creation"""
        network_data = await service.create_concept_network_visualization(
            sample_concepts, sample_relationships
        )
        
        assert isinstance(network_data, NetworkGraphData)
        assert len(network_data.nodes) == len(sample_concepts)
        assert len(network_data.edges) == len(sample_relationships)
        
        # Check node structure
        node = network_data.nodes[0]
        assert 'id' in node
        assert 'label' in node
        assert 'size' in node
        assert 'color' in node
        
        # Check edge structure
        edge = network_data.edges[0]
        assert 'from' in edge
        assert 'to' in edge
        assert 'width' in edge
        assert 'color' in edge

    @pytest.mark.asyncio
    async def test_create_learning_velocity_heatmap(self, service):
        """Test learning velocity heatmap creation"""
        learning_data = [
            {
                'description': 'Learning about project management in Q1',
                'timestamp': '2024-01-15T10:00:00Z',
                'learning_depth': 0.8
            },
            {
                'description': 'Team communication learning in Q1',
                'timestamp': '2024-01-16T10:00:00Z',
                'learning_depth': 0.6
            }
        ]
        
        time_periods = ['Q1-2024', 'Q2-2024']
        topics = ['project_management', 'team_communication']
        
        chart_data = await service.create_learning_velocity_heatmap(
            learning_data, time_periods, topics
        )
        
        assert isinstance(chart_data, ChartData)
        assert len(chart_data.labels) == len(time_periods)
        assert len(chart_data.datasets) > 0
        
        # Check heatmap data structure
        dataset = chart_data.datasets[0]
        assert 'data' in dataset
        assert len(dataset['data']) == len(topics)

    @pytest.mark.asyncio
    async def test_create_intervention_effectiveness_chart(self, service):
        """Test intervention effectiveness chart creation"""
        interventions = [
            {
                'type': 'communication_enhancement',
                'effectiveness_history': [
                    {'timestamp': '2024-01-15T10:00:00Z', 'effectiveness_score': 0.6},
                    {'timestamp': '2024-01-20T10:00:00Z', 'effectiveness_score': 0.7},
                    {'timestamp': '2024-01-25T10:00:00Z', 'effectiveness_score': 0.8}
                ]
            },
            {
                'type': 'process_improvement',
                'effectiveness_history': [
                    {'timestamp': '2024-01-15T10:00:00Z', 'effectiveness_score': 0.5},
                    {'timestamp': '2024-01-20T10:00:00Z', 'effectiveness_score': 0.6},
                    {'timestamp': '2024-01-25T10:00:00Z', 'effectiveness_score': 0.75}
                ]
            }
        ]
        
        chart_data = await service.create_intervention_effectiveness_chart(interventions)
        
        assert isinstance(chart_data, ChartData)
        assert len(chart_data.datasets) == 2  # Two intervention types
        
        # Check dataset structure
        for dataset in chart_data.datasets:
            assert 'label' in dataset
            assert 'data' in dataset
            assert 'borderColor' in dataset

    @pytest.mark.asyncio
    async def test_create_dashboard_success(self, service):
        """Test successful dashboard creation"""
        dashboard = await service.create_dashboard('executive_overview', 'user-123')
        
        assert isinstance(dashboard, Dashboard)
        assert dashboard.name == 'Executive Pattern Overview'
        assert dashboard.category == DashboardSection.PATTERN_OVERVIEW
        assert len(dashboard.widgets) > 0
        assert 'user-123' in dashboard.access_permissions
        assert dashboard.created_by == 'user-123'

    @pytest.mark.asyncio
    async def test_create_dashboard_invalid_template(self, service):
        """Test dashboard creation with invalid template"""
        with pytest.raises(ValueError, match="Dashboard template 'invalid_template' not found"):
            await service.create_dashboard('invalid_template', 'user-123')

    def test_get_concept_color(self, service):
        """Test concept color assignment"""
        # Test known concept types
        assert service._get_concept_color('decision') == '#e74c3c'
        assert service._get_concept_color('action') == '#2ecc71'
        assert service._get_concept_color('person') == '#1abc9c'
        
        # Test unknown concept type (should return default)
        assert service._get_concept_color('unknown_type') == '#95a5a6'

    def test_get_relationship_color(self, service):
        """Test relationship color assignment"""
        # Test known relationship types
        assert service._get_relationship_color('causes') == '#e74c3c'
        assert service._get_relationship_color('solves') == '#2ecc71'
        assert service._get_relationship_color('supports') == '#27ae60'
        
        # Test unknown relationship type (should return default)
        assert service._get_relationship_color('unknown_type') == '#95a5a6'

    def test_calculate_learning_velocity(self, service):
        """Test learning velocity calculation"""
        learning_data = [
            {
                'description': 'Learning about project management',
                'timestamp': '2024-01-15T10:00:00Z',
                'learning_depth': 0.8
            },
            {
                'description': 'More project management insights',
                'timestamp': '2024-01-16T10:00:00Z',
                'learning_depth': 0.6
            }
        ]
        
        velocity = service._calculate_learning_velocity(learning_data, 'project', '2024-01')
        
        assert isinstance(velocity, float)
        assert velocity >= 0
        assert velocity <= 1

    def test_generate_heatmap_colors(self, service):
        """Test heatmap color generation"""
        data = [[0.1, 0.5, 0.9], [0.3, 0.7, 0.2]]
        
        colors = service._generate_heatmap_colors(data)
        
        assert len(colors) == len(data)
        assert len(colors[0]) == len(data[0])
        
        # Check that colors are valid RGBA strings
        for row in colors:
            for color in row:
                assert color.startswith('rgba(')
                assert color.endswith(')')


class TestInterventionManagementService:
    """Test intervention management service functionality"""
    
    @pytest.fixture
    def service(self):
        """Create intervention management service instance"""
        return InterventionManagementService()
    
    @pytest.fixture
    def sample_patterns(self):
        """Sample patterns for intervention recommendations"""
        return [
            {
                'id': 'pattern-001',
                'pattern_type': 'communication_breakdown',
                'title': 'Recurring Communication Issues',
                'severity': 'high',
                'frequency': 5,
                'confidence_score': 0.8,
                'affected_participants': ['Alice', 'Bob', 'Charlie']
            },
            {
                'id': 'pattern-002',
                'pattern_type': 'process_inefficiency',
                'title': 'Slow Decision Making',
                'severity': 'medium',
                'frequency': 3,
                'confidence_score': 0.7,
                'affected_participants': ['Alice', 'David']
            }
        ]

    @pytest.mark.asyncio
    async def test_generate_intervention_recommendations(self, service, sample_patterns):
        """Test intervention recommendation generation"""
        recommendations = await service.generate_intervention_recommendations(sample_patterns)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check recommendation structure
        recommendation = recommendations[0]
        assert isinstance(recommendation, InterventionRecommendation)
        assert recommendation.target_pattern_id in ['pattern-001', 'pattern-002']
        assert isinstance(recommendation.recommended_intervention_type, InterventionType)
        assert recommendation.confidence_score > 0

    def test_determine_intervention_type(self, service):
        """Test intervention type determination"""
        # Communication pattern
        comm_pattern = {'title': 'Communication breakdown in team meetings'}
        assert service._determine_intervention_type(comm_pattern) == InterventionType.COMMUNICATION_ENHANCEMENT
        
        # Process pattern
        process_pattern = {'title': 'Inefficient workflow process'}
        assert service._determine_intervention_type(process_pattern) == InterventionType.PROCESS_IMPROVEMENT
        
        # Team pattern
        team_pattern = {'title': 'Team collaboration issues'}
        assert service._determine_intervention_type(team_pattern) == InterventionType.TEAM_BUILDING
        
        # Default case
        unknown_pattern = {'title': 'Some unknown issue'}
        assert service._determine_intervention_type(unknown_pattern) == InterventionType.PROCESS_IMPROVEMENT

    def test_calculate_expected_effectiveness(self, service):
        """Test expected effectiveness calculation"""
        pattern = {
            'severity': 'high',
            'frequency': 5,
            'confidence_score': 0.8
        }
        
        effectiveness = service._calculate_expected_effectiveness(pattern, InterventionType.COMMUNICATION_ENHANCEMENT)
        
        assert isinstance(effectiveness, float)
        assert 0 <= effectiveness <= 1

    def test_assess_implementation_complexity(self, service):
        """Test implementation complexity assessment"""
        # Small team pattern
        small_pattern = {'affected_participants': ['Alice', 'Bob']}
        complexity = service._assess_implementation_complexity(small_pattern, InterventionType.TEAM_BUILDING)
        assert complexity in ['low', 'medium', 'high', 'very_high']
        
        # Large team pattern
        large_pattern = {'affected_participants': [f'Person{i}' for i in range(15)]}
        complexity = service._assess_implementation_complexity(large_pattern, InterventionType.CULTURE_CHANGE)
        assert complexity in ['high', 'very_high']  # Should be higher complexity

    @pytest.mark.asyncio
    async def test_create_intervention_plan(self, service):
        """Test intervention plan creation"""
        recommendation = InterventionRecommendation(
            id='rec-001',
            target_pattern_id='pattern-001',
            recommended_intervention_type=InterventionType.COMMUNICATION_ENHANCEMENT,
            rationale='Team needs better communication',
            expected_effectiveness=0.8,
            implementation_complexity='medium',
            resource_estimate={'hours': 40, 'cost': 1000},
            timeline_estimate='8 weeks',
            success_probability=0.75,
            alternative_approaches=[],
            similar_case_studies=[],
            confidence_score=0.8
        )
        
        plan = await service.create_intervention_plan(recommendation)
        
        assert plan.id is not None
        assert plan.intervention_type == InterventionType.COMMUNICATION_ENHANCEMENT
        assert len(plan.implementation_steps) > 0
        assert 'planned_start' in plan.timeline
        assert 'planned_end' in plan.timeline

    @pytest.mark.asyncio
    async def test_track_intervention_effectiveness_no_execution(self, service):
        """Test intervention effectiveness tracking with no execution"""
        with pytest.raises(ValueError, match="Intervention execution nonexistent not found"):
            await service.track_intervention_effectiveness('nonexistent')


class TestPredictiveAnalyticsService:
    """Test predictive analytics service functionality"""
    
    @pytest.fixture
    def service(self):
        """Create predictive analytics service instance"""
        return PredictiveAnalyticsService()

    @pytest.mark.asyncio
    async def test_add_time_series_data(self, service):
        """Test adding time series data"""
        timestamp = datetime.utcnow()
        value = 0.75
        metadata = {'source': 'test'}
        
        await service.add_time_series_data('test_variable', timestamp, value, metadata)
        
        # Check that data was added
        assert 'test_variable' in service.time_series_data
        assert len(service.time_series_data['test_variable']) == 1
        
        data_point = service.time_series_data['test_variable'][0]
        assert data_point['timestamp'] == timestamp
        assert data_point['value'] == value
        assert data_point['metadata'] == metadata

    @pytest.mark.asyncio
    async def test_detect_anomalies_insufficient_data(self, service):
        """Test anomaly detection with insufficient data"""
        anomalies = await service.detect_anomalies('nonexistent_variable')
        
        assert isinstance(anomalies, list)
        assert len(anomalies) == 0

    @pytest.mark.asyncio
    async def test_analyze_trends_insufficient_data(self, service):
        """Test trend analysis with insufficient data"""
        with pytest.raises(ValueError, match="Insufficient data for trend analysis"):
            await service.analyze_trends('nonexistent_variable')

    def test_prepare_time_series_data(self, service):
        """Test time series data preparation"""
        from src.services.predictive_analytics_service import TimeSeriesData
        
        timestamps = [datetime.utcnow() - timedelta(days=i) for i in range(5, 0, -1)]
        values = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        time_series = TimeSeriesData(
            timestamps=timestamps,
            values=values,
            metadata={},
            data_quality_score=0.8,
            seasonality_detected=False,
            trend_detected=True
        )
        
        X, y = service._prepare_time_series_data(time_series)
        
        assert X.shape[0] == len(timestamps)
        assert len(y) == len(values)
        assert y.tolist() == values

    def test_determine_confidence_level(self, service):
        """Test confidence level determination"""
        from src.services.predictive_analytics_service import ConfidenceLevel
        
        # High accuracy, lots of data
        confidence = service._determine_confidence_level(0.95, 100)
        assert confidence == ConfidenceLevel.VERY_HIGH
        
        # Medium accuracy, medium data
        confidence = service._determine_confidence_level(0.7, 25)
        assert confidence == ConfidenceLevel.MEDIUM
        
        # Low accuracy, little data
        confidence = service._determine_confidence_level(0.4, 5)
        assert confidence == ConfidenceLevel.VERY_LOW

    def test_analyze_trend_direction(self, service):
        """Test trend direction analysis"""
        import numpy as np
        
        # Increasing trend
        increasing_predictions = np.array([1.0, 1.1, 1.2, 1.3, 1.4])
        direction = service._analyze_trend_direction(increasing_predictions)
        assert direction == "increasing"
        
        # Decreasing trend
        decreasing_predictions = np.array([1.4, 1.3, 1.2, 1.1, 1.0])
        direction = service._analyze_trend_direction(decreasing_predictions)
        assert direction == "decreasing"
        
        # Stable trend
        stable_predictions = np.array([1.0, 1.01, 0.99, 1.02, 0.98])
        direction = service._analyze_trend_direction(stable_predictions)
        assert direction == "stable"

    @pytest.mark.asyncio
    async def test_get_predictive_dashboard_data(self, service):
        """Test predictive dashboard data generation"""
        dashboard_data = await service.get_predictive_dashboard_data()
        
        assert isinstance(dashboard_data, dict)
        assert 'summary_stats' in dashboard_data
        assert 'recent_forecasts' in dashboard_data
        assert 'recent_anomalies' in dashboard_data
        assert 'last_updated' in dashboard_data
        
        # Check summary stats structure
        summary_stats = dashboard_data['summary_stats']
        assert 'total_forecasts' in summary_stats
        assert 'average_forecast_accuracy' in summary_stats
        assert 'recent_anomalies' in summary_stats


if __name__ == '__main__':
    pytest.main([__file__])