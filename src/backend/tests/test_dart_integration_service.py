"""
Tests for Dart Action Management Integration Service
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json
import aiohttp

from src.services.dart_integration_service import (
    DartIntegrationService,
    ActionItem,
    ActionPriority,
    ActionStatus,
    ActionDependency,
    DependencyType,
    ProjectTag
)


class TestDartIntegrationService:
    """Test cases for DartIntegrationService"""
    
    @pytest.fixture
    def service(self):
        """Create a DartIntegrationService instance for testing"""
        return DartIntegrationService("https://api.dart.test.com", "test-api-key")
    
    @pytest.fixture
    def sample_meeting_data(self):
        """Sample meeting data for testing"""
        return {
            'id': 'meeting_123',
            'title': 'Project Planning Meeting',
            'date': '2024-01-15T10:00:00Z',
            'participants': ['alice@example.com', 'bob@example.com'],
            'duration': 3600
        }
    
    @pytest.fixture
    def sample_oracle_analysis(self):
        """Sample Oracle analysis data for testing"""
        return {
            'action_register': {
                'actions': [
                    {
                        'title': 'Implement user authentication',
                        'description': 'Set up OAuth2 authentication system',
                        'assignee': 'alice@example.com',
                        'priority': 'high',
                        'due_date': '2024-01-30',
                        'estimated_hours': 16,
                        'exponential_potential': 0.8,
                        'velocity_estimate': 5
                    },
                    {
                        'title': 'Create API documentation',
                        'description': 'Document all REST API endpoints',
                        'assignee': 'bob@example.com',
                        'priority': 'medium',
                        'due_date': '2024-02-05',
                        'estimated_hours': 8,
                        'exponential_potential': 0.4,
                        'velocity_estimate': 3
                    }
                ]
            },
            'decisions_agreements': {
                'decisions': [
                    {
                        'id': 'decision_1',
                        'title': 'Use React for frontend',
                        'owner': 'alice@example.com',
                        'implementation_plan': {
                            'steps': [
                                {
                                    'title': 'Set up React project',
                                    'description': 'Initialize React application with TypeScript',
                                    'assignee': 'alice@example.com',
                                    'deadline': '2024-01-25',
                                    'estimated_effort': 4
                                }
                            ]
                        }
                    }
                ]
            },
            'strategic_implications': {
                'action_plans': [
                    {
                        'title': 'Develop mobile app strategy',
                        'description': 'Create comprehensive mobile application strategy',
                        'owner': 'bob@example.com',
                        'target_date': '2024-02-15',
                        'estimated_effort': 20,
                        'exponential_potential': 0.9,
                        'framework_alignment': {
                            'sdg_alignment': 0.7,
                            'doughnut_economy': 0.6
                        }
                    }
                ]
            }
        }
    
    @pytest.fixture
    def sample_action_item(self):
        """Sample action item for testing"""
        return ActionItem(
            id='action_123',
            title='Test Action',
            description='This is a test action',
            assignee='test@example.com',
            priority=ActionPriority.HIGH,
            status=ActionStatus.NOT_STARTED,
            due_date=datetime.utcnow() + timedelta(days=7),
            estimated_hours=8,
            tags=['test', 'technical'],
            meeting_id='meeting_123',
            exponential_potential=0.7,
            velocity_estimate=4
        )
    
    @pytest.mark.asyncio
    async def test_generate_actions_from_meeting(self, service, sample_meeting_data, sample_oracle_analysis):
        """Test action generation from meeting data"""
        actions = await service.generate_actions_from_meeting(sample_meeting_data, sample_oracle_analysis)
        
        assert len(actions) >= 3  # Should generate at least 3 actions
        
        # Check action from action_register
        auth_action = next((a for a in actions if 'authentication' in a.title.lower()), None)
        assert auth_action is not None
        assert auth_action.assignee == 'alice@example.com'
        assert auth_action.priority == ActionPriority.HIGH
        assert auth_action.estimated_hours == 16
        assert auth_action.exponential_potential == 0.8
        assert auth_action.meeting_id == 'meeting_123'
        
        # Check action from decision implementation
        react_action = next((a for a in actions if 'React' in a.title), None)
        assert react_action is not None
        assert 'decision-implementation' in react_action.tags
        assert react_action.priority == ActionPriority.HIGH
        
        # Check action from strategic plan
        mobile_action = next((a for a in actions if 'mobile' in a.title.lower()), None)
        assert mobile_action is not None
        assert 'strategic' in mobile_action.tags
        assert mobile_action.exponential_potential == 0.9
        
        # Verify all actions have IDs and are cached
        for action in actions:
            assert action.id is not None
            assert action.id in service.action_cache
            assert action.id in service.pending_sync
    
    @pytest.mark.asyncio
    async def test_auto_assign_tags_and_priority(self, service, sample_meeting_data, sample_oracle_analysis):
        """Test automatic tag and priority assignment"""
        actions = await service.generate_actions_from_meeting(sample_meeting_data, sample_oracle_analysis)
        
        # Check for auto-assigned tags
        for action in actions:
            assert 'meeting-follow-up' in action.tags
            
            # Check technical tag assignment
            if any(keyword in action.title.lower() + action.description.lower() 
                   for keyword in ['implement', 'api', 'system']):
                assert 'technical' in action.tags
            
            # Check documentation tag assignment
            if 'documentation' in action.title.lower() + action.description.lower():
                assert 'documentation' in action.tags
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.post')
    async def test_sync_action_to_dart_create(self, mock_post, service, sample_action_item):
        """Test syncing new action to Dart"""
        # Mock successful creation response
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json = AsyncMock(return_value={'id': 'dart_123'})
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Add action to cache
        service.action_cache[sample_action_item.id] = sample_action_item
        
        # Sync action
        success = await service.sync_action_to_dart(sample_action_item)
        
        assert success is True
        assert sample_action_item.dart_id == 'dart_123'
        assert service.dart_id_mapping['dart_123'] == sample_action_item.id
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert '/api/actions' in call_args[1]['url']
        
        # Verify request data
        request_data = call_args[1]['json']
        assert request_data['title'] == sample_action_item.title
        assert request_data['assignee'] == sample_action_item.assignee
        assert request_data['priority'] == sample_action_item.priority.value
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.put')
    async def test_sync_action_to_dart_update(self, mock_put, service, sample_action_item):
        """Test syncing existing action to Dart"""
        # Set dart_id to simulate existing action
        sample_action_item.dart_id = 'dart_123'
        
        # Mock successful update response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={'id': 'dart_123'})
        mock_put.return_value.__aenter__.return_value = mock_response
        
        # Add action to cache
        service.action_cache[sample_action_item.id] = sample_action_item
        
        # Sync action
        success = await service.sync_action_to_dart(sample_action_item)
        
        assert success is True
        
        # Verify API call
        mock_put.assert_called_once()
        call_args = mock_put.call_args
        assert f'/api/actions/{sample_action_item.dart_id}' in call_args[1]['url']
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_sync_actions_from_dart(self, mock_get, service):
        """Test syncing actions from Dart"""
        # Mock Dart API response
        dart_actions_response = {
            'actions': [
                {
                    'id': 'dart_456',
                    'title': 'External Action',
                    'description': 'Action created in Dart',
                    'assignee': 'external@example.com',
                    'priority': 'medium',
                    'status': 'in_progress',
                    'due_date': '2024-02-01T12:00:00Z',
                    'estimated_hours': 6,
                    'tags': ['external'],
                    'metadata': {
                        'source': 'intelligence_os_platform',
                        'meeting_id': 'meeting_456',
                        'exponential_potential': 0.5
                    }
                }
            ]
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=dart_actions_response)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Sync actions
        updated_actions = await service.sync_actions_from_dart()
        
        assert len(updated_actions) == 1
        action = updated_actions[0]
        assert action.title == 'External Action'
        assert action.status == ActionStatus.IN_PROGRESS
        assert action.dart_id == 'dart_456'
        assert action.meeting_id == 'meeting_456'
        
        # Verify action is cached
        assert action.id in service.action_cache
        assert service.dart_id_mapping['dart_456'] == action.id
    
    @pytest.mark.asyncio
    async def test_track_action_progress(self, service, sample_action_item):
        """Test action progress tracking"""
        # Add action to cache
        service.action_cache[sample_action_item.id] = sample_action_item
        
        # Track progress
        progress_data = await service.track_action_progress(sample_action_item.id)
        
        assert 'error' not in progress_data
        assert progress_data['action_id'] == sample_action_item.id
        assert progress_data['title'] == sample_action_item.title
        assert progress_data['status'] == sample_action_item.status.value
        assert progress_data['priority'] == sample_action_item.priority.value
        assert progress_data['progress_percentage'] == 0.0  # NOT_STARTED
        assert progress_data['is_overdue'] is False
        
        # Test overdue action
        sample_action_item.due_date = datetime.utcnow() - timedelta(days=1)
        progress_data = await service.track_action_progress(sample_action_item.id)
        assert progress_data['is_overdue'] is True
        assert 'days_overdue' in progress_data
    
    @pytest.mark.asyncio
    async def test_analyze_action_dependencies(self, service):
        """Test action dependency analysis"""
        # Create test actions with different characteristics
        actions = [
            ActionItem(
                id='action_1',
                title='Research user requirements',
                description='Conduct user research',
                tags=['research'],
                priority=ActionPriority.HIGH,
                meeting_id='meeting_1'
            ),
            ActionItem(
                id='action_2',
                title='Implement user authentication',
                description='Implement OAuth2 authentication',
                tags=['decision-implementation', 'technical'],
                priority=ActionPriority.MEDIUM,
                meeting_id='meeting_1'
            ),
            ActionItem(
                id='action_3',
                title='Create API endpoints',
                description='Develop REST API endpoints',
                tags=['technical'],
                priority=ActionPriority.LOW,
                meeting_id='meeting_1'
            )
        ]
        
        # Add actions to cache
        for action in actions:
            service.action_cache[action.id] = action
        
        # Analyze dependencies
        dependencies = await service.analyze_action_dependencies(actions)
        
        assert len(dependencies) > 0
        
        # Check for expected dependency patterns
        decision_deps = [d for d in dependencies if d.dependency_type == DependencyType.DEPENDS_ON]
        assert len(decision_deps) > 0
        
        # Verify dependencies are stored
        for dep in dependencies:
            assert dep.source_action_id in service.dependencies
    
    @pytest.mark.asyncio
    async def test_generate_resource_allocation_recommendations(self, service):
        """Test resource allocation recommendations"""
        # Create actions with different assignees and workloads
        actions = [
            ActionItem(
                id='action_1',
                title='Heavy task 1',
                assignee='overloaded@example.com',
                estimated_hours=40,
                status=ActionStatus.NOT_STARTED,
                priority=ActionPriority.HIGH
            ),
            ActionItem(
                id='action_2',
                title='Heavy task 2',
                assignee='overloaded@example.com',
                estimated_hours=60,
                status=ActionStatus.IN_PROGRESS,
                priority=ActionPriority.MEDIUM
            ),
            ActionItem(
                id='action_3',
                title='Light task',
                assignee='underloaded@example.com',
                estimated_hours=8,
                status=ActionStatus.NOT_STARTED,
                priority=ActionPriority.LOW
            ),
            ActionItem(
                id='action_4',
                title='Overdue task',
                assignee='overloaded@example.com',
                estimated_hours=16,
                status=ActionStatus.NOT_STARTED,
                due_date=datetime.utcnow() - timedelta(days=2),
                priority=ActionPriority.HIGH
            )
        ]
        
        # Add actions to cache
        for action in actions:
            service.action_cache[action.id] = action
        
        # Generate recommendations
        recommendations = await service.generate_resource_allocation_recommendations(actions)
        
        assert 'error' not in recommendations
        assert 'workload_analysis' in recommendations
        assert 'capacity_warnings' in recommendations
        assert 'optimization_suggestions' in recommendations
        assert 'timeline_adjustments' in recommendations
        
        # Check workload analysis
        workload = recommendations['workload_analysis']
        assert 'overloaded@example.com' in workload
        assert 'underloaded@example.com' in workload
        
        overloaded_workload = workload['overloaded@example.com']
        assert overloaded_workload['total_hours'] == 116  # 40 + 60 + 16
        assert overloaded_workload['action_count'] == 3
        assert overloaded_workload['overdue_count'] == 1
        
        # Check capacity warnings
        warnings = recommendations['capacity_warnings']
        assert len(warnings) > 0
        
        # Should have overload warning
        overload_warnings = [w for w in warnings if w.get('overload_hours')]
        assert len(overload_warnings) > 0
        
        # Should have overdue warning
        overdue_warnings = [w for w in warnings if w.get('type') == 'overdue_actions']
        assert len(overdue_warnings) > 0
    
    def test_map_priority(self, service):
        """Test priority mapping"""
        assert service._map_priority('low') == ActionPriority.LOW
        assert service._map_priority('medium') == ActionPriority.MEDIUM
        assert service._map_priority('high') == ActionPriority.HIGH
        assert service._map_priority('critical') == ActionPriority.CRITICAL
        assert service._map_priority('urgent') == ActionPriority.CRITICAL
        assert service._map_priority('invalid') == ActionPriority.MEDIUM  # Default
    
    def test_parse_due_date(self, service):
        """Test due date parsing"""
        # Test valid formats
        assert service._parse_due_date('2024-01-15') is not None
        assert service._parse_due_date('2024-01-15T10:00:00') is not None
        assert service._parse_due_date('2024-01-15T10:00:00Z') is not None
        
        # Test invalid formats
        assert service._parse_due_date('invalid-date') is None
        assert service._parse_due_date('') is None
        assert service._parse_due_date(None) is None
    
    def test_generate_action_id(self, service):
        """Test action ID generation"""
        id1 = service._generate_action_id()
        id2 = service._generate_action_id()
        
        assert id1 != id2
        assert id1.startswith('action_')
        assert id2.startswith('action_')
    
    def test_actions_are_related(self, service):
        """Test action relationship detection"""
        action1 = ActionItem(
            title='Implement user authentication system',
            description='Set up OAuth2 authentication with JWT tokens'
        )
        action2 = ActionItem(
            title='Create user registration API',
            description='Develop API endpoints for user registration and authentication'
        )
        action3 = ActionItem(
            title='Design marketing campaign',
            description='Create marketing materials for product launch'
        )
        
        # Related actions (share keywords: user, authentication, API)
        assert service._actions_are_related(action1, action2) is True
        
        # Unrelated actions
        assert service._actions_are_related(action1, action3) is False
    
    def test_is_technical_dependency(self, service):
        """Test technical dependency detection"""
        database_action = ActionItem(
            title='Set up database schema',
            description='Create database tables and relationships'
        )
        api_action = ActionItem(
            title='Create API endpoints',
            description='Develop REST API for data access'
        )
        ui_action = ActionItem(
            title='Build user interface',
            description='Create frontend components'
        )
        
        # Database -> API dependency
        assert service._is_technical_dependency(database_action, api_action) is True
        
        # API -> UI dependency
        assert service._is_technical_dependency(api_action, ui_action) is True
        
        # No dependency between database and UI directly
        assert service._is_technical_dependency(database_action, ui_action) is False
    
    def test_has_resource_conflict(self, service):
        """Test resource conflict detection"""
        now = datetime.utcnow()
        
        action1 = ActionItem(
            due_date=now + timedelta(days=5),
            estimated_hours=16  # 2 days
        )
        action2 = ActionItem(
            due_date=now + timedelta(days=6),
            estimated_hours=8   # 1 day
        )
        action3 = ActionItem(
            due_date=now + timedelta(days=10),
            estimated_hours=8   # 1 day
        )
        
        # Overlapping timeframes
        assert service._has_resource_conflict(action1, action2) is True
        
        # Non-overlapping timeframes
        assert service._has_resource_conflict(action1, action3) is False
    
    @pytest.mark.asyncio
    async def test_get_action_status_report(self, service):
        """Test action status report generation"""
        # Add test actions with different statuses
        actions = [
            ActionItem(id='1', status=ActionStatus.NOT_STARTED, priority=ActionPriority.HIGH, assignee='alice@example.com'),
            ActionItem(id='2', status=ActionStatus.IN_PROGRESS, priority=ActionPriority.MEDIUM, assignee='alice@example.com'),
            ActionItem(id='3', status=ActionStatus.COMPLETED, priority=ActionPriority.LOW, assignee='bob@example.com'),
            ActionItem(id='4', status=ActionStatus.NOT_STARTED, priority=ActionPriority.CRITICAL, 
                      assignee='bob@example.com', due_date=datetime.utcnow() - timedelta(days=1))
        ]
        
        for action in actions:
            service.action_cache[action.id] = action
        
        # Add some pending sync items
        service.pending_sync.add('1')
        service.pending_sync.add('2')
        
        report = await service.get_action_status_report()
        
        assert 'error' not in report
        assert report['total_actions'] == 4
        
        # Check status breakdown
        status_breakdown = report['status_breakdown']
        assert status_breakdown['not_started'] == 2
        assert status_breakdown['in_progress'] == 1
        assert status_breakdown['completed'] == 1
        
        # Check priority breakdown
        priority_breakdown = report['priority_breakdown']
        assert priority_breakdown['high'] == 1
        assert priority_breakdown['medium'] == 1
        assert priority_breakdown['low'] == 1
        assert priority_breakdown['critical'] == 1
        
        # Check overdue count
        assert report['overdue_count'] == 1
        
        # Check assignee breakdown
        assignee_breakdown = report['assignee_breakdown']
        assert assignee_breakdown['alice@example.com'] == 2
        assert assignee_breakdown['bob@example.com'] == 2
        
        # Check sync status
        sync_status = report['sync_status']
        assert sync_status['pending_sync_count'] == 2
        assert sync_status['dart_synced_count'] == 0  # No dart_id set
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling in various scenarios"""
        # Test tracking non-existent action
        progress_data = await service.track_action_progress('non_existent')
        assert 'error' in progress_data
        
        # Test empty action list for dependency analysis
        dependencies = await service.analyze_action_dependencies([])
        assert len(dependencies) == 0
        
        # Test resource allocation with no actions
        recommendations = await service.generate_resource_allocation_recommendations([])
        assert 'workload_analysis' in recommendations
        assert len(recommendations['workload_analysis']) == 0


if __name__ == '__main__':
    pytest.main([__file__])