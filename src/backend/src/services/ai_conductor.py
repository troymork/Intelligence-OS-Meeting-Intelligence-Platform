"""
AI Conductor Service for Intelligence OS
Orchestrates multiple AI engines for comprehensive meeting analysis
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import structlog
from concurrent.futures import ThreadPoolExecutor, as_completed
import openai

from .ai_performers import (
    BaseAIPerformer,
    StructuralExtractionPerformer,
    PatternAnalysisPerformer,
    StrategicSynthesisPerformer,
    NarrativeIntegrationPerformer,
    SolutionArchitecturePerformer,
    HumanNeedsPerformer
)
from .ai_communication import ai_communication_hub, AIMessage, MessageType, MessagePriority
from .ai_performers.message_handlers import BasePerformerMessageHandler
from .ai_audit import ai_audit_system, AuditEventType, AuditLevel

logger = structlog.get_logger(__name__)

class AnalysisDimension(Enum):
    """Oracle 9.1 Protocol analysis dimensions"""
    STRUCTURAL_EXTRACTION = "structural_extraction"
    PATTERN_SUBTEXT = "pattern_subtext"
    STRATEGIC_SYNTHESIS = "strategic_synthesis"
    NARRATIVE_INTEGRATION = "narrative_integration"
    SOLUTION_ARCHITECTURE = "solution_architecture"
    HUMAN_NEEDS_DYNAMICS = "human_needs_dynamics"

class ProcessingStatus(Enum):
    """Processing status for AI tasks"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AnalysisTask:
    """Individual analysis task for AI performers"""
    id: str
    dimension: AnalysisDimension
    input_data: Dict[str, Any]
    priority: Priority
    assigned_performer: Optional[str] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    processing_time: float = 0.0
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AIPerformer:
    """AI Performer that handles specific analysis dimensions"""
    id: str
    name: str
    specialties: List[AnalysisDimension]
    max_concurrent_tasks: int
    current_tasks: List[str] = field(default_factory=list)
    total_tasks_completed: int = 0
    average_processing_time: float = 0.0
    success_rate: float = 1.0
    last_activity: Optional[datetime] = None
    capabilities: Dict[str, Any] = field(default_factory=dict)
    status: str = "ready"

@dataclass
class AnalysisSession:
    """Complete analysis session coordinated by the conductor"""
    id: str
    meeting_id: Optional[str]
    transcript_id: Optional[str]
    input_data: Dict[str, Any]
    tasks: List[AnalysisTask]
    results: Dict[AnalysisDimension, Dict[str, Any]] = field(default_factory=dict)
    overall_confidence: float = 0.0
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)

