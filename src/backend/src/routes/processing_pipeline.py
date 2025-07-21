"""
Processing Pipeline API Routes
Provides endpoints for dual-pipeline processing coordination
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import structlog
from ..services.processing_coordinator import (
    ProcessingCoordinator, 
    PipelineType, 
    ProcessingPriority,
    ProcessingStatus
)
from ..services.state_synchronization_service import StateSynchronizationService
from ..security.auth import require_auth
from ..security.validation import validate_json_input
from ..security.rate_limiting import rate_limit

logger = structlog.get_logger(__name__)

# Create blueprint
processing_pipeline_bp = Blueprint('processing_pipeline', __name__, url_prefix='/api/processing')

# Initialize services
coordinator = ProcessingCoordinator()
sync_service = StateSynchronizationService()

@processing_pipeline_bp.route('/submit', methods=['POST'])
@require_auth
@rate_limit(limit=200, window=3600)  # 200 requests per hour
@validate_json_input
def submit_processing_task():
    """
    Submit a processing task to the dual-pipeline system
    
    Expected JSON payload:
    {
        "task_type": "transcript_analysis|pattern_recognition|oracle_generation|knowledge_graph|predictive_analytics|intervention_analysis",
        "input_data": {...},
        "priority": "immediate|fast|normal|comprehensive|deep",
        "enable_dual_pipeline": true,
        "metadata": {...}
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        task_type_str = data.get('task_type')
        input_data = data.get('input_data')
        
        if not task_type_str or not input_data:
            return jsonify({
                'error': 'task_type and input_data are required',
                'status': 'error'
            }), 400
        
        # Validate task type
        try:
            task_type = PipelineType(task_type_str)
        except ValueError:
            return jsonify({
                'error': f'Invalid task_type. Must be one of: {[t.value for t in PipelineType]}',
                'status': 'error'
            }), 400
        
        # Parse priority
        priority_str = data.get('priority', 'normal')
        try:
            priority = ProcessingPriority(priority_str)
        except ValueError:
            return jsonify({
                'error': f'Invalid priority. Must be one of: {[p.value for p in ProcessingPriority]}',
                'status': 'error'
            }), 400
        
        # Parse other parameters
        enable_dual_pipeline = data.get('enable_dual_pipeline', True)
        metadata = data.get('metadata', {})
        
        logger.info("Submitting processing task",
                   task_type=task_type.value,
                   priority=priority.value,
                   dual_pipeline=enable_dual_pipeline)
        
        # Submit task
        task_ids = coordinator.submit_processing_task(
            task_type=task_type,
            input_data=input_data,
            priority=priority,
            metadata=metadata,
            enable_dual_pipeline=enable_dual_pipeline
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'task_ids': task_ids,
                'dual_pipeline_enabled': enable_dual_pipeline,
                'estimated_completion': _estimate_completion_times(priority, enable_dual_pipeline)
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Task submission failed", error=str(e))
        return jsonify({
            'error': 'Task submission failed',
            'details': str(e),
            'status': 'error'
        }), 500

@processing_pipeline_bp.route('/status/<task_id>', methods=['GET'])
@require_auth
@rate_limit(limit=500, window=3600)  # 500 requests per hour
def get_task_status(task_id):
    """
    Get status and result of a processing task
    """
    try:
        # Get task status
        result = coordinator.get_task_status(task_id)
        
        if not result:
            return jsonify({
                'error': 'Task not found',
                'status': 'error'
            }), 404
        
        # Serialize result
        serialized_result = {
            'task_id': result.task_id,
            'pipeline': result.pipeline.value,
            'status': result.status.value,
            'result_data': result.result_data,
            'processing_time': result.processing_time,
            'confidence_score': result.confidence_score,
            'is_preliminary': result.is_preliminary,
            'next_enhancement_eta': result.next_enhancement_eta.isoformat() if result.next_enhancement_eta else None,
            'error_details': result.error_details
        }
        
        return jsonify({
            'status': 'success',
            'data': serialized_result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Task status retrieval failed", task_id=task_id, error=str(e))
        return jsonify({
            'error': 'Task status retrieval failed',
            'details': str(e),
            'status': 'error'
        }), 500

@processing_pipeline_bp.route('/sync/<sync_id>', methods=['GET'])
@require_auth
@rate_limit(limit=300, window=3600)  # 300 requests per hour
def get_synchronized_result(sync_id):
    """
    Get synchronized result from dual-pipeline processing
    """
    try:
        # Get synchronized result
        result = coordinator.get_synchronized_result(sync_id)
        
        if not result:
            return jsonify({
                'error': 'Sync session not found or not ready',
                'status': 'error'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Synchronized result retrieval failed", sync_id=sync_id, error=str(e))
        return jsonify({
            'error': 'Synchronized result retrieval failed',
            'details': str(e),
            'status': 'error'
        }), 500

@processing_pipeline_bp.route('/sync/manual', methods=['POST'])
@require_auth
@rate_limit(limit=50, window=3600)  # 50 requests per hour
@validate_json_input
def manual_synchronization():
    """
    Manually synchronize results from different pipelines
    
    Expected JSON payload:
    {
        "real_time_result": {...},
        "comprehensive_result": {...},
        "data_type": "transcript_analysis|pattern_recognition|oracle_generation|knowledge_graph|predictive_analytics|intervention_analysis",
        "sync_id": "optional_sync_id"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        real_time_result = data.get('real_time_result')
        comprehensive_result = data.get('comprehensive_result')
        data_type = data.get('data_type')
        
        if not all([real_time_result, comprehensive_result, data_type]):
            return jsonify({
                'error': 'real_time_result, comprehensive_result, and data_type are required',
                'status': 'error'
            }), 400
        
        sync_id = data.get('sync_id')
        
        logger.info("Starting manual synchronization",
                   data_type=data_type,
                   sync_id=sync_id)
        
        # Perform synchronization
        sync_result = sync_service.synchronize_results(
            real_time_result=real_time_result,
            comprehensive_result=comprehensive_result,
            data_type=data_type,
            sync_id=sync_id
        )
        
        # Serialize sync result
        serialized_result = {
            'sync_id': sync_result.sync_id,
            'status': sync_result.status.value,
            'merged_result': sync_result.merged_result,
            'conflicts': [_serialize_conflict(c) for c in sync_result.conflicts],
            'consistency_score': sync_result.consistency_score,
            'sync_confidence': sync_result.sync_confidence,
            'processing_time': sync_result.processing_time,
            'real_time_weight': sync_result.real_time_weight,
            'comprehensive_weight': sync_result.comprehensive_weight,
            'metadata': sync_result.metadata,
            'created_at': sync_result.created_at.isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': serialized_result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Manual synchronization failed", error=str(e))
        return jsonify({
            'error': 'Manual synchronization failed',
            'details': str(e),
            'status': 'error'
        }), 500

@processing_pipeline_bp.route('/metrics', methods=['GET'])
@require_auth
@rate_limit(limit=100, window=3600)  # 100 requests per hour
def get_processing_metrics():
    """
    Get processing pipeline metrics and performance statistics
    """
    try:
        # Get coordinator metrics
        coordinator_metrics = {
            'real_time_pipeline': {
                'queue_length': coordinator.real_time_queue.qsize(),
                'active_workers': coordinator.real_time_executor._threads,
                'metrics': coordinator.pipeline_metrics[coordinator.ProcessingPipeline.REAL_TIME].__dict__
            },
            'comprehensive_pipeline': {
                'queue_length': coordinator.comprehensive_queue.qsize(),
                'active_workers': coordinator.comprehensive_executor._threads,
                'metrics': coordinator.pipeline_metrics[coordinator.ProcessingPipeline.COMPREHENSIVE].__dict__
            },
            'active_tasks': len(coordinator.active_tasks),
            'completed_tasks': len(coordinator.completed_tasks),
            'state_syncs': len(coordinator.state_sync)
        }
        
        # Get synchronization metrics
        sync_metrics = sync_service.get_sync_metrics()
        
        # Combine metrics
        combined_metrics = {
            'processing_pipelines': coordinator_metrics,
            'synchronization': sync_metrics,
            'system_health': _calculate_system_health(coordinator_metrics, sync_metrics),
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': combined_metrics,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Metrics retrieval failed", error=str(e))
        return jsonify({
            'error': 'Metrics retrieval failed',
            'details': str(e),
            'status': 'error'
        }), 500

@processing_pipeline_bp.route('/health', methods=['GET'])
@require_auth
@rate_limit(limit=200, window=3600)  # 200 requests per hour
def get_system_health():
    """
    Get system health status for processing pipelines
    """
    try:
        # Check pipeline health
        rt_queue_size = coordinator.real_time_queue.qsize()
        comp_queue_size = coordinator.comprehensive_queue.qsize()
        
        # Health indicators
        health_status = {
            'overall_status': 'healthy',
            'real_time_pipeline': {
                'status': 'healthy' if rt_queue_size < 100 else 'degraded' if rt_queue_size < 500 else 'unhealthy',
                'queue_size': rt_queue_size,
                'max_queue_size': coordinator.config['max_queue_size']
            },
            'comprehensive_pipeline': {
                'status': 'healthy' if comp_queue_size < 50 else 'degraded' if comp_queue_size < 200 else 'unhealthy',
                'queue_size': comp_queue_size,
                'max_queue_size': coordinator.config['max_queue_size']
            },
            'synchronization_service': {
                'status': 'healthy',
                'active_sessions': len(sync_service.sync_sessions),
                'success_rate': sync_service.sync_metrics.get('successful_syncs', 0) / max(sync_service.sync_metrics.get('total_syncs', 1), 1)
            },
            'last_check': datetime.utcnow().isoformat()
        }
        
        # Determine overall status
        pipeline_statuses = [
            health_status['real_time_pipeline']['status'],
            health_status['comprehensive_pipeline']['status'],
            health_status['synchronization_service']['status']
        ]
        
        if 'unhealthy' in pipeline_statuses:
            health_status['overall_status'] = 'unhealthy'
        elif 'degraded' in pipeline_statuses:
            health_status['overall_status'] = 'degraded'
        
        return jsonify({
            'status': 'success',
            'data': health_status,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return jsonify({
            'error': 'Health check failed',
            'details': str(e),
            'status': 'error'
        }), 500

@processing_pipeline_bp.route('/cancel/<task_id>', methods=['POST'])
@require_auth
@rate_limit(limit=100, window=3600)  # 100 requests per hour
def cancel_task(task_id):
    """
    Cancel a processing task
    """
    try:
        # Check if task exists and is cancellable
        if task_id not in coordinator.active_tasks:
            return jsonify({
                'error': 'Task not found or already completed',
                'status': 'error'
            }), 404
        
        task = coordinator.active_tasks[task_id]
        
        if task.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED, ProcessingStatus.CANCELLED]:
            return jsonify({
                'error': 'Task cannot be cancelled in current status',
                'status': 'error'
            }), 400
        
        # Cancel task
        task.status = ProcessingStatus.CANCELLED
        task.completed_at = datetime.utcnow()
        task.error = "Task cancelled by user request"
        
        # Move to completed tasks
        coordinator.completed_tasks.append(task)
        del coordinator.active_tasks[task_id]
        
        logger.info("Task cancelled", task_id=task_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'task_id': task_id,
                'cancelled_at': task.completed_at.isoformat()
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Task cancellation failed", task_id=task_id, error=str(e))
        return jsonify({
            'error': 'Task cancellation failed',
            'details': str(e),
            'status': 'error'
        }), 500

# Helper functions
def _estimate_completion_times(priority: ProcessingPriority, dual_pipeline: bool) -> Dict[str, str]:
    """Estimate completion times based on priority and pipeline configuration"""
    estimates = {
        ProcessingPriority.IMMEDIATE: {'real_time': '< 1 second', 'comprehensive': 'N/A'},
        ProcessingPriority.FAST: {'real_time': '< 5 seconds', 'comprehensive': '< 30 seconds'},
        ProcessingPriority.NORMAL: {'real_time': '< 10 seconds', 'comprehensive': '< 2 minutes'},
        ProcessingPriority.COMPREHENSIVE: {'real_time': 'N/A', 'comprehensive': '< 5 minutes'},
        ProcessingPriority.DEEP: {'real_time': 'N/A', 'comprehensive': '< 30 minutes'}
    }
    
    estimate = estimates.get(priority, estimates[ProcessingPriority.NORMAL])
    
    if not dual_pipeline:
        if priority in [ProcessingPriority.IMMEDIATE, ProcessingPriority.FAST]:
            return {'estimated_completion': estimate['real_time']}
        else:
            return {'estimated_completion': estimate['comprehensive']}
    
    return {
        'real_time_completion': estimate['real_time'],
        'comprehensive_completion': estimate['comprehensive']
    }

def _serialize_conflict(conflict) -> Dict[str, Any]:
    """Serialize sync conflict for API response"""
    return {
        'id': conflict.id,
        'field_path': conflict.field_path,
        'real_time_value': conflict.real_time_value,
        'comprehensive_value': conflict.comprehensive_value,
        'conflict_type': conflict.conflict_type,
        'severity': conflict.severity,
        'resolution_strategy': conflict.resolution_strategy.value,
        'resolved_value': conflict.resolved_value,
        'resolution_confidence': conflict.resolution_confidence,
        'manual_review_required': conflict.manual_review_required
    }

def _calculate_system_health(coordinator_metrics: Dict[str, Any], 
                           sync_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall system health score"""
    try:
        # Calculate health factors
        rt_queue_health = 1.0 - min(coordinator_metrics['real_time_pipeline']['queue_length'] / 1000, 1.0)
        comp_queue_health = 1.0 - min(coordinator_metrics['comprehensive_pipeline']['queue_length'] / 500, 1.0)
        sync_success_rate = sync_metrics.get('successful_syncs', 0) / max(sync_metrics.get('total_syncs', 1), 1)
        
        # Overall health score
        overall_health = (rt_queue_health + comp_queue_health + sync_success_rate) / 3
        
        return {
            'overall_health_score': overall_health,
            'real_time_queue_health': rt_queue_health,
            'comprehensive_queue_health': comp_queue_health,
            'synchronization_success_rate': sync_success_rate,
            'status': 'healthy' if overall_health > 0.8 else 'degraded' if overall_health > 0.6 else 'unhealthy'
        }
        
    except Exception as e:
        logger.error("System health calculation failed", error=str(e))
        return {
            'overall_health_score': 0.5,
            'status': 'unknown',
            'error': str(e)
        }