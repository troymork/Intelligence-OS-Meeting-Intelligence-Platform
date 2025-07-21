"""
Processing Coordinator Service
Manages dual-pipeline processing architecture for real-time and comprehensive analysis
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog
from collections import defaultdict, deque
import json
import threading
from concurrent.futures import ThreadPoolExecutor, Future
import queue
import time

logger = structlog.get_logger(__name__)

class ProcessingPipeline(Enum):
    """Types of processing pipelines"""
    REAL_TIME = "real_time"
    COMPREHENSIVE = "comprehensive"
    HYBRID = "hybrid"

class ProcessingPriority(Enum):
    """Processing priority levels"""
    IMMEDIATE = "immediate"      # < 1 second
    FAST = "fast"               # < 5 seconds
    NORMAL = "normal"           # < 30 seconds
    COMPREHENSIVE = "comprehensive"  # < 5 minutes
    DEEP = "deep"               # < 30 minutes

class ProcessingStatus(Enum):
    """Status of processing tasks"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class PipelineType(Enum):
    """Types of analysis pipelines"""
    TRANSCRIPT_ANALYSIS = "transcript_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"
    ORACLE_GENERATION = "oracle_generation"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    INTERVENTION_ANALYSIS = "intervention_analysis"

@dataclass
class ProcessingTask:
    """Individual processing task"""
    id: str
    task_type: PipelineType
    pipeline: ProcessingPipeline
    priority: ProcessingPriority
    input_data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: ProcessingStatus = ProcessingStatus.QUEUED
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timeout_seconds: int = 300  # 5 minutes default
    dependencies: List[str] = field(default_factory=list)
    callbacks: List[Callable] = field(default_factory=list)

@dataclass
class ProcessingResult:
    """Result of processing operation"""
    task_id: str
    pipeline: ProcessingPipeline
    status: ProcessingStatus
    result_data: Optional[Dict[str, Any]]
    processing_time: float
    confidence_score: float
    is_preliminary: bool
    next_enhancement_eta: Optional[datetime]
    error_details: Optional[str] = None

@dataclass
class PipelineMetrics:
    """Metrics for pipeline performance"""
    pipeline: ProcessingPipeline
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_processing_time: float
    throughput_per_minute: float
    queue_length: int
    active_workers: int
    success_rate: float
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class StateSync:
    """State synchronization between pipelines"""
    sync_id: str
    real_time_result: Optional[Dict[str, Any]]
    comprehensive_result: Optional[Dict[str, Any]]
    sync_status: str  # pending, partial, complete
    consistency_score: float
    last_sync: datetime = field(default_factory=datetime.utcnow)
    conflicts: List[str] = field(default_factory=list)

