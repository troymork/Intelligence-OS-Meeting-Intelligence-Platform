"""
State Synchronization Service
Ensures consistency between real-time and comprehensive processing results
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog
from collections import defaultdict
import json
import threading
import time
from deepdiff import DeepDiff
import numpy as np

logger = structlog.get_logger(__name__)

class SyncStrategy(Enum):
    """Strategies for synchronizing results"""
    MERGE_WEIGHTED = "merge_weighted"
    COMPREHENSIVE_PRIORITY = "comprehensive_priority"
    REAL_TIME_PRIORITY = "real_time_priority"
    CONFIDENCE_BASED = "confidence_based"
    TEMPORAL_PRIORITY = "temporal_priority"

class ConflictResolution(Enum):
    """Methods for resolving conflicts between results"""
    HIGHEST_CONFIDENCE = "highest_confidence"
    MOST_RECENT = "most_recent"
    COMPREHENSIVE_WINS = "comprehensive_wins"
    MANUAL_REVIEW = "manual_review"
    WEIGHTED_AVERAGE = "weighted_average"

class SyncStatus(Enum):
    """Status of synchronization process"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SYNCHRONIZED = "synchronized"
    CONFLICT_DETECTED = "conflict_detected"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class SyncConflict:
    """Represents a conflict between pipeline results"""
    id: str
    field_path: str
    real_time_value: Any
    comprehensive_value: Any
    conflict_type: str  # value_mismatch, type_mismatch, missing_field
    severity: str  # low, medium, high, critical
    resolution_strategy: ConflictResolution
    resolved_value: Optional[Any] = None
    resolution_confidence: float = 0.0
    manual_review_required: bool = False

@dataclass
class SyncResult:
    """Result of synchronization process"""
    sync_id: str
    status: SyncStatus
    merged_result: Optional[Dict[str, Any]]
    conflicts: List[SyncConflict]
    consistency_score: float
    sync_confidence: float
    processing_time: float
    real_time_weight: float
    comprehensive_weight: float
    metadata: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SyncConfiguration:
    """Configuration for synchronization process"""
    sync_strategy: SyncStrategy
    conflict_resolution: ConflictResolution
    confidence_threshold: float
    max_sync_time_seconds: int
    field_weights: Dict[str, float]
    critical_fields: List[str]
    ignore_fields: List[str]
    auto_resolve_conflicts: bool

