"""
Tests for Notion Integration Service
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from src.services.notion_integration_service import (
    NotionIntegrationService,
    NotionPropertyType,
    SyncDirection,
    ConflictResolution,
    SyncStatus,
    NotionDatabaseSchema,
    SyncMapping,
    SyncRecord,
    ConflictRecord,
    notion_integration_service
)

class TestNotionIntegrationService:
    """Test cases for NotionIntegrationService"""
    
    @pytest.fixture
    def notion_service(self):
        """Create Notion service instance for testing"""
        return NotionIntegrationService()
    
    @pytest.fixture
    def sample_meeting_data(self):
        """Sample meeting data"""
        return {
            'id': 'meeting_123',
            'title': 'Weekly Team Standup',
            'date': datetime(2024, 1, 15, 9, 0, 0),
            'duration_minutes': 30,
            'participants': ['John Doe', 'Jane Smith', 'Bob Wilson'],
            'meeting_type': 'Standup',
            'status': 'Completed',
            'recording_url': 'https://example.com/recording',
            'transcript': 'Meeting transcript content...',
            'analysis_status': 'Completed',
            'oracle_analysis_id': 'oracle_123'
        }
    
    @pytest.fixture
    def sample_decision_data(self):
        """Sample decision data"""
        return {
            'id': 'decision_123',
            'title': 'Adopt New Framework',
            'description': 'Decision to adopt the new development framework',
            'meeting_id': 'meeting_123',
            'decision_maker': 'John Doe',
            'stakeholders': ['Engineering Team', 'Product Team'],
            'priority': 'High',
            'status': 'Approved',
            'implementation_date': datetime(2024, 2, 1),
            'rationale': 'Framework will improve development velocity',
            'impact_assessment': 'Positive impact on team productivity',
            'success_criteria': 'Reduce development time by 20%',
            'tags': ['framework', 'development', 'productivity']
        }
    
    @pytest.fixture
    def sample_notion_page(self):
        """Sample Notion page response"""
        return {
            'id': 'page_123',
            'url': 'https://notion.so/page_123',
            'last_edited_time': '2024-01-15T10:00:00.000Z',
            'properties': {
                'Meeting ID': {
                    'type': 'title',
                    'title': [{'type': 'text', 'text': {'content': 'meeting_123'}, 'plain_text': 'meeting_123'}]
                },
                'Title': {
                    'type': 'rich_text',
                    'rich_text': [{'type': 'text', 'text': {'content': 'Weekly Team Standup'}, 'plain_text': 'Weekly Team Standup'}]
                },
                'Status': {
                    'type': 'select',
                    'select': {'name': 'Completed'}
                },
                'Participants': {
                    'type': 'multi_select',
                    'multi_select': [
                        {'name': 'John Doe'},
                        {'name': 'Jane Smith'},
                        {'name': 'Bob Wilson'}
                    ]
                }
            }
        }
    
    def test_notion_service_initialization(self, notion_service):
        """Test Notion service initialization"""
        assert notion_service is not None
        assert notion_service.base_url == 'https://api.notion.com/v1'
        assert notion_service.notion_version == '2022-06-28'
        assert len(notion_service.database_configs) == 6
        assert len(notion_service.field_mappings) == 6
        assert len(notion_service.transformers) > 0
        
        # Check database configurations
        expected_databases = ['meetings', 'decisions', 'actions', 'insights', 'solutions', 'human_needs']
        for db_type in expected_databases:
            assert db_type in notion_service.database_configs
            assert db_type in notion_service.field_mappings
    
    def test_database_configs_structure(self, notion_service):
        """Test database configuration structure"""
        for db_type, config in notion_service.database_configs.items():
            assert 'name' in config
            assert 'description' in config
            assert 'icon' in config
            assert 'properties' in config
            
            # Check properties structure
            properties = config['properties']
            assert len(properties) > 0
            
            for prop_name, prop_config in properties.items():
                assert 'type' in prop_config
                assert isinstance(prop_config['type'], NotionPropertyType)
                assert 'required' in prop_config
    
    def test_field_mappings_structure(self, notion_service):
        """Test field mappings structure"""
        for db_type, mappings in notion_service.field_mappings.items():
            assert len(mappings) > 0
            
            for mapping in mappings:
                assert isinstance(mapping, SyncMapping)
                assert mapping.intelligence_os_field is not None
                assert mapping.notion_property is not None
                assert isinstance(mapping.property_type, NotionPropertyType)
    
    @pytest.mark.asyncio
    async def test_datetime_transformation(self, notion_service):
        """Test datetime transformation functions"""
        test_datetime = datetime(2024, 1, 15, 9, 0, 0)
        
        # Test to Notion
        result_to = await notion_service._datetime_to_notion(test_datetime, 'to_notion')
        assert isinstance(result_to, str)
        assert '2024-01-15' in result_to
        
        # Test from Notion
        result_from = await notion_service._datetime_to_notion('2024-01-15T09:00:00Z', 'from_notion')
        assert isinstance(result_from, datetime)
        assert result_from.year == 2024
        assert result_from.month == 1
        assert result_from.day == 15
    
    @pytest.mark.asyncio
    async def test_text_to_rich_text_transformation(self, notion_service):
        """Test text to rich text transformation"""
        test_text = "This is a test text"
        
        # Test to Notion
        result_to = await notion_service._text_to_rich_text(test_text, 'to_notion')
        assert isinstance(result_to, list)
        assert len(result_to) == 1
        assert result_to[0]['type'] == 'text'
        assert result_to[0]['text']['content'] == test_text
        
        # Test from Notion
        notion_rich_text = [{'type': 'text', 'text': {'content': test_text}, 'plain_text': test_text}]
        result_from = await notion_service._text_to_rich_text(notion_rich_text, 'from_notion')
        assert result_from == test_text
    
    @pytest.mark.asyncio
    async def test_list_to_multiselect_transformation(self, notion_service):
        """Test list to multi-select transformation"""
        test_list = ['Option 1', 'Option 2', 'Option 3']
        
        # Test to Notion
        result_to = await notion_service._list_to_multiselect(test_list, 'to_notion')
        assert isinstance(result_to, list)
        assert len(result_to) == 3
        assert all('name' in item for item in result_to)
        assert result_to[0]['name'] == 'Option 1'
        
        # Test from Notion
        notion_multiselect = [{'name': 'Option 1'}, {'name': 'Option 2'}, {'name': 'Option 3'}]
        result_from = await notion_service._list_to_multiselect(notion_multiselect, 'from_notion')
        assert result_from == test_list
    
    @pytest.mark.asyncio
    async def test_transform_to_notion(self, notion_service, sample_meeting_data):
        """Test data transformation to Notion format"""
        mappings = notion_service.field_mappings['meetings']
        
        result = await notion_service._transform_to_notion(sample_meeting_data, mappings)
        
        assert isinstance(result, dict)
        assert 'Meeting ID' in result
        assert 'Title' in result
        assert 'Status' in result
        
        # Check title property
        title_prop = result['Meeting ID']
        assert title_prop['title'][0]['text']['content'] == 'meeting_123'
        
        # Check rich text property
        title_rich_text = result['Title']
        assert title_rich_text['rich_text'][0]['text']['content'] == 'Weekly Team Standup'
        
        # Check select property
        status_prop = result['Status']
        assert status_prop['select']['name'] == 'Completed'
    
    @pytest.mark.asyncio
    async def test_transform_from_notion(self, notion_service, sample_notion_page):
        """Test data transformation from Notion format"""
        mappings = notion_service.field_mappings['meetings']
        
        result = await notion_service._transform_from_notion(sample_notion_page['properties'], mappings)
        
        assert isinstance(result, dict)
        assert result['id'] == 'meeting_123'
        assert result['title'] == 'Weekly Team Standup'
        assert result['status'] == 'Completed'
        assert 'participants' in result
        assert len(result['participants']) == 3
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.post')
    async def test_create_notion_page(self, mock_post, notion_service):
        """Test Notion page creation"""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'id': 'page_123',
            'url': 'https://notion.so/page_123'
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Initialize session
        await notion_service.initialize_session()
        
        properties = {
            'Meeting ID': {
                'title': [{'type': 'text', 'text': {'content': 'meeting_123'}}]
            }
        }
        
        result = await notion_service._create_notion_page('database_123', properties)
        
        assert result['success'] is True
        assert result['page_id'] == 'page_123'
        assert 'url' in result
        
        await notion_service.close_session()
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.patch')
    async def test_update_notion_page(self, mock_patch, notion_service):
        """Test Notion page update"""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'id': 'page_123',
            'url': 'https://notion.so/page_123'
        })
        mock_patch.return_value.__aenter__.return_value = mock_response
        
        # Initialize session
        await notion_service.initialize_session()
        
        properties = {
            'Status': {
                'select': {'name': 'Updated'}
            }
        }
        
        result = await notion_service._update_notion_page('page_123', properties)
        
        assert result['success'] is True
        assert result['page_id'] == 'page_123'
        
        await notion_service.close_session()
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_get_notion_page(self, mock_get, notion_service, sample_notion_page):
        """Test Notion page retrieval"""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_notion_page)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Initialize session
        await notion_service.initialize_session()
        
        result = await notion_service._get_notion_page('page_123')
        
        assert result is not None
        assert result['id'] == 'page_123'
        assert 'properties' in result
        
        await notion_service.close_session()
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.post')
    async def test_get_database_pages(self, mock_post, notion_service, sample_notion_page):
        """Test database pages retrieval"""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'results': [sample_notion_page],
            'has_more': False,
            'next_cursor': None
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Initialize session
        await notion_service.initialize_session()
        
        result = await notion_service._get_database_pages('database_123')
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['id'] == 'page_123'
        
        await notion_service.close_session()
    
    @pytest.mark.asyncio
    async def test_check_for_conflicts(self, notion_service):
        """Test conflict detection"""
        # Mock local data
        with patch.object(notion_service, '_get_local_record') as mock_local:
            with patch.object(notion_service, '_get_last_sync_time') as mock_sync_time:
                mock_local.return_value = {
                    'id': 'meeting_123',
                    'title': 'Old Title',
                    'status': 'In Progress',
                    'last_modified': datetime.utcnow()
                }
                mock_sync_time.return_value = datetime.utcnow() - timedelta(hours=1)
                
                intelligence_os_data = {
                    'id': 'meeting_123',
                    'title': 'New Title',
                    'status': 'Completed'
                }
                
                notion_page = {
                    'id': 'page_123',
                    'last_edited_time': datetime.utcnow().isoformat()
                }
                
                conflict = await notion_service._check_for_conflicts(
                    'meetings', intelligence_os_data, notion_page
                )
                
                assert conflict is not None
                assert isinstance(conflict, ConflictRecord)
                assert conflict.database_type == 'meetings'
                assert conflict.record_id == 'meeting_123'
                assert len(conflict.conflict_fields) > 0
    
    @pytest.mark.asyncio
    async def test_handle_conflict_latest_wins(self, notion_service):
        """Test conflict resolution with latest wins strategy"""
        conflict = ConflictRecord(
            id='conflict_123',
            database_type='meetings',
            record_id='meeting_123',
            notion_page_id='page_123',
            intelligence_os_data={
                'id': 'meeting_123',
                'title': 'Old Title',
                'last_modified': datetime.utcnow() - timedelta(hours=1)
            },
            notion_data={
                'id': 'meeting_123',
                'title': 'New Title'
            },
            conflict_fields=['title'],
            resolution_strategy=ConflictResolution.LATEST_WINS,
            created_at=datetime.utcnow()
        )
        
        result = await notion_service._handle_conflict(conflict)
        
        assert result['resolved'] is True
        assert 'resolved_data' in result
        assert result['strategy'] == 'latest_wins'
    
    @pytest.mark.asyncio
    async def test_merge_conflicting_fields(self, notion_service):
        """Test field merging for conflicts"""
        conflict = ConflictRecord(
            id='conflict_123',
            database_type='meetings',
            record_id='meeting_123',
            notion_page_id='page_123',
            intelligence_os_data={
                'id': 'meeting_123',
                'tags': ['tag1', 'tag2'],
                'description': 'Original description',
                'status': 'In Progress'
            },
            notion_data={
                'id': 'meeting_123',
                'tags': ['tag2', 'tag3'],
                'description': 'Updated description',
                'status': 'Completed'
            },
            conflict_fields=['tags', 'description', 'status'],
            resolution_strategy=ConflictResolution.MERGE_FIELDS,
            created_at=datetime.utcnow()
        )
        
        merged_data = await notion_service._merge_conflicting_fields(conflict)
        
        assert 'tag1' in merged_data['tags']
        assert 'tag2' in merged_data['tags']
        assert 'tag3' in merged_data['tags']
        assert 'Original description' in merged_data['description']
        assert 'Updated description' in merged_data['description']
        assert merged_data['status'] == 'Completed'  # Notion wins for status
    
    @pytest.mark.asyncio
    async def test_sync_to_notion(self, notion_service, sample_meeting_data):
        """Test synchronization to Notion"""
        # Mock database schema
        notion_service.database_schemas['meetings'] = NotionDatabaseSchema(
            database_id='database_123',
            name='Meetings',
            properties={},
            title_property='Meeting ID'
        )
        
        with patch.object(notion_service, '_find_notion_page') as mock_find:
            with patch.object(notion_service, '_create_notion_page') as mock_create:
                mock_find.return_value = None  # No existing page
                mock_create.return_value = {
                    'success': True,
                    'page_id': 'page_123',
                    'url': 'https://notion.so/page_123'
                }
                
                result = await notion_service.sync_to_notion('meetings', sample_meeting_data, 'meeting_123')
                
                assert result['success'] is True
                assert result['page_id'] == 'page_123'
                
                # Check sync record was created
                sync_records = [r for r in notion_service.sync_records.values() 
                              if r.database_type == 'meetings' and r.record_id == 'meeting_123']
                assert len(sync_records) == 1
                assert sync_records[0].direction == SyncDirection.TO_NOTION
                assert sync_records[0].status == SyncStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_sync_from_notion(self, notion_service, sample_notion_page):
        """Test synchronization from Notion"""
        # Mock database schema
        notion_service.database_schemas['meetings'] = NotionDatabaseSchema(
            database_id='database_123',
            name='Meetings',
            properties={},
            title_property='Meeting ID'
        )
        
        with patch.object(notion_service, '_get_database_pages') as mock_pages:
            with patch.object(notion_service, '_check_for_conflicts') as mock_conflicts:
                with patch.object(notion_service, '_update_intelligence_os_data') as mock_update:
                    mock_pages.return_value = [sample_notion_page]
                    mock_conflicts.return_value = None  # No conflicts
                    mock_update.return_value = {'success': True}
                    
                    result = await notion_service.sync_from_notion('meetings')
                    
                    assert result['success'] is True
                    assert result['records_synced'] == 1
                    assert len(result['data']) == 1
    
    @pytest.mark.asyncio
    async def test_bidirectional_sync(self, notion_service):
        """Test bidirectional synchronization"""
        with patch.object(notion_service, 'sync_from_notion') as mock_from:
            with patch.object(notion_service, '_get_local_records') as mock_local:
                with patch.object(notion_service, 'sync_to_notion') as mock_to:
                    mock_from.return_value = {
                        'success': True,
                        'records_synced': 2,
                        'data': []
                    }
                    mock_local.return_value = [{'id': 'meeting_123'}]
                    mock_to.return_value = {'success': True}
                    
                    result = await notion_service.bidirectional_sync('meetings')
                    
                    assert result['success'] is True
                    assert 'from_notion' in result
                    assert 'to_notion' in result
                    assert 'sync_timestamp' in result
    
    @pytest.mark.asyncio
    async def test_get_sync_status(self, notion_service):
        """Test sync status retrieval"""
        # Add some test sync records
        notion_service.sync_records['sync_1'] = SyncRecord(
            id='sync_1',
            database_type='meetings',
            record_id='meeting_123',
            notion_page_id='page_123',
            direction=SyncDirection.TO_NOTION,
            status=SyncStatus.COMPLETED,
            last_sync=datetime.utcnow()
        )
        
        notion_service.sync_records['sync_2'] = SyncRecord(
            id='sync_2',
            database_type='meetings',
            record_id='meeting_456',
            notion_page_id='page_456',
            direction=SyncDirection.FROM_NOTION,
            status=SyncStatus.FAILED,
            last_sync=datetime.utcnow()
        )
        
        status = await notion_service.get_sync_status('meetings')
        
        assert status['database_type'] == 'meetings'
        assert status['total_records'] == 2
        assert 'status_breakdown' in status
        assert status['status_breakdown']['completed'] == 1
        assert status['status_breakdown']['failed'] == 1
        assert status['conflicts'] == 0
    
    @pytest.mark.asyncio
    async def test_get_conflicts(self, notion_service):
        """Test conflicts retrieval"""
        # Add test conflict
        notion_service.conflict_records['conflict_1'] = ConflictRecord(
            id='conflict_1',
            database_type='meetings',
            record_id='meeting_123',
            notion_page_id='page_123',
            intelligence_os_data={},
            notion_data={},
            conflict_fields=['title'],
            resolution_strategy=ConflictResolution.LATEST_WINS,
            created_at=datetime.utcnow()
        )
        
        conflicts = await notion_service.get_conflicts()
        
        assert len(conflicts) == 1
        assert conflicts[0]['id'] == 'conflict_1'
        assert conflicts[0]['database_type'] == 'meetings'
        assert conflicts[0]['conflict_fields'] == ['title']
    
    @pytest.mark.asyncio
    async def test_resolve_conflict(self, notion_service):
        """Test manual conflict resolution"""
        # Add test conflict
        conflict = ConflictRecord(
            id='conflict_1',
            database_type='meetings',
            record_id='meeting_123',
            notion_page_id='page_123',
            intelligence_os_data={'title': 'Old Title'},
            notion_data={'title': 'New Title'},
            conflict_fields=['title'],
            resolution_strategy=ConflictResolution.MANUAL_REVIEW,
            created_at=datetime.utcnow()
        )
        
        notion_service.conflict_records['conflict_1'] = conflict
        
        result = await notion_service.resolve_conflict('conflict_1', ConflictResolution.NOTION_WINS)
        
        assert result['success'] is True
        assert result['conflict_id'] == 'conflict_1'
        assert result['resolution_strategy'] == 'notion_wins'
    
    def test_find_title_property(self, notion_service):
        """Test title property identification"""
        properties = {
            'Name': {'type': 'rich_text'},
            'Title': {'type': 'title'},
            'Status': {'type': 'select'}
        }
        
        title_prop = notion_service._find_title_property(properties)
        assert title_prop == 'Title'
        
        # Test fallback
        properties_no_title = {
            'Name': {'type': 'rich_text'},
            'Status': {'type': 'select'}
        }
        
        title_prop_fallback = notion_service._find_title_property(properties_no_title)
        assert title_prop_fallback == 'Name'
    
    def test_global_instance(self):
        """Test global Notion service instance"""
        assert notion_integration_service is not None
        assert isinstance(notion_integration_service, NotionIntegrationService)

if __name__ == '__main__':
    pytest.main([__file__])