class ProcessingCoordinator:
    """Coordinates dual-pipeline processing architecture"""
    
    def __init__(self):
        # Processing queues
        self.real_time_queue = queue.PriorityQueue()
        self.comprehensive_queue = queue.PriorityQueue()
        
        # Task tracking
        self.active_tasks = {}  # task_id -> ProcessingTask
        self.completed_tasks = deque(maxlen=1000)  # Recent completed tasks
        self.task_results = {}  # task_id -> ProcessingResult
        
        # State synchronization
        self.state_sync = {}  # sync_id -> StateSync
        
        # Worker pools
        self.real_time_executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="rt_worker"
        )
        self.comprehensive_executor = ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="comp_worker"
        )
        
        # Pipeline processors
        self.pipeline_processors = self._initialize_pipeline_processors()
        
        # Metrics tracking
        self.pipeline_metrics = {
            ProcessingPipeline.REAL_TIME: PipelineMetrics(
                pipeline=ProcessingPipeline.REAL_TIME,
                total_tasks=0, completed_tasks=0, failed_tasks=0,
                average_processing_time=0.0, throughput_per_minute=0.0,
                queue_length=0, active_workers=0, success_rate=0.0
            ),
            ProcessingPipeline.COMPREHENSIVE: PipelineMetrics(
                pipeline=ProcessingPipeline.COMPREHENSIVE,
                total_tasks=0, completed_tasks=0, failed_tasks=0,
                average_processing_time=0.0, throughput_per_minute=0.0,
                queue_length=0, active_workers=0, success_rate=0.0
            )
        }
        
        # Configuration
        self.config = {
            'real_time_timeout_seconds': 10,
            'comprehensive_timeout_seconds': 1800,  # 30 minutes
            'max_queue_size': 1000,
            'sync_check_interval_seconds': 5,
            'metrics_update_interval_seconds': 30,
            'task_cleanup_interval_seconds': 3600  # 1 hour
        }
        
        # Start background processes
        self._start_background_processes()
    
    def _initialize_pipeline_processors(self) -> Dict[PipelineType, Dict[str, Callable]]:
        """Initialize pipeline processors for different analysis types"""
        return {
            PipelineType.TRANSCRIPT_ANALYSIS: {
                'real_time': self._process_transcript_real_time,
                'comprehensive': self._process_transcript_comprehensive
            },
            PipelineType.PATTERN_RECOGNITION: {
                'real_time': self._process_patterns_real_time,
                'comprehensive': self._process_patterns_comprehensive
            },
            PipelineType.ORACLE_GENERATION: {
                'real_time': self._process_oracle_real_time,
                'comprehensive': self._process_oracle_comprehensive
            },
            PipelineType.KNOWLEDGE_GRAPH: {
                'real_time': self._process_knowledge_real_time,
                'comprehensive': self._process_knowledge_comprehensive
            },
            PipelineType.PREDICTIVE_ANALYTICS: {
                'real_time': self._process_predictive_real_time,
                'comprehensive': self._process_predictive_comprehensive
            },
            PipelineType.INTERVENTION_ANALYSIS: {
                'real_time': self._process_intervention_real_time,
                'comprehensive': self._process_intervention_comprehensive
            }
        }
    
    async def submit_processing_task(self, 
                                   task_type: PipelineType,
                                   input_data: Dict[str, Any],
                                   priority: ProcessingPriority = ProcessingPriority.NORMAL,
                                   metadata: Optional[Dict[str, Any]] = None,
                                   enable_dual_pipeline: bool = True) -> Dict[str, str]:
        """Submit a processing task to appropriate pipeline(s)"""
        try:
            task_ids = {}
            
            # Determine which pipelines to use
            pipelines_to_use = self._determine_pipelines(priority, enable_dual_pipeline)
            
            for pipeline in pipelines_to_use:
                task_id = str(uuid.uuid4())
                
                # Create processing task
                task = ProcessingTask(
                    id=task_id,
                    task_type=task_type,
                    pipeline=pipeline,
                    priority=priority,
                    input_data=input_data.copy(),
                    metadata=metadata or {},
                    timeout_seconds=self._get_timeout_for_pipeline(pipeline)
                )
                
                # Add to active tasks
                self.active_tasks[task_id] = task
                
                # Queue task
                await self._queue_task(task)
                
                task_ids[pipeline.value] = task_id
                
                logger.info("Processing task submitted",
                           task_id=task_id,
                           task_type=task_type.value,
                           pipeline=pipeline.value,
                           priority=priority.value)
            
            # Create state sync if dual pipeline
            if len(task_ids) > 1:
                sync_id = str(uuid.uuid4())
                self.state_sync[sync_id] = StateSync(
                    sync_id=sync_id,
                    sync_status='pending'
                )
                
                # Link tasks to sync
                for task_id in task_ids.values():
                    self.active_tasks[task_id].metadata['sync_id'] = sync_id
            
            return task_ids
            
        except Exception as e:
            logger.error("Task submission failed", error=str(e))
            raise
    
    def _determine_pipelines(self, priority: ProcessingPriority, 
                           enable_dual_pipeline: bool) -> List[ProcessingPipeline]:
        """Determine which pipelines to use based on priority and settings"""
        if not enable_dual_pipeline:
            # Single pipeline based on priority
            if priority in [ProcessingPriority.IMMEDIATE, ProcessingPriority.FAST]:
                return [ProcessingPipeline.REAL_TIME]
            else:
                return [ProcessingPipeline.COMPREHENSIVE]
        
        # Dual pipeline for most cases
        if priority == ProcessingPriority.IMMEDIATE:
            return [ProcessingPipeline.REAL_TIME]
        elif priority in [ProcessingPriority.FAST, ProcessingPriority.NORMAL]:
            return [ProcessingPipeline.REAL_TIME, ProcessingPipeline.COMPREHENSIVE]
        else:
            return [ProcessingPipeline.COMPREHENSIVE]
    
    def _get_timeout_for_pipeline(self, pipeline: ProcessingPipeline) -> int:
        """Get timeout for specific pipeline"""
        if pipeline == ProcessingPipeline.REAL_TIME:
            return self.config['real_time_timeout_seconds']
        else:
            return self.config['comprehensive_timeout_seconds']
    
    async def _queue_task(self, task: ProcessingTask):
        """Queue task in appropriate pipeline"""
        try:
            # Priority for queue (lower number = higher priority)
            priority_map = {
                ProcessingPriority.IMMEDIATE: 1,
                ProcessingPriority.FAST: 2,
                ProcessingPriority.NORMAL: 3,
                ProcessingPriority.COMPREHENSIVE: 4,
                ProcessingPriority.DEEP: 5
            }
            
            queue_priority = priority_map.get(task.priority, 3)
            queue_item = (queue_priority, time.time(), task)
            
            if task.pipeline == ProcessingPipeline.REAL_TIME:
                if self.real_time_queue.qsize() < self.config['max_queue_size']:
                    self.real_time_queue.put(queue_item)
                else:
                    raise Exception("Real-time queue is full")
            else:
                if self.comprehensive_queue.qsize() < self.config['max_queue_size']:
                    self.comprehensive_queue.put(queue_item)
                else:
                    raise Exception("Comprehensive queue is full")
            
            # Update metrics
            self.pipeline_metrics[task.pipeline].queue_length += 1
            
        except Exception as e:
            logger.error("Task queuing failed", task_id=task.id, error=str(e))
            task.status = ProcessingStatus.FAILED
            task.error = str(e)
            raise
    
    async def get_task_status(self, task_id: str) -> Optional[ProcessingResult]:
        """Get status and result of a processing task"""
        try:
            # Check if task is in results cache
            if task_id in self.task_results:
                return self.task_results[task_id]
            
            # Check if task is still active
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                
                return ProcessingResult(
                    task_id=task_id,
                    pipeline=task.pipeline,
                    status=task.status,
                    result_data=task.result,
                    processing_time=self._calculate_processing_time(task),
                    confidence_score=self._calculate_confidence_score(task),
                    is_preliminary=(task.status == ProcessingStatus.PROCESSING),
                    next_enhancement_eta=self._estimate_completion_time(task),
                    error_details=task.error
                )
            
            # Task not found
            return None
            
        except Exception as e:
            logger.error("Task status retrieval failed", task_id=task_id, error=str(e))
            return None
    
    async def get_synchronized_result(self, sync_id: str) -> Optional[Dict[str, Any]]:
        """Get synchronized result from dual-pipeline processing"""
        try:
            if sync_id not in self.state_sync:
                return None
            
            sync_state = self.state_sync[sync_id]
            
            if sync_state.sync_status == 'complete':
                # Return merged result
                return self._merge_pipeline_results(
                    sync_state.real_time_result,
                    sync_state.comprehensive_result
                )
            elif sync_state.sync_status == 'partial':
                # Return available result with indication
                if sync_state.real_time_result:
                    result = sync_state.real_time_result.copy()
                    result['_is_preliminary'] = True
                    result['_comprehensive_eta'] = self._estimate_comprehensive_completion(sync_id)
                    return result
            
            return None
            
        except Exception as e:
            logger.error("Synchronized result retrieval failed", sync_id=sync_id, error=str(e))
            return None
    
    def _start_background_processes(self):
        """Start background processing threads"""
        # Real-time processing worker
        threading.Thread(
            target=self._real_time_worker,
            daemon=True,
            name="real_time_processor"
        ).start()
        
        # Comprehensive processing worker
        threading.Thread(
            target=self._comprehensive_worker,
            daemon=True,
            name="comprehensive_processor"
        ).start()
        
        # State synchronization worker
        threading.Thread(
            target=self._sync_worker,
            daemon=True,
            name="state_sync_processor"
        ).start()
        
        # Metrics update worker
        threading.Thread(
            target=self._metrics_worker,
            daemon=True,
            name="metrics_processor"
        ).start()
    
    def _real_time_worker(self):
        """Real-time processing worker thread"""
        while True:
            try:
                # Get task from queue (blocking with timeout)
                try:
                    priority, timestamp, task = self.real_time_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process task
                self._process_task(task)
                
                # Mark queue task as done
                self.real_time_queue.task_done()
                
            except Exception as e:
                logger.error("Real-time worker error", error=str(e))
                time.sleep(1)
    
    def _comprehensive_worker(self):
        """Comprehensive processing worker thread"""
        while True:
            try:
                # Get task from queue (blocking with timeout)
                try:
                    priority, timestamp, task = self.comprehensive_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process task
                self._process_task(task)
                
                # Mark queue task as done
                self.comprehensive_queue.task_done()
                
            except Exception as e:
                logger.error("Comprehensive worker error", error=str(e))
                time.sleep(1)
    
    def _process_task(self, task: ProcessingTask):
        """Process a single task"""
        try:
            # Update task status
            task.status = ProcessingStatus.PROCESSING
            task.started_at = datetime.utcnow()
            
            # Get appropriate processor
            processor_map = self.pipeline_processors.get(task.task_type, {})
            processor_key = 'real_time' if task.pipeline == ProcessingPipeline.REAL_TIME else 'comprehensive'
            processor = processor_map.get(processor_key)
            
            if not processor:
                raise Exception(f"No processor found for {task.task_type.value} in {task.pipeline.value} pipeline")
            
            # Process with timeout
            start_time = time.time()
            
            try:
                # Execute processor
                result = processor(task.input_data, task.metadata)
                
                # Update task with result
                task.result = result
                task.status = ProcessingStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.progress = 1.0
                
                # Create processing result
                processing_result = ProcessingResult(
                    task_id=task.id,
                    pipeline=task.pipeline,
                    status=task.status,
                    result_data=result,
                    processing_time=time.time() - start_time,
                    confidence_score=self._calculate_confidence_score(task),
                    is_preliminary=False,
                    next_enhancement_eta=None
                )
                
                # Cache result
                self.task_results[task.id] = processing_result
                
                # Update state sync if applicable
                if 'sync_id' in task.metadata:
                    self._update_state_sync(task.metadata['sync_id'], task)
                
                # Execute callbacks
                for callback in task.callbacks:
                    try:
                        callback(processing_result)
                    except Exception as callback_error:
                        logger.error("Callback execution failed", 
                                   task_id=task.id, 
                                   error=str(callback_error))
                
                logger.info("Task processing completed",
                           task_id=task.id,
                           pipeline=task.pipeline.value,
                           processing_time=time.time() - start_time)
                
            except Exception as processing_error:
                # Handle processing failure
                task.status = ProcessingStatus.FAILED
                task.error = str(processing_error)
                task.completed_at = datetime.utcnow()
                
                logger.error("Task processing failed",
                           task_id=task.id,
                           pipeline=task.pipeline.value,
                           error=str(processing_error))
            
            # Move to completed tasks
            self.completed_tasks.append(task)
            
            # Remove from active tasks
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            
            # Update metrics
            self._update_pipeline_metrics(task.pipeline, task)
            
        except Exception as e:
            logger.error("Task processing error", task_id=task.id, error=str(e))
            task.status = ProcessingStatus.FAILED
            task.error = str(e)
    
    # Placeholder processor methods (to be implemented with actual processing logic)
    def _process_transcript_real_time(self, input_data: Dict[str, Any], 
                                    metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Real-time transcript processing"""
        # Simplified real-time processing
        return {
            'type': 'transcript_analysis',
            'pipeline': 'real_time',
            'summary': 'Quick transcript analysis completed',
            'key_points': ['Point 1', 'Point 2'],
            'confidence': 0.7,
            'processing_time': 0.5
        }
    
    def _process_transcript_comprehensive(self, input_data: Dict[str, Any], 
                                        metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive transcript processing"""
        # Comprehensive processing with full analysis
        time.sleep(2)  # Simulate longer processing
        return {
            'type': 'transcript_analysis',
            'pipeline': 'comprehensive',
            'summary': 'Comprehensive transcript analysis completed',
            'detailed_analysis': {'sentiment': 0.8, 'topics': ['topic1', 'topic2']},
            'key_points': ['Detailed Point 1', 'Detailed Point 2', 'Detailed Point 3'],
            'confidence': 0.95,
            'processing_time': 2.0
        }
    
    def _process_patterns_real_time(self, input_data: Dict[str, Any], 
                                  metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Real-time pattern processing"""
        return {
            'type': 'pattern_recognition',
            'pipeline': 'real_time',
            'patterns_detected': 2,
            'confidence': 0.6
        }
    
    def _process_patterns_comprehensive(self, input_data: Dict[str, Any], 
                                      metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive pattern processing"""
        time.sleep(3)  # Simulate longer processing
        return {
            'type': 'pattern_recognition',
            'pipeline': 'comprehensive',
            'patterns_detected': 5,
            'detailed_patterns': ['pattern1', 'pattern2', 'pattern3'],
            'confidence': 0.9
        }
    
    def _process_oracle_real_time(self, input_data: Dict[str, Any], 
                                metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Real-time Oracle processing"""
        return {
            'type': 'oracle_generation',
            'pipeline': 'real_time',
            'summary': 'Quick Oracle insights',
            'confidence': 0.65
        }
    
    def _process_oracle_comprehensive(self, input_data: Dict[str, Any], 
                                    metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive Oracle processing"""
        time.sleep(5)  # Simulate longer processing
        return {
            'type': 'oracle_generation',
            'pipeline': 'comprehensive',
            'full_oracle_output': {'decisions': [], 'actions': [], 'insights': []},
            'confidence': 0.92
        }
    
    def _process_knowledge_real_time(self, input_data: Dict[str, Any], 
                                   metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Real-time knowledge graph processing"""
        return {
            'type': 'knowledge_graph',
            'pipeline': 'real_time',
            'concepts_identified': 3,
            'confidence': 0.7
        }
    
    def _process_knowledge_comprehensive(self, input_data: Dict[str, Any], 
                                       metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive knowledge graph processing"""
        time.sleep(4)  # Simulate longer processing
        return {
            'type': 'knowledge_graph',
            'pipeline': 'comprehensive',
            'concepts_identified': 12,
            'relationships_mapped': 8,
            'confidence': 0.88
        }
    
    def _process_predictive_real_time(self, input_data: Dict[str, Any], 
                                    metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Real-time predictive processing"""
        return {
            'type': 'predictive_analytics',
            'pipeline': 'real_time',
            'quick_forecast': 'trend_stable',
            'confidence': 0.6
        }
    
    def _process_predictive_comprehensive(self, input_data: Dict[str, Any], 
                                        metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive predictive processing"""
        time.sleep(6)  # Simulate longer processing
        return {
            'type': 'predictive_analytics',
            'pipeline': 'comprehensive',
            'detailed_forecast': {'trend': 'improving', 'probability': 0.85},
            'confidence': 0.91
        }
    
    def _process_intervention_real_time(self, input_data: Dict[str, Any], 
                                      metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Real-time intervention processing"""
        return {
            'type': 'intervention_analysis',
            'pipeline': 'real_time',
            'quick_recommendations': ['recommendation1'],
            'confidence': 0.65
        }
    
    def _process_intervention_comprehensive(self, input_data: Dict[str, Any], 
                                         metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive intervention processing"""
        time.sleep(3)  # Simulate longer processing
        return {
            'type': 'intervention_analysis',
            'pipeline': 'comprehensive',
            'detailed_recommendations': ['rec1', 'rec2', 'rec3'],
            'implementation_plans': ['plan1', 'plan2'],
            'confidence': 0.89
        }

# Global coordinator instance
processing_coordinator = ProcessingCoordinator()