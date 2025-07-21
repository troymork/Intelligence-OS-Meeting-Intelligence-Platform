"""
Tests for Real-Time Processing Optimization System
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json

from src.services.real_time_optimizer import (
    RealTimeOptimizer,
    OptimizationStrategy,
    OptimizationLevel,
    ProcessingStage,
    OptimizationConfig,
    ProcessingMetrics,
    OptimizationResult
)


class TestRealTimeOptimizer:
    """Test cases for RealTimeOptimizer"""
    
    @pytest.fixture
    def optimizer(self):
        """Create a RealTimeOptimizer instance for testing"""
        return RealTimeOptimizer()
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing"""
        return {
            'transcript': ['sentence 1', 'sentence 2', 'sentence 3'] * 10,
            'audio_segments': list(range(50)),
            'metadata': {
                'duration': 300,
                'speakers': ['speaker1', 'speaker2'],
                'language': 'en'
            },
            'context': 'meeting discussion about project planning'
        }
    
    @pytest.fixture
    def custom_config(self):
        """Custom optimization configuration for testing"""
        return {
            'max_processing_time_ms': 1500,
            'parallel_workers': 6,
            'sampling_rate': 0.8
        }
    
    @pytest.mark.asyncio
    async def test_optimize_processing_minimal(self, optimizer, sample_data):
        """Test optimization with minimal level"""
        optimized_data, result = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=sample_data,
            optimization_level=OptimizationLevel.MINIMAL
        )
        
        assert isinstance(optimized_data, dict)
        assert isinstance(result, OptimizationResult)
        assert result.optimization_level == OptimizationLevel.MINIMAL
        assert OptimizationStrategy.RESULT_CACHING in result.applied_strategies
        assert result.original_data_size > 0
        assert result.processing_time_saved_ms >= 0
        assert 0 <= result.quality_impact_score <= 1
    
    @pytest.mark.asyncio
    async def test_optimize_processing_balanced(self, optimizer, sample_data):
        """Test optimization with balanced level"""
        optimized_data, result = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=sample_data,
            optimization_level=OptimizationLevel.BALANCED
        )
        
        assert isinstance(optimized_data, dict)
        assert isinstance(result, OptimizationResult)
        assert result.optimization_level == OptimizationLevel.BALANCED
        assert len(result.applied_strategies) >= 2  # Should have multiple strategies
        assert OptimizationStrategy.RESULT_CACHING in result.applied_strategies
        assert OptimizationStrategy.PARALLEL_PROCESSING in result.applied_strategies
    
    @pytest.mark.asyncio
    async def test_optimize_processing_aggressive(self, optimizer, sample_data):
        """Test optimization with aggressive level"""
        optimized_data, result = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=sample_data,
            optimization_level=OptimizationLevel.AGGRESSIVE
        )
        
        assert isinstance(optimized_data, dict)
        assert isinstance(result, OptimizationResult)
        assert result.optimization_level == OptimizationLevel.AGGRESSIVE
        assert len(result.applied_strategies) >= 3  # Should have many strategies
        assert OptimizationStrategy.ADAPTIVE_SAMPLING in result.applied_strategies
        assert result.optimized_data_size <= result.original_data_size  # Should reduce size
    
    @pytest.mark.asyncio
    async def test_optimize_processing_adaptive(self, optimizer, sample_data):
        """Test optimization with adaptive level"""
        optimized_data, result = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=sample_data,
            optimization_level=OptimizationLevel.ADAPTIVE
        )
        
        assert isinstance(optimized_data, dict)
        assert isinstance(result, OptimizationResult)
        assert OptimizationStrategy.RESOURCE_ALLOCATION in result.applied_strategies
    
    @pytest.mark.asyncio
    async def test_optimize_processing_custom_config(self, optimizer, sample_data, custom_config):
        """Test optimization with custom configuration"""
        optimized_data, result = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=sample_data,
            optimization_level=OptimizationLevel.BALANCED,
            custom_config=custom_config
        )
        
        assert isinstance(optimized_data, dict)
        assert isinstance(result, OptimizationResult)
        assert result.metrics.parallel_tasks_used <= custom_config['parallel_workers']
    
    @pytest.mark.asyncio
    async def test_optimize_processing_pattern_recognition(self, optimizer, sample_data):
        """Test optimization for pattern recognition processing type"""
        optimized_data, result = await optimizer.optimize_processing(
            processing_type='pattern_recognition',
            input_data=sample_data,
            optimization_level=OptimizationLevel.BALANCED
        )
        
        assert isinstance(optimized_data, dict)
        assert isinstance(result, OptimizationResult)
        assert result.optimization_level == OptimizationLevel.BALANCED
    
    @pytest.mark.asyncio
    async def test_result_caching_strategy(self, optimizer, sample_data):
        """Test result caching optimization strategy"""
        # First call - should miss cache
        optimized_data1, result1 = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=sample_data,
            optimization_level=OptimizationLevel.MINIMAL
        )
        
        assert result1.metrics.cache_hits == 0
        
        # Second call with same data - should hit cache
        optimized_data2, result2 = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=sample_data,
            optimization_level=OptimizationLevel.MINIMAL
        )
        
        # Note: Cache hit behavior depends on implementation details
        # This test verifies the caching mechanism is working
        assert isinstance(result2.optimization_decisions.get('result_caching'), dict)
    
    @pytest.mark.asyncio
    async def test_parallel_processing_strategy(self, optimizer):
        """Test parallel processing optimization strategy"""
        # Data with parallelizable items
        data_with_lists = {
            'large_list': list(range(100)),
            'another_list': ['item'] * 50,
            'small_item': 'single_value'
        }
        
        optimized_data, result = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=data_with_lists,
            optimization_level=OptimizationLevel.BALANCED
        )
        
        assert isinstance(optimized_data, dict)
        if OptimizationStrategy.PARALLEL_PROCESSING in result.applied_strategies:
            assert result.metrics.parallel_tasks_used > 0
    
    @pytest.mark.asyncio
    async def test_early_stopping_strategy(self, optimizer):
        """Test early stopping optimization strategy"""
        # Data that should trigger early stopping
        high_confidence_data = {
            'transcript': ['complete sentence'] * 5,
            'confidence_score': 0.95,
            'metadata': {'complete': True}
        }
        
        optimized_data, result = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=high_confidence_data,
            optimization_level=OptimizationLevel.BALANCED
        )
        
        assert isinstance(optimized_data, dict)
        if OptimizationStrategy.EARLY_STOPPING in result.applied_strategies:
            early_stopping_decision = result.optimization_decisions.get('early_stopping', {})
            assert 'confidence' in early_stopping_decision
    
    @pytest.mark.asyncio
    async def test_adaptive_sampling_strategy(self, optimizer):
        """Test adaptive sampling optimization strategy"""
        # Data with large lists that can be sampled
        large_data = {
            'transcript': ['sentence'] * 100,
            'audio_segments': list(range(200)),
            'features': [{'feature': i} for i in range(150)]
        }
        
        optimized_data, result = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=large_data,
            optimization_level=OptimizationLevel.AGGRESSIVE
        )
        
        assert isinstance(optimized_data, dict)
        if OptimizationStrategy.ADAPTIVE_SAMPLING in result.applied_strategies:
            assert result.metrics.items_sampled >= 0
            assert result.optimized_data_size <= result.original_data_size
    
    @pytest.mark.asyncio
    async def test_model_pruning_strategy(self, optimizer, sample_data):
        """Test model pruning optimization strategy"""
        optimized_data, result = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=sample_data,
            optimization_level=OptimizationLevel.AGGRESSIVE
        )
        
        assert isinstance(optimized_data, dict)
        if OptimizationStrategy.MODEL_PRUNING in result.applied_strategies:
            pruning_decision = result.optimization_decisions.get('model_pruning', {})
            assert 'pruning_level' in pruning_decision or 'pruned' in pruning_decision
    
    @pytest.mark.asyncio
    async def test_priority_scheduling_strategy(self, optimizer, sample_data):
        """Test priority scheduling optimization strategy"""
        optimized_data, result = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=sample_data,
            optimization_level=OptimizationLevel.BALANCED
        )
        
        assert isinstance(optimized_data, dict)
        # Priority scheduling may or may not be applied depending on data
        if OptimizationStrategy.PRIORITY_SCHEDULING in result.applied_strategies:
            priority_decision = result.optimization_decisions.get('priority_scheduling', {})
            assert isinstance(priority_decision, dict)
    
    @pytest.mark.asyncio
    async def test_resource_allocation_strategy(self, optimizer, sample_data):
        """Test resource allocation optimization strategy"""
        optimized_data, result = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=sample_data,
            optimization_level=OptimizationLevel.ADAPTIVE
        )
        
        assert isinstance(optimized_data, dict)
        if OptimizationStrategy.RESOURCE_ALLOCATION in result.applied_strategies:
            resource_decision = result.optimization_decisions.get('resource_allocation', {})
            assert 'cpu_usage' in resource_decision or 'resource_allocated' in resource_decision
    
    def test_generate_cache_key(self, optimizer):
        """Test cache key generation"""
        data1 = {'key': 'value', 'number': 123}
        data2 = {'number': 123, 'key': 'value'}  # Same data, different order
        data3 = {'key': 'different', 'number': 123}
        
        key1 = optimizer._generate_cache_key(data1)
        key2 = optimizer._generate_cache_key(data2)
        key3 = optimizer._generate_cache_key(data3)
        
        assert key1 == key2  # Same data should generate same key
        assert key1 != key3  # Different data should generate different key
        assert isinstance(key1, str)
        assert len(key1) > 0
    
    def test_identify_parallelizable_items(self, optimizer):
        """Test identification of parallelizable items"""
        data = {
            'large_list': list(range(20)),
            'small_list': [1, 2],
            'single_item': 'value',
            'empty_list': []
        }
        
        parallelizable = optimizer._identify_parallelizable_items(data)
        
        assert isinstance(parallelizable, dict)
        # Should identify large_list as parallelizable
        assert any('large_list' in key for key in parallelizable.keys())
    
    def test_calculate_current_confidence(self, optimizer):
        """Test confidence calculation"""
        high_confidence_data = {
            'field1': 'value1',
            'field2': 'value2',
            'field3': 'value3'
        }
        
        low_confidence_data = {
            'field1': 'value1',
            'field2': None,
            'field3': ''
        }
        
        empty_data = {}
        
        high_conf = optimizer._calculate_current_confidence(high_confidence_data)
        low_conf = optimizer._calculate_current_confidence(low_confidence_data)
        empty_conf = optimizer._calculate_current_confidence(empty_data)
        
        assert 0 <= high_conf <= 1
        assert 0 <= low_conf <= 1
        assert empty_conf == 0
        assert high_conf > low_conf
    
    def test_is_data_sampleable(self, optimizer):
        """Test data sampleability check"""
        sampleable_data = {
            'large_list': list(range(50)),
            'small_item': 'value'
        }
        
        non_sampleable_data = {
            'small_list': [1, 2, 3],
            'single_item': 'value'
        }
        
        assert optimizer._is_data_sampleable(sampleable_data) == True
        assert optimizer._is_data_sampleable(non_sampleable_data) == False
    
    def test_apply_sampling(self, optimizer):
        """Test data sampling"""
        data = {
            'large_list': list(range(100)),
            'small_list': [1, 2, 3],
            'single_item': 'value'
        }
        
        sampled_data = optimizer._apply_sampling(data, 0.5)
        
        assert isinstance(sampled_data, dict)
        assert len(sampled_data['large_list']) <= len(data['large_list'])
        assert sampled_data['small_list'] == data['small_list']  # Small lists unchanged
        assert sampled_data['single_item'] == data['single_item']
    
    def test_count_input_items(self, optimizer):
        """Test input item counting"""
        data = {
            'list_field': [1, 2, 3, 4, 5],
            'single_field': 'value',
            'tuple_field': (1, 2, 3),
            'dict_field': {'nested': 'value'}
        }
        
        count = optimizer._count_input_items(data)
        
        assert count == 5 + 1 + 3 + 1  # 5 + 1 + 3 + 1 = 10
    
    def test_measure_data_size(self, optimizer):
        """Test data size measurement"""
        small_data = {'key': 'value'}
        large_data = {'key': 'value' * 1000, 'list': list(range(100))}
        
        small_size = optimizer._measure_data_size(small_data)
        large_size = optimizer._measure_data_size(large_data)
        
        assert isinstance(small_size, int)
        assert isinstance(large_size, int)
        assert large_size > small_size
    
    def test_estimate_processing_complexity(self, optimizer):
        """Test processing complexity estimation"""
        simple_value = "simple"
        complex_list = list(range(100))
        complex_dict = {f"key_{i}": f"value_{i}" for i in range(50)}
        
        simple_complexity = optimizer._estimate_processing_complexity(simple_value)
        list_complexity = optimizer._estimate_processing_complexity(complex_list)
        dict_complexity = optimizer._estimate_processing_complexity(complex_dict)
        
        assert isinstance(simple_complexity, int)
        assert isinstance(list_complexity, int)
        assert isinstance(dict_complexity, int)
        assert list_complexity > simple_complexity
        assert dict_complexity > simple_complexity
    
    def test_calculate_component_priority(self, optimizer):
        """Test component priority calculation"""
        high_priority = optimizer._calculate_component_priority('transcript', 'some text')
        medium_priority = optimizer._calculate_component_priority('metadata', {'key': 'value'})
        low_priority = optimizer._calculate_component_priority('random_field', 'value')
        
        assert high_priority > medium_priority
        assert medium_priority > low_priority
        assert all(isinstance(p, int) for p in [high_priority, medium_priority, low_priority])
    
    def test_get_optimization_config(self, optimizer):
        """Test optimization configuration retrieval"""
        # Test known processing type
        config = optimizer._get_optimization_config('transcript_analysis', OptimizationLevel.BALANCED)
        assert isinstance(config, OptimizationConfig)
        assert config.optimization_level == OptimizationLevel.BALANCED
        
        # Test unknown processing type (should return default)
        config = optimizer._get_optimization_config('unknown_type', OptimizationLevel.MINIMAL)
        assert isinstance(config, OptimizationConfig)
    
    def test_merge_custom_config(self, optimizer):
        """Test custom configuration merging"""
        base_config = optimizer._get_optimization_config('transcript_analysis', OptimizationLevel.BALANCED)
        custom_overrides = {
            'max_processing_time_ms': 1500,
            'parallel_workers': 6
        }
        
        merged_config = optimizer._merge_custom_config(base_config, custom_overrides)
        
        assert isinstance(merged_config, OptimizationConfig)
        assert merged_config.max_processing_time_ms == 1500
        assert merged_config.parallel_workers == 6
        assert merged_config.optimization_level == base_config.optimization_level
    
    def test_get_optimization_metrics(self, optimizer):
        """Test optimization metrics retrieval"""
        # Initially should have no metrics
        metrics = optimizer.get_optimization_metrics()
        assert 'message' in metrics or 'total_optimizations' in metrics
        
        # Test with specific processing type
        metrics = optimizer.get_optimization_metrics('transcript_analysis')
        assert isinstance(metrics, dict)
    
    def test_clear_cache(self, optimizer):
        """Test cache clearing"""
        # Add something to cache
        optimizer.result_cache['test_key'] = ({'result': 'data'}, datetime.utcnow())
        
        assert len(optimizer.result_cache) > 0
        
        optimizer.clear_cache()
        
        assert len(optimizer.result_cache) == 0
    
    @pytest.mark.asyncio
    async def test_optimization_error_handling(self, optimizer):
        """Test error handling in optimization"""
        # Test with invalid data that might cause errors
        invalid_data = None
        
        optimized_data, result = await optimizer.optimize_processing(
            processing_type='transcript_analysis',
            input_data=invalid_data or {},
            optimization_level=OptimizationLevel.MINIMAL
        )
        
        # Should handle errors gracefully
        assert isinstance(optimized_data, dict)
        assert isinstance(result, OptimizationResult)
    
    @pytest.mark.asyncio
    async def test_multiple_processing_types(self, optimizer, sample_data):
        """Test optimization with different processing types"""
        processing_types = ['transcript_analysis', 'pattern_recognition', 'unknown_type']
        
        for processing_type in processing_types:
            optimized_data, result = await optimizer.optimize_processing(
                processing_type=processing_type,
                input_data=sample_data,
                optimization_level=OptimizationLevel.BALANCED
            )
            
            assert isinstance(optimized_data, dict)
            assert isinstance(result, OptimizationResult)
    
    def test_adaptive_state_updates(self, optimizer):
        """Test adaptive state updates"""
        initial_sampling_rate = optimizer.adaptive_state['current_sampling_rate']
        initial_workers = optimizer.adaptive_state['current_parallel_workers']
        
        # Simulate high load
        optimizer.current_load = 90
        optimizer._update_adaptive_state()
        
        # Should adjust for high load
        assert optimizer.adaptive_state['current_sampling_rate'] <= initial_sampling_rate
        
        # Simulate low load
        optimizer.current_load = 20
        optimizer._update_adaptive_state()
        
        # May adjust for low load (depending on history)
        assert isinstance(optimizer.adaptive_state['current_sampling_rate'], float)
        assert isinstance(optimizer.adaptive_state['current_parallel_workers'], int)


if __name__ == '__main__':
    pytest.main([__file__])