class AIConductor:
    """AI Conductor that orchestrates multiple AI performers for comprehensive analysis"""
    
    def __init__(self):
        self.performers: Dict[str, AIPerformer] = {}
        self.ai_performers: Dict[str, BaseAIPerformer] = {}
        self.active_sessions: Dict[str, AnalysisSession] = {}
        self.task_queue: List[AnalysisTask] = []
        self.completed_sessions: List[str] = []
        
        # OpenAI client for AI processing
        self.openai_client = None
        
        # Processing configuration
        self.max_concurrent_sessions = 10
        self.task_timeout = 300  # 5 minutes
        self.retry_attempts = 3
        
        # Performance tracking
        self.performance_metrics = {
            'total_sessions': 0,
            'successful_sessions': 0,
            'failed_sessions': 0,
            'average_session_time': 0.0,
            'total_tasks_processed': 0
        }
        
        # Initialize AI performers
        self._initialize_performers()
    
    async def initialize(self):
        """Initialize the AI Conductor"""
        try:
            # Initialize OpenAI client
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized for AI Conductor")
            
            # Initialize communication hub
            await ai_communication_hub.initialize()
            logger.info("AI Communication Hub initialized")
            
            # Initialize audit system
            await ai_audit_system.initialize()
            logger.info("AI Audit System initialized")
            
            # Initialize all AI performers
            for performer_id, ai_performer in self.ai_performers.items():
                await ai_performer.initialize()
                
                # Create message handler for each performer
                message_handler = BasePerformerMessageHandler(performer_id, ai_performer)
                ai_performer.message_handler = message_handler
                ai_performer.communication_hub = ai_communication_hub
                
                # Register performer with communication hub
                ai_communication_hub.register_performer(
                    performer_id, 
                    ai_performer.capabilities, 
                    message_handler
                )
                
                logger.info(f"AI performer initialized and registered: {performer_id}")
            
            # Start background task processor
            self.processing_task = asyncio.create_task(self._background_processor())
            
            logger.info("AI Conductor initialized successfully",
                       performers=len(self.performers),
                       ai_performers=len(self.ai_performers),
                       max_concurrent_sessions=self.max_concurrent_sessions)
            
        except Exception as e:
            logger.error("Failed to initialize AI Conductor", error=str(e))
            raise
    
    def _initialize_performers(self):
        """Initialize AI performers for each analysis dimension"""
        
        # Create actual AI performer instances
        self.ai_performers['structural_extractor'] = StructuralExtractionPerformer()
        self.ai_performers['pattern_analyzer'] = PatternAnalysisPerformer()
        self.ai_performers['strategic_synthesizer'] = StrategicSynthesisPerformer()
        self.ai_performers['narrative_integrator'] = NarrativeIntegrationPerformer()
        self.ai_performers['solution_architect'] = SolutionArchitecturePerformer()
        self.ai_performers['human_needs_analyzer'] = HumanNeedsPerformer()
        
        # Create metadata performers for tracking
        self.performers['structural_extractor'] = AIPerformer(
            id='structural_extractor',
            name='Structural Extraction AI',
            specialties=[AnalysisDimension.STRUCTURAL_EXTRACTION],
            max_concurrent_tasks=3,
            capabilities=self.ai_performers['structural_extractor'].capabilities
        )
        
        self.performers['pattern_analyzer'] = AIPerformer(
            id='pattern_analyzer',
            name='Pattern Analysis AI',
            specialties=[AnalysisDimension.PATTERN_SUBTEXT],
            max_concurrent_tasks=2,
            capabilities=self.ai_performers['pattern_analyzer'].capabilities
        )
        
        self.performers['strategic_synthesizer'] = AIPerformer(
            id='strategic_synthesizer',
            name='Strategic Synthesis AI',
            specialties=[AnalysisDimension.STRATEGIC_SYNTHESIS],
            max_concurrent_tasks=2,
            capabilities=self.ai_performers['strategic_synthesizer'].capabilities
        )
        
        self.performers['narrative_integrator'] = AIPerformer(
            id='narrative_integrator',
            name='Narrative Integration AI',
            specialties=[AnalysisDimension.NARRATIVE_INTEGRATION],
            max_concurrent_tasks=2,
            capabilities=self.ai_performers['narrative_integrator'].capabilities
        )
        
        self.performers['solution_architect'] = AIPerformer(
            id='solution_architect',
            name='Solution Architecture AI',
            specialties=[AnalysisDimension.SOLUTION_ARCHITECTURE],
            max_concurrent_tasks=2,
            capabilities=self.ai_performers['solution_architect'].capabilities
        )
        
        self.performers['human_needs_analyzer'] = AIPerformer(
            id='human_needs_analyzer',
            name='Human Needs Analysis AI',
            specialties=[AnalysisDimension.HUMAN_NEEDS_DYNAMICS],
            max_concurrent_tasks=2,
            capabilities=self.ai_performers['human_needs_analyzer'].capabilities
        )
    
    async def start_analysis_session(self, meeting_id: str = None, transcript_id: str = None,
                                   input_data: Dict[str, Any] = None) -> AnalysisSession:
        """Start a new comprehensive analysis session"""
        try:
            session_id = str(uuid.uuid4())
            
            # Create analysis session
            session = AnalysisSession(
                id=session_id,
                meeting_id=meeting_id,
                transcript_id=transcript_id,
                input_data=input_data or {},
                tasks=[]
            )
            
            # Create tasks for each analysis dimension
            for dimension in AnalysisDimension:
                task = AnalysisTask(
                    id=f"{session_id}_{dimension.value}",
                    dimension=dimension,
                    input_data=input_data or {},
                    priority=self._determine_task_priority(dimension, input_data)
                )
                session.tasks.append(task)
                self.task_queue.append(task)
            
            self.active_sessions[session_id] = session
            self.performance_metrics['total_sessions'] += 1
            
            # Log session start event
            await ai_audit_system.log_event(
                AuditEventType.TASK_STARTED,
                AuditLevel.INFO,
                'ai_conductor',
                {
                    'session_type': 'comprehensive_analysis',
                    'tasks_created': len(session.tasks),
                    'dimensions': [dim.value for dim in AnalysisDimension],
                    'meeting_id': meeting_id,
                    'transcript_id': transcript_id
                },
                session_id=session_id
            )
            
            logger.info("Analysis session started",
                       session_id=session_id,
                       meeting_id=meeting_id,
                       transcript_id=transcript_id,
                       tasks_created=len(session.tasks))
            
            return session
            
        except Exception as e:
            logger.error("Failed to start analysis session", error=str(e))
            raise
    
    def _determine_task_priority(self, dimension: AnalysisDimension, 
                                input_data: Dict[str, Any]) -> Priority:
        """Determine task priority based on dimension and input data"""
        
        # Structural extraction is typically highest priority as other tasks depend on it
        if dimension == AnalysisDimension.STRUCTURAL_EXTRACTION:
            return Priority.CRITICAL
        
        # Human needs analysis is high priority for Oracle 9.1 Protocol
        elif dimension == AnalysisDimension.HUMAN_NEEDS_DYNAMICS:
            return Priority.HIGH
        
        # Strategic synthesis is important for organizational alignment
        elif dimension == AnalysisDimension.STRATEGIC_SYNTHESIS:
            return Priority.HIGH
        
        # Other dimensions are medium priority
        else:
            return Priority.MEDIUM
    
    async def _background_processor(self):
        """Background task processor that manages task assignment and execution"""
        while True:
            try:
                await asyncio.sleep(1)  # Process every second
                
                # Process pending tasks
                await self._process_task_queue()
                
                # Check for completed sessions
                await self._check_completed_sessions()
                
                # Update performer statistics
                await self._update_performer_stats()
                
                # Clean up old sessions
                await self._cleanup_old_sessions()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Background processor error", error=str(e))
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_task_queue(self):
        """Process pending tasks in the queue"""
        try:
            # Sort tasks by priority
            self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)
            
            # Process tasks
            tasks_to_remove = []
            
            for task in self.task_queue:
                if task.status != ProcessingStatus.PENDING:
                    tasks_to_remove.append(task)
                    continue
                
                # Find available performer
                performer = await self._find_available_performer(task.dimension)
                if performer:
                    # Assign task to performer
                    await self._assign_task_to_performer(task, performer)
                    tasks_to_remove.append(task)
            
            # Remove processed tasks from queue
            for task in tasks_to_remove:
                if task in self.task_queue:
                    self.task_queue.remove(task)
                    
        except Exception as e:
            logger.error("Task queue processing failed", error=str(e))
    
    async def _find_available_performer(self, dimension: AnalysisDimension) -> Optional[AIPerformer]:
        """Find an available performer for the given dimension"""
        try:
            for performer in self.performers.values():
                if (dimension in performer.specialties and 
                    len(performer.current_tasks) < performer.max_concurrent_tasks and
                    performer.status == "ready"):
                    return performer
            return None
            
        except Exception as e:
            logger.error("Performer search failed", error=str(e))
            return None
    
    async def _assign_task_to_performer(self, task: AnalysisTask, performer: AIPerformer):
        """Assign a task to a performer and start processing"""
        try:
            task.assigned_performer = performer.id
            task.status = ProcessingStatus.ASSIGNED
            task.start_time = datetime.utcnow()
            
            performer.current_tasks.append(task.id)
            performer.last_activity = datetime.utcnow()
            
            # Start task processing
            asyncio.create_task(self._execute_task(task, performer))
            
            logger.debug("Task assigned to performer",
                        task_id=task.id,
                        performer_id=performer.id,
                        dimension=task.dimension.value)
            
        except Exception as e:
            logger.error("Task assignment failed", error=str(e))
            task.status = ProcessingStatus.FAILED
            task.error_message = str(e)
    
    async def _execute_task(self, task: AnalysisTask, performer: AIPerformer):
        """Execute a task using the assigned performer"""
        try:
            task.status = ProcessingStatus.PROCESSING
            
            # Get the actual AI performer instance
            ai_performer = self.ai_performers.get(performer.id)
            if not ai_performer:
                raise ValueError(f"AI performer not found: {performer.id}")
            
            # Execute the task using the AI performer
            result = await ai_performer.process_task(task.id, task.input_data)
            
            # Update task with results
            task.result = result
            task.status = ProcessingStatus.COMPLETED
            task.end_time = datetime.utcnow()
            task.processing_time = (task.end_time - task.start_time).total_seconds()
            task.confidence = result.get('confidence', 0.8)
            
            # Update performer stats
            performer.current_tasks.remove(task.id)
            performer.total_tasks_completed += 1
            
            # Update session results
            await self._update_session_results(task)
            
            logger.info("Task completed successfully",
                       task_id=task.id,
                       dimension=task.dimension.value,
                       processing_time=task.processing_time,
                       confidence=task.confidence)
            
        except Exception as e:
            logger.error("Task execution failed", 
                        task_id=task.id,
                        dimension=task.dimension.value,
                        error=str(e))
            
            task.status = ProcessingStatus.FAILED
            task.error_message = str(e)
            task.end_time = datetime.utcnow()
            
            if task.id in performer.current_tasks:
                performer.current_tasks.remove(task.id)
    

    
    async def _update_session_results(self, task: AnalysisTask):
        """Update session results with completed task"""
        try:
            # Find the session this task belongs to
            session_id = task.id.split('_')[0]
            
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.results[task.dimension] = task.result
                
                # Check if all tasks are completed
                completed_tasks = sum(1 for t in session.tasks if t.status == ProcessingStatus.COMPLETED)
                total_tasks = len(session.tasks)
                
                if completed_tasks == total_tasks:
                    # Session is complete
                    session.status = ProcessingStatus.COMPLETED
                    session.end_time = datetime.utcnow()
                    
                    # Calculate overall confidence
                    confidences = [t.confidence for t in session.tasks if t.confidence > 0]
                    session.overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                    
                    logger.info("Analysis session completed",
                               session_id=session_id,
                               total_tasks=total_tasks,
                               overall_confidence=session.overall_confidence)
                    
                    self.performance_metrics['successful_sessions'] += 1
                
        except Exception as e:
            logger.error("Session results update failed", error=str(e))
    
    async def _check_completed_sessions(self):
        """Check for completed sessions and move them to completed list"""
        try:
            completed_session_ids = []
            
            for session_id, session in self.active_sessions.items():
                if session.status == ProcessingStatus.COMPLETED:
                    completed_session_ids.append(session_id)
            
            # Move completed sessions
            for session_id in completed_session_ids:
                self.completed_sessions.append(session_id)
                del self.active_sessions[session_id]
                
        except Exception as e:
            logger.error("Completed sessions check failed", error=str(e))
    
    async def _update_performer_stats(self):
        """Update performer statistics"""
        try:
            for performer in self.performers.values():
                # Update success rate and average processing time
                # This would be implemented based on task completion data
                pass
                
        except Exception as e:
            logger.error("Performer stats update failed", error=str(e))
    
    async def _cleanup_old_sessions(self):
        """Clean up old completed sessions"""
        try:
            # Keep only last 100 completed sessions
            if len(self.completed_sessions) > 100:
                self.completed_sessions = self.completed_sessions[-100:]
                
        except Exception as e:
            logger.error("Session cleanup failed", error=str(e))
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an analysis session"""
        try:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                
                return {
                    'session_id': session.id,
                    'status': session.status.value,
                    'meeting_id': session.meeting_id,
                    'transcript_id': session.transcript_id,
                    'start_time': session.start_time.isoformat(),
                    'end_time': session.end_time.isoformat() if session.end_time else None,
                    'overall_confidence': session.overall_confidence,
                    'tasks': [
                        {
                            'id': task.id,
                            'dimension': task.dimension.value,
                            'status': task.status.value,
                            'assigned_performer': task.assigned_performer,
                            'confidence': task.confidence,
                            'processing_time': task.processing_time
                        } for task in session.tasks
                    ],
                    'results_available': len(session.results)
                }
            
            return None
            
        except Exception as e:
            logger.error("Get session status failed", error=str(e))
            return None
    
    async def get_session_results(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get results of a completed analysis session"""
        try:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                
                if session.status == ProcessingStatus.COMPLETED:
                    return {
                        'session_id': session.id,
                        'overall_confidence': session.overall_confidence,
                        'results': {dim.value: result for dim, result in session.results.items()},
                        'processing_summary': {
                            'total_tasks': len(session.tasks),
                            'completed_tasks': sum(1 for t in session.tasks if t.status == ProcessingStatus.COMPLETED),
                            'failed_tasks': sum(1 for t in session.tasks if t.status == ProcessingStatus.FAILED),
                            'total_processing_time': sum(t.processing_time for t in session.tasks),
                            'average_confidence': session.overall_confidence
                        }
                    }
            
            return None
            
        except Exception as e:
            logger.error("Get session results failed", error=str(e))
            return None
    
    async def get_conductor_status(self) -> Dict[str, Any]:
        """Get overall conductor status and metrics"""
        try:
            return {
                'status': 'active',
                'active_sessions': len(self.active_sessions),
                'queued_tasks': len(self.task_queue),
                'performers': {
                    performer_id: {
                        'name': performer.name,
                        'specialties': [s.value for s in performer.specialties],
                        'current_tasks': len(performer.current_tasks),
                        'max_concurrent_tasks': performer.max_concurrent_tasks,
                        'total_completed': performer.total_tasks_completed,
                        'success_rate': performer.success_rate,
                        'status': performer.status
                    } for performer_id, performer in self.performers.items()
                },
                'performance_metrics': self.performance_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Get conductor status failed", error=str(e))
            return {'status': 'error', 'error': str(e)}

# Global AI Conductor instance
ai_conductor = AIConductor()