class StateSynchronizationService:
    """Service for synchronizing state between processing pipelines"""
    
    def __init__(self):
        self.sync_sessions = {}  # sync_id -> SyncResult
        self.sync_configurations = self._initialize_sync_configurations()
        self.field_comparators = self._initialize_field_comparators()
        self.conflict_resolvers = self._initialize_conflict_resolvers()
        
        # Synchronization metrics
        self.sync_metrics = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'conflicts_detected': 0,
            'conflicts_resolved': 0,
            'average_consistency_score': 0.0,
            'average_sync_time': 0.0
        }
        
        # Configuration
        self.config = {
            'default_sync_timeout': 300,  # 5 minutes
            'consistency_threshold': 0.8,
            'conflict_severity_threshold': 0.7,
            'auto_resolve_threshold': 0.9,
            'max_concurrent_syncs': 50
        }
    
    def _initialize_sync_configurations(self) -> Dict[str, SyncConfiguration]:
        """Initialize synchronization configurations for different data types"""
        return {
            'transcript_analysis': SyncConfiguration(
                sync_strategy=SyncStrategy.CONFIDENCE_BASED,
                conflict_resolution=ConflictResolution.HIGHEST_CONFIDENCE,
                confidence_threshold=0.7,
                max_sync_time_seconds=60,
                field_weights={
                    'summary': 0.9,
                    'key_points': 0.8,
                    'sentiment': 0.7,
                    'topics': 0.8,
                    'confidence': 1.0
                },
                critical_fields=['summary', 'confidence'],
                ignore_fields=['processing_time', 'pipeline'],
                auto_resolve_conflicts=True
            ),
            'pattern_recognition': SyncConfiguration(
                sync_strategy=SyncStrategy.COMPREHENSIVE_PRIORITY,
                conflict_resolution=ConflictResolution.COMPREHENSIVE_WINS,
                confidence_threshold=0.8,
                max_sync_time_seconds=120,
                field_weights={
                    'patterns_detected': 0.9,
                    'pattern_details': 1.0,
                    'confidence': 1.0
                },
                critical_fields=['patterns_detected', 'confidence'],
                ignore_fields=['processing_time'],
                auto_resolve_conflicts=True
            ),
            'oracle_generation': SyncConfiguration(
                sync_strategy=SyncStrategy.MERGE_WEIGHTED,
                conflict_resolution=ConflictResolution.WEIGHTED_AVERAGE,
                confidence_threshold=0.75,
                max_sync_time_seconds=180,
                field_weights={
                    'decisions': 1.0,
                    'actions': 1.0,
                    'insights': 0.8,
                    'confidence': 1.0
                },
                critical_fields=['decisions', 'actions', 'confidence'],
                ignore_fields=['processing_time'],
                auto_resolve_conflicts=False
            ),
            'knowledge_graph': SyncConfiguration(
                sync_strategy=SyncStrategy.COMPREHENSIVE_PRIORITY,
                conflict_resolution=ConflictResolution.COMPREHENSIVE_WINS,
                confidence_threshold=0.8,
                max_sync_time_seconds=150,
                field_weights={
                    'concepts_identified': 0.9,
                    'relationships_mapped': 1.0,
                    'confidence': 1.0
                },
                critical_fields=['concepts_identified', 'relationships_mapped'],
                ignore_fields=['processing_time'],
                auto_resolve_conflicts=True
            ),
            'predictive_analytics': SyncConfiguration(
                sync_strategy=SyncStrategy.CONFIDENCE_BASED,
                conflict_resolution=ConflictResolution.HIGHEST_CONFIDENCE,
                confidence_threshold=0.85,
                max_sync_time_seconds=200,
                field_weights={
                    'forecast': 1.0,
                    'probability': 0.9,
                    'confidence': 1.0
                },
                critical_fields=['forecast', 'confidence'],
                ignore_fields=['processing_time'],
                auto_resolve_conflicts=True
            ),
            'intervention_analysis': SyncConfiguration(
                sync_strategy=SyncStrategy.MERGE_WEIGHTED,
                conflict_resolution=ConflictResolution.WEIGHTED_AVERAGE,
                confidence_threshold=0.75,
                max_sync_time_seconds=120,
                field_weights={
                    'recommendations': 1.0,
                    'implementation_plans': 0.9,
                    'confidence': 1.0
                },
                critical_fields=['recommendations', 'confidence'],
                ignore_fields=['processing_time'],
                auto_resolve_conflicts=True
            )
        }
    
    def _initialize_field_comparators(self) -> Dict[str, callable]:
        """Initialize field comparison functions"""
        return {
            'numeric': self._compare_numeric_fields,
            'string': self._compare_string_fields,
            'list': self._compare_list_fields,
            'dict': self._compare_dict_fields,
            'confidence': self._compare_confidence_fields
        }
    
    def _initialize_conflict_resolvers(self) -> Dict[ConflictResolution, callable]:
        """Initialize conflict resolution functions"""
        return {
            ConflictResolution.HIGHEST_CONFIDENCE: self._resolve_by_confidence,
            ConflictResolution.MOST_RECENT: self._resolve_by_recency,
            ConflictResolution.COMPREHENSIVE_WINS: self._resolve_comprehensive_priority,
            ConflictResolution.WEIGHTED_AVERAGE: self._resolve_by_weighted_average,
            ConflictResolution.MANUAL_REVIEW: self._resolve_manual_review
        }
    
    async def synchronize_results(self, 
                                real_time_result: Dict[str, Any],
                                comprehensive_result: Dict[str, Any],
                                data_type: str,
                                sync_id: Optional[str] = None) -> SyncResult:
        """Synchronize results from real-time and comprehensive pipelines"""
        try:
            if not sync_id:
                sync_id = str(uuid.uuid4())
            
            start_time = time.time()
            
            logger.info("Starting result synchronization",
                       sync_id=sync_id,
                       data_type=data_type)
            
            # Get synchronization configuration
            sync_config = self.sync_configurations.get(
                data_type, 
                self.sync_configurations['transcript_analysis']  # Default
            )
            
            # Detect conflicts
            conflicts = await self._detect_conflicts(
                real_time_result, 
                comprehensive_result, 
                sync_config
            )
            
            # Resolve conflicts
            resolved_conflicts = []
            for conflict in conflicts:
                resolved_conflict = await self._resolve_conflict(conflict, sync_config)
                resolved_conflicts.append(resolved_conflict)
            
            # Merge results
            merged_result = await self._merge_results(
                real_time_result,
                comprehensive_result,
                resolved_conflicts,
                sync_config
            )
            
            # Calculate metrics
            consistency_score = self._calculate_consistency_score(
                real_time_result, 
                comprehensive_result, 
                conflicts
            )
            
            sync_confidence = self._calculate_sync_confidence(
                merged_result, 
                resolved_conflicts, 
                consistency_score
            )
            
            # Determine weights
            rt_weight, comp_weight = self._calculate_pipeline_weights(
                real_time_result, 
                comprehensive_result, 
                sync_config
            )
            
            # Create sync result
            sync_result = SyncResult(
                sync_id=sync_id,
                status=SyncStatus.SYNCHRONIZED if len([c for c in resolved_conflicts if not c.resolved_value]) == 0 else SyncStatus.CONFLICT_DETECTED,
                merged_result=merged_result,
                conflicts=resolved_conflicts,
                consistency_score=consistency_score,
                sync_confidence=sync_confidence,
                processing_time=time.time() - start_time,
                real_time_weight=rt_weight,
                comprehensive_weight=comp_weight,
                metadata={
                    'data_type': data_type,
                    'sync_strategy': sync_config.sync_strategy.value,
                    'conflict_resolution': sync_config.conflict_resolution.value,
                    'auto_resolved_conflicts': len([c for c in resolved_conflicts if c.resolved_value is not None])
                }
            )
            
            # Store sync result
            self.sync_sessions[sync_id] = sync_result
            
            # Update metrics
            self._update_sync_metrics(sync_result)
            
            logger.info("Result synchronization completed",
                       sync_id=sync_id,
                       consistency_score=consistency_score,
                       conflicts_count=len(conflicts),
                       processing_time=sync_result.processing_time)
            
            return sync_result
            
        except Exception as e:
            logger.error("Result synchronization failed", 
                        sync_id=sync_id, 
                        error=str(e))
            
            # Return failed sync result
            return SyncResult(
                sync_id=sync_id or str(uuid.uuid4()),
                status=SyncStatus.FAILED,
                merged_result=None,
                conflicts=[],
                consistency_score=0.0,
                sync_confidence=0.0,
                processing_time=time.time() - start_time if 'start_time' in locals() else 0.0,
                real_time_weight=0.5,
                comprehensive_weight=0.5,
                metadata={'error': str(e)}
            )
    
    async def _detect_conflicts(self, 
                              real_time_result: Dict[str, Any],
                              comprehensive_result: Dict[str, Any],
                              sync_config: SyncConfiguration) -> List[SyncConflict]:
        """Detect conflicts between pipeline results"""
        try:
            conflicts = []
            
            # Use DeepDiff to find differences
            diff = DeepDiff(
                real_time_result, 
                comprehensive_result,
                ignore_order=True,
                exclude_paths=sync_config.ignore_fields
            )
            
            # Process different types of differences
            if 'values_changed' in diff:
                for path, change in diff['values_changed'].items():
                    conflict = self._create_value_conflict(
                        path, 
                        change['old_value'], 
                        change['new_value'],
                        sync_config
                    )
                    conflicts.append(conflict)
            
            if 'type_changes' in diff:
                for path, change in diff['type_changes'].items():
                    conflict = self._create_type_conflict(
                        path,
                        change['old_value'],
                        change['new_value'],
                        sync_config
                    )
                    conflicts.append(conflict)
            
            if 'dictionary_item_added' in diff:
                for path in diff['dictionary_item_added']:
                    conflict = self._create_missing_field_conflict(
                        path,
                        'comprehensive_only',
                        comprehensive_result,
                        sync_config
                    )
                    conflicts.append(conflict)
            
            if 'dictionary_item_removed' in diff:
                for path in diff['dictionary_item_removed']:
                    conflict = self._create_missing_field_conflict(
                        path,
                        'real_time_only',
                        real_time_result,
                        sync_config
                    )
                    conflicts.append(conflict)
            
            return conflicts
            
        except Exception as e:
            logger.error("Conflict detection failed", error=str(e))
            return []
    
    def _create_value_conflict(self, 
                             path: str, 
                             rt_value: Any, 
                             comp_value: Any,
                             sync_config: SyncConfiguration) -> SyncConflict:
        """Create a value mismatch conflict"""
        field_name = path.split('.')[-1] if '.' in path else path
        
        # Determine severity
        severity = 'high' if field_name in sync_config.critical_fields else 'medium'
        
        # Determine resolution strategy
        resolution_strategy = sync_config.conflict_resolution
        
        return SyncConflict(
            id=str(uuid.uuid4()),
            field_path=path,
            real_time_value=rt_value,
            comprehensive_value=comp_value,
            conflict_type='value_mismatch',
            severity=severity,
            resolution_strategy=resolution_strategy,
            manual_review_required=(severity == 'high' and not sync_config.auto_resolve_conflicts)
        )
    
    def _create_type_conflict(self,
                            path: str,
                            rt_value: Any,
                            comp_value: Any,
                            sync_config: SyncConfiguration) -> SyncConflict:
        """Create a type mismatch conflict"""
        field_name = path.split('.')[-1] if '.' in path else path
        severity = 'critical' if field_name in sync_config.critical_fields else 'high'
        
        return SyncConflict(
            id=str(uuid.uuid4()),
            field_path=path,
            real_time_value=rt_value,
            comprehensive_value=comp_value,
            conflict_type='type_mismatch',
            severity=severity,
            resolution_strategy=sync_config.conflict_resolution,
            manual_review_required=True  # Type conflicts usually need manual review
        )
    
    def _create_missing_field_conflict(self,
                                     path: str,
                                     missing_in: str,
                                     available_result: Dict[str, Any],
                                     sync_config: SyncConfiguration) -> SyncConflict:
        """Create a missing field conflict"""
        field_name = path.split('.')[-1] if '.' in path else path
        severity = 'high' if field_name in sync_config.critical_fields else 'low'
        
        return SyncConflict(
            id=str(uuid.uuid4()),
            field_path=path,
            real_time_value=None if missing_in == 'real_time_only' else available_result.get(field_name),
            comprehensive_value=None if missing_in == 'comprehensive_only' else available_result.get(field_name),
            conflict_type='missing_field',
            severity=severity,
            resolution_strategy=sync_config.conflict_resolution,
            manual_review_required=(severity == 'high')
        )
    
    async def _resolve_conflict(self, 
                              conflict: SyncConflict, 
                              sync_config: SyncConfiguration) -> SyncConflict:
        """Resolve a single conflict"""
        try:
            if conflict.manual_review_required and not sync_config.auto_resolve_conflicts:
                # Mark for manual review
                conflict.resolved_value = None
                conflict.resolution_confidence = 0.0
                return conflict
            
            # Get resolver function
            resolver = self.conflict_resolvers.get(conflict.resolution_strategy)
            if not resolver:
                logger.warning("No resolver found for strategy", 
                             strategy=conflict.resolution_strategy.value)
                return conflict
            
            # Resolve conflict
            resolved_value, confidence = resolver(conflict, sync_config)
            
            conflict.resolved_value = resolved_value
            conflict.resolution_confidence = confidence
            
            return conflict
            
        except Exception as e:
            logger.error("Conflict resolution failed", 
                        conflict_id=conflict.id, 
                        error=str(e))
            return conflict
    
    def _resolve_by_confidence(self, 
                             conflict: SyncConflict, 
                             sync_config: SyncConfiguration) -> Tuple[Any, float]:
        """Resolve conflict by choosing value with higher confidence"""
        # This is a simplified implementation
        # In practice, you'd extract confidence from the actual results
        rt_confidence = 0.7  # Default real-time confidence
        comp_confidence = 0.9  # Default comprehensive confidence
        
        if comp_confidence > rt_confidence:
            return conflict.comprehensive_value, comp_confidence
        else:
            return conflict.real_time_value, rt_confidence
    
    def _resolve_by_recency(self, 
                          conflict: SyncConflict, 
                          sync_config: SyncConfiguration) -> Tuple[Any, float]:
        """Resolve conflict by choosing most recent value"""
        # Comprehensive results are typically more recent
        return conflict.comprehensive_value, 0.8
    
    def _resolve_comprehensive_priority(self, 
                                      conflict: SyncConflict, 
                                      sync_config: SyncConfiguration) -> Tuple[Any, float]:
        """Resolve conflict by prioritizing comprehensive result"""
        return conflict.comprehensive_value, 0.9
    
    def _resolve_by_weighted_average(self, 
                                   conflict: SyncConflict, 
                                   sync_config: SyncConfiguration) -> Tuple[Any, float]:
        """Resolve conflict by weighted average (for numeric values)"""
        try:
            rt_val = conflict.real_time_value
            comp_val = conflict.comprehensive_value
            
            # Check if both values are numeric
            if isinstance(rt_val, (int, float)) and isinstance(comp_val, (int, float)):
                # Use 30% real-time, 70% comprehensive weighting
                weighted_avg = rt_val * 0.3 + comp_val * 0.7
                return weighted_avg, 0.8
            else:
                # Fall back to comprehensive priority for non-numeric values
                return comp_val, 0.7
                
        except Exception as e:
            logger.error("Weighted average resolution failed", error=str(e))
            return conflict.comprehensive_value, 0.5
    
    def _resolve_manual_review(self, 
                             conflict: SyncConflict, 
                             sync_config: SyncConfiguration) -> Tuple[Any, float]:
        """Mark conflict for manual review"""
        return None, 0.0
    
    async def _merge_results(self, 
                           real_time_result: Dict[str, Any],
                           comprehensive_result: Dict[str, Any],
                           resolved_conflicts: List[SyncConflict],
                           sync_config: SyncConfiguration) -> Dict[str, Any]:
        """Merge results using resolved conflicts"""
        try:
            # Start with comprehensive result as base
            merged_result = comprehensive_result.copy()
            
            # Apply conflict resolutions
            for conflict in resolved_conflicts:
                if conflict.resolved_value is not None:
                    # Apply resolved value
                    self._set_nested_value(merged_result, conflict.field_path, conflict.resolved_value)
            
            # Add metadata about synchronization
            merged_result['_sync_metadata'] = {
                'sync_strategy': sync_config.sync_strategy.value,
                'conflicts_resolved': len([c for c in resolved_conflicts if c.resolved_value is not None]),
                'manual_review_required': len([c for c in resolved_conflicts if c.manual_review_required]),
                'sync_timestamp': datetime.utcnow().isoformat()
            }
            
            return merged_result
            
        except Exception as e:
            logger.error("Result merging failed", error=str(e))
            return comprehensive_result  # Fall back to comprehensive result
    
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any):
        """Set value in nested dictionary using dot notation path"""
        try:
            keys = path.replace("root['", "").replace("']", "").split("']['")
            current = data
            
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            current[keys[-1]] = value
            
        except Exception as e:
            logger.error("Setting nested value failed", path=path, error=str(e))
    
    def _calculate_consistency_score(self, 
                                   real_time_result: Dict[str, Any],
                                   comprehensive_result: Dict[str, Any],
                                   conflicts: List[SyncConflict]) -> float:
        """Calculate consistency score between results"""
        try:
            if not conflicts:
                return 1.0
            
            # Count total fields
            total_fields = len(self._flatten_dict(real_time_result))
            
            # Weight conflicts by severity
            severity_weights = {'low': 0.1, 'medium': 0.3, 'high': 0.7, 'critical': 1.0}
            
            total_conflict_weight = sum(
                severity_weights.get(conflict.severity, 0.5) 
                for conflict in conflicts
            )
            
            # Calculate consistency score
            consistency_score = max(0.0, 1.0 - (total_conflict_weight / total_fields))
            
            return consistency_score
            
        except Exception as e:
            logger.error("Consistency score calculation failed", error=str(e))
            return 0.5
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def get_sync_metrics(self) -> Dict[str, Any]:
        """Get synchronization metrics"""
        return {
            **self.sync_metrics,
            'active_sync_sessions': len(self.sync_sessions),
            'last_updated': datetime.utcnow().isoformat()
        }

# Global service instance
state_sync_service = StateSynchronizationService()