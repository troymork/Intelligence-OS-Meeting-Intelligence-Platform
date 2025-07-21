"""
Tests for Processing Coordinator and State Synchronization
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.services.processing_coordinator import (
    ProcessingCoordinator,
    ProcessingTask,
    ProcessingResult,
    PipelineType,
    ProcessingPriority,
    ProcessingStatus,
    ProcessingPipeline
)
from src.services.state_synchronization_service import (
    StateSynchronizationService,
    SyncStrategy,
    ConflictResolution,
    SyncStatus,
    SyncConflict
)

class TestProcessingCoordinator:
    """Test processing coordinator functionality"""
    
    @pytest.fixture
    def coordinator(self):
        """Create processing coordinator instance"""
        return ProcessingCoordinator()
    
    @pytest.fixture
    def sample_input_data(self):
        """Sample input data for processing tasks"""
        return {
            'transcript': 'This is a sample meeting transcript for testing purposes.',
            'participants': ['Alice', 'Bob', 'Charlie'],
            'meeting_id': 'test-meeting-001',
            'timestamp': datetime.utcnow().isoformat()
        }

    @pytest.mark.asyncio
    async def test_submit_processing_task_single_pipeline(self, coordinator, sample_input_data):
        """Test submitting task to single pipeline"""
        task_ids = await coordinator.submit_processing_task(
            task_type=PipelineType.TRANSCRIPT_ANALYSIS,
            input_data=sample_input_data,
            priority=ProcessingPriority.IMMEDIATE,
            enable_dual_pipeline=False
        )
        
        assert isinstance(task_ids, dict)
        assert len(task_ids) == 1
        assert 'real_time' in task_ids
        
        # Check task was created
        task_id = task_ids['real_time']
        assert task_id in coordinator.active_tasks
        
        task = coordinator.active_tasks[task_id]
        assert task.task_type == PipelineType.TRANSCRIPT_ANALYSIS
        assert task.priority == ProcessingPriority.IMMEDIATE
        assert task.pipeline == ProcessingPipeline.REAL_TIME

    @pytest.mark.asyncio
    async def test_submit_processing_task_dual_pipeline(self, coordinator, sample_input_data):
        """Test submitting task to dual pipeline"""
        task_ids = await coordinator.submit_processing_task(
            task_type=PipelineType.PATTERN_RECOGNITION,
            input_data=sample_input_data,
            priority=ProcessingPriority.NORMAL,
            enable_dual_pipeline=True
        )
        
        assert isinstance(task_ids, dict)
        assert len(task_ids) == 2
        assert 'real_time' in task_ids
        assert 'comprehensive' in task_ids
        
        # Check both tasks were created
        for pipeline, task_id in task_ids.items():
            assert task_id in coordinator.active_tasks
            task = coordinator.active_tasks[task_id]
            assert task.task_type == PipelineType.PATTERN_RECOGNITION
            assert task.priority == ProcessingPriority.NORMAL

    def test_determine_pipelines_immediate_priority(self, coordinator):
        """Test pipeline determination for immediate priority"""
        pipelines = coordinator._determine_pipelines(ProcessingPriority.IMMEDIATE, True)
        assert pipelines == [ProcessingPipeline.REAL_TIME]

    def test_determine_pipelines_normal_priority_dual(self, coordinator):
        """Test pipeline determination for normal priority with dual pipeline"""
        pipelines = coordinator._determine_pipelines(ProcessingPriority.NORMAL, True)
        assert ProcessingPipeline.REAL_TIME in pipelines
        assert ProcessingPipeline.COMPREHENSIVE in pipelines

    def test_determine_pipelines_comprehensive_priority(self, coordinator):
        """Test pipeline determination for comprehensive priority"""
        pipelines = coordinator._determine_pipelines(ProcessingPriority.COMPREHENSIVE, True)
        assert pipelines == [ProcessingPipeline.COMPREHENSIVE]

    def test_get_timeout_for_pipeline(self, coordinator):
        """Test timeout determination for different pipelines"""
        rt_timeout = coordinator._get_timeout_for_pipeline(ProcessingPipeline.REAL_TIME)
        comp_timeout = coordinator._get_timeout_for_pipeline(ProcessingPipeline.COMPREHENSIVE)
        
        assert rt_timeout == coordinator.config['real_time_timeout_seconds']
        assert comp_timeout == coordinator.config['comprehensive_timeout_seconds']
        assert rt_timeout < comp_timeout

    @pytest.mark.asyncio
    async def test_get_task_status_active_task(self, coordinator, sample_input_data):
        """Test getting status of active task"""
        # Submit task
        task_ids = await coordinator.submit_processing_task(
            task_type=PipelineType.TRANSCRIPT_ANALYSIS,
            input_data=sample_input_data,
            priority=ProcessingPriority.FAST,
            enable_dual_pipeline=False
        )
        
        task_id = task_ids['real_time']
        
        # Get task status
        result = await coordinator.get_task_status(task_id)
        
        assert result is not None
        assert isinstance(result, ProcessingResult)
        assert result.task_id == task_id
        assert result.pipeline == ProcessingPipeline.REAL_TIME

    @pytest.mark.asyncio
    async def test_get_task_status_nonexistent_task(self, coordinator):
        """Test getting status of nonexistent task"""
        result = await coordinator.get_task_status('nonexistent-task-id')
        assert result is None

    def test_process_transcript_real_time(self, coordinator, sample_input_data):
        """Test real-time transcript processing"""
        result = coordinator._process_transcript_real_time(sample_input_data, {})
        
        assert isinstance(result, dict)
        assert result['type'] == 'transcript_analysis'
        assert result['pipeline'] == 'real_time'
        assert 'summary' in result
        assert 'confidence' in result
        assert result['confidence'] > 0

    def test_process_transcript_comprehensive(self, coordinator, sample_input_data):
        """Test comprehensive transcript processing"""
        result = coordinator._process_transcript_comprehensive(sample_input_data, {})
        
        assert isinstance(result, dict)
        assert result['type'] == 'transcript_analysis'
        assert result['pipeline'] == 'comprehensive'
        assert 'detailed_analysis' in result
        assert 'confidence' in result
        assert result['confidence'] > result.get('processing_time', 0)  # Should have higher confidence

    def test_process_patterns_real_time(self, coordinator, sample_input_data):
        """Test real-time pattern processing"""
        result = coordinator._process_patterns_real_time(sample_input_data, {})
        
        assert isinstance(result, dict)
        assert result['type'] == 'pattern_recognition'
        assert result['pipeline'] == 'real_time'
        assert 'patterns_detected' in result
        assert isinstance(result['patterns_detected'], int)

    def test_process_patterns_comprehensive(self, coordinator, sample_input_data):
        """Test comprehensive pattern processing"""
        result = coordinator._process_patterns_comprehensive(sample_input_data, {})
        
        assert isinstance(result, dict)
        assert result['type'] == 'pattern_recognition'
        assert result['pipeline'] == 'comprehensive'
        assert 'detailed_patterns' in result
        assert result['patterns_detected'] > 0

    def test_process_oracle_real_time(self, coordinator, sample_input_data):
        """Test real-time Oracle processing"""
        result = coordinator._process_oracle_real_time(sample_input_data, {})
        
        assert isinstance(result, dict)
        assert result['type'] == 'oracle_generation'
        assert result['pipeline'] == 'real_time'
        assert 'summary' in result

    def test_process_oracle_comprehensive(self, coordinator, sample_input_data):
        """Test comprehensive Oracle processing"""
        result = coordinator._process_oracle_comprehensive(sample_input_data, {})
        
        assert isinstance(result, dict)
        assert result['type'] == 'oracle_generation'
        assert result['pipeline'] == 'comprehensive'
        assert 'full_oracle_output' in result

    def test_processing_task_creation(self):
        """Test ProcessingTask creation"""
        task = ProcessingTask(
            id='test-task-001',
            task_type=PipelineType.KNOWLEDGE_GRAPH,
            pipeline=ProcessingPipeline.COMPREHENSIVE,
            priority=ProcessingPriority.NORMAL,
            input_data={'test': 'data'},
            metadata={'source': 'test'}
        )
        
        assert task.id == 'test-task-001'
        assert task.task_type == PipelineType.KNOWLEDGE_GRAPH
        assert task.pipeline == ProcessingPipeline.COMPREHENSIVE
        assert task.priority == ProcessingPriority.NORMAL
        assert task.status == ProcessingStatus.QUEUED
        assert task.progress == 0.0

    def test_processing_result_creation(self):
        """Test ProcessingResult creation"""
        result = ProcessingResult(
            task_id='test-task-001',
            pipeline=ProcessingPipeline.REAL_TIME,
            status=ProcessingStatus.COMPLETED,
            result_data={'result': 'test'},
            processing_time=1.5,
            confidence_score=0.85,
            is_preliminary=False,
            next_enhancement_eta=None
        )
        
        assert result.task_id == 'test-task-001'
        assert result.pipeline == ProcessingPipeline.REAL_TIME
        assert result.status == ProcessingStatus.COMPLETED
        assert result.processing_time == 1.5
        assert result.confidence_score == 0.85
        assert not result.is_preliminary


class TestStateSynchronizationService:
    """Test state synchronization service functionality"""
    
    @pytest.fixture
    def sync_service(self):
        """Create state synchronization service instance"""
        return StateSynchronizationService()
    
    @pytest.fixture
    def sample_real_time_result(self):
        """Sample real-time processing result"""
        return {
            'type': 'transcript_analysis',
            'pipeline': 'real_time',
            'summary': 'Quick analysis of meeting transcript',
            'key_points': ['Point 1', 'Point 2'],
            'confidence': 0.7,
            'processing_time': 0.5
        }
    
    @pytest.fixture
    def sample_comprehensive_result(self):
        """Sample comprehensive processing result"""
        return {
            'type': 'transcript_analysis',
            'pipeline': 'comprehensive',
            'summary': 'Detailed analysis of meeting transcript with insights',
            'key_points': ['Detailed Point 1', 'Detailed Point 2', 'Additional Point 3'],
            'detailed_analysis': {
                'sentiment': 0.8,
                'topics': ['topic1', 'topic2'],
                'participants': ['Alice', 'Bob']
            },
            'confidence': 0.95,
            'processing_time': 2.0
        }

    @pytest.mark.asyncio
    async def test_synchronize_results_success(self, sync_service, sample_real_time_result, sample_comprehensive_result):
        """Test successful result synchronization"""
        sync_result = await sync_service.synchronize_results(
            real_time_result=sample_real_time_result,
            comprehensive_result=sample_comprehensive_result,
            data_type='transcript_analysis'
        )
        
        assert sync_result.status in [SyncStatus.SYNCHRONIZED, SyncStatus.CONFLICT_DETECTED]
        assert sync_result.merged_result is not None
        assert sync_result.consistency_score >= 0
        assert sync_result.sync_confidence >= 0
        assert sync_result.processing_time > 0

    @pytest.mark.asyncio
    async def test_detect_conflicts_value_differences(self, sync_service, sample_real_time_result, sample_comprehensive_result):
        """Test conflict detection for value differences"""
        # Modify results to create conflicts
        rt_result = sample_real_time_result.copy()
        comp_result = sample_comprehensive_result.copy()
        
        rt_result['confidence'] = 0.6
        comp_result['confidence'] = 0.9
        
        sync_config = sync_service.sync_configurations['transcript_analysis']
        conflicts = await sync_service._detect_conflicts(rt_result, comp_result, sync_config)
        
        assert isinstance(conflicts, list)
        # Should detect confidence difference
        confidence_conflicts = [c for c in conflicts if 'confidence' in c.field_path]
        assert len(confidence_conflicts) > 0

    @pytest.mark.asyncio
    async def test_detect_conflicts_missing_fields(self, sync_service, sample_real_time_result, sample_comprehensive_result):
        """Test conflict detection for missing fields"""
        # Remove field from real-time result
        rt_result = sample_real_time_result.copy()
        del rt_result['key_points']
        
        sync_config = sync_service.sync_configurations['transcript_analysis']
        conflicts = await sync_service._detect_conflicts(rt_result, sample_comprehensive_result, sync_config)
        
        assert isinstance(conflicts, list)
        # Should detect missing key_points field
        missing_field_conflicts = [c for c in conflicts if c.conflict_type == 'missing_field']
        assert len(missing_field_conflicts) > 0

    def test_create_value_conflict(self, sync_service):
        """Test value conflict creation"""
        sync_config = sync_service.sync_configurations['transcript_analysis']
        
        conflict = sync_service._create_value_conflict(
            path='confidence',
            rt_value=0.7,
            comp_value=0.9,
            sync_config=sync_config
        )
        
        assert isinstance(conflict, SyncConflict)
        assert conflict.field_path == 'confidence'
        assert conflict.real_time_value == 0.7
        assert conflict.comprehensive_value == 0.9
        assert conflict.conflict_type == 'value_mismatch'
        assert conflict.severity == 'high'  # confidence is a critical field

    def test_create_type_conflict(self, sync_service):
        """Test type conflict creation"""
        sync_config = sync_service.sync_configurations['transcript_analysis']
        
        conflict = sync_service._create_type_conflict(
            path='key_points',
            rt_value=['point1', 'point2'],
            comp_value='point1, point2',  # Different type (string vs list)
            sync_config=sync_config
        )
        
        assert isinstance(conflict, SyncConflict)
        assert conflict.conflict_type == 'type_mismatch'
        assert conflict.manual_review_required == True

    def test_resolve_by_confidence(self, sync_service):
        """Test conflict resolution by confidence"""
        conflict = SyncConflict(
            id='test-conflict',
            field_path='summary',
            real_time_value='Quick summary',
            comprehensive_value='Detailed comprehensive summary',
            conflict_type='value_mismatch',
            severity='medium',
            resolution_strategy=ConflictResolution.HIGHEST_CONFIDENCE
        )
        
        sync_config = sync_service.sync_configurations['transcript_analysis']
        resolved_value, confidence = sync_service._resolve_by_confidence(conflict, sync_config)
        
        # Should choose comprehensive result (higher confidence)
        assert resolved_value == 'Detailed comprehensive summary'
        assert confidence > 0

    def test_resolve_comprehensive_priority(self, sync_service):
        """Test conflict resolution with comprehensive priority"""
        conflict = SyncConflict(
            id='test-conflict',
            field_path='summary',
            real_time_value='Quick summary',
            comprehensive_value='Detailed comprehensive summary',
            conflict_type='value_mismatch',
            severity='medium',
            resolution_strategy=ConflictResolution.COMPREHENSIVE_WINS
        )
        
        sync_config = sync_service.sync_configurations['pattern_recognition']
        resolved_value, confidence = sync_service._resolve_comprehensive_priority(conflict, sync_config)
        
        assert resolved_value == 'Detailed comprehensive summary'
        assert confidence == 0.9

    def test_resolve_by_weighted_average_numeric(self, sync_service):
        """Test conflict resolution by weighted average for numeric values"""
        conflict = SyncConflict(
            id='test-conflict',
            field_path='confidence',
            real_time_value=0.7,
            comprehensive_value=0.9,
            conflict_type='value_mismatch',
            severity='high',
            resolution_strategy=ConflictResolution.WEIGHTED_AVERAGE
        )
        
        sync_config = sync_service.sync_configurations['oracle_generation']
        resolved_value, confidence = sync_service._resolve_by_weighted_average(conflict, sync_config)
        
        # Should be weighted average: 0.7 * 0.3 + 0.9 * 0.7 = 0.84
        expected_value = 0.7 * 0.3 + 0.9 * 0.7
        assert abs(resolved_value - expected_value) < 0.01
        assert confidence > 0

    def test_resolve_by_weighted_average_non_numeric(self, sync_service):
        """Test conflict resolution by weighted average for non-numeric values"""
        conflict = SyncConflict(
            id='test-conflict',
            field_path='summary',
            real_time_value='Quick summary',
            comprehensive_value='Detailed summary',
            conflict_type='value_mismatch',
            severity='medium',
            resolution_strategy=ConflictResolution.WEIGHTED_AVERAGE
        )
        
        sync_config = sync_service.sync_configurations['oracle_generation']
        resolved_value, confidence = sync_service._resolve_by_weighted_average(conflict, sync_config)
        
        # Should fall back to comprehensive priority for non-numeric
        assert resolved_value == 'Detailed summary'
        assert confidence > 0

    def test_calculate_consistency_score_no_conflicts(self, sync_service):
        """Test consistency score calculation with no conflicts"""
        rt_result = {'field1': 'value1', 'field2': 'value2'}
        comp_result = {'field1': 'value1', 'field2': 'value2'}
        conflicts = []
        
        score = sync_service._calculate_consistency_score(rt_result, comp_result, conflicts)
        assert score == 1.0

    def test_calculate_consistency_score_with_conflicts(self, sync_service):
        """Test consistency score calculation with conflicts"""
        rt_result = {'field1': 'value1', 'field2': 'value2', 'field3': 'value3'}
        comp_result = {'field1': 'different', 'field2': 'value2', 'field3': 'value3'}
        
        conflicts = [
            SyncConflict(
                id='conflict1',
                field_path='field1',
                real_time_value='value1',
                comprehensive_value='different',
                conflict_type='value_mismatch',
                severity='medium',
                resolution_strategy=ConflictResolution.HIGHEST_CONFIDENCE
            )
        ]
        
        score = sync_service._calculate_consistency_score(rt_result, comp_result, conflicts)
        assert 0 <= score < 1.0  # Should be less than 1 due to conflicts

    def test_flatten_dict(self, sync_service):
        """Test dictionary flattening"""
        nested_dict = {
            'level1': {
                'level2': {
                    'level3': 'value'
                },
                'other': 'value2'
            },
            'top_level': 'value3'
        }
        
        flattened = sync_service._flatten_dict(nested_dict)
        
        assert 'level1.level2.level3' in flattened
        assert flattened['level1.level2.level3'] == 'value'
        assert 'level1.other' in flattened
        assert flattened['level1.other'] == 'value2'
        assert 'top_level' in flattened
        assert flattened['top_level'] == 'value3'

    def test_get_sync_metrics(self, sync_service):
        """Test sync metrics retrieval"""
        metrics = sync_service.get_sync_metrics()
        
        assert isinstance(metrics, dict)
        assert 'total_syncs' in metrics
        assert 'successful_syncs' in metrics
        assert 'conflicts_detected' in metrics
        assert 'active_sync_sessions' in metrics
        assert 'last_updated' in metrics


if __name__ == '__main__':
    pytest.main([__file__])