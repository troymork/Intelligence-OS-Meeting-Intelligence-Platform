"""
Tests for Strategic Dashboard Service
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.services.strategic_dashboard_service import (
    StrategicDashboardService,
    VisualizationType,
    DashboardSection,
    MetricType,
    strategic_dashboard_service
)

class TestStrategicDashboardService:
    """Test cases for StrategicDashboardService"""
    
    @pytest.fixture
    def dashboard_service(self):
        """Create dashboard service instance for testing"""
        return StrategicDashboardService()
    
    @pytest.fixture
    def sample_filters(self):
        """Sample filters for testing"""
        return {
            'organization': 'test_org',
            'department': 'sustainability',
            'priority': 'high'
        }
    
    @pytest.fixture
    def sample_time_range(self):
        """Sample time range for testing"""
        return {
            'start': datetime.utcnow() - timedelta(days=90),
            'end': datetime.utcnow()
        }
    
    def test_dashboard_service_initialization(self, dashboard_service):
        """Test dashboard service initialization"""
        assert dashboard_service is not None
        assert len(dashboard_service.dashboard_configs) > 0
        assert len(dashboard_service.metric_calculators) > 0
        assert dashboard_service.cache_ttl == 300
        
        # Check dashboard configurations
        assert 'overview' in dashboard_service.dashboard_configs
        assert 'sdg_alignment' in dashboard_service.dashboard_configs
        assert 'doughnut_economy' in dashboard_service.dashboard_configs
        assert 'agreement_economy' in dashboard_service.dashboard_configs
    
    def test_dashboard_configs_structure(self, dashboard_service):
        """Test dashboard configuration structure"""
        overview_config = dashboard_service.dashboard_configs['overview']
        
        assert 'title' in overview_config
        assert 'description' in overview_config
        assert 'sections' in overview_config
        assert 'refresh_interval' in overview_config
        
        # Check sections structure
        sections = overview_config['sections']
        assert len(sections) > 0
        
        for section in sections:
            assert 'id' in section
            assert 'title' in section
            assert 'visualizations' in section
    
    @pytest.mark.asyncio
    async def test_generate_dashboard_data_overview(self, dashboard_service, sample_filters, sample_time_range):
        """Test overview dashboard data generation"""
        result = await dashboard_service.generate_dashboard_data(
            dashboard_type='overview',
            filters=sample_filters,
            time_range=sample_time_range
        )
        
        # Check result structure
        assert 'dashboard_id' in result
        assert 'type' in result
        assert result['type'] == 'overview'
        assert 'title' in result
        assert 'generated_at' in result
        assert 'sections' in result
        assert 'metrics' in result
        assert 'visualizations' in result
        assert 'insights' in result
        assert 'recommendations' in result
        
        # Check sections
        assert len(result['sections']) > 0
        
        # Check metrics
        assert len(result['metrics']) > 0
        for metric in result['metrics']:
            assert 'id' in metric
            assert 'name' in metric
            assert 'value' in metric
            assert 'unit' in metric
    
    @pytest.mark.asyncio
    async def test_generate_dashboard_data_sdg(self, dashboard_service):
        """Test SDG dashboard data generation"""
        result = await dashboard_service.generate_dashboard_data(
            dashboard_type='sdg_alignment'
        )
        
        assert result['type'] == 'sdg_alignment'
        assert 'SDG' in result['title']
        assert len(result['metrics']) > 0
        assert len(result['visualizations']) > 0
    
    @pytest.mark.asyncio
    async def test_generate_dashboard_data_doughnut(self, dashboard_service):
        """Test Doughnut Economy dashboard data generation"""
        result = await dashboard_service.generate_dashboard_data(
            dashboard_type='doughnut_economy'
        )
        
        assert result['type'] == 'doughnut_economy'
        assert 'Doughnut' in result['title']
        assert len(result['metrics']) > 0
        
        # Check for regenerative and distributive metrics
        metric_names = [m['name'] for m in result['metrics']]
        assert any('Regenerative' in name for name in metric_names)
        assert any('Distributive' in name for name in metric_names)
    
    @pytest.mark.asyncio
    async def test_generate_dashboard_data_agreement(self, dashboard_service):
        """Test Agreement Economy dashboard data generation"""
        result = await dashboard_service.generate_dashboard_data(
            dashboard_type='agreement_economy'
        )
        
        assert result['type'] == 'agreement_economy'
        assert 'Agreement' in result['title']
        assert len(result['metrics']) > 0
        
        # Check for collaboration and value sharing metrics
        metric_names = [m['name'] for m in result['metrics']]
        assert any('Collaboration' in name for name in metric_names)
        assert any('Value Sharing' in name for name in metric_names)
    
    @pytest.mark.asyncio
    async def test_generate_dashboard_data_invalid_type(self, dashboard_service):
        """Test dashboard data generation with invalid type"""
        result = await dashboard_service.generate_dashboard_data(
            dashboard_type='invalid_type'
        )
        
        assert 'error' in result
        assert result['dashboard_id'] is not None
    
    @pytest.mark.asyncio
    async def test_calculate_overall_alignment(self, dashboard_service):
        """Test overall alignment calculation"""
        result = await dashboard_service._calculate_overall_alignment()
        
        assert 'score' in result
        assert 'trend' in result
        assert 'change_percentage' in result
        assert 'components' in result
        assert 'last_updated' in result
        
        # Check score range
        assert 0.0 <= result['score'] <= 1.0
        
        # Check trend values
        assert result['trend'] in ['up', 'down', 'stable']
        
        # Check components
        components = result['components']
        assert 'sdg_alignment' in components
        assert 'doughnut_alignment' in components
        assert 'agreement_alignment' in components
    
    @pytest.mark.asyncio
    async def test_calculate_sdg_alignment(self, dashboard_service):
        """Test SDG alignment calculation"""
        result = await dashboard_service._calculate_sdg_alignment()
        
        assert 'overall_score' in result
        assert 'individual_scores' in result
        assert 'top_performing' in result
        assert 'bottom_performing' in result
        assert 'trend' in result
        assert 'change_percentage' in result
        
        # Check individual scores
        individual_scores = result['individual_scores']
        assert len(individual_scores) == 17  # 17 SDGs
        
        for sdg_id, score in individual_scores.items():
            assert sdg_id.startswith('sdg_')
            assert 0.0 <= score <= 1.0
        
        # Check top and bottom performing
        assert len(result['top_performing']) == 3
        assert len(result['bottom_performing']) == 3
        
        for sdg in result['top_performing']:
            assert 'id' in sdg
            assert 'name' in sdg
            assert 'score' in sdg
    
    @pytest.mark.asyncio
    async def test_calculate_doughnut_alignment(self, dashboard_service):
        """Test Doughnut Economy alignment calculation"""
        result = await dashboard_service._calculate_doughnut_alignment()
        
        assert 'regenerative_score' in result
        assert 'distributive_score' in result
        assert 'regenerative_indicators' in result
        assert 'distributive_indicators' in result
        assert 'balance_score' in result
        
        # Check score ranges
        assert 0.0 <= result['regenerative_score'] <= 1.0
        assert 0.0 <= result['distributive_score'] <= 1.0
        
        # Check indicators
        regen_indicators = result['regenerative_indicators']
        distrib_indicators = result['distributive_indicators']
        
        assert len(regen_indicators) > 0
        assert len(distrib_indicators) > 0
        
        # Check specific indicators
        assert 'climate_change' in regen_indicators
        assert 'food_security' in distrib_indicators
    
    @pytest.mark.asyncio
    async def test_calculate_agreement_alignment(self, dashboard_service):
        """Test Agreement Economy alignment calculation"""
        result = await dashboard_service._calculate_agreement_alignment()
        
        assert 'collaboration_score' in result
        assert 'value_sharing_score' in result
        assert 'collaboration_metrics' in result
        assert 'value_sharing_metrics' in result
        assert 'overall_agreement_score' in result
        
        # Check score ranges
        assert 0.0 <= result['collaboration_score'] <= 1.0
        assert 0.0 <= result['value_sharing_score'] <= 1.0
        
        # Check metrics
        collab_metrics = result['collaboration_metrics']
        value_metrics = result['value_sharing_metrics']
        
        assert 'partnership_strength' in collab_metrics
        assert 'trust_level' in collab_metrics
        assert 'benefit_distribution' in value_metrics
        assert 'knowledge_sharing' in value_metrics
    
    @pytest.mark.asyncio
    async def test_generate_key_metrics_overview(self, dashboard_service):
        """Test key metrics generation for overview dashboard"""
        metrics = await dashboard_service._generate_key_metrics('overview')
        
        assert len(metrics) > 0
        
        # Check for expected metrics
        metric_ids = [m['id'] for m in metrics]
        assert 'overall_alignment' in metric_ids
        assert 'opportunity_count' in metric_ids
        assert 'action_completion' in metric_ids
        
        # Check metric structure
        for metric in metrics:
            assert 'id' in metric
            assert 'name' in metric
            assert 'value' in metric
            assert 'trend' in metric
            assert 'unit' in metric
            assert 'format' in metric
            
            # Check value ranges where applicable
            if metric['format'] == 'percentage':
                assert 0.0 <= metric['value'] <= 1.0
    
    @pytest.mark.asyncio
    async def test_generate_visualizations_overview(self, dashboard_service):
        """Test visualization generation for overview dashboard"""
        visualizations = await dashboard_service._generate_visualizations('overview')
        
        assert len(visualizations) > 0
        
        # Check for expected visualizations
        viz_ids = [v['id'] for v in visualizations]
        assert 'framework_radar' in viz_ids
        assert 'opportunity_matrix' in viz_ids
        assert 'alignment_timeline' in viz_ids
        
        # Check visualization structure
        for viz in visualizations:
            assert 'id' in viz
            assert 'type' in viz
            assert 'title' in viz
            assert 'data' in viz
            assert 'config' in viz
    
    @pytest.mark.asyncio
    async def test_generate_framework_radar_data(self, dashboard_service):
        """Test framework radar chart data generation"""
        data = await dashboard_service._generate_framework_radar_data()
        
        assert 'datasets' in data
        assert 'labels' in data
        
        datasets = data['datasets']
        assert len(datasets) >= 1
        
        for dataset in datasets:
            assert 'label' in dataset
            assert 'data' in dataset
            assert 'backgroundColor' in dataset
            assert 'borderColor' in dataset
        
        # Check labels
        labels = data['labels']
        assert 'SDG Alignment' in labels
        assert 'Doughnut Economy' in labels
        assert 'Agreement Economy' in labels
    
    @pytest.mark.asyncio
    async def test_generate_opportunity_matrix_data(self, dashboard_service):
        """Test opportunity matrix data generation"""
        data = await dashboard_service._generate_opportunity_matrix_data()
        
        assert 'data' in data
        assert 'quadrants' in data
        
        opportunities = data['data']
        assert len(opportunities) > 0
        
        for opp in opportunities:
            assert 'id' in opp
            assert 'name' in opp
            assert 'impact_score' in opp
            assert 'effort_score' in opp
            assert 'priority_score' in opp
            assert 'framework_alignment' in opp
            assert 'status' in opp
            
            # Check score ranges
            assert 0.0 <= opp['impact_score'] <= 1.0
            assert 0.0 <= opp['effort_score'] <= 1.0
        
        # Check quadrants
        quadrants = data['quadrants']
        assert 'high_impact_low_effort' in quadrants
        assert 'high_impact_high_effort' in quadrants
        assert 'low_impact_low_effort' in quadrants
        assert 'low_impact_high_effort' in quadrants
    
    @pytest.mark.asyncio
    async def test_generate_sdg_wheel_data(self, dashboard_service):
        """Test SDG wheel data generation"""
        data = await dashboard_service._generate_sdg_wheel_data()
        
        assert 'sdgs' in data
        assert 'overall_score' in data
        assert 'target_score' in data
        
        sdgs = data['sdgs']
        assert len(sdgs) == 17  # 17 SDGs
        
        for sdg in sdgs:
            assert 'id' in sdg
            assert 'name' in sdg
            assert 'score' in sdg
            assert 'target' in sdg
            assert 'trend' in sdg
            assert 'color' in sdg
            
            # Check score range
            assert 0.0 <= sdg['score'] <= 1.0
            assert sdg['trend'] in ['up', 'down', 'stable']
    
    @pytest.mark.asyncio
    async def test_generate_doughnut_chart_data(self, dashboard_service):
        """Test doughnut chart data generation"""
        data = await dashboard_service._generate_doughnut_chart_data()
        
        assert 'social_foundation' in data
        assert 'ecological_ceiling' in data
        assert 'safe_operating_space' in data
        assert 'overshoot_areas' in data
        assert 'shortfall_areas' in data
        
        # Check social foundation
        social_foundation = data['social_foundation']
        assert 'indicators' in social_foundation
        
        social_indicators = social_foundation['indicators']
        assert len(social_indicators) > 0
        
        for indicator in social_indicators:
            assert 'name' in indicator
            assert 'value' in indicator
            assert 'threshold' in indicator
        
        # Check ecological ceiling
        ecological_ceiling = data['ecological_ceiling']
        assert 'indicators' in ecological_ceiling
        
        eco_indicators = ecological_ceiling['indicators']
        assert len(eco_indicators) > 0
    
    @pytest.mark.asyncio
    async def test_generate_collaboration_network_data(self, dashboard_service):
        """Test collaboration network data generation"""
        data = await dashboard_service._generate_collaboration_network_data()
        
        assert 'nodes' in data
        assert 'edges' in data
        assert 'network_metrics' in data
        
        nodes = data['nodes']
        edges = data['edges']
        
        assert len(nodes) > 0
        assert len(edges) > 0
        
        # Check node structure
        for node in nodes:
            assert 'id' in node
            assert 'name' in node
            assert 'type' in node
            assert 'size' in node
            assert 'collaboration_strength' in node
        
        # Check edge structure
        for edge in edges:
            assert 'source' in edge
            assert 'target' in edge
            assert 'weight' in edge
            assert 'agreement_strength' in edge
            assert 'type' in edge
        
        # Check network metrics
        network_metrics = data['network_metrics']
        assert 'density' in network_metrics
        assert 'centralization' in network_metrics
        assert 'total_agreements' in network_metrics
    
    @pytest.mark.asyncio
    async def test_create_opportunity_map(self, dashboard_service):
        """Test opportunity map creation"""
        opportunity_data = {
            'opportunity_id': 'test_opp_1',
            'name': 'Test Opportunity',
            'impact_score': 0.8,
            'effort_score': 0.4,
            'priority_level': 'high',
            'framework_alignment': {'sdg': 0.7, 'doughnut': 0.8},
            'status': 'identified'
        }
        
        opportunity_id = await dashboard_service.create_opportunity_map(opportunity_data)
        
        assert opportunity_id is not None
        assert opportunity_id in dashboard_service.opportunity_maps
        
        created_opportunity = dashboard_service.opportunity_maps[opportunity_id]
        assert created_opportunity.name == 'Test Opportunity'
        assert created_opportunity.impact_score == 0.8
        assert created_opportunity.priority_level == 'high'
    
    @pytest.mark.asyncio
    async def test_track_action_progress(self, dashboard_service):
        """Test action progress tracking"""
        action_data = {
            'action_id': 'test_action_1',
            'title': 'Test Action',
            'description': 'Test action description',
            'owner': 'test_owner',
            'status': 'in_progress',
            'progress_percentage': 0.6,
            'strategic_alignment': {'sdg': 0.75}
        }
        
        action_id = await dashboard_service.track_action_progress(action_data)
        
        assert action_id is not None
        assert action_id in dashboard_service.action_tracking
        
        tracked_action = dashboard_service.action_tracking[action_id]
        assert tracked_action.title == 'Test Action'
        assert tracked_action.status == 'in_progress'
        assert tracked_action.progress_percentage == 0.6
    
    @pytest.mark.asyncio
    async def test_get_dashboard_summary(self, dashboard_service):
        """Test dashboard summary generation"""
        summary = await dashboard_service.get_dashboard_summary('overview')
        
        assert 'dashboard_type' in summary
        assert summary['dashboard_type'] == 'overview'
        assert 'summary_generated_at' in summary
        assert 'key_metrics' in summary
        assert 'top_insights' in summary
        assert 'priority_recommendations' in summary
        assert 'data_freshness' in summary
        
        # Check key metrics
        assert len(summary['key_metrics']) > 0
        
        # Check insights (should be limited to top 3)
        assert len(summary['top_insights']) <= 3
        
        # Check recommendations (should be limited to top 2)
        assert len(summary['priority_recommendations']) <= 2
    
    def test_visualization_type_mapping(self, dashboard_service):
        """Test visualization type mapping"""
        assert dashboard_service._get_visualization_type('framework_comparison_radar') == 'radar_chart'
        assert dashboard_service._get_visualization_type('opportunity_matrix') == 'scatter_plot'
        assert dashboard_service._get_visualization_type('alignment_timeline') == 'line_chart'
        assert dashboard_service._get_visualization_type('unknown_viz') == 'unknown'
    
    def test_visualization_title_mapping(self, dashboard_service):
        """Test visualization title mapping"""
        assert 'Strategic Alignment' in dashboard_service._get_visualization_title('overall_alignment_gauge')
        assert 'Framework Alignment' in dashboard_service._get_visualization_title('framework_comparison_radar')
        assert 'Opportunity Matrix' in dashboard_service._get_visualization_title('opportunity_matrix')
    
    def test_visualization_config_generation(self, dashboard_service):
        """Test visualization configuration generation"""
        config = dashboard_service._get_visualization_config('test_viz')
        
        assert 'responsive' in config
        assert 'animation' in config
        assert 'legend' in config
        assert 'tooltip' in config
        
        assert config['responsive'] is True
        assert config['animation'] is True
    
    @pytest.mark.asyncio
    async def test_caching_mechanism(self, dashboard_service):
        """Test dashboard data caching"""
        # First call should generate data
        result1 = await dashboard_service.generate_dashboard_data('overview')
        
        # Second call should use cache (same filters)
        result2 = await dashboard_service.generate_dashboard_data('overview')
        
        # Results should be identical (from cache)
        assert result1['dashboard_id'] == result2['dashboard_id']
        
        # Different filters should generate new data
        result3 = await dashboard_service.generate_dashboard_data('overview', {'test': 'filter'})
        assert result3['dashboard_id'] != result1['dashboard_id']
    
    @pytest.mark.asyncio
    async def test_error_handling(self, dashboard_service):
        """Test error handling in dashboard service"""
        # Test with invalid dashboard type
        result = await dashboard_service.generate_dashboard_data('invalid_type')
        assert 'error' in result
        
        # Test summary with invalid type
        summary = await dashboard_service.get_dashboard_summary('invalid_type')
        assert 'error' in summary
    
    def test_global_instance(self):
        """Test global dashboard service instance"""
        assert strategic_dashboard_service is not None
        assert isinstance(strategic_dashboard_service, StrategicDashboardService)

if __name__ == '__main__':
    pytest.main([__file__])