"""
AI Decision Audit and Transparency System for Intelligence OS
Provides comprehensive logging and audit capabilities for AI decision-making processes
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import structlog
from pathlib import Path

logger = structlog.get_logger(__name__)

class AuditEventType(Enum):
    """Types of audit events"""
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    COLLABORATION_INITIATED = "collaboration_initiated"
    COLLABORATION_COMPLETED = "collaboration_completed"
    CONFLICT_DETECTED = "conflict_detected"
    CONFLICT_RESOLVED = "conflict_resolved"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    DECISION_MADE = "decision_made"
    INSIGHT_GENERATED = "insight_generated"
    VALIDATION_PERFORMED = "validation_performed"
    SYNTHESIS_CREATED = "synthesis_created"

class AuditLevel(Enum):
    """Audit logging levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class AuditEvent:
    """Individual audit event record"""
    id: str
    event_type: AuditEventType
    level: AuditLevel
    performer_id: str
    session_id: Optional[str]
    task_id: Optional[str]
    message_id: Optional[str]
    timestamp: datetime
    event_data: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit event to dictionary for serialization"""
        return {
            'id': self.id,
            'event_type': self.event_type.value,
            'level': self.level.value,
            'performer_id': self.performer_id,
            'session_id': self.session_id,
            'task_id': self.task_id,
            'message_id': self.message_id,
            'timestamp': self.timestamp.isoformat(),
            'event_data': self.event_data,
            'context': self.context,
            'metadata': self.metadata
        }

@dataclass
class DecisionTrace:
    """Traces the decision-making process of AI performers"""
    id: str
    performer_id: str
    decision_type: str
    input_data: Dict[str, Any]
    reasoning_steps: List[Dict[str, Any]]
    final_decision: Dict[str, Any]
    confidence_score: float
    alternative_options: List[Dict[str, Any]] = field(default_factory=list)
    influencing_factors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    task_id: Optional[str] = None

class AIAuditSystem:
    """Comprehensive audit system for AI decision transparency"""
    
    def __init__(self):
        self.audit_events: List[AuditEvent] = []
        self.decision_traces: List[DecisionTrace] = []
        self.audit_storage_path = os.getenv('AUDIT_STORAGE_PATH', './audit_logs')
        self.max_memory_events = int(os.getenv('MAX_MEMORY_AUDIT_EVENTS', '10000'))
        self.audit_retention_days = int(os.getenv('AUDIT_RETENTION_DAYS', '90'))
        
        # Performance metrics
        self.metrics = {
            'total_events': 0,
            'events_by_type': {},
            'events_by_performer': {},
            'decisions_traced': 0,
            'conflicts_detected': 0,
            'collaborations_tracked': 0
        }
        
        # Ensure audit directory exists
        Path(self.audit_storage_path).mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize the audit system"""
        try:
            # Start background cleanup task
            self.cleanup_task = asyncio.create_task(self._background_cleanup())
            
            logger.info("AI Audit System initialized successfully",
                       storage_path=self.audit_storage_path,
                       max_memory_events=self.max_memory_events)
            
        except Exception as e:
            logger.error("Failed to initialize AI Audit System", error=str(e))
            raise
    
    async def log_event(self, event_type: AuditEventType, level: AuditLevel,
                       performer_id: str, event_data: Dict[str, Any],
                       session_id: str = None, task_id: str = None,
                       message_id: str = None, context: Dict[str, Any] = None,
                       metadata: Dict[str, Any] = None) -> str:
        """Log an audit event"""
        try:
            event_id = str(uuid.uuid4())
            
            event = AuditEvent(
                id=event_id,
                event_type=event_type,
                level=level,
                performer_id=performer_id,
                session_id=session_id,
                task_id=task_id,
                message_id=message_id,
                timestamp=datetime.utcnow(),
                event_data=event_data,
                context=context or {},
                metadata=metadata or {}
            )
            
            # Add to memory storage
            self.audit_events.append(event)
            
            # Update metrics
            self.metrics['total_events'] += 1
            
            event_type_str = event_type.value
            if event_type_str not in self.metrics['events_by_type']:
                self.metrics['events_by_type'][event_type_str] = 0
            self.metrics['events_by_type'][event_type_str] += 1
            
            if performer_id not in self.metrics['events_by_performer']:
                self.metrics['events_by_performer'][performer_id] = 0
            self.metrics['events_by_performer'][performer_id] += 1
            
            # Persist to storage if critical or error
            if level in [AuditLevel.ERROR, AuditLevel.CRITICAL]:
                await self._persist_event(event)
            
            # Log to structured logger
            logger.log(
                level.value,
                f"AI Audit: {event_type.value}",
                event_id=event_id,
                performer_id=performer_id,
                session_id=session_id,
                task_id=task_id,
                event_data=event_data
            )
            
            return event_id
            
        except Exception as e:
            logger.error("Failed to log audit event", error=str(e))
            return ""
    
    async def trace_decision(self, performer_id: str, decision_type: str,
                           input_data: Dict[str, Any], reasoning_steps: List[Dict[str, Any]],
                           final_decision: Dict[str, Any], confidence_score: float,
                           alternative_options: List[Dict[str, Any]] = None,
                           influencing_factors: List[str] = None,
                           session_id: str = None, task_id: str = None) -> str:
        """Trace a decision-making process"""
        try:
            trace_id = str(uuid.uuid4())
            
            decision_trace = DecisionTrace(
                id=trace_id,
                performer_id=performer_id,
                decision_type=decision_type,
                input_data=input_data,
                reasoning_steps=reasoning_steps,
                final_decision=final_decision,
                confidence_score=confidence_score,
                alternative_options=alternative_options or [],
                influencing_factors=influencing_factors or [],
                session_id=session_id,
                task_id=task_id
            )
            
            self.decision_traces.append(decision_trace)
            self.metrics['decisions_traced'] += 1
            
            # Log the decision event
            await self.log_event(
                AuditEventType.DECISION_MADE,
                AuditLevel.INFO,
                performer_id,
                {
                    'decision_type': decision_type,
                    'confidence_score': confidence_score,
                    'alternatives_considered': len(alternative_options or []),
                    'reasoning_steps': len(reasoning_steps)
                },
                session_id=session_id,
                task_id=task_id,
                context={'trace_id': trace_id}
            )
            
            return trace_id
            
        except Exception as e:
            logger.error("Failed to trace decision", error=str(e))
            return ""
    
    async def log_collaboration_event(self, event_type: AuditEventType,
                                    initiator_id: str, participants: List[str],
                                    session_id: str, event_data: Dict[str, Any]):
        """Log collaboration-related events"""
        try:
            await self.log_event(
                event_type,
                AuditLevel.INFO,
                initiator_id,
                {
                    'participants': participants,
                    'participant_count': len(participants),
                    **event_data
                },
                session_id=session_id,
                context={'collaboration': True}
            )
            
            if event_type == AuditEventType.COLLABORATION_INITIATED:
                self.metrics['collaborations_tracked'] += 1
            
        except Exception as e:
            logger.error("Failed to log collaboration event", error=str(e))
    
    async def log_conflict_event(self, conflict_type: str, involved_performers: List[str],
                               session_id: str, conflict_data: Dict[str, Any],
                               resolution: Dict[str, Any] = None):
        """Log conflict detection and resolution events"""
        try:
            # Log conflict detection
            await self.log_event(
                AuditEventType.CONFLICT_DETECTED,
                AuditLevel.WARNING,
                'system',
                {
                    'conflict_type': conflict_type,
                    'involved_performers': involved_performers,
                    'conflict_data': conflict_data
                },
                session_id=session_id,
                context={'conflict': True}
            )
            
            self.metrics['conflicts_detected'] += 1
            
            # Log resolution if provided
            if resolution:
                await self.log_event(
                    AuditEventType.CONFLICT_RESOLVED,
                    AuditLevel.INFO,
                    'system',
                    {
                        'conflict_type': conflict_type,
                        'resolution': resolution,
                        'involved_performers': involved_performers
                    },
                    session_id=session_id,
                    context={'conflict_resolution': True}
                )
            
        except Exception as e:
            logger.error("Failed to log conflict event", error=str(e))
    
    async def get_audit_trail(self, session_id: str = None, performer_id: str = None,
                            event_type: AuditEventType = None,
                            start_time: datetime = None, end_time: datetime = None,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit trail with filtering options"""
        try:
            filtered_events = self.audit_events.copy()
            
            # Apply filters
            if session_id:
                filtered_events = [e for e in filtered_events if e.session_id == session_id]
            
            if performer_id:
                filtered_events = [e for e in filtered_events if e.performer_id == performer_id]
            
            if event_type:
                filtered_events = [e for e in filtered_events if e.event_type == event_type]
            
            if start_time:
                filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
            
            if end_time:
                filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
            
            # Sort by timestamp (most recent first)
            filtered_events.sort(key=lambda e: e.timestamp, reverse=True)
            
            # Apply limit
            filtered_events = filtered_events[:limit]
            
            return [event.to_dict() for event in filtered_events]
            
        except Exception as e:
            logger.error("Failed to get audit trail", error=str(e))
            return []
    
    async def get_decision_trace(self, trace_id: str = None, performer_id: str = None,
                               session_id: str = None, task_id: str = None) -> List[Dict[str, Any]]:
        """Get decision traces with filtering options"""
        try:
            filtered_traces = self.decision_traces.copy()
            
            # Apply filters
            if trace_id:
                filtered_traces = [t for t in filtered_traces if t.id == trace_id]
            
            if performer_id:
                filtered_traces = [t for t in filtered_traces if t.performer_id == performer_id]
            
            if session_id:
                filtered_traces = [t for t in filtered_traces if t.session_id == session_id]
            
            if task_id:
                filtered_traces = [t for t in filtered_traces if t.task_id == task_id]
            
            # Sort by timestamp (most recent first)
            filtered_traces.sort(key=lambda t: t.timestamp, reverse=True)
            
            return [
                {
                    'id': trace.id,
                    'performer_id': trace.performer_id,
                    'decision_type': trace.decision_type,
                    'input_data': trace.input_data,
                    'reasoning_steps': trace.reasoning_steps,
                    'final_decision': trace.final_decision,
                    'confidence_score': trace.confidence_score,
                    'alternative_options': trace.alternative_options,
                    'influencing_factors': trace.influencing_factors,
                    'timestamp': trace.timestamp.isoformat(),
                    'session_id': trace.session_id,
                    'task_id': trace.task_id
                }
                for trace in filtered_traces
            ]
            
        except Exception as e:
            logger.error("Failed to get decision traces", error=str(e))
            return []
    
    async def generate_transparency_report(self, session_id: str) -> Dict[str, Any]:
        """Generate a comprehensive transparency report for a session"""
        try:
            # Get all events for the session
            session_events = await self.get_audit_trail(session_id=session_id, limit=1000)
            
            # Get all decision traces for the session
            session_decisions = await self.get_decision_trace(session_id=session_id)
            
            # Analyze the session
            performers_involved = list(set(event['performer_id'] for event in session_events))
            event_types = {}
            for event in session_events:
                event_type = event['event_type']
                if event_type not in event_types:
                    event_types[event_type] = 0
                event_types[event_type] += 1
            
            # Calculate metrics
            total_decisions = len(session_decisions)
            avg_confidence = sum(d['confidence_score'] for d in session_decisions) / total_decisions if total_decisions > 0 else 0
            
            conflicts = [e for e in session_events if e['event_type'] == 'conflict_detected']
            collaborations = [e for e in session_events if e['event_type'] == 'collaboration_initiated']
            
            return {
                'session_id': session_id,
                'report_generated_at': datetime.utcnow().isoformat(),
                'summary': {
                    'total_events': len(session_events),
                    'performers_involved': len(performers_involved),
                    'decisions_made': total_decisions,
                    'average_confidence': avg_confidence,
                    'conflicts_detected': len(conflicts),
                    'collaborations_initiated': len(collaborations)
                },
                'performers': performers_involved,
                'event_breakdown': event_types,
                'timeline': session_events[:50],  # Last 50 events
                'key_decisions': session_decisions[:10],  # Top 10 decisions
                'conflicts': conflicts,
                'collaborations': collaborations,
                'transparency_score': self._calculate_transparency_score(session_events, session_decisions)
            }
            
        except Exception as e:
            logger.error("Failed to generate transparency report", error=str(e))
            return {'error': str(e)}
    
    def _calculate_transparency_score(self, events: List[Dict[str, Any]], 
                                    decisions: List[Dict[str, Any]]) -> float:
        """Calculate a transparency score based on audit completeness"""
        try:
            score = 0.0
            
            # Base score for having events
            if events:
                score += 0.3
            
            # Score for decision tracing
            if decisions:
                score += 0.3
                
                # Bonus for detailed reasoning
                detailed_decisions = sum(1 for d in decisions if len(d.get('reasoning_steps', [])) > 0)
                if detailed_decisions > 0:
                    score += 0.2 * (detailed_decisions / len(decisions))
            
            # Score for collaboration transparency
            collaboration_events = [e for e in events if 'collaboration' in e.get('context', {})]
            if collaboration_events:
                score += 0.1
            
            # Score for conflict transparency
            conflict_events = [e for e in events if 'conflict' in e.get('context', {})]
            if conflict_events:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error("Failed to calculate transparency score", error=str(e))
            return 0.0
    
    async def _persist_event(self, event: AuditEvent):
        """Persist an audit event to storage"""
        try:
            # Create daily log file
            date_str = event.timestamp.strftime('%Y-%m-%d')
            log_file = Path(self.audit_storage_path) / f"audit_{date_str}.jsonl"
            
            # Append event to file
            with open(log_file, 'a') as f:
                f.write(json.dumps(event.to_dict()) + '\n')
                
        except Exception as e:
            logger.error("Failed to persist audit event", error=str(e))
    
    async def _background_cleanup(self):
        """Background task for cleaning up old audit data"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Clean up memory storage
                if len(self.audit_events) > self.max_memory_events:
                    # Keep only the most recent events
                    self.audit_events = self.audit_events[-self.max_memory_events:]
                
                # Clean up old decision traces
                cutoff_time = datetime.utcnow() - timedelta(days=self.audit_retention_days)
                self.decision_traces = [
                    trace for trace in self.decision_traces
                    if trace.timestamp > cutoff_time
                ]
                
                # Clean up old log files
                await self._cleanup_old_log_files()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Audit cleanup failed", error=str(e))
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def _cleanup_old_log_files(self):
        """Clean up old audit log files"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.audit_retention_days)
            audit_dir = Path(self.audit_storage_path)
            
            for log_file in audit_dir.glob("audit_*.jsonl"):
                try:
                    # Extract date from filename
                    date_str = log_file.stem.replace('audit_', '')
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    if file_date < cutoff_date:
                        log_file.unlink()
                        logger.info("Deleted old audit log file", file=str(log_file))
                        
                except Exception as e:
                    logger.warning("Failed to process audit log file", file=str(log_file), error=str(e))
                    
        except Exception as e:
            logger.error("Failed to cleanup old log files", error=str(e))
    
    async def get_audit_metrics(self) -> Dict[str, Any]:
        """Get audit system metrics"""
        try:
            return {
                'metrics': self.metrics,
                'memory_usage': {
                    'audit_events': len(self.audit_events),
                    'decision_traces': len(self.decision_traces),
                    'max_memory_events': self.max_memory_events
                },
                'configuration': {
                    'storage_path': self.audit_storage_path,
                    'retention_days': self.audit_retention_days
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to get audit metrics", error=str(e))
            return {'error': str(e)}

# Global audit system instance
ai_audit_system = AIAuditSystem()