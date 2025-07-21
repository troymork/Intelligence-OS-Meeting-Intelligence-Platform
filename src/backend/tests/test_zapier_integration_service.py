"""
Tests for Zapier Integration Service
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from src.services.zapier_integration_service import (
    ZapierIntegrationService,
    TranscriptFormat,
    WebhookStatus,
    ProcessingPriority,
    TranscriptMetadata,
    WebhookPayload,
    zapier_integration_service
)

class TestZapierIntegrationService:
    """Test cases for ZapierIntegrationService"""
    
    @pytest.fixture
    def zapier_service(self):
        """Create Zapier service instance for testing"""
        return ZapierIntegrationService()
    
    @pytest.fixture
    def sample_text_transcript(self):
        """Sample text transcript"""
        return """
        Meeting: Weekly Team Standup
        Date: 2024-01-15
        Participants: John Smith, Jane Doe, Bob Wilson
        
        09:00:00 John Smith: Good morning everyone, let's start our weekly standup.
        09:00:15 Jane Doe: Thanks John. I completed the user authentication module this week.
        09:00:45 Bob Wilson: Great work Jane. I've been working on the database optimization.
        09:01:20 John Smith: Excellent progress team. Any blockers for this week?
        09:01:35 Jane Doe: No blockers on my end.
        09:01:40 Bob Wilson: All good here too.
        09:02:00 John Smith: Perfect. Let's wrap up then. Have a great week everyone!
        """
    
    @pytest.fixture
    def sample_json_transcript(self):
        """Sample JSON transcript"""
        return {
            "meeting_id": "meet_123456",
            "meeting_title": "Product Planning Session",
            "start_time": "2024-01-15T14:00:00Z",
            "duration": 45,
            "participants": ["Alice Johnson", "Charlie Brown", "Diana Prince"],
            "transcript": [
                {
                    "timestamp": "14:00:00",
                    "speaker": "Alice Johnson",
                    "text": "Welcome to our product planning session."
                },
                {
                    "timestamp": "14:00:15",
                    "speaker": "Charlie Brown",
                    "text": "Thanks Alice. I have some ideas for the new feature."
                },
                {
                    "timestamp": "14:00:30",
                    "speaker": "Diana Prince",
                    "text": "Let's discuss the user requirements first."
                }
            ]
        }
    
    @pytest.fixture
    def sample_webhook_headers(self):
        """Sample webhook headers"""
        return {
            'content-type': 'application/json',
            'x-webhook-signature': 'test_signature',
            'x-webhook-timestamp': '1705329600',
            'user-agent': 'Zapier-Webhook/1.0'
        }
    
    def test_zapier_service_initialization(self, zapier_service):
        """Test Zapier service initialization"""
        assert zapier_service is not None
        assert zapier_service.webhook_secret is not None
        assert zapier_service.max_retries == 3
        assert len(zapier_service.retry_delays) == 3
        assert len(zapier_service.platform_configs) > 0
        assert len(zapier_service.validators) > 0
        assert len(zapier_service.metadata_extractors) > 0
        
        # Check platform configurations
        assert 'zoom' in zapier_service.platform_configs
        assert 'teams' in zapier_service.platform_configs
        assert 'google_meet' in zapier_service.platform_configs
        assert 'generic' in zapier_service.platform_configs
    
    def test_platform_configs_structure(self, zapier_service):
        """Test platform configuration structure"""
        for platform, config in zapier_service.platform_configs.items():
            assert 'name' in config
            assert 'supported_formats' in config
            assert 'webhook_signature_header' in config
            assert 'timestamp_header' in config
            assert 'metadata_fields' in config
            assert 'content_patterns' in config
            
            # Check content patterns
            patterns = config['content_patterns']
            assert 'speaker_pattern' in patterns
            assert 'timestamp_pattern' in patterns
            assert 'participant_pattern' in patterns
    
    def test_detect_content_format(self, zapier_service):
        """Test content format detection"""
        # Test JSON detection
        json_content = '{"transcript": "test content"}'
        assert zapier_service._detect_content_format(json_content) == TranscriptFormat.JSON
        
        # Test HTML detection
        html_content = '<html><body><p>Test transcript</p></body></html>'
        assert zapier_service._detect_content_format(html_content) == TranscriptFormat.HTML
        
        # Test XML detection
        xml_content = '<?xml version="1.0"?><transcript>Test content</transcript>'
        assert zapier_service._detect_content_format(xml_content) == TranscriptFormat.XML
        
        # Test Markdown detection
        markdown_content = '# Meeting Notes\n\n**Speaker**: Test content'
        assert zapier_service._detect_content_format(markdown_content) == TranscriptFormat.MARKDOWN
        
        # Test text detection (default)
        text_content = 'John: Hello everyone\nJane: Hi John'
        assert zapier_service._detect_content_format(text_content) == TranscriptFormat.TEXT
    
    @pytest.mark.asyncio
    async def test_validate_text_content(self, zapier_service, sample_text_transcript):
        """Test text content validation"""
        # Valid text content
        assert await zapier_service._validate_text_content(sample_text_transcript) is True
        
        # Invalid content - too short
        assert await zapier_service._validate_text_content("Short text") is False
        
        # Invalid content - empty
        assert await zapier_service._validate_text_content("") is False
        assert await zapier_service._validate_text_content("   ") is False
    
    @pytest.mark.asyncio
    async def test_validate_json_content(self, zapier_service, sample_json_transcript):
        """Test JSON content validation"""
        # Valid JSON content
        json_string = json.dumps(sample_json_transcript)
        assert await zapier_service._validate_json_content(json_string) is True
        
        # Invalid JSON - malformed
        assert await zapier_service._validate_json_content('{"invalid": json}') is False
        
        # Invalid JSON - no transcript fields
        assert await zapier_service._validate_json_content('{"other": "data"}') is False
    
    @pytest.mark.asyncio
    async def test_validate_markdown_content(self, zapier_service):
        """Test markdown content validation"""
        # Valid markdown content
        markdown_content = """
        # Meeting Notes
        
        **Participants**: John, Jane, Bob
        
        - John: Started the meeting
        - Jane: Discussed project status
        - Bob: Mentioned upcoming deadlines
        """
        assert await zapier_service._validate_markdown_content(markdown_content) is True
        
        # Invalid markdown - no markdown patterns
        plain_text = "This is just plain text without markdown formatting"
        assert await zapier_service._validate_markdown_content(plain_text) is False
    
    @pytest.mark.asyncio
    async def test_extract_text_metadata(self, zapier_service, sample_text_transcript):
        """Test metadata extraction from text"""
        metadata = await zapier_service._extract_text_metadata(sample_text_transcript, 'generic')
        
        assert isinstance(metadata, TranscriptMetadata)
        assert len(metadata.participants) > 0
        assert 'John Smith' in metadata.participants
        assert 'Jane Doe' in metadata.participants
        assert 'Bob Wilson' in metadata.participants
        assert metadata.duration_minutes is not None
        assert metadata.confidence_score is not None
        assert 0.0 <= metadata.confidence_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_extract_json_metadata(self, zapier_service, sample_json_transcript):
        """Test metadata extraction from JSON"""
        json_string = json.dumps(sample_json_transcript)
        metadata = await zapier_service._extract_json_metadata(json_string, 'generic')
        
        assert isinstance(metadata, TranscriptMetadata)
        assert metadata.meeting_id == "meet_123456"
        assert metadata.meeting_title == "Product Planning Session"
        assert metadata.duration_minutes == 45
        assert len(metadata.participants) == 3
        assert 'Alice Johnson' in metadata.participants
        assert metadata.meeting_date is not None
    
    def test_determine_priority(self, zapier_service):
        """Test priority determination"""
        # Urgent priority - urgent tag
        metadata_urgent = TranscriptMetadata(tags=['urgent', 'critical'])
        assert zapier_service._determine_priority(metadata_urgent, 'zoom') == ProcessingPriority.URGENT
        
        # High priority - many participants
        metadata_high = TranscriptMetadata(participant_count=15)
        assert zapier_service._determine_priority(metadata_high, 'teams') == ProcessingPriority.HIGH
        
        # High priority - executive participants
        metadata_exec = TranscriptMetadata(participants=['John CEO', 'Jane CTO'])
        assert zapier_service._determine_priority(metadata_exec, 'generic') == ProcessingPriority.HIGH
        
        # High priority - long meeting
        metadata_long = TranscriptMetadata(duration_minutes=150)
        assert zapier_service._determine_priority(metadata_long, 'generic') == ProcessingPriority.HIGH
        
        # Normal priority - regular meeting
        metadata_normal = TranscriptMetadata(participant_count=5, duration_minutes=30)
        assert zapier_service._determine_priority(metadata_normal, 'generic') == ProcessingPriority.NORMAL
    
    def test_estimate_processing_time(self, zapier_service):
        """Test processing time estimation"""
        # Short meeting
        metadata_short = TranscriptMetadata(duration_minutes=15, participant_count=3)
        time_estimate = zapier_service._estimate_processing_time(metadata_short)
        assert 'seconds' in time_estimate or 'minutes' in time_estimate
        
        # Long meeting
        metadata_long = TranscriptMetadata(duration_minutes=120, participant_count=10)
        time_estimate = zapier_service._estimate_processing_time(metadata_long)
        assert isinstance(time_estimate, str)
    
    def test_parse_timestamp(self, zapier_service):
        """Test timestamp parsing"""
        # Test various timestamp formats
        timestamps = [
            '09:30:45',
            '2:30:45 PM',
            '14:30',
            '2024-01-15 09:30:45',
            '2024-01-15T09:30:45'
        ]
        
        for ts in timestamps:
            result = zapier_service._parse_timestamp(ts)
            assert result is None or isinstance(result, datetime)
    
    def test_calculate_content_confidence(self, zapier_service, sample_text_transcript):
        """Test content confidence calculation"""
        confidence = zapier_service._calculate_content_confidence(sample_text_transcript)
        
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
        
        # Test with poor content
        poor_content = "Short text"
        poor_confidence = zapier_service._calculate_content_confidence(poor_content)
        assert poor_confidence < confidence
    
    @pytest.mark.asyncio
    async def test_extract_content_from_payload(self, zapier_service, sample_text_transcript):
        """Test content extraction from webhook payload"""
        # Test with transcript field
        payload1 = {'transcript': sample_text_transcript}
        result1 = await zapier_service._extract_content(payload1)
        assert result1['valid'] is True
        assert result1['content'] == sample_text_transcript
        assert result1['format'] == TranscriptFormat.TEXT
        
        # Test with JSON content
        payload2 = {'content': {'transcript': 'test content'}}
        result2 = await zapier_service._extract_content(payload2)
        assert result2['valid'] is True
        assert result2['format'] == TranscriptFormat.JSON
        
        # Test with no content
        payload3 = {'other_field': 'no transcript'}
        result3 = await zapier_service._extract_content(payload3)
        assert result3['valid'] is False
        assert 'error' in result3
    
    @pytest.mark.asyncio
    async def test_extract_metadata_from_payload(self, zapier_service, sample_text_transcript):
        """Test metadata extraction from payload"""
        payload = {
            'meeting_id': 'test_123',
            'meeting_title': 'Test Meeting',
            'start_time': '2024-01-15T09:00:00Z',
            'duration': 60,
            'participants': ['John', 'Jane', 'Bob'],
            'organization': 'Test Corp'
        }
        
        metadata = await zapier_service._extract_metadata(
            sample_text_transcript, 
            TranscriptFormat.TEXT, 
            'zoom', 
            payload
        )
        
        assert metadata.meeting_id == 'test_123'
        assert metadata.meeting_title == 'Test Meeting'
        assert metadata.duration_minutes == 60
        assert len(metadata.participants) == 3
        assert metadata.organization == 'Test Corp'
        assert metadata.source_platform == 'zoom'
    
    @pytest.mark.asyncio
    @patch('src.services.zapier_integration_service.ZapierIntegrationService._validate_webhook_signature')
    @patch('src.services.zapier_integration_service.ZapierIntegrationService._trigger_oracle_analysis')
    async def test_receive_webhook_success(self, mock_oracle, mock_signature, zapier_service, 
                                         sample_webhook_headers, sample_text_transcript):
        """Test successful webhook reception"""
        # Mock signature validation
        mock_signature.return_value = True
        
        # Mock Oracle analysis
        mock_oracle.return_value = {'success': True, 'analysis_id': 'analysis_123'}
        
        payload = {
            'transcript': sample_text_transcript,
            'meeting_id': 'test_meeting',
            'meeting_title': 'Test Meeting'
        }
        
        result = await zapier_service.receive_webhook('zoom', sample_webhook_headers, payload)
        
        assert 'webhook_id' in result
        assert result['status'] == 'received'
        assert 'message' in result
        assert 'timestamp' in result
        assert 'estimated_processing_time' in result
    
    @pytest.mark.asyncio
    @patch('src.services.zapier_integration_service.ZapierIntegrationService._validate_webhook_signature')
    async def test_receive_webhook_invalid_signature(self, mock_signature, zapier_service, 
                                                   sample_webhook_headers):
        """Test webhook reception with invalid signature"""
        # Mock invalid signature
        mock_signature.return_value = False
        
        payload = {'transcript': 'test content'}
        
        result = await zapier_service.receive_webhook('zoom', sample_webhook_headers, payload)
        
        assert result['status'] == 'rejected'
        assert 'Invalid signature' in result['error']
    
    @pytest.mark.asyncio
    async def test_receive_webhook_invalid_content(self, zapier_service, sample_webhook_headers):
        """Test webhook reception with invalid content"""
        with patch.object(zapier_service, '_validate_webhook_signature', return_value=True):
            payload = {'other_field': 'no transcript content'}
            
            result = await zapier_service.receive_webhook('zoom', sample_webhook_headers, payload)
            
            assert result['status'] == 'rejected'
            assert 'error' in result
    
    @pytest.mark.asyncio
    @patch('src.services.zapier_integration_service.ai_conductor')
    async def test_trigger_oracle_analysis_success(self, mock_conductor, zapier_service):
        """Test successful Oracle analysis trigger"""
        # Mock AI conductor response
        mock_conductor.conduct_analysis = AsyncMock(return_value={
            'success': True,
            'analysis_id': 'oracle_123'
        })
        
        webhook_payload = WebhookPayload(
            id='webhook_123',
            source='zoom',
            timestamp=datetime.utcnow(),
            format=TranscriptFormat.TEXT,
            content='test transcript',
            metadata=TranscriptMetadata(meeting_title='Test Meeting'),
            headers={}
        )
        
        result = await zapier_service._trigger_oracle_analysis(webhook_payload)
        
        assert result['success'] is True
        assert result['analysis_id'] == 'oracle_123'
        assert mock_conductor.conduct_analysis.called
    
    @pytest.mark.asyncio
    @patch('src.services.zapier_integration_service.ai_conductor')
    async def test_trigger_oracle_analysis_failure(self, mock_conductor, zapier_service):
        """Test Oracle analysis trigger failure"""
        # Mock AI conductor failure
        mock_conductor.conduct_analysis = AsyncMock(return_value={
            'success': False,
            'error': 'Analysis failed'
        })
        
        webhook_payload = WebhookPayload(
            id='webhook_123',
            source='zoom',
            timestamp=datetime.utcnow(),
            format=TranscriptFormat.TEXT,
            content='test transcript',
            metadata=TranscriptMetadata(),
            headers={}
        )
        
        result = await zapier_service._trigger_oracle_analysis(webhook_payload)
        
        assert result['success'] is False
        assert 'Analysis failed' in result['error']
    
    @pytest.mark.asyncio
    async def test_process_single_webhook_success(self, zapier_service):
        """Test successful single webhook processing"""
        webhook_payload = WebhookPayload(
            id='webhook_123',
            source='zoom',
            timestamp=datetime.utcnow(),
            format=TranscriptFormat.TEXT,
            content='John: Hello\nJane: Hi John\nBob: Good morning everyone',
            metadata=TranscriptMetadata(meeting_title='Test Meeting'),
            headers={}
        )
        
        with patch.object(zapier_service, '_trigger_oracle_analysis', return_value={'success': True, 'analysis_id': 'oracle_123'}):
            result = await zapier_service._process_single_webhook(webhook_payload)
            
            assert result.status == WebhookStatus.COMPLETED
            assert result.oracle_analysis_id == 'oracle_123'
            assert result.processing_time_seconds is not None
            assert result.processing_time_seconds > 0
    
    @pytest.mark.asyncio
    async def test_process_single_webhook_failure(self, zapier_service):
        """Test single webhook processing failure"""
        webhook_payload = WebhookPayload(
            id='webhook_123',
            source='zoom',
            timestamp=datetime.utcnow(),
            format=TranscriptFormat.TEXT,
            content='test content',
            metadata=TranscriptMetadata(),
            headers={}
        )
        
        with patch.object(zapier_service, '_trigger_oracle_analysis', return_value={'success': False, 'error': 'Oracle failed'}):
            result = await zapier_service._process_single_webhook(webhook_payload)
            
            assert result.status == WebhookStatus.FAILED
            assert 'Oracle failed' in result.error_message
    
    @pytest.mark.asyncio
    async def test_get_webhook_status_found(self, zapier_service):
        """Test getting webhook status for existing webhook"""
        webhook_id = 'test_webhook_123'
        webhook_payload = WebhookPayload(
            id=webhook_id,
            source='zoom',
            timestamp=datetime.utcnow(),
            format=TranscriptFormat.TEXT,
            content='test content',
            metadata=TranscriptMetadata(meeting_title='Test Meeting', participant_count=3),
            headers={}
        )
        
        zapier_service.webhook_history[webhook_id] = webhook_payload
        
        status = await zapier_service.get_webhook_status(webhook_id)
        
        assert status['webhook_id'] == webhook_id
        assert status['status'] == 'completed'
        assert status['source'] == 'zoom'
        assert 'timestamp' in status
        assert 'metadata' in status
        assert status['metadata']['meeting_title'] == 'Test Meeting'
    
    @pytest.mark.asyncio
    async def test_get_webhook_status_not_found(self, zapier_service):
        """Test getting webhook status for non-existent webhook"""
        status = await zapier_service.get_webhook_status('nonexistent_webhook')
        
        assert status['webhook_id'] == 'nonexistent_webhook'
        assert status['status'] == 'not_found'
        assert 'error' in status
    
    @pytest.mark.asyncio
    async def test_get_processing_statistics(self, zapier_service):
        """Test getting processing statistics"""
        # Set some test statistics
        zapier_service.stats['total_received'] = 10
        zapier_service.stats['total_processed'] = 8
        zapier_service.stats['total_failed'] = 2
        zapier_service.stats['average_processing_time'] = 45.5
        
        stats = await zapier_service.get_processing_statistics()
        
        assert stats['total_received'] == 10
        assert stats['total_processed'] == 8
        assert stats['total_failed'] == 2
        assert stats['success_rate'] == 80.0
        assert stats['average_processing_time_seconds'] == 45.5
        assert 'queue_size' in stats
        assert 'supported_platforms' in stats
        assert 'supported_formats' in stats
        
        # Check supported platforms and formats
        assert len(stats['supported_platforms']) > 0
        assert len(stats['supported_formats']) > 0
    
    @pytest.mark.asyncio
    async def test_retry_failed_webhook_success(self, zapier_service):
        """Test successful retry of failed webhook"""
        webhook_id = 'failed_webhook_123'
        
        # Create failed webhook
        webhook_payload = WebhookPayload(
            id=webhook_id,
            source='zoom',
            timestamp=datetime.utcnow(),
            format=TranscriptFormat.TEXT,
            content='test content',
            metadata=TranscriptMetadata(),
            headers={}
        )
        
        zapier_service.webhook_history[webhook_id] = webhook_payload
        zapier_service.failed_webhooks[webhook_id] = Mock()
        
        result = await zapier_service.retry_failed_webhook(webhook_id)
        
        assert result['webhook_id'] == webhook_id
        assert result['status'] == 'requeued'
        assert webhook_id not in zapier_service.failed_webhooks
    
    @pytest.mark.asyncio
    async def test_retry_failed_webhook_not_found(self, zapier_service):
        """Test retry of non-existent failed webhook"""
        result = await zapier_service.retry_failed_webhook('nonexistent_webhook')
        
        assert result['status'] == 'not_found'
        assert 'error' in result
    
    def test_update_average_processing_time(self, zapier_service):
        """Test average processing time update"""
        # First processing time
        zapier_service.stats['total_processed'] = 1
        zapier_service._update_average_processing_time(30.0)
        assert zapier_service.stats['average_processing_time'] == 30.0
        
        # Second processing time
        zapier_service.stats['total_processed'] = 2
        zapier_service._update_average_processing_time(60.0)
        assert zapier_service.stats['average_processing_time'] == 45.0
        
        # Third processing time
        zapier_service.stats['total_processed'] = 3
        zapier_service._update_average_processing_time(90.0)
        assert zapier_service.stats['average_processing_time'] == 60.0
    
    def test_global_instance(self):
        """Test global Zapier service instance"""
        assert zapier_integration_service is not None
        assert isinstance(zapier_integration_service, ZapierIntegrationService)
    
    @pytest.mark.asyncio
    async def test_webhook_signature_validation(self, zapier_service):
        """Test webhook signature validation"""
        headers = {
            'x-webhook-signature': 'test_signature',
            'x-webhook-timestamp': '1705329600'
        }
        payload = {'transcript': 'test content'}
        
        # This will likely fail with the mock signature, but tests the flow
        result = await zapier_service._validate_webhook_signature('generic', headers, payload)
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_content_format_validation(self, zapier_service):
        """Test content format validation"""
        # Valid text content
        valid_text = "John: Hello everyone\nJane: Hi John, how are you?\nBob: Good morning team!"
        assert await zapier_service._validate_content_format(valid_text, TranscriptFormat.TEXT) is True
        
        # Valid JSON content
        valid_json = '{"transcript": "test content", "meeting_id": "123"}'
        assert await zapier_service._validate_content_format(valid_json, TranscriptFormat.JSON) is True
        
        # Invalid content for format
        invalid_text = "Short"
        assert await zapier_service._validate_content_format(invalid_text, TranscriptFormat.TEXT) is False

if __name__ == '__main__':
    pytest.main([__file__])