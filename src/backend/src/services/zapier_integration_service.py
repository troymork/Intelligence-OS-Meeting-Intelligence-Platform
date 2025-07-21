"""
Zapier Integration Service for Intelligence OS
Handles automated transcript processing from external sources via webhooks
"""

import os
import asyncio
import logging
import uuid
import hashlib
import hmac
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import re
import structlog
from collections import defaultdict
import aiohttp
import base64

logger = structlog.get_logger(__name__)

class TranscriptFormat(Enum):
    """Supported transcript formats"""
    MARKDOWN = "markdown"
    TEXT = "text"
    JSON = "json"
    HTML = "html"
    XML = "xml"

class WebhookStatus(Enum):
    """Webhook processing status"""
    RECEIVED = "received"
    VALIDATED = "validated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class ProcessingPriority(Enum):
    """Processing priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class TranscriptMetadata:
    """Metadata extracted from transcript"""
    meeting_id: Optional[str] = None
    meeting_title: Optional[str] = None
    meeting_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    participant_count: Optional[int] = None
    participants: List[str] = field(default_factory=list)
    meeting_type: Optional[str] = None
    organization: Optional[str] = None
    department: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    source_platform: Optional[str] = None
    language: Optional[str] = None
    confidence_score: Optional[float] = None

@dataclass
class WebhookPayload:
    """Webhook payload structure"""
    id: str
    source: str
    timestamp: datetime
    format: TranscriptFormat
    content: str
    metadata: TranscriptMetadata
    headers: Dict[str, str]
    signature: Optional[str] = None
    retry_count: int = 0
    priority: ProcessingPriority = ProcessingPriority.NORMAL

@dataclass
class ProcessingResult:
    """Result of transcript processing"""
    webhook_id: str
    status: WebhookStatus
    oracle_analysis_id: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    next_retry_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class ZapierIntegrationService:
    """Service for handling Zapier webhook integrations"""
    
    def __init__(self):
        self.webhook_secret = os.getenv('ZAPIER_WEBHOOK_SECRET', 'default-secret-key')
        self.max_retries = int(os.getenv('MAX_WEBHOOK_RETRIES', '3'))
        self.retry_delays = [60, 300, 900]  # 1min, 5min, 15min
        
        # Storage for webhook processing
        self.webhook_history = {}
        self.processing_queue = asyncio.Queue()
        self.failed_webhooks = {}
        
        # Processing statistics
        self.stats = {
            'total_received': 0,
            'total_processed': 0,
            'total_failed': 0,
            'average_processing_time': 0.0,
            'last_processed': None
        }
        
        # Supported platforms and their configurations
        self.platform_configs = self._initialize_platform_configs()
        
        # Content validators
        self.validators = self._initialize_validators()
        
        # Metadata extractors
        self.metadata_extractors = self._initialize_metadata_extractors()
    
    def _initialize_platform_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific configurations"""
        return {
            'zoom': {
                'name': 'Zoom',
                'supported_formats': [TranscriptFormat.TEXT, TranscriptFormat.JSON],
                'webhook_signature_header': 'x-zoom-signature',
                'timestamp_header': 'x-zoom-timestamp',
                'metadata_fields': ['meeting_id', 'meeting_title', 'start_time', 'duration', 'participants'],
                'content_patterns': {
                    'speaker_pattern': r'^(\d{2}:\d{2}:\d{2})\s+([^:]+):\s*(.+)$',
                    'timestamp_pattern': r'^\d{2}:\d{2}:\d{2}',
                    'participant_pattern': r'Participants:\s*(.+)'
                }
            },
            'teams': {
                'name': 'Microsoft Teams',
                'supported_formats': [TranscriptFormat.TEXT, TranscriptFormat.JSON],
                'webhook_signature_header': 'x-teams-signature',
                'timestamp_header': 'x-teams-timestamp',
                'metadata_fields': ['meeting_id', 'subject', 'start_time', 'end_time', 'organizer', 'attendees'],
                'content_patterns': {
                    'speaker_pattern': r'^([^:]+):\s*(.+)$',
                    'timestamp_pattern': r'\[(\d{2}:\d{2}:\d{2})\]',
                    'participant_pattern': r'Attendees:\s*(.+)'
                }
            },
            'google_meet': {
                'name': 'Google Meet',
                'supported_formats': [TranscriptFormat.TEXT, TranscriptFormat.JSON],
                'webhook_signature_header': 'x-goog-signature',
                'timestamp_header': 'x-goog-timestamp',
                'metadata_fields': ['meeting_code', 'meeting_title', 'start_time', 'duration', 'participants'],
                'content_patterns': {
                    'speaker_pattern': r'^([^:]+):\s*(.+)$',
                    'timestamp_pattern': r'(\d{1,2}:\d{2}:\d{2}\s*[AP]M)',
                    'participant_pattern': r'Participants:\s*(.+)'
                }
            },
            'webex': {
                'name': 'Cisco Webex',
                'supported_formats': [TranscriptFormat.TEXT, TranscriptFormat.XML],
                'webhook_signature_header': 'x-webex-signature',
                'timestamp_header': 'x-webex-timestamp',
                'metadata_fields': ['meeting_id', 'meeting_title', 'start_time', 'duration', 'host', 'attendees'],
                'content_patterns': {
                    'speaker_pattern': r'^(\d{2}:\d{2}:\d{2})\s+([^:]+):\s*(.+)$',
                    'timestamp_pattern': r'^\d{2}:\d{2}:\d{2}',
                    'participant_pattern': r'Attendees:\s*(.+)'
                }
            },
            'generic': {
                'name': 'Generic Platform',
                'supported_formats': [TranscriptFormat.TEXT, TranscriptFormat.MARKDOWN, TranscriptFormat.JSON],
                'webhook_signature_header': 'x-webhook-signature',
                'timestamp_header': 'x-webhook-timestamp',
                'metadata_fields': ['title', 'date', 'participants'],
                'content_patterns': {
                    'speaker_pattern': r'^([^:]+):\s*(.+)$',
                    'timestamp_pattern': r'(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)',
                    'participant_pattern': r'(?:Participants|Attendees):\s*(.+)'
                }
            }
        }
    
    def _initialize_validators(self) -> Dict[str, callable]:
        """Initialize content validators"""
        return {
            'text': self._validate_text_content,
            'markdown': self._validate_markdown_content,
            'json': self._validate_json_content,
            'html': self._validate_html_content,
            'xml': self._validate_xml_content
        }
    
    def _initialize_metadata_extractors(self) -> Dict[str, callable]:
        """Initialize metadata extractors"""
        return {
            'text': self._extract_text_metadata,
            'markdown': self._extract_markdown_metadata,
            'json': self._extract_json_metadata,
            'html': self._extract_html_metadata,
            'xml': self._extract_xml_metadata
        }
    
    async def receive_webhook(self, source: str, headers: Dict[str, str], 
                            payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive and process incoming webhook from Zapier
        """
        try:
            webhook_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()
            
            logger.info("Webhook received", webhook_id=webhook_id, source=source)
            
            # Validate webhook signature
            if not await self._validate_webhook_signature(source, headers, payload):
                logger.warning("Invalid webhook signature", webhook_id=webhook_id, source=source)
                return {
                    'webhook_id': webhook_id,
                    'status': 'rejected',
                    'error': 'Invalid signature',
                    'timestamp': timestamp.isoformat()
                }
            
            # Extract and validate content
            content_result = await self._extract_content(payload)
            if not content_result['valid']:
                logger.error("Invalid content format", webhook_id=webhook_id, error=content_result['error'])
                return {
                    'webhook_id': webhook_id,
                    'status': 'rejected',
                    'error': content_result['error'],
                    'timestamp': timestamp.isoformat()
                }
            
            # Extract metadata
            metadata = await self._extract_metadata(
                content_result['content'], 
                content_result['format'], 
                source,
                payload
            )
            
            # Create webhook payload
            webhook_payload = WebhookPayload(
                id=webhook_id,
                source=source,
                timestamp=timestamp,
                format=content_result['format'],
                content=content_result['content'],
                metadata=metadata,
                headers=headers,
                signature=headers.get('x-webhook-signature'),
                priority=self._determine_priority(metadata, source)
            )
            
            # Store webhook for processing
            self.webhook_history[webhook_id] = webhook_payload
            
            # Add to processing queue
            await self.processing_queue.put(webhook_payload)
            
            # Update statistics
            self.stats['total_received'] += 1
            
            logger.info("Webhook queued for processing", webhook_id=webhook_id)
            
            return {
                'webhook_id': webhook_id,
                'status': 'received',
                'message': 'Webhook received and queued for processing',
                'timestamp': timestamp.isoformat(),
                'estimated_processing_time': self._estimate_processing_time(metadata)
            }
            
        except Exception as e:
            logger.error("Webhook reception failed", error=str(e), source=source)
            return {
                'webhook_id': str(uuid.uuid4()),
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def process_webhook_queue(self):
        """
        Process webhooks from the queue
        """
        while True:
            try:
                # Get webhook from queue
                webhook_payload = await self.processing_queue.get()
                
                # Process the webhook
                result = await self._process_single_webhook(webhook_payload)
                
                # Handle result
                if result.status == WebhookStatus.FAILED and result.retry_count < self.max_retries:
                    # Schedule retry
                    await self._schedule_retry(webhook_payload, result)
                else:
                    # Mark as completed or permanently failed
                    self.webhook_history[webhook_payload.id] = webhook_payload
                    
                    if result.status == WebhookStatus.COMPLETED:
                        self.stats['total_processed'] += 1
                        self.stats['last_processed'] = datetime.utcnow().isoformat()
                        if result.processing_time_seconds:
                            self._update_average_processing_time(result.processing_time_seconds)
                    else:
                        self.stats['total_failed'] += 1
                        self.failed_webhooks[webhook_payload.id] = result
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error("Queue processing error", error=str(e))
                await asyncio.sleep(5)  # Brief pause before continuing
    
    async def _process_single_webhook(self, webhook_payload: WebhookPayload) -> ProcessingResult:
        """
        Process a single webhook payload
        """
        start_time = datetime.utcnow()
        result = ProcessingResult(
            webhook_id=webhook_payload.id,
            status=WebhookStatus.PROCESSING,
            retry_count=webhook_payload.retry_count
        )
        
        try:
            logger.info("Processing webhook", webhook_id=webhook_payload.id)
            
            # Validate content format
            if not await self._validate_content_format(webhook_payload.content, webhook_payload.format):
                result.status = WebhookStatus.FAILED
                result.error_message = "Invalid content format"
                return result
            
            # Trigger Oracle 9.1 Protocol analysis
            oracle_result = await self._trigger_oracle_analysis(webhook_payload)
            
            if oracle_result['success']:
                result.status = WebhookStatus.COMPLETED
                result.oracle_analysis_id = oracle_result['analysis_id']
                result.completed_at = datetime.utcnow()
                result.processing_time_seconds = (result.completed_at - start_time).total_seconds()
                
                logger.info("Webhook processed successfully", 
                           webhook_id=webhook_payload.id,
                           analysis_id=result.oracle_analysis_id,
                           processing_time=result.processing_time_seconds)
            else:
                result.status = WebhookStatus.FAILED
                result.error_message = oracle_result.get('error', 'Oracle analysis failed')
                
                logger.error("Oracle analysis failed", 
                           webhook_id=webhook_payload.id,
                           error=result.error_message)
            
        except Exception as e:
            result.status = WebhookStatus.FAILED
            result.error_message = str(e)
            logger.error("Webhook processing failed", webhook_id=webhook_payload.id, error=str(e))
        
        return result
    
    async def _validate_webhook_signature(self, source: str, headers: Dict[str, str], 
                                        payload: Dict[str, Any]) -> bool:
        """
        Validate webhook signature for security
        """
        try:
            platform_config = self.platform_configs.get(source, self.platform_configs['generic'])
            signature_header = platform_config['webhook_signature_header']
            timestamp_header = platform_config['timestamp_header']
            
            # Get signature and timestamp from headers
            signature = headers.get(signature_header)
            timestamp = headers.get(timestamp_header)
            
            if not signature:
                logger.warning("Missing webhook signature", source=source)
                return False
            
            # Create expected signature
            payload_string = json.dumps(payload, sort_keys=True)
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                f"{timestamp}{payload_string}".encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error("Signature validation failed", error=str(e), source=source)
            return False
    
    async def _extract_content(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and validate content from webhook payload
        """
        try:
            # Try different content fields
            content_fields = ['transcript', 'content', 'text', 'body', 'data']
            content = None
            content_format = None
            
            for field in content_fields:
                if field in payload and payload[field]:
                    content = payload[field]
                    break
            
            if not content:
                return {'valid': False, 'error': 'No content found in payload'}
            
            # Determine format
            if isinstance(content, dict):
                content_format = TranscriptFormat.JSON
                content = json.dumps(content)
            elif isinstance(content, str):
                # Detect format based on content
                content_format = self._detect_content_format(content)
            else:
                return {'valid': False, 'error': 'Unsupported content type'}
            
            # Validate content
            validator = self.validators.get(content_format.value)
            if validator and not await validator(content):
                return {'valid': False, 'error': f'Invalid {content_format.value} format'}
            
            return {
                'valid': True,
                'content': content,
                'format': content_format
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Content extraction failed: {str(e)}'}
    
    def _detect_content_format(self, content: str) -> TranscriptFormat:
        """
        Detect content format based on content analysis
        """
        content_lower = content.lower().strip()
        
        # Check for JSON
        if content_lower.startswith('{') and content_lower.endswith('}'):
            try:
                json.loads(content)
                return TranscriptFormat.JSON
            except:
                pass
        
        # Check for HTML
        if '<html' in content_lower or '<div' in content_lower or '<p>' in content_lower:
            return TranscriptFormat.HTML
        
        # Check for XML
        if content_lower.startswith('<?xml') or '<transcript>' in content_lower:
            return TranscriptFormat.XML
        
        # Check for Markdown
        if re.search(r'#{1,6}\s', content) or '**' in content or '*' in content:
            return TranscriptFormat.MARKDOWN
        
        # Default to text
        return TranscriptFormat.TEXT
    
    async def _extract_metadata(self, content: str, format: TranscriptFormat, 
                              source: str, payload: Dict[str, Any]) -> TranscriptMetadata:
        """
        Extract metadata from content and payload
        """
        try:
            metadata = TranscriptMetadata()
            
            # Extract from payload first
            metadata.meeting_id = payload.get('meeting_id') or payload.get('id')
            metadata.meeting_title = payload.get('meeting_title') or payload.get('title') or payload.get('subject')
            metadata.source_platform = source
            
            # Parse meeting date
            date_fields = ['meeting_date', 'start_time', 'date', 'timestamp']
            for field in date_fields:
                if field in payload and payload[field]:
                    try:
                        if isinstance(payload[field], str):
                            metadata.meeting_date = datetime.fromisoformat(payload[field].replace('Z', '+00:00'))
                        elif isinstance(payload[field], (int, float)):
                            metadata.meeting_date = datetime.fromtimestamp(payload[field])
                        break
                    except:
                        continue
            
            # Extract duration
            if 'duration' in payload:
                try:
                    metadata.duration_minutes = int(payload['duration'])
                except:
                    pass
            
            # Extract participants
            participant_fields = ['participants', 'attendees', 'members']
            for field in participant_fields:
                if field in payload and payload[field]:
                    if isinstance(payload[field], list):
                        metadata.participants = payload[field]
                    elif isinstance(payload[field], str):
                        metadata.participants = [p.strip() for p in payload[field].split(',')]
                    break
            
            # Extract from content using format-specific extractor
            extractor = self.metadata_extractors.get(format.value)
            if extractor:
                content_metadata = await extractor(content, source)
                
                # Merge content metadata (content takes precedence for some fields)
                if not metadata.participants and content_metadata.participants:
                    metadata.participants = content_metadata.participants
                if not metadata.duration_minutes and content_metadata.duration_minutes:
                    metadata.duration_minutes = content_metadata.duration_minutes
                if content_metadata.confidence_score:
                    metadata.confidence_score = content_metadata.confidence_score
            
            # Set participant count
            if metadata.participants:
                metadata.participant_count = len(metadata.participants)
            
            # Extract additional fields
            metadata.organization = payload.get('organization')
            metadata.department = payload.get('department')
            metadata.meeting_type = payload.get('meeting_type', 'general')
            metadata.language = payload.get('language', 'en')
            
            # Extract tags
            if 'tags' in payload:
                if isinstance(payload['tags'], list):
                    metadata.tags = payload['tags']
                elif isinstance(payload['tags'], str):
                    metadata.tags = [t.strip() for t in payload['tags'].split(',')]
            
            return metadata
            
        except Exception as e:
            logger.error("Metadata extraction failed", error=str(e))
            return TranscriptMetadata(source_platform=source)    

    def _determine_priority(self, metadata: TranscriptMetadata, source: str) -> ProcessingPriority:
        """
        Determine processing priority based on metadata
        """
        try:
            # High priority conditions
            if metadata.meeting_type and 'urgent' in metadata.meeting_type.lower():
                return ProcessingPriority.URGENT
            
            if metadata.tags and any('urgent' in tag.lower() or 'critical' in tag.lower() for tag in metadata.tags):
                return ProcessingPriority.URGENT
            
            if metadata.participant_count and metadata.participant_count > 10:
                return ProcessingPriority.HIGH
            
            # Check for executive or leadership meetings
            if metadata.participants:
                leadership_keywords = ['ceo', 'cto', 'cfo', 'president', 'director', 'vp', 'executive']
                for participant in metadata.participants:
                    if any(keyword in participant.lower() for keyword in leadership_keywords):
                        return ProcessingPriority.HIGH
            
            # Check meeting duration (longer meetings might be more important)
            if metadata.duration_minutes and metadata.duration_minutes > 120:  # 2+ hours
                return ProcessingPriority.HIGH
            
            return ProcessingPriority.NORMAL
            
        except Exception as e:
            logger.error("Priority determination failed", error=str(e))
            return ProcessingPriority.NORMAL
    
    def _estimate_processing_time(self, metadata: TranscriptMetadata) -> str:
        """
        Estimate processing time based on content complexity
        """
        try:
            base_time = 30  # Base 30 seconds
            
            # Add time based on duration
            if metadata.duration_minutes:
                base_time += metadata.duration_minutes * 0.5  # 0.5 seconds per minute
            
            # Add time based on participant count
            if metadata.participant_count:
                base_time += metadata.participant_count * 2  # 2 seconds per participant
            
            # Convert to human-readable format
            if base_time < 60:
                return f"{int(base_time)} seconds"
            elif base_time < 3600:
                return f"{int(base_time / 60)} minutes"
            else:
                return f"{int(base_time / 3600)} hours"
                
        except Exception as e:
            logger.error("Processing time estimation failed", error=str(e))
            return "2-5 minutes"
    
    # Content Validators
    async def _validate_text_content(self, content: str) -> bool:
        """Validate text content"""
        try:
            if not content or not content.strip():
                return False
            
            # Check minimum length
            if len(content.strip()) < 50:
                return False
            
            # Check for basic transcript patterns
            patterns = [
                r'[A-Za-z]+:\s*[A-Za-z]',  # Speaker: Text pattern
                r'\d{1,2}:\d{2}',  # Timestamp pattern
                r'[A-Za-z]{3,}\s+[A-Za-z]{3,}'  # At least some words
            ]
            
            return any(re.search(pattern, content) for pattern in patterns)
            
        except Exception as e:
            logger.error("Text validation failed", error=str(e))
            return False
    
    async def _validate_markdown_content(self, content: str) -> bool:
        """Validate markdown content"""
        try:
            if not await self._validate_text_content(content):
                return False
            
            # Additional markdown-specific checks
            markdown_patterns = [
                r'#{1,6}\s',  # Headers
                r'\*\*[^*]+\*\*',  # Bold text
                r'\*[^*]+\*',  # Italic text
                r'^\s*[-*+]\s',  # List items
            ]
            
            return any(re.search(pattern, content, re.MULTILINE) for pattern in markdown_patterns)
            
        except Exception as e:
            logger.error("Markdown validation failed", error=str(e))
            return False
    
    async def _validate_json_content(self, content: str) -> bool:
        """Validate JSON content"""
        try:
            data = json.loads(content)
            
            # Check for required fields in transcript JSON
            required_fields = ['transcript', 'content', 'text', 'messages']
            if not any(field in data for field in required_fields):
                return False
            
            return True
            
        except json.JSONDecodeError:
            return False
        except Exception as e:
            logger.error("JSON validation failed", error=str(e))
            return False
    
    async def _validate_html_content(self, content: str) -> bool:
        """Validate HTML content"""
        try:
            if not content or not content.strip():
                return False
            
            # Basic HTML structure check
            if not re.search(r'<[^>]+>', content):
                return False
            
            # Check for transcript-like content within HTML
            text_content = re.sub(r'<[^>]+>', '', content)
            return await self._validate_text_content(text_content)
            
        except Exception as e:
            logger.error("HTML validation failed", error=str(e))
            return False
    
    async def _validate_xml_content(self, content: str) -> bool:
        """Validate XML content"""
        try:
            import xml.etree.ElementTree as ET
            
            # Parse XML
            root = ET.fromstring(content)
            
            # Check for transcript-like structure
            transcript_tags = ['transcript', 'meeting', 'conversation', 'dialogue']
            if root.tag.lower() not in transcript_tags:
                # Check if any child elements contain transcript data
                for child in root:
                    if child.tag.lower() in transcript_tags:
                        return True
                return False
            
            return True
            
        except ET.ParseError:
            return False
        except Exception as e:
            logger.error("XML validation failed", error=str(e))
            return False
    
    # Metadata Extractors
    async def _extract_text_metadata(self, content: str, source: str) -> TranscriptMetadata:
        """Extract metadata from text content"""
        try:
            metadata = TranscriptMetadata()
            platform_config = self.platform_configs.get(source, self.platform_configs['generic'])
            
            # Extract participants using platform-specific patterns
            participant_pattern = platform_config['content_patterns']['participant_pattern']
            participant_match = re.search(participant_pattern, content, re.IGNORECASE)
            if participant_match:
                participants_text = participant_match.group(1)
                metadata.participants = [p.strip() for p in participants_text.split(',')]
            
            # Extract speakers from content
            speaker_pattern = platform_config['content_patterns']['speaker_pattern']
            speakers = set()
            for match in re.finditer(speaker_pattern, content, re.MULTILINE):
                if len(match.groups()) >= 2:
                    speaker = match.group(2).strip()
                    if speaker and len(speaker) < 50:  # Reasonable speaker name length
                        speakers.add(speaker)
            
            if speakers and not metadata.participants:
                metadata.participants = list(speakers)
            
            # Estimate duration from timestamps
            timestamp_pattern = platform_config['content_patterns']['timestamp_pattern']
            timestamps = re.findall(timestamp_pattern, content)
            if len(timestamps) >= 2:
                try:
                    # Parse first and last timestamps
                    first_time = self._parse_timestamp(timestamps[0])
                    last_time = self._parse_timestamp(timestamps[-1])
                    if first_time and last_time:
                        duration = (last_time - first_time).total_seconds() / 60
                        metadata.duration_minutes = int(duration)
                except:
                    pass
            
            # Calculate confidence score based on content quality
            metadata.confidence_score = self._calculate_content_confidence(content)
            
            return metadata
            
        except Exception as e:
            logger.error("Text metadata extraction failed", error=str(e))
            return TranscriptMetadata()
    
    async def _extract_markdown_metadata(self, content: str, source: str) -> TranscriptMetadata:
        """Extract metadata from markdown content"""
        try:
            # Start with text extraction
            metadata = await self._extract_text_metadata(content, source)
            
            # Extract title from markdown headers
            title_match = re.search(r'^#{1,3}\s*(.+)$', content, re.MULTILINE)
            if title_match:
                metadata.meeting_title = title_match.group(1).strip()
            
            # Extract metadata from markdown frontmatter
            frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                try:
                    import yaml
                    frontmatter = yaml.safe_load(frontmatter_match.group(1))
                    
                    if 'title' in frontmatter:
                        metadata.meeting_title = frontmatter['title']
                    if 'date' in frontmatter:
                        metadata.meeting_date = datetime.fromisoformat(str(frontmatter['date']))
                    if 'participants' in frontmatter:
                        metadata.participants = frontmatter['participants']
                    if 'duration' in frontmatter:
                        metadata.duration_minutes = int(frontmatter['duration'])
                        
                except:
                    pass
            
            return metadata
            
        except Exception as e:
            logger.error("Markdown metadata extraction failed", error=str(e))
            return TranscriptMetadata()
    
    async def _extract_json_metadata(self, content: str, source: str) -> TranscriptMetadata:
        """Extract metadata from JSON content"""
        try:
            data = json.loads(content)
            metadata = TranscriptMetadata()
            
            # Extract common fields
            field_mappings = {
                'meeting_id': ['meeting_id', 'id', 'meetingId'],
                'meeting_title': ['meeting_title', 'title', 'subject', 'name'],
                'meeting_date': ['meeting_date', 'start_time', 'date', 'timestamp'],
                'duration_minutes': ['duration', 'duration_minutes', 'length'],
                'participants': ['participants', 'attendees', 'members', 'speakers'],
                'meeting_type': ['meeting_type', 'type', 'category'],
                'organization': ['organization', 'org', 'company'],
                'language': ['language', 'lang', 'locale']
            }
            
            for attr, possible_keys in field_mappings.items():
                for key in possible_keys:
                    if key in data and data[key]:
                        if attr == 'meeting_date':
                            try:
                                if isinstance(data[key], str):
                                    setattr(metadata, attr, datetime.fromisoformat(data[key].replace('Z', '+00:00')))
                                elif isinstance(data[key], (int, float)):
                                    setattr(metadata, attr, datetime.fromtimestamp(data[key]))
                            except:
                                pass
                        elif attr == 'participants' and isinstance(data[key], list):
                            setattr(metadata, attr, data[key])
                        elif attr == 'duration_minutes':
                            try:
                                setattr(metadata, attr, int(data[key]))
                            except:
                                pass
                        else:
                            setattr(metadata, attr, data[key])
                        break
            
            # Extract transcript content for further analysis
            transcript_content = None
            transcript_fields = ['transcript', 'content', 'text', 'messages']
            for field in transcript_fields:
                if field in data:
                    if isinstance(data[field], str):
                        transcript_content = data[field]
                    elif isinstance(data[field], list):
                        # Handle array of messages/segments
                        transcript_content = '\n'.join([
                            f"{msg.get('speaker', 'Unknown')}: {msg.get('text', '')}"
                            for msg in data[field] if isinstance(msg, dict)
                        ])
                    break
            
            # If we have transcript content, extract additional metadata
            if transcript_content:
                text_metadata = await self._extract_text_metadata(transcript_content, source)
                if not metadata.participants and text_metadata.participants:
                    metadata.participants = text_metadata.participants
                if not metadata.duration_minutes and text_metadata.duration_minutes:
                    metadata.duration_minutes = text_metadata.duration_minutes
                if text_metadata.confidence_score:
                    metadata.confidence_score = text_metadata.confidence_score
            
            return metadata
            
        except Exception as e:
            logger.error("JSON metadata extraction failed", error=str(e))
            return TranscriptMetadata()
    
    async def _extract_html_metadata(self, content: str, source: str) -> TranscriptMetadata:
        """Extract metadata from HTML content"""
        try:
            metadata = TranscriptMetadata()
            
            # Extract title from HTML
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
            if title_match:
                metadata.meeting_title = title_match.group(1).strip()
            
            # Extract meta tags
            meta_patterns = {
                'meeting_date': r'<meta[^>]*name=["\']date["\'][^>]*content=["\']([^"\']+)["\']',
                'organization': r'<meta[^>]*name=["\']organization["\'][^>]*content=["\']([^"\']+)["\']',
                'meeting_type': r'<meta[^>]*name=["\']type["\'][^>]*content=["\']([^"\']+)["\']'
            }
            
            for attr, pattern in meta_patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    if attr == 'meeting_date':
                        try:
                            metadata.meeting_date = datetime.fromisoformat(match.group(1).replace('Z', '+00:00'))
                        except:
                            pass
                    else:
                        setattr(metadata, attr, match.group(1))
            
            # Extract text content and analyze
            text_content = re.sub(r'<[^>]+>', '', content)
            text_metadata = await self._extract_text_metadata(text_content, source)
            
            # Merge metadata
            if not metadata.participants and text_metadata.participants:
                metadata.participants = text_metadata.participants
            if not metadata.duration_minutes and text_metadata.duration_minutes:
                metadata.duration_minutes = text_metadata.duration_minutes
            if text_metadata.confidence_score:
                metadata.confidence_score = text_metadata.confidence_score
            
            return metadata
            
        except Exception as e:
            logger.error("HTML metadata extraction failed", error=str(e))
            return TranscriptMetadata()
    
    async def _extract_xml_metadata(self, content: str, source: str) -> TranscriptMetadata:
        """Extract metadata from XML content"""
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(content)
            metadata = TranscriptMetadata()
            
            # Extract attributes from root element
            if 'id' in root.attrib:
                metadata.meeting_id = root.attrib['id']
            if 'title' in root.attrib:
                metadata.meeting_title = root.attrib['title']
            if 'date' in root.attrib:
                try:
                    metadata.meeting_date = datetime.fromisoformat(root.attrib['date'].replace('Z', '+00:00'))
                except:
                    pass
            
            # Extract from child elements
            for child in root:
                if child.tag.lower() == 'metadata':
                    for meta_child in child:
                        if meta_child.tag.lower() == 'title':
                            metadata.meeting_title = meta_child.text
                        elif meta_child.tag.lower() == 'date':
                            try:
                                metadata.meeting_date = datetime.fromisoformat(meta_child.text.replace('Z', '+00:00'))
                            except:
                                pass
                        elif meta_child.tag.lower() == 'duration':
                            try:
                                metadata.duration_minutes = int(meta_child.text)
                            except:
                                pass
                        elif meta_child.tag.lower() == 'participants':
                            participants = []
                            for participant in meta_child:
                                if participant.text:
                                    participants.append(participant.text)
                            metadata.participants = participants
                
                elif child.tag.lower() in ['transcript', 'content']:
                    # Extract text content for analysis
                    text_content = ET.tostring(child, encoding='unicode', method='text')
                    text_metadata = await self._extract_text_metadata(text_content, source)
                    
                    if not metadata.participants and text_metadata.participants:
                        metadata.participants = text_metadata.participants
                    if not metadata.duration_minutes and text_metadata.duration_minutes:
                        metadata.duration_minutes = text_metadata.duration_minutes
                    if text_metadata.confidence_score:
                        metadata.confidence_score = text_metadata.confidence_score
            
            return metadata
            
        except Exception as e:
            logger.error("XML metadata extraction failed", error=str(e))
            return TranscriptMetadata()
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime"""
        try:
            # Common timestamp formats
            formats = [
                '%H:%M:%S',
                '%I:%M:%S %p',
                '%H:%M',
                '%I:%M %p',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %I:%M:%S %p'
            ]
            
            for fmt in formats:
                try:
                    # For time-only formats, use today's date
                    if '%Y' not in fmt:
                        today = datetime.now().date()
                        time_obj = datetime.strptime(timestamp_str.strip(), fmt).time()
                        return datetime.combine(today, time_obj)
                    else:
                        return datetime.strptime(timestamp_str.strip(), fmt)
                except ValueError:
                    continue
            
            return None
            
        except Exception as e:
            logger.error("Timestamp parsing failed", error=str(e), timestamp=timestamp_str)
            return None
    
    def _calculate_content_confidence(self, content: str) -> float:
        """Calculate confidence score for content quality"""
        try:
            score = 0.0
            
            # Length factor (longer content generally better)
            length_score = min(len(content) / 5000, 1.0) * 0.2
            score += length_score
            
            # Speaker diversity (more speakers = more structured)
            speakers = set()
            speaker_patterns = [
                r'^([^:]+):\s*(.+)$',  # Name: Text
                r'^\s*([A-Za-z\s]+):\s*(.+)$'  # Spaced Name: Text
            ]
            
            for pattern in speaker_patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    speaker = match.group(1).strip()
                    if len(speaker) < 50 and len(speaker) > 1:
                        speakers.add(speaker)
            
            speaker_score = min(len(speakers) / 10, 1.0) * 0.3
            score += speaker_score
            
            # Timestamp presence
            timestamp_patterns = [
                r'\d{1,2}:\d{2}:\d{2}',
                r'\d{1,2}:\d{2}\s*[AP]M',
                r'\[\d{1,2}:\d{2}:\d{2}\]'
            ]
            
            timestamp_count = sum(len(re.findall(pattern, content)) for pattern in timestamp_patterns)
            timestamp_score = min(timestamp_count / 50, 1.0) * 0.2
            score += timestamp_score
            
            # Word diversity
            words = re.findall(r'\b\w+\b', content.lower())
            unique_words = set(words)
            if words:
                diversity_score = len(unique_words) / len(words) * 0.2
                score += diversity_score
            
            # Structure indicators
            structure_patterns = [
                r'^\s*\d+\.',  # Numbered lists
                r'^\s*[-*+]',  # Bullet points
                r'#{1,6}\s',   # Headers
                r'\*\*[^*]+\*\*'  # Bold text
            ]
            
            structure_count = sum(len(re.findall(pattern, content, re.MULTILINE)) for pattern in structure_patterns)
            structure_score = min(structure_count / 20, 1.0) * 0.1
            score += structure_score
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error("Confidence calculation failed", error=str(e))
            return 0.5
    
    async def _validate_content_format(self, content: str, format: TranscriptFormat) -> bool:
        """Validate content matches expected format"""
        try:
            validator = self.validators.get(format.value)
            if validator:
                return await validator(content)
            return True  # No validator available, assume valid
            
        except Exception as e:
            logger.error("Content format validation failed", error=str(e))
            return False
    
    async def _trigger_oracle_analysis(self, webhook_payload: WebhookPayload) -> Dict[str, Any]:
        """
        Trigger Oracle 9.1 Protocol analysis for the transcript
        """
        try:
            # Import the AI conductor service
            from .ai_conductor import ai_conductor
            
            # Prepare analysis request
            analysis_request = {
                'content': webhook_payload.content,
                'format': webhook_payload.format.value,
                'metadata': {
                    'meeting_id': webhook_payload.metadata.meeting_id,
                    'meeting_title': webhook_payload.metadata.meeting_title,
                    'meeting_date': webhook_payload.metadata.meeting_date.isoformat() if webhook_payload.metadata.meeting_date else None,
                    'duration_minutes': webhook_payload.metadata.duration_minutes,
                    'participants': webhook_payload.metadata.participants,
                    'source_platform': webhook_payload.metadata.source_platform,
                    'webhook_id': webhook_payload.id,
                    'priority': webhook_payload.priority.value
                },
                'analysis_type': 'oracle_9_1_protocol',
                'source': 'zapier_webhook'
            }
            
            # Trigger analysis
            analysis_result = await ai_conductor.conduct_analysis(analysis_request)
            
            if analysis_result.get('success'):
                logger.info("Oracle analysis triggered successfully", 
                           webhook_id=webhook_payload.id,
                           analysis_id=analysis_result.get('analysis_id'))
                
                return {
                    'success': True,
                    'analysis_id': analysis_result.get('analysis_id'),
                    'message': 'Oracle 9.1 Protocol analysis initiated'
                }
            else:
                logger.error("Oracle analysis failed", 
                           webhook_id=webhook_payload.id,
                           error=analysis_result.get('error'))
                
                return {
                    'success': False,
                    'error': analysis_result.get('error', 'Analysis initiation failed')
                }
                
        except Exception as e:
            logger.error("Oracle analysis trigger failed", webhook_id=webhook_payload.id, error=str(e))
            return {
                'success': False,
                'error': f'Failed to trigger Oracle analysis: {str(e)}'
            }
    
    async def _schedule_retry(self, webhook_payload: WebhookPayload, result: ProcessingResult):
        """
        Schedule webhook for retry
        """
        try:
            webhook_payload.retry_count += 1
            result.retry_count = webhook_payload.retry_count
            
            # Calculate retry delay
            delay_index = min(webhook_payload.retry_count - 1, len(self.retry_delays) - 1)
            delay_seconds = self.retry_delays[delay_index]
            
            result.next_retry_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
            
            logger.info("Scheduling webhook retry", 
                       webhook_id=webhook_payload.id,
                       retry_count=webhook_payload.retry_count,
                       next_retry_at=result.next_retry_at.isoformat())
            
            # Schedule the retry (in a real implementation, this would use a task scheduler)
            await asyncio.sleep(delay_seconds)
            await self.processing_queue.put(webhook_payload)
            
        except Exception as e:
            logger.error("Retry scheduling failed", webhook_id=webhook_payload.id, error=str(e))
    
    def _update_average_processing_time(self, processing_time: float):
        """Update average processing time statistic"""
        try:
            current_avg = self.stats['average_processing_time']
            total_processed = self.stats['total_processed']
            
            if total_processed == 1:
                self.stats['average_processing_time'] = processing_time
            else:
                # Calculate running average
                self.stats['average_processing_time'] = (
                    (current_avg * (total_processed - 1) + processing_time) / total_processed
                )
                
        except Exception as e:
            logger.error("Average processing time update failed", error=str(e))
    
    # Public API Methods
    async def get_webhook_status(self, webhook_id: str) -> Dict[str, Any]:
        """Get status of a specific webhook"""
        try:
            if webhook_id in self.webhook_history:
                webhook = self.webhook_history[webhook_id]
                return {
                    'webhook_id': webhook_id,
                    'status': 'completed' if webhook_id not in self.failed_webhooks else 'failed',
                    'source': webhook.source,
                    'timestamp': webhook.timestamp.isoformat(),
                    'format': webhook.format.value,
                    'priority': webhook.priority.value,
                    'retry_count': webhook.retry_count,
                    'metadata': {
                        'meeting_title': webhook.metadata.meeting_title,
                        'participant_count': webhook.metadata.participant_count,
                        'duration_minutes': webhook.metadata.duration_minutes
                    }
                }
            else:
                return {
                    'webhook_id': webhook_id,
                    'status': 'not_found',
                    'error': 'Webhook not found in history'
                }
                
        except Exception as e:
            logger.error("Webhook status retrieval failed", webhook_id=webhook_id, error=str(e))
            return {
                'webhook_id': webhook_id,
                'status': 'error',
                'error': str(e)
            }
    
    async def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        try:
            return {
                'total_received': self.stats['total_received'],
                'total_processed': self.stats['total_processed'],
                'total_failed': self.stats['total_failed'],
                'success_rate': (
                    self.stats['total_processed'] / max(self.stats['total_received'], 1) * 100
                ),
                'average_processing_time_seconds': round(self.stats['average_processing_time'], 2),
                'queue_size': self.processing_queue.qsize(),
                'failed_webhooks_count': len(self.failed_webhooks),
                'last_processed': self.stats['last_processed'],
                'supported_platforms': list(self.platform_configs.keys()),
                'supported_formats': [fmt.value for fmt in TranscriptFormat]
            }
            
        except Exception as e:
            logger.error("Statistics retrieval failed", error=str(e))
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def retry_failed_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Manually retry a failed webhook"""
        try:
            if webhook_id not in self.failed_webhooks:
                return {
                    'webhook_id': webhook_id,
                    'status': 'not_found',
                    'error': 'Failed webhook not found'
                }
            
            if webhook_id not in self.webhook_history:
                return {
                    'webhook_id': webhook_id,
                    'status': 'error',
                    'error': 'Webhook history not found'
                }
            
            # Reset retry count and requeue
            webhook_payload = self.webhook_history[webhook_id]
            webhook_payload.retry_count = 0
            
            await self.processing_queue.put(webhook_payload)
            
            # Remove from failed webhooks
            del self.failed_webhooks[webhook_id]
            
            logger.info("Webhook manually retried", webhook_id=webhook_id)
            
            return {
                'webhook_id': webhook_id,
                'status': 'requeued',
                'message': 'Webhook has been requeued for processing'
            }
            
        except Exception as e:
            logger.error("Manual retry failed", webhook_id=webhook_id, error=str(e))
            return {
                'webhook_id': webhook_id,
                'status': 'error',
                'error': str(e)
            }

# Global Zapier integration service instance
zapier_integration_service = ZapierIntegrationService()