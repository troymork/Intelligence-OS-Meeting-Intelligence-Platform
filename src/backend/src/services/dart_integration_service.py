"""
Dart Action Management Integration Service
Handles action item generation, synchronization, tracking, and dependency mapping
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog
import aiohttp
import json
from urllib.parse import urljoin
import hashlib

logger = structlog.get_logger(__name__)

class ActionPriority(Enum):
    """Action priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ActionStatus(Enum):
    """Action status types"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class DependencyType(Enum):
    """Action dependency types"""
    BLOCKS = "blocks"
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
    SUBTASK_OF = "subtask_of"

@dataclass
class ActionItem:
    """Represents an action item"""
    id: Optional[str] = None
    title: str = ""
    description: str = ""
    assignee: Optional[str] = None
    priority: ActionPriority = ActionPriority.MEDIUM
    status: ActionStatus = ActionStatus.NOT_STARTED
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    project_id: Optional[str] = None
    meeting_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    dart_id: Optional[str] = None  # ID in Dart system
    exponential_potential: Optional[float] = None
    velocity_estimate: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ActionDependency:
    """Represents a dependency between actions"""
    source_action_id: str
    target_action_id: str
    dependency_type: DependencyType
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ProjectTag:
    """Represents a project tag for categorization"""
    name: str
    color: Optional[str] = None
    description: Optional[str] = None
    auto_assigned: bool = False

class DartIntegrationService:
    """Service for integrating with Dart Action Management system"""
    
    def __init__(self, dart_api_url: str, api_key: str):
        self.dart_api_url = dart_api_url.rstrip('/')
        self.api_key = api_key
        self.session = None
        
        # Configuration
        self.config = {
            'timeout_seconds': 30,
            'retry_attempts': 3,
            'retry_delay_seconds': 1,
            'batch_size': 50,
            'sync_interval_minutes': 15,
            'auto_tag_enabled': True,
            'dependency_analysis_enabled': True
        }
        
        # Action tracking
        self.action_cache = {}  # local_id -> ActionItem
        self.dart_id_mapping = {}  # dart_id -> local_id
        self.pending_sync = set()  # Set of action IDs pending sync
        
        # Project tags for auto-assignment
        self.project_tags = self._initialize_project_tags()
        
        # Dependency tracking
        self.dependencies = {}  # action_id -> List[ActionDependency]
        
        # Start background sync
        self._start_background_sync()
    
    def _initialize_project_tags(self) -> List[ProjectTag]:
        """Initialize project tags for auto-assignment"""
        return [
            ProjectTag("strategic", "#FF6B6B", "Strategic initiatives and high-level planning", True),
            ProjectTag("technical", "#4ECDC4", "Technical implementation and development", True),
            ProjectTag("research", "#45B7D1", "Research and analysis tasks", True),
            ProjectTag("communication", "#96CEB4", "Communication and coordination tasks", True),
            ProjectTag("urgent", "#FFEAA7", "Urgent tasks requiring immediate attention", True),
            ProjectTag("meeting-follow-up", "#DDA0DD", "Follow-up actions from meetings", True),
            ProjectTag("decision-implementation", "#FFB347", "Tasks to implement decisions", True),
            ProjectTag("process-improvement", "#98D8C8", "Process optimization and improvement", True),
            ProjectTag("stakeholder-engagement", "#F7DC6F", "Stakeholder communication and engagement", True),
            ProjectTag("documentation", "#AED6F1", "Documentation and knowledge management", True)
        ]
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'Intelligence-OS-Platform/1.0'
            }
            timeout = aiohttp.ClientTimeout(total=self.config['timeout_seconds'])
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self.session
    
    async def generate_actions_from_meeting(self, 
                                          meeting_data: Dict[str, Any],
                                          oracle_analysis: Dict[str, Any]) -> List[ActionItem]:
        """Generate action items from meeting data and Oracle analysis"""
        try:
            actions = []
            
            # Extract actions from Oracle analysis
            if 'action_register' in oracle_analysis:
                for action_data in oracle_analysis['action_register'].get('actions', []):
                    action = await self._create_action_from_oracle_data(action_data, meeting_data)
                    actions.append(action)
            
            # Extract actions from decisions
            if 'decisions_agreements' in oracle_analysis:
                for decision in oracle_analysis['decisions_agreements'].get('decisions', []):
                    if 'implementation_plan' in decision:
                        for step in decision['implementation_plan'].get('steps', []):
                            action = await self._create_action_from_decision_step(step, decision, meeting_data)
                            actions.append(action)
            
            # Extract actions from strategic implications
            if 'strategic_implications' in oracle_analysis:
                for implication in oracle_analysis['strategic_implications'].get('action_plans', []):
                    action = await self._create_action_from_strategic_plan(implication, meeting_data)
                    actions.append(action)
            
            # Auto-assign tags and priorities
            for action in actions:
                await self._auto_assign_tags_and_priority(action, meeting_data, oracle_analysis)
            
            # Store actions in cache
            for action in actions:
                action.id = self._generate_action_id()
                self.action_cache[action.id] = action
                self.pending_sync.add(action.id)
            
            logger.info("Generated actions from meeting",
                       meeting_id=meeting_data.get('id'),
                       action_count=len(actions))
            
            return actions
            
        except Exception as e:
            logger.error("Failed to generate actions from meeting", 
                        meeting_id=meeting_data.get('id'),
                        error=str(e))
            return []
    
    async def _create_action_from_oracle_data(self, 
                                            action_data: Dict[str, Any], 
                                            meeting_data: Dict[str, Any]) -> ActionItem:
        """Create action item from Oracle analysis action data"""
        return ActionItem(
            title=action_data.get('title', 'Untitled Action'),
            description=action_data.get('description', ''),
            assignee=action_data.get('assignee'),
            priority=self._map_priority(action_data.get('priority', 'medium')),
            due_date=self._parse_due_date(action_data.get('due_date')),
            estimated_hours=action_data.get('estimated_hours'),
            meeting_id=meeting_data.get('id'),
            exponential_potential=action_data.get('exponential_potential'),
            velocity_estimate=action_data.get('velocity_estimate'),
            context={
                'source': 'oracle_analysis',
                'meeting_title': meeting_data.get('title'),
                'meeting_date': meeting_data.get('date'),
                'original_data': action_data
            }
        )
    
    async def _create_action_from_decision_step(self, 
                                              step: Dict[str, Any], 
                                              decision: Dict[str, Any],
                                              meeting_data: Dict[str, Any]) -> ActionItem:
        """Create action item from decision implementation step"""
        return ActionItem(
            title=f"Implement: {step.get('title', 'Decision Step')}",
            description=f"Implementation step for decision: {decision.get('title', 'Unknown Decision')}\n\n{step.get('description', '')}",
            assignee=step.get('assignee') or decision.get('owner'),
            priority=ActionPriority.HIGH,  # Decision implementations are high priority
            due_date=self._parse_due_date(step.get('deadline')),
            estimated_hours=step.get('estimated_effort'),
            meeting_id=meeting_data.get('id'),
            tags=['decision-implementation'],
            context={
                'source': 'decision_implementation',
                'decision_id': decision.get('id'),
                'decision_title': decision.get('title'),
                'meeting_title': meeting_data.get('title'),
                'meeting_date': meeting_data.get('date'),
                'step_data': step
            }
        )
    
    async def _create_action_from_strategic_plan(self, 
                                               plan: Dict[str, Any],
                                               meeting_data: Dict[str, Any]) -> ActionItem:
        """Create action item from strategic action plan"""
        return ActionItem(
            title=plan.get('title', 'Strategic Action'),
            description=plan.get('description', ''),
            assignee=plan.get('owner'),
            priority=ActionPriority.HIGH,  # Strategic actions are high priority
            due_date=self._parse_due_date(plan.get('target_date')),
            estimated_hours=plan.get('estimated_effort'),
            meeting_id=meeting_data.get('id'),
            tags=['strategic'],
            exponential_potential=plan.get('exponential_potential'),
            context={
                'source': 'strategic_plan',
                'framework_alignment': plan.get('framework_alignment'),
                'meeting_title': meeting_data.get('title'),
                'meeting_date': meeting_data.get('date'),
                'plan_data': plan
            }
        )
    
    async def _auto_assign_tags_and_priority(self, 
                                           action: ActionItem, 
                                           meeting_data: Dict[str, Any],
                                           oracle_analysis: Dict[str, Any]):
        """Auto-assign tags and priority based on content analysis"""
        if not self.config['auto_tag_enabled']:
            return
        
        # Analyze content for tag assignment
        content = f"{action.title} {action.description}".lower()
        
        # Auto-assign tags based on keywords
        tag_keywords = {
            'technical': ['implement', 'develop', 'code', 'system', 'api', 'database', 'technical'],
            'research': ['research', 'analyze', 'investigate', 'study', 'explore', 'evaluate'],
            'communication': ['communicate', 'notify', 'inform', 'update', 'present', 'share'],
            'urgent': ['urgent', 'asap', 'immediately', 'critical', 'emergency'],
            'documentation': ['document', 'write', 'create guide', 'manual', 'specification'],
            'process-improvement': ['improve', 'optimize', 'streamline', 'enhance', 'refactor']
        }
        
        for tag_name, keywords in tag_keywords.items():
            if any(keyword in content for keyword in keywords):
                if tag_name not in action.tags:
                    action.tags.append(tag_name)
        
        # Auto-assign priority based on content and context
        if action.priority == ActionPriority.MEDIUM:  # Only adjust if not explicitly set
            if any(word in content for word in ['urgent', 'critical', 'asap', 'immediately']):
                action.priority = ActionPriority.CRITICAL
            elif any(word in content for word in ['important', 'high priority', 'strategic']):
                action.priority = ActionPriority.HIGH
            elif action.exponential_potential and action.exponential_potential > 0.8:
                action.priority = ActionPriority.HIGH
        
        # Add meeting follow-up tag
        if 'meeting-follow-up' not in action.tags:
            action.tags.append('meeting-follow-up')
    
    async def sync_action_to_dart(self, action: ActionItem) -> bool:
        """Sync a single action to Dart system"""
        try:
            session = await self._get_session()
            
            # Prepare action data for Dart API
            dart_data = {
                'title': action.title,
                'description': action.description,
                'assignee': action.assignee,
                'priority': action.priority.value,
                'status': action.status.value,
                'due_date': action.due_date.isoformat() if action.due_date else None,
                'estimated_hours': action.estimated_hours,
                'tags': action.tags,
                'project_id': action.project_id,
                'metadata': {
                    'meeting_id': action.meeting_id,
                    'exponential_potential': action.exponential_potential,
                    'velocity_estimate': action.velocity_estimate,
                    'context': action.context,
                    'source': 'intelligence_os_platform'
                }
            }
            
            if action.dart_id:
                # Update existing action
                url = urljoin(self.dart_api_url, f'/api/actions/{action.dart_id}')
                async with session.put(url, json=dart_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        action.updated_at = datetime.utcnow()
                        logger.info("Updated action in Dart", action_id=action.id, dart_id=action.dart_id)
                        return True
                    else:
                        logger.error("Failed to update action in Dart", 
                                   action_id=action.id, 
                                   status=response.status,
                                   response=await response.text())
                        return False
            else:
                # Create new action
                url = urljoin(self.dart_api_url, '/api/actions')
                async with session.post(url, json=dart_data) as response:
                    if response.status == 201:
                        result = await response.json()
                        action.dart_id = result.get('id')
                        action.updated_at = datetime.utcnow()
                        self.dart_id_mapping[action.dart_id] = action.id
                        logger.info("Created action in Dart", action_id=action.id, dart_id=action.dart_id)
                        return True
                    else:
                        logger.error("Failed to create action in Dart", 
                                   action_id=action.id, 
                                   status=response.status,
                                   response=await response.text())
                        return False
                        
        except Exception as e:
            logger.error("Error syncing action to Dart", action_id=action.id, error=str(e))
            return False
    
    async def sync_actions_from_dart(self) -> List[ActionItem]:
        """Sync actions from Dart system to local cache"""
        try:
            session = await self._get_session()
            url = urljoin(self.dart_api_url, '/api/actions')
            
            # Get actions with Intelligence OS metadata
            params = {
                'source': 'intelligence_os_platform',
                'limit': self.config['batch_size']
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    dart_actions = await response.json()
                    updated_actions = []
                    
                    for dart_action in dart_actions.get('actions', []):
                        local_action = await self._update_local_action_from_dart(dart_action)
                        if local_action:
                            updated_actions.append(local_action)
                    
                    logger.info("Synced actions from Dart", count=len(updated_actions))
                    return updated_actions
                else:
                    logger.error("Failed to fetch actions from Dart", status=response.status)
                    return []
                    
        except Exception as e:
            logger.error("Error syncing actions from Dart", error=str(e))
            return []
    
    async def _update_local_action_from_dart(self, dart_action: Dict[str, Any]) -> Optional[ActionItem]:
        """Update local action from Dart action data"""
        try:
            dart_id = dart_action.get('id')
            local_id = self.dart_id_mapping.get(dart_id)
            
            if local_id and local_id in self.action_cache:
                # Update existing local action
                action = self.action_cache[local_id]
                action.status = ActionStatus(dart_action.get('status', 'not_started'))
                action.assignee = dart_action.get('assignee')
                action.due_date = self._parse_due_date(dart_action.get('due_date'))
                action.updated_at = datetime.utcnow()
                
                # Update progress tracking
                if 'progress' in dart_action:
                    action.context['dart_progress'] = dart_action['progress']
                
                return action
            else:
                # Create new local action from Dart data
                metadata = dart_action.get('metadata', {})
                if metadata.get('source') == 'intelligence_os_platform':
                    action = ActionItem(
                        id=self._generate_action_id(),
                        title=dart_action.get('title', ''),
                        description=dart_action.get('description', ''),
                        assignee=dart_action.get('assignee'),
                        priority=ActionPriority(dart_action.get('priority', 'medium')),
                        status=ActionStatus(dart_action.get('status', 'not_started')),
                        due_date=self._parse_due_date(dart_action.get('due_date')),
                        estimated_hours=dart_action.get('estimated_hours'),
                        tags=dart_action.get('tags', []),
                        project_id=dart_action.get('project_id'),
                        meeting_id=metadata.get('meeting_id'),
                        dart_id=dart_id,
                        exponential_potential=metadata.get('exponential_potential'),
                        velocity_estimate=metadata.get('velocity_estimate'),
                        context=metadata.get('context', {})
                    )
                    
                    self.action_cache[action.id] = action
                    self.dart_id_mapping[dart_id] = action.id
                    return action
            
            return None
            
        except Exception as e:
            logger.error("Error updating local action from Dart", dart_id=dart_action.get('id'), error=str(e))
            return None
    
    async def track_action_progress(self, action_id: str) -> Dict[str, Any]:
        """Track progress of an action"""
        try:
            if action_id not in self.action_cache:
                return {'error': 'Action not found'}
            
            action = self.action_cache[action_id]
            
            # Get latest status from Dart if available
            if action.dart_id:
                await self._refresh_action_from_dart(action)
            
            # Calculate progress metrics
            progress_data = {
                'action_id': action_id,
                'dart_id': action.dart_id,
                'title': action.title,
                'status': action.status.value,
                'priority': action.priority.value,
                'assignee': action.assignee,
                'due_date': action.due_date.isoformat() if action.due_date else None,
                'estimated_hours': action.estimated_hours,
                'exponential_potential': action.exponential_potential,
                'velocity_estimate': action.velocity_estimate,
                'tags': action.tags,
                'created_at': action.created_at.isoformat(),
                'updated_at': action.updated_at.isoformat(),
                'days_since_created': (datetime.utcnow() - action.created_at).days,
                'is_overdue': False,
                'progress_percentage': self._calculate_progress_percentage(action)
            }
            
            # Check if overdue
            if action.due_date and datetime.utcnow() > action.due_date:
                progress_data['is_overdue'] = True
                progress_data['days_overdue'] = (datetime.utcnow() - action.due_date).days
            
            return progress_data
            
        except Exception as e:
            logger.error("Error tracking action progress", action_id=action_id, error=str(e))
            return {'error': str(e)}
    
    async def _refresh_action_from_dart(self, action: ActionItem):
        """Refresh action data from Dart system"""
        try:
            if not action.dart_id:
                return
            
            session = await self._get_session()
            url = urljoin(self.dart_api_url, f'/api/actions/{action.dart_id}')
            
            async with session.get(url) as response:
                if response.status == 200:
                    dart_action = await response.json()
                    await self._update_local_action_from_dart(dart_action)
                    
        except Exception as e:
            logger.error("Error refreshing action from Dart", action_id=action.id, error=str(e))
    
    def _calculate_progress_percentage(self, action: ActionItem) -> float:
        """Calculate progress percentage based on status and context"""
        status_progress = {
            ActionStatus.NOT_STARTED: 0.0,
            ActionStatus.IN_PROGRESS: 50.0,
            ActionStatus.BLOCKED: 25.0,
            ActionStatus.COMPLETED: 100.0,
            ActionStatus.CANCELLED: 0.0
        }
        
        base_progress = status_progress.get(action.status, 0.0)
        
        # Adjust based on Dart progress if available
        if 'dart_progress' in action.context:
            dart_progress = action.context['dart_progress'].get('percentage', base_progress)
            return max(base_progress, dart_progress)
        
        return base_progress  
  
    async def analyze_action_dependencies(self, actions: List[ActionItem]) -> List[ActionDependency]:
        """Analyze and create dependencies between actions"""
        try:
            dependencies = []
            
            # Group actions by meeting and context
            meeting_groups = {}
            for action in actions:
                meeting_id = action.meeting_id or 'unknown'
                if meeting_id not in meeting_groups:
                    meeting_groups[meeting_id] = []
                meeting_groups[meeting_id].append(action)
            
            # Analyze dependencies within each meeting
            for meeting_id, meeting_actions in meeting_groups.items():
                meeting_deps = await self._analyze_meeting_action_dependencies(meeting_actions)
                dependencies.extend(meeting_deps)
            
            # Analyze cross-meeting dependencies
            cross_deps = await self._analyze_cross_meeting_dependencies(actions)
            dependencies.extend(cross_deps)
            
            # Store dependencies
            for dep in dependencies:
                if dep.source_action_id not in self.dependencies:
                    self.dependencies[dep.source_action_id] = []
                self.dependencies[dep.source_action_id].append(dep)
            
            logger.info("Analyzed action dependencies", 
                       total_actions=len(actions),
                       dependencies_found=len(dependencies))
            
            return dependencies
            
        except Exception as e:
            logger.error("Error analyzing action dependencies", error=str(e))
            return []
    
    async def _analyze_meeting_action_dependencies(self, actions: List[ActionItem]) -> List[ActionDependency]:
        """Analyze dependencies between actions from the same meeting"""
        dependencies = []
        
        # Sort actions by priority and creation order
        sorted_actions = sorted(actions, key=lambda x: (x.priority.value, x.created_at))
        
        for i, action in enumerate(sorted_actions):
            # Check for decision implementation dependencies
            if 'decision-implementation' in action.tags:
                # Decision implementations may depend on research or communication actions
                for other_action in sorted_actions[:i]:
                    if any(tag in other_action.tags for tag in ['research', 'communication']):
                        if self._actions_are_related(action, other_action):
                            dep = ActionDependency(
                                source_action_id=action.id,
                                target_action_id=other_action.id,
                                dependency_type=DependencyType.DEPENDS_ON,
                                description=f"Decision implementation depends on {other_action.title}"
                            )
                            dependencies.append(dep)
            
            # Check for strategic action dependencies
            if 'strategic' in action.tags:
                # Strategic actions may block other actions
                for other_action in sorted_actions[i+1:]:
                    if action.priority.value > other_action.priority.value:
                        if self._actions_are_related(action, other_action):
                            dep = ActionDependency(
                                source_action_id=action.id,
                                target_action_id=other_action.id,
                                dependency_type=DependencyType.BLOCKS,
                                description=f"Strategic action blocks {other_action.title}"
                            )
                            dependencies.append(dep)
            
            # Check for technical dependencies
            if 'technical' in action.tags:
                # Technical actions may have implementation order dependencies
                for other_action in sorted_actions:
                    if other_action != action and 'technical' in other_action.tags:
                        if self._is_technical_dependency(action, other_action):
                            dep = ActionDependency(
                                source_action_id=action.id,
                                target_action_id=other_action.id,
                                dependency_type=DependencyType.DEPENDS_ON,
                                description=f"Technical implementation dependency"
                            )
                            dependencies.append(dep)
        
        return dependencies
    
    async def _analyze_cross_meeting_dependencies(self, actions: List[ActionItem]) -> List[ActionDependency]:
        """Analyze dependencies between actions from different meetings"""
        dependencies = []
        
        # Group actions by assignee
        assignee_groups = {}
        for action in actions:
            if action.assignee:
                if action.assignee not in assignee_groups:
                    assignee_groups[action.assignee] = []
                assignee_groups[action.assignee].append(action)
        
        # Check for resource conflicts and dependencies
        for assignee, assignee_actions in assignee_groups.items():
            # Sort by due date and priority
            sorted_actions = sorted(assignee_actions, 
                                  key=lambda x: (x.due_date or datetime.max, x.priority.value))
            
            for i, action in enumerate(sorted_actions):
                # Check for resource conflicts (same assignee, overlapping timeframes)
                for other_action in sorted_actions[i+1:]:
                    if self._has_resource_conflict(action, other_action):
                        dep = ActionDependency(
                            source_action_id=action.id,
                            target_action_id=other_action.id,
                            dependency_type=DependencyType.BLOCKS,
                            description=f"Resource conflict: same assignee ({assignee})"
                        )
                        dependencies.append(dep)
        
        return dependencies
    
    def _actions_are_related(self, action1: ActionItem, action2: ActionItem) -> bool:
        """Check if two actions are related based on content similarity"""
        # Simple keyword-based similarity check
        keywords1 = set(action1.title.lower().split() + action1.description.lower().split())
        keywords2 = set(action2.title.lower().split() + action2.description.lower().split())
        
        # Remove common words
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        keywords1 -= common_words
        keywords2 -= common_words
        
        if not keywords1 or not keywords2:
            return False
        
        # Calculate Jaccard similarity
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        similarity = intersection / union if union > 0 else 0
        
        return similarity > 0.2  # 20% similarity threshold
    
    def _is_technical_dependency(self, action1: ActionItem, action2: ActionItem) -> bool:
        """Check if there's a technical dependency between actions"""
        # Check for common technical dependency patterns
        dependency_patterns = [
            (['database', 'schema'], ['api', 'endpoint']),
            (['api', 'service'], ['frontend', 'ui']),
            (['authentication', 'auth'], ['user', 'access']),
            (['infrastructure', 'deployment'], ['application', 'service'])
        ]
        
        content1 = f"{action1.title} {action1.description}".lower()
        content2 = f"{action2.title} {action2.description}".lower()
        
        for prereq_keywords, dependent_keywords in dependency_patterns:
            has_prereq = any(keyword in content1 for keyword in prereq_keywords)
            has_dependent = any(keyword in content2 for keyword in dependent_keywords)
            
            if has_prereq and has_dependent:
                return True
        
        return False
    
    def _has_resource_conflict(self, action1: ActionItem, action2: ActionItem) -> bool:
        """Check if two actions have resource conflicts"""
        # Same assignee is already checked by caller
        
        # Check for overlapping time periods
        if action1.due_date and action2.due_date:
            # Estimate start dates based on due date and estimated hours
            est_hours1 = action1.estimated_hours or 8  # Default 1 day
            est_hours2 = action2.estimated_hours or 8
            
            start1 = action1.due_date - timedelta(hours=est_hours1)
            end1 = action1.due_date
            start2 = action2.due_date - timedelta(hours=est_hours2)
            end2 = action2.due_date
            
            # Check for overlap
            return not (end1 <= start2 or end2 <= start1)
        
        return False
    
    async def generate_resource_allocation_recommendations(self, actions: List[ActionItem]) -> Dict[str, Any]:
        """Generate resource allocation recommendations"""
        try:
            recommendations = {
                'workload_analysis': {},
                'capacity_warnings': [],
                'optimization_suggestions': [],
                'timeline_adjustments': []
            }
            
            # Analyze workload by assignee
            assignee_workload = {}
            for action in actions:
                if action.assignee and action.status not in [ActionStatus.COMPLETED, ActionStatus.CANCELLED]:
                    if action.assignee not in assignee_workload:
                        assignee_workload[action.assignee] = {
                            'total_hours': 0,
                            'action_count': 0,
                            'high_priority_count': 0,
                            'overdue_count': 0,
                            'actions': []
                        }
                    
                    workload = assignee_workload[action.assignee]
                    workload['total_hours'] += action.estimated_hours or 8
                    workload['action_count'] += 1
                    workload['actions'].append(action)
                    
                    if action.priority in [ActionPriority.HIGH, ActionPriority.CRITICAL]:
                        workload['high_priority_count'] += 1
                    
                    if action.due_date and datetime.utcnow() > action.due_date:
                        workload['overdue_count'] += 1
            
            recommendations['workload_analysis'] = assignee_workload
            
            # Generate capacity warnings
            for assignee, workload in assignee_workload.items():
                # Assume 40 hours per week capacity
                weekly_capacity = 40
                weeks_ahead = 4  # Look 4 weeks ahead
                total_capacity = weekly_capacity * weeks_ahead
                
                if workload['total_hours'] > total_capacity:
                    recommendations['capacity_warnings'].append({
                        'assignee': assignee,
                        'total_hours': workload['total_hours'],
                        'capacity': total_capacity,
                        'overload_hours': workload['total_hours'] - total_capacity,
                        'overload_percentage': ((workload['total_hours'] - total_capacity) / total_capacity) * 100,
                        'action_count': workload['action_count']
                    })
                
                if workload['overdue_count'] > 0:
                    recommendations['capacity_warnings'].append({
                        'assignee': assignee,
                        'type': 'overdue_actions',
                        'overdue_count': workload['overdue_count'],
                        'message': f"{assignee} has {workload['overdue_count']} overdue actions"
                    })
            
            # Generate optimization suggestions
            await self._generate_optimization_suggestions(recommendations, assignee_workload)
            
            # Generate timeline adjustments
            await self._generate_timeline_adjustments(recommendations, actions)
            
            logger.info("Generated resource allocation recommendations",
                       assignee_count=len(assignee_workload),
                       warnings=len(recommendations['capacity_warnings']),
                       suggestions=len(recommendations['optimization_suggestions']))
            
            return recommendations
            
        except Exception as e:
            logger.error("Error generating resource allocation recommendations", error=str(e))
            return {'error': str(e)}
    
    async def _generate_optimization_suggestions(self, recommendations: Dict[str, Any], assignee_workload: Dict[str, Any]):
        """Generate optimization suggestions for resource allocation"""
        # Find overloaded and underloaded assignees
        overloaded = []
        underloaded = []
        
        for assignee, workload in assignee_workload.items():
            weekly_capacity = 40
            weeks_ahead = 4
            total_capacity = weekly_capacity * weeks_ahead
            utilization = workload['total_hours'] / total_capacity
            
            if utilization > 1.2:  # 120% utilization
                overloaded.append((assignee, workload, utilization))
            elif utilization < 0.6:  # 60% utilization
                underloaded.append((assignee, workload, utilization))
        
        # Suggest redistributions
        for overloaded_assignee, overloaded_workload, _ in overloaded:
            for underloaded_assignee, underloaded_workload, _ in underloaded:
                # Find actions that could be redistributed
                redistributable_actions = [
                    action for action in overloaded_workload['actions']
                    if action.priority not in [ActionPriority.CRITICAL] and
                    'technical' not in action.tags  # Avoid technical actions that may require specific skills
                ]
                
                if redistributable_actions:
                    recommendations['optimization_suggestions'].append({
                        'type': 'redistribute_actions',
                        'from_assignee': overloaded_assignee,
                        'to_assignee': underloaded_assignee,
                        'suggested_actions': [
                            {
                                'id': action.id,
                                'title': action.title,
                                'estimated_hours': action.estimated_hours or 8
                            }
                            for action in redistributable_actions[:3]  # Suggest up to 3 actions
                        ],
                        'potential_hours_saved': sum(action.estimated_hours or 8 for action in redistributable_actions[:3])
                    })
        
        # Suggest priority adjustments
        for assignee, workload in assignee_workload.items():
            if workload['high_priority_count'] > 5:  # Too many high priority actions
                recommendations['optimization_suggestions'].append({
                    'type': 'priority_adjustment',
                    'assignee': assignee,
                    'high_priority_count': workload['high_priority_count'],
                    'suggestion': 'Consider reducing priority of some actions to improve focus',
                    'actions_to_review': [
                        {
                            'id': action.id,
                            'title': action.title,
                            'current_priority': action.priority.value
                        }
                        for action in workload['actions']
                        if action.priority == ActionPriority.HIGH
                    ][:3]
                })
    
    async def _generate_timeline_adjustments(self, recommendations: Dict[str, Any], actions: List[ActionItem]):
        """Generate timeline adjustment suggestions"""
        # Find actions with unrealistic timelines
        for action in actions:
            if action.due_date and action.estimated_hours:
                days_until_due = (action.due_date - datetime.utcnow()).days
                estimated_days = (action.estimated_hours / 8)  # Assume 8 hours per day
                
                if days_until_due < estimated_days and days_until_due > 0:
                    recommendations['timeline_adjustments'].append({
                        'action_id': action.id,
                        'title': action.title,
                        'assignee': action.assignee,
                        'current_due_date': action.due_date.isoformat(),
                        'days_until_due': days_until_due,
                        'estimated_days_needed': estimated_days,
                        'suggested_due_date': (datetime.utcnow() + timedelta(days=estimated_days + 1)).isoformat(),
                        'reason': 'Insufficient time allocated based on estimated effort'
                    })
    
    def _map_priority(self, priority_str: str) -> ActionPriority:
        """Map priority string to ActionPriority enum"""
        priority_mapping = {
            'low': ActionPriority.LOW,
            'medium': ActionPriority.MEDIUM,
            'high': ActionPriority.HIGH,
            'critical': ActionPriority.CRITICAL,
            'urgent': ActionPriority.CRITICAL
        }
        return priority_mapping.get(priority_str.lower(), ActionPriority.MEDIUM)
    
    def _parse_due_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse due date string to datetime"""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            formats = [
                '%Y-%m-%d',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If no format matches, return None
            return None
            
        except Exception:
            return None
    
    def _generate_action_id(self) -> str:
        """Generate a unique action ID"""
        return f"action_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.utcnow()) % 10000}"
    
    def _start_background_sync(self):
        """Start background synchronization process"""
        async def sync_worker():
            while True:
                try:
                    # Sync pending actions to Dart
                    if self.pending_sync:
                        pending_ids = list(self.pending_sync)
                        for action_id in pending_ids:
                            if action_id in self.action_cache:
                                success = await self.sync_action_to_dart(self.action_cache[action_id])
                                if success:
                                    self.pending_sync.discard(action_id)
                    
                    # Sync actions from Dart
                    await self.sync_actions_from_dart()
                    
                    # Wait for next sync interval
                    await asyncio.sleep(self.config['sync_interval_minutes'] * 60)
                    
                except Exception as e:
                    logger.error("Background sync error", error=str(e))
                    await asyncio.sleep(60)  # Wait 1 minute before retrying
        
        # Start the background task
        asyncio.create_task(sync_worker())
    
    async def get_action_status_report(self) -> Dict[str, Any]:
        """Get comprehensive action status report"""
        try:
            total_actions = len(self.action_cache)
            
            # Count by status
            status_counts = {}
            for status in ActionStatus:
                status_counts[status.value] = sum(
                    1 for action in self.action_cache.values() 
                    if action.status == status
                )
            
            # Count by priority
            priority_counts = {}
            for priority in ActionPriority:
                priority_counts[priority.value] = sum(
                    1 for action in self.action_cache.values() 
                    if action.priority == priority
                )
            
            # Count overdue actions
            overdue_count = sum(
                1 for action in self.action_cache.values()
                if action.due_date and datetime.utcnow() > action.due_date and 
                action.status not in [ActionStatus.COMPLETED, ActionStatus.CANCELLED]
            )
            
            # Count by assignee
            assignee_counts = {}
            for action in self.action_cache.values():
                if action.assignee:
                    assignee_counts[action.assignee] = assignee_counts.get(action.assignee, 0) + 1
            
            # Sync status
            sync_status = {
                'pending_sync_count': len(self.pending_sync),
                'dart_synced_count': sum(1 for action in self.action_cache.values() if action.dart_id),
                'last_sync_time': datetime.utcnow().isoformat()
            }
            
            return {
                'total_actions': total_actions,
                'status_breakdown': status_counts,
                'priority_breakdown': priority_counts,
                'overdue_count': overdue_count,
                'assignee_breakdown': assignee_counts,
                'sync_status': sync_status,
                'dependencies_count': sum(len(deps) for deps in self.dependencies.values())
            }
            
        except Exception as e:
            logger.error("Error generating action status report", error=str(e))
            return {'error': str(e)}
    
    async def close(self):
        """Close the service and cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("Dart integration service closed")