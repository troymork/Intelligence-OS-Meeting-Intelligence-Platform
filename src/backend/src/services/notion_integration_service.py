"""
Notion Database Integration Service for Intelligence OS
Handles bidirectional synchronization with Notion databases for Oracle 9.1 Protocol data
"""

import os
import asyncio
import logging
import uuid
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
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

class NotionPropertyType(Enum):
    """Notion property types"""
    TITLE = "title"
    RICH_TEXT = "rich_text"
    NUMBER = "number"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    DATE = "date"
    PEOPLE = "people"
    FILES = "files"
    CHECKBOX = "checkbox"
    URL = "url"
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    FORMULA = "formula"
    RELATION = "relation"
    ROLLUP = "rollup"
    CREATED_TIME = "created_time"
    CREATED_BY = "created_by"
    LAST_EDITED_TIME = "last_edited_time"
    LAST_EDITED_BY = "last_edited_by"

class SyncDirection(Enum):
    """Synchronization directions"""
    TO_NOTION = "to_notion"
    FROM_NOTION = "from_notion"
    BIDIRECTIONAL = "bidirectional"

class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    LATEST_WINS = "latest_wins"
    NOTION_WINS = "notion_wins"
    INTELLIGENCE_OS_WINS = "intelligence_os_wins"
    MANUAL_REVIEW = "manual_review"
    MERGE_FIELDS = "merge_fields"

class SyncStatus(Enum):
    """Synchronization status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"
    SKIPPED = "skipped"

@dataclass
class NotionDatabaseSchema:
    """Notion database schema definition"""
    database_id: str
    name: str
    properties: Dict[str, Dict[str, Any]]
    title_property: str
    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None
    url: Optional[str] = None

@dataclass
class SyncMapping:
    """Mapping between Intelligence OS and Notion fields"""
    intelligence_os_field: str
    notion_property: str
    property_type: NotionPropertyType
    transformation_function: Optional[str] = None
    validation_rules: List[str] = field(default_factory=list)
    bidirectional: bool = True

@dataclass
class SyncRecord:
    """Record of synchronization operation"""
    id: str
    database_type: str
    record_id: str
    notion_page_id: Optional[str]
    direction: SyncDirection
    status: SyncStatus
    last_sync: datetime
    conflict_details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0

@dataclass
class ConflictRecord:
    """Record of synchronization conflict"""
    id: str
    database_type: str
    record_id: str
    notion_page_id: str
    intelligence_os_data: Dict[str, Any]
    notion_data: Dict[str, Any]
    conflict_fields: List[str]
    resolution_strategy: ConflictResolution
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_data: Optional[Dict[str, Any]] = None

class NotionIntegrationService:
    """Service for Notion database integration and synchronization"""
    
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.notion_version = os.getenv('NOTION_VERSION', '2022-06-28')
        self.base_url = 'https://api.notion.com/v1'
        
        # Sync configuration
        self.sync_interval = int(os.getenv('NOTION_SYNC_INTERVAL', '300'))  # 5 minutes
        self.max_retries = int(os.getenv('NOTION_MAX_RETRIES', '3'))
        self.batch_size = int(os.getenv('NOTION_BATCH_SIZE', '100'))
        
        # Storage for sync operations
        self.database_schemas = {}
        self.sync_mappings = {}
        self.sync_records = {}
        self.conflict_records = {}
        
        # Initialize database configurations
        self.database_configs = self._initialize_database_configs()
        
        # Initialize field mappings
        self.field_mappings = self._initialize_field_mappings()
        
        # Transformation functions
        self.transformers = self._initialize_transformers()
        
        # HTTP session for API calls
        self.session = None
    
    def _initialize_database_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize Oracle 9.1 Protocol database configurations"""
        return {
            'meetings': {
                'name': 'Meetings Database',
                'description': 'Central repository for all meeting records and metadata',
                'icon': '🏢',
                'properties': {
                    'Meeting ID': {'type': NotionPropertyType.TITLE, 'required': True},
                    'Title': {'type': NotionPropertyType.RICH_TEXT, 'required': True},
                    'Date': {'type': NotionPropertyType.DATE, 'required': True},
                    'Duration': {'type': NotionPropertyType.NUMBER, 'required': False},
                    'Participants': {'type': NotionPropertyType.MULTI_SELECT, 'required': False},
                    'Meeting Type': {'type': NotionPropertyType.SELECT, 'required': False},
                    'Status': {'type': NotionPropertyType.SELECT, 'required': True},
                    'Recording URL': {'type': NotionPropertyType.URL, 'required': False},
                    'Transcript': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Analysis Status': {'type': NotionPropertyType.SELECT, 'required': True},
                    'Oracle Analysis ID': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Created': {'type': NotionPropertyType.CREATED_TIME, 'required': False},
                    'Last Updated': {'type': NotionPropertyType.LAST_EDITED_TIME, 'required': False}
                },
                'select_options': {
                    'Meeting Type': ['Standup', 'Planning', 'Review', 'Retrospective', 'All-Hands', 'One-on-One', 'Other'],
                    'Status': ['Scheduled', 'In Progress', 'Completed', 'Cancelled'],
                    'Analysis Status': ['Pending', 'Processing', 'Completed', 'Failed']
                }
            },
            'decisions': {
                'name': 'Decisions & Agreements',
                'description': 'Track all decisions and agreements made in meetings',
                'icon': '⚖️',
                'properties': {
                    'Decision ID': {'type': NotionPropertyType.TITLE, 'required': True},
                    'Decision Title': {'type': NotionPropertyType.RICH_TEXT, 'required': True},
                    'Description': {'type': NotionPropertyType.RICH_TEXT, 'required': True},
                    'Meeting': {'type': NotionPropertyType.RELATION, 'required': True, 'relation_database': 'meetings'},
                    'Decision Maker': {'type': NotionPropertyType.PEOPLE, 'required': False},
                    'Stakeholders': {'type': NotionPropertyType.MULTI_SELECT, 'required': False},
                    'Priority': {'type': NotionPropertyType.SELECT, 'required': True},
                    'Status': {'type': NotionPropertyType.SELECT, 'required': True},
                    'Implementation Date': {'type': NotionPropertyType.DATE, 'required': False},
                    'Rationale': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Impact Assessment': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Success Criteria': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Tags': {'type': NotionPropertyType.MULTI_SELECT, 'required': False},
                    'Created': {'type': NotionPropertyType.CREATED_TIME, 'required': False},
                    'Last Updated': {'type': NotionPropertyType.LAST_EDITED_TIME, 'required': False}
                },
                'select_options': {
                    'Priority': ['Critical', 'High', 'Medium', 'Low'],
                    'Status': ['Proposed', 'Approved', 'In Progress', 'Implemented', 'Rejected', 'On Hold']
                }
            },
            'actions': {
                'name': 'Action Register',
                'description': 'Track all action items and their progress',
                'icon': '✅',
                'properties': {
                    'Action ID': {'type': NotionPropertyType.TITLE, 'required': True},
                    'Action Title': {'type': NotionPropertyType.RICH_TEXT, 'required': True},
                    'Description': {'type': NotionPropertyType.RICH_TEXT, 'required': True},
                    'Meeting': {'type': NotionPropertyType.RELATION, 'required': True, 'relation_database': 'meetings'},
                    'Owner': {'type': NotionPropertyType.PEOPLE, 'required': True},
                    'Assignees': {'type': NotionPropertyType.PEOPLE, 'required': False},
                    'Priority': {'type': NotionPropertyType.SELECT, 'required': True},
                    'Status': {'type': NotionPropertyType.SELECT, 'required': True},
                    'Due Date': {'type': NotionPropertyType.DATE, 'required': False},
                    'Progress': {'type': NotionPropertyType.NUMBER, 'required': False},
                    'Velocity Estimate': {'type': NotionPropertyType.NUMBER, 'required': False},
                    'Exponential Potential': {'type': NotionPropertyType.NUMBER, 'required': False},
                    'Dependencies': {'type': NotionPropertyType.RELATION, 'required': False, 'relation_database': 'actions'},
                    'Tags': {'type': NotionPropertyType.MULTI_SELECT, 'required': False},
                    'Notes': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Created': {'type': NotionPropertyType.CREATED_TIME, 'required': False},
                    'Last Updated': {'type': NotionPropertyType.LAST_EDITED_TIME, 'required': False}
                },
                'select_options': {
                    'Priority': ['Urgent', 'High', 'Medium', 'Low'],
                    'Status': ['Not Started', 'In Progress', 'Blocked', 'Completed', 'Cancelled']
                }
            },
            'insights': {
                'name': 'Meeting Insights',
                'description': 'Key insights and patterns identified from meetings',
                'icon': '💡',
                'properties': {
                    'Insight ID': {'type': NotionPropertyType.TITLE, 'required': True},
                    'Insight Title': {'type': NotionPropertyType.RICH_TEXT, 'required': True},
                    'Description': {'type': NotionPropertyType.RICH_TEXT, 'required': True},
                    'Meeting': {'type': NotionPropertyType.RELATION, 'required': True, 'relation_database': 'meetings'},
                    'Category': {'type': NotionPropertyType.SELECT, 'required': True},
                    'Confidence Score': {'type': NotionPropertyType.NUMBER, 'required': False},
                    'Impact Level': {'type': NotionPropertyType.SELECT, 'required': False},
                    'Stakeholders': {'type': NotionPropertyType.MULTI_SELECT, 'required': False},
                    'Related Patterns': {'type': NotionPropertyType.MULTI_SELECT, 'required': False},
                    'Recommendations': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Follow-up Required': {'type': NotionPropertyType.CHECKBOX, 'required': False},
                    'Tags': {'type': NotionPropertyType.MULTI_SELECT, 'required': False},
                    'Created': {'type': NotionPropertyType.CREATED_TIME, 'required': False},
                    'Last Updated': {'type': NotionPropertyType.LAST_EDITED_TIME, 'required': False}
                },
                'select_options': {
                    'Category': ['Strategic', 'Operational', 'Cultural', 'Technical', 'Process', 'Communication'],
                    'Impact Level': ['Critical', 'High', 'Medium', 'Low', 'Informational']
                }
            },
            'solutions': {
                'name': 'Solution Portfolio',
                'description': 'Comprehensive solutions and implementation plans',
                'icon': '🔧',
                'properties': {
                    'Solution ID': {'type': NotionPropertyType.TITLE, 'required': True},
                    'Solution Title': {'type': NotionPropertyType.RICH_TEXT, 'required': True},
                    'Description': {'type': NotionPropertyType.RICH_TEXT, 'required': True},
                    'Meeting': {'type': NotionPropertyType.RELATION, 'required': True, 'relation_database': 'meetings'},
                    'Problem Statement': {'type': NotionPropertyType.RICH_TEXT, 'required': True},
                    'Solution Type': {'type': NotionPropertyType.SELECT, 'required': True},
                    'Implementation Plan': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Resource Requirements': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Timeline': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Success Metrics': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Risk Assessment': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Priority': {'type': NotionPropertyType.SELECT, 'required': True},
                    'Status': {'type': NotionPropertyType.SELECT, 'required': True},
                    'Owner': {'type': NotionPropertyType.PEOPLE, 'required': False},
                    'Tags': {'type': NotionPropertyType.MULTI_SELECT, 'required': False},
                    'Created': {'type': NotionPropertyType.CREATED_TIME, 'required': False},
                    'Last Updated': {'type': NotionPropertyType.LAST_EDITED_TIME, 'required': False}
                },
                'select_options': {
                    'Solution Type': ['Process', 'Technology', 'Organizational', 'Strategic', 'Cultural', 'Hybrid'],
                    'Priority': ['Critical', 'High', 'Medium', 'Low'],
                    'Status': ['Proposed', 'Approved', 'In Development', 'Testing', 'Implemented', 'Rejected']
                }
            },
            'human_needs': {
                'name': 'Human Needs Analysis',
                'description': 'Individual and team human needs assessment and interventions',
                'icon': '🧠',
                'properties': {
                    'Analysis ID': {'type': NotionPropertyType.TITLE, 'required': True},
                    'Meeting': {'type': NotionPropertyType.RELATION, 'required': True, 'relation_database': 'meetings'},
                    'Individual': {'type': NotionPropertyType.PEOPLE, 'required': False},
                    'Team': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Certainty Score': {'type': NotionPropertyType.NUMBER, 'required': False},
                    'Variety Score': {'type': NotionPropertyType.NUMBER, 'required': False},
                    'Significance Score': {'type': NotionPropertyType.NUMBER, 'required': False},
                    'Connection Score': {'type': NotionPropertyType.NUMBER, 'required': False},
                    'Growth Score': {'type': NotionPropertyType.NUMBER, 'required': False},
                    'Contribution Score': {'type': NotionPropertyType.NUMBER, 'required': False},
                    'Overall Balance': {'type': NotionPropertyType.NUMBER, 'required': False},
                    'Primary Need': {'type': NotionPropertyType.SELECT, 'required': False},
                    'Need Imbalances': {'type': NotionPropertyType.MULTI_SELECT, 'required': False},
                    'Interventions': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Recommendations': {'type': NotionPropertyType.RICH_TEXT, 'required': False},
                    'Follow-up Date': {'type': NotionPropertyType.DATE, 'required': False},
                    'Privacy Level': {'type': NotionPropertyType.SELECT, 'required': True},
                    'Created': {'type': NotionPropertyType.CREATED_TIME, 'required': False},
                    'Last Updated': {'type': NotionPropertyType.LAST_EDITED_TIME, 'required': False}
                },
                'select_options': {
                    'Primary Need': ['Certainty', 'Variety', 'Significance', 'Connection', 'Growth', 'Contribution'],
                    'Privacy Level': ['Public', 'Team', 'Manager', 'Private']
                }
            }
        }
    
    def _initialize_field_mappings(self) -> Dict[str, List[SyncMapping]]:
        """Initialize field mappings between Intelligence OS and Notion"""
        return {
            'meetings': [
                SyncMapping('id', 'Meeting ID', NotionPropertyType.TITLE),
                SyncMapping('title', 'Title', NotionPropertyType.RICH_TEXT),
                SyncMapping('date', 'Date', NotionPropertyType.DATE, 'datetime_to_notion'),
                SyncMapping('duration_minutes', 'Duration', NotionPropertyType.NUMBER),
                SyncMapping('participants', 'Participants', NotionPropertyType.MULTI_SELECT, 'list_to_multiselect'),
                SyncMapping('meeting_type', 'Meeting Type', NotionPropertyType.SELECT),
                SyncMapping('status', 'Status', NotionPropertyType.SELECT),
                SyncMapping('recording_url', 'Recording URL', NotionPropertyType.URL),
                SyncMapping('transcript', 'Transcript', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('analysis_status', 'Analysis Status', NotionPropertyType.SELECT),
                SyncMapping('oracle_analysis_id', 'Oracle Analysis ID', NotionPropertyType.RICH_TEXT)
            ],
            'decisions': [
                SyncMapping('id', 'Decision ID', NotionPropertyType.TITLE),
                SyncMapping('title', 'Decision Title', NotionPropertyType.RICH_TEXT),
                SyncMapping('description', 'Description', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('meeting_id', 'Meeting', NotionPropertyType.RELATION, 'id_to_relation'),
                SyncMapping('decision_maker', 'Decision Maker', NotionPropertyType.PEOPLE, 'name_to_people'),
                SyncMapping('stakeholders', 'Stakeholders', NotionPropertyType.MULTI_SELECT, 'list_to_multiselect'),
                SyncMapping('priority', 'Priority', NotionPropertyType.SELECT),
                SyncMapping('status', 'Status', NotionPropertyType.SELECT),
                SyncMapping('implementation_date', 'Implementation Date', NotionPropertyType.DATE, 'datetime_to_notion'),
                SyncMapping('rationale', 'Rationale', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('impact_assessment', 'Impact Assessment', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('success_criteria', 'Success Criteria', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('tags', 'Tags', NotionPropertyType.MULTI_SELECT, 'list_to_multiselect')
            ],
            'actions': [
                SyncMapping('id', 'Action ID', NotionPropertyType.TITLE),
                SyncMapping('title', 'Action Title', NotionPropertyType.RICH_TEXT),
                SyncMapping('description', 'Description', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('meeting_id', 'Meeting', NotionPropertyType.RELATION, 'id_to_relation'),
                SyncMapping('owner', 'Owner', NotionPropertyType.PEOPLE, 'name_to_people'),
                SyncMapping('assignees', 'Assignees', NotionPropertyType.PEOPLE, 'list_to_people'),
                SyncMapping('priority', 'Priority', NotionPropertyType.SELECT),
                SyncMapping('status', 'Status', NotionPropertyType.SELECT),
                SyncMapping('due_date', 'Due Date', NotionPropertyType.DATE, 'datetime_to_notion'),
                SyncMapping('progress', 'Progress', NotionPropertyType.NUMBER),
                SyncMapping('velocity_estimate', 'Velocity Estimate', NotionPropertyType.NUMBER),
                SyncMapping('exponential_potential', 'Exponential Potential', NotionPropertyType.NUMBER),
                SyncMapping('dependencies', 'Dependencies', NotionPropertyType.RELATION, 'list_to_relation'),
                SyncMapping('tags', 'Tags', NotionPropertyType.MULTI_SELECT, 'list_to_multiselect'),
                SyncMapping('notes', 'Notes', NotionPropertyType.RICH_TEXT, 'text_to_rich_text')
            ],
            'insights': [
                SyncMapping('id', 'Insight ID', NotionPropertyType.TITLE),
                SyncMapping('title', 'Insight Title', NotionPropertyType.RICH_TEXT),
                SyncMapping('description', 'Description', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('meeting_id', 'Meeting', NotionPropertyType.RELATION, 'id_to_relation'),
                SyncMapping('category', 'Category', NotionPropertyType.SELECT),
                SyncMapping('confidence_score', 'Confidence Score', NotionPropertyType.NUMBER),
                SyncMapping('impact_level', 'Impact Level', NotionPropertyType.SELECT),
                SyncMapping('stakeholders', 'Stakeholders', NotionPropertyType.MULTI_SELECT, 'list_to_multiselect'),
                SyncMapping('related_patterns', 'Related Patterns', NotionPropertyType.MULTI_SELECT, 'list_to_multiselect'),
                SyncMapping('recommendations', 'Recommendations', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('follow_up_required', 'Follow-up Required', NotionPropertyType.CHECKBOX),
                SyncMapping('tags', 'Tags', NotionPropertyType.MULTI_SELECT, 'list_to_multiselect')
            ],
            'solutions': [
                SyncMapping('id', 'Solution ID', NotionPropertyType.TITLE),
                SyncMapping('title', 'Solution Title', NotionPropertyType.RICH_TEXT),
                SyncMapping('description', 'Description', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('meeting_id', 'Meeting', NotionPropertyType.RELATION, 'id_to_relation'),
                SyncMapping('problem_statement', 'Problem Statement', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('solution_type', 'Solution Type', NotionPropertyType.SELECT),
                SyncMapping('implementation_plan', 'Implementation Plan', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('resource_requirements', 'Resource Requirements', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('timeline', 'Timeline', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('success_metrics', 'Success Metrics', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('risk_assessment', 'Risk Assessment', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('priority', 'Priority', NotionPropertyType.SELECT),
                SyncMapping('status', 'Status', NotionPropertyType.SELECT),
                SyncMapping('owner', 'Owner', NotionPropertyType.PEOPLE, 'name_to_people'),
                SyncMapping('tags', 'Tags', NotionPropertyType.MULTI_SELECT, 'list_to_multiselect')
            ],
            'human_needs': [
                SyncMapping('id', 'Analysis ID', NotionPropertyType.TITLE),
                SyncMapping('meeting_id', 'Meeting', NotionPropertyType.RELATION, 'id_to_relation'),
                SyncMapping('individual', 'Individual', NotionPropertyType.PEOPLE, 'name_to_people'),
                SyncMapping('team', 'Team', NotionPropertyType.RICH_TEXT),
                SyncMapping('certainty_score', 'Certainty Score', NotionPropertyType.NUMBER),
                SyncMapping('variety_score', 'Variety Score', NotionPropertyType.NUMBER),
                SyncMapping('significance_score', 'Significance Score', NotionPropertyType.NUMBER),
                SyncMapping('connection_score', 'Connection Score', NotionPropertyType.NUMBER),
                SyncMapping('growth_score', 'Growth Score', NotionPropertyType.NUMBER),
                SyncMapping('contribution_score', 'Contribution Score', NotionPropertyType.NUMBER),
                SyncMapping('overall_balance', 'Overall Balance', NotionPropertyType.NUMBER),
                SyncMapping('primary_need', 'Primary Need', NotionPropertyType.SELECT),
                SyncMapping('need_imbalances', 'Need Imbalances', NotionPropertyType.MULTI_SELECT, 'list_to_multiselect'),
                SyncMapping('interventions', 'Interventions', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('recommendations', 'Recommendations', NotionPropertyType.RICH_TEXT, 'text_to_rich_text'),
                SyncMapping('follow_up_date', 'Follow-up Date', NotionPropertyType.DATE, 'datetime_to_notion'),
                SyncMapping('privacy_level', 'Privacy Level', NotionPropertyType.SELECT)
            ]
        }
    
    def _initialize_transformers(self) -> Dict[str, callable]:
        """Initialize data transformation functions"""
        return {
            'datetime_to_notion': self._datetime_to_notion,
            'notion_to_datetime': self._notion_to_datetime,
            'text_to_rich_text': self._text_to_rich_text,
            'rich_text_to_text': self._rich_text_to_text,
            'list_to_multiselect': self._list_to_multiselect,
            'multiselect_to_list': self._multiselect_to_list,
            'name_to_people': self._name_to_people,
            'people_to_name': self._people_to_name,
            'list_to_people': self._list_to_people,
            'people_to_list': self._people_to_list,
            'id_to_relation': self._id_to_relation,
            'relation_to_id': self._relation_to_id,
            'list_to_relation': self._list_to_relation,
            'relation_to_list': self._relation_to_list
        }    

    async def initialize_session(self):
        """Initialize HTTP session for Notion API calls"""
        if not self.session:
            headers = {
                'Authorization': f'Bearer {self.notion_token}',
                'Notion-Version': self.notion_version,
                'Content-Type': 'application/json'
            }
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    # Database Schema Management
    async def create_database_schema(self, database_type: str, parent_page_id: str) -> Dict[str, Any]:
        """
        Create a new Notion database with Oracle 9.1 Protocol schema
        """
        try:
            await self.initialize_session()
            
            if database_type not in self.database_configs:
                raise ValueError(f"Unknown database type: {database_type}")
            
            config = self.database_configs[database_type]
            
            # Build properties schema
            properties = {}
            for prop_name, prop_config in config['properties'].items():
                prop_type = prop_config['type']
                
                if prop_type == NotionPropertyType.TITLE:
                    properties[prop_name] = {"title": {}}
                elif prop_type == NotionPropertyType.RICH_TEXT:
                    properties[prop_name] = {"rich_text": {}}
                elif prop_type == NotionPropertyType.NUMBER:
                    properties[prop_name] = {"number": {"format": "number"}}
                elif prop_type == NotionPropertyType.SELECT:
                    options = []
                    if prop_name in config.get('select_options', {}):
                        for option in config['select_options'][prop_name]:
                            options.append({"name": option, "color": "default"})
                    properties[prop_name] = {"select": {"options": options}}
                elif prop_type == NotionPropertyType.MULTI_SELECT:
                    options = []
                    if prop_name in config.get('select_options', {}):
                        for option in config['select_options'][prop_name]:
                            options.append({"name": option, "color": "default"})
                    properties[prop_name] = {"multi_select": {"options": options}}
                elif prop_type == NotionPropertyType.DATE:
                    properties[prop_name] = {"date": {}}
                elif prop_type == NotionPropertyType.PEOPLE:
                    properties[prop_name] = {"people": {}}
                elif prop_type == NotionPropertyType.CHECKBOX:
                    properties[prop_name] = {"checkbox": {}}
                elif prop_type == NotionPropertyType.URL:
                    properties[prop_name] = {"url": {}}
                elif prop_type == NotionPropertyType.RELATION:
                    if 'relation_database' in prop_config:
                        # Will be set up after all databases are created
                        properties[prop_name] = {"relation": {"database_id": "placeholder"}}
                elif prop_type in [NotionPropertyType.CREATED_TIME, NotionPropertyType.CREATED_BY,
                                 NotionPropertyType.LAST_EDITED_TIME, NotionPropertyType.LAST_EDITED_BY]:
                    properties[prop_name] = {prop_type.value: {}}
            
            # Create database
            payload = {
                "parent": {"page_id": parent_page_id},
                "title": [{"type": "text", "text": {"content": config['name']}}],
                "description": [{"type": "text", "text": {"content": config['description']}}],
                "icon": {"type": "emoji", "emoji": config['icon']},
                "properties": properties
            }
            
            async with self.session.post(f"{self.base_url}/databases", json=payload) as response:
                if response.status == 200:
                    database_data = await response.json()
                    database_id = database_data['id']
                    
                    # Store schema
                    schema = NotionDatabaseSchema(
                        database_id=database_id,
                        name=config['name'],
                        properties=database_data['properties'],
                        title_property=self._find_title_property(database_data['properties']),
                        created_time=datetime.fromisoformat(database_data['created_time'].replace('Z', '+00:00')),
                        url=database_data['url']
                    )
                    
                    self.database_schemas[database_type] = schema
                    
                    logger.info("Database schema created", database_type=database_type, database_id=database_id)
                    
                    return {
                        'success': True,
                        'database_id': database_id,
                        'database_type': database_type,
                        'url': database_data['url']
                    }
                else:
                    error_data = await response.json()
                    logger.error("Database creation failed", error=error_data, status=response.status)
                    return {
                        'success': False,
                        'error': error_data.get('message', 'Database creation failed'),
                        'status': response.status
                    }
                    
        except Exception as e:
            logger.error("Database schema creation failed", error=str(e), database_type=database_type)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def setup_database_relations(self) -> Dict[str, Any]:
        """
        Set up relations between databases after all are created
        """
        try:
            await self.initialize_session()
            
            relations_updated = 0
            
            for database_type, config in self.database_configs.items():
                if database_type not in self.database_schemas:
                    continue
                
                schema = self.database_schemas[database_type]
                
                # Find relation properties that need database IDs
                for prop_name, prop_config in config['properties'].items():
                    if (prop_config['type'] == NotionPropertyType.RELATION and 
                        'relation_database' in prop_config):
                        
                        related_db_type = prop_config['relation_database']
                        if related_db_type in self.database_schemas:
                            related_db_id = self.database_schemas[related_db_type].database_id
                            
                            # Update the relation property
                            payload = {
                                "properties": {
                                    prop_name: {
                                        "relation": {
                                            "database_id": related_db_id,
                                            "type": "dual_property",
                                            "dual_property": {}
                                        }
                                    }
                                }
                            }
                            
                            async with self.session.patch(f"{self.base_url}/databases/{schema.database_id}", 
                                                        json=payload) as response:
                                if response.status == 200:
                                    relations_updated += 1
                                    logger.info("Relation updated", 
                                              database_type=database_type,
                                              property=prop_name,
                                              related_database=related_db_type)
                                else:
                                    error_data = await response.json()
                                    logger.error("Relation update failed", 
                                               error=error_data,
                                               database_type=database_type,
                                               property=prop_name)
            
            return {
                'success': True,
                'relations_updated': relations_updated
            }
            
        except Exception as e:
            logger.error("Database relations setup failed", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_title_property(self, properties: Dict[str, Any]) -> str:
        """Find the title property in database schema"""
        for prop_name, prop_data in properties.items():
            if prop_data.get('type') == 'title':
                return prop_name
        return 'Name'  # Default fallback
    
    # Data Synchronization Methods
    async def sync_to_notion(self, database_type: str, record_data: Dict[str, Any], 
                           record_id: str = None) -> Dict[str, Any]:
        """
        Synchronize data from Intelligence OS to Notion
        """
        try:
            await self.initialize_session()
            
            if database_type not in self.database_schemas:
                return {
                    'success': False,
                    'error': f'Database schema not found for {database_type}'
                }
            
            schema = self.database_schemas[database_type]
            mappings = self.field_mappings.get(database_type, [])
            
            # Transform data to Notion format
            notion_properties = await self._transform_to_notion(record_data, mappings)
            
            # Check if record exists
            existing_page = None
            if record_id:
                existing_page = await self._find_notion_page(database_type, record_id)
            
            if existing_page:
                # Update existing page
                result = await self._update_notion_page(existing_page['id'], notion_properties)
            else:
                # Create new page
                result = await self._create_notion_page(schema.database_id, notion_properties)
            
            if result['success']:
                # Record sync operation
                sync_record = SyncRecord(
                    id=str(uuid.uuid4()),
                    database_type=database_type,
                    record_id=record_id or record_data.get('id', str(uuid.uuid4())),
                    notion_page_id=result['page_id'],
                    direction=SyncDirection.TO_NOTION,
                    status=SyncStatus.COMPLETED,
                    last_sync=datetime.utcnow()
                )
                
                self.sync_records[sync_record.id] = sync_record
                
                logger.info("Data synced to Notion", 
                           database_type=database_type,
                           record_id=sync_record.record_id,
                           page_id=result['page_id'])
            
            return result
            
        except Exception as e:
            logger.error("Sync to Notion failed", error=str(e), database_type=database_type)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def sync_from_notion(self, database_type: str, page_id: str = None) -> Dict[str, Any]:
        """
        Synchronize data from Notion to Intelligence OS
        """
        try:
            await self.initialize_session()
            
            if database_type not in self.database_schemas:
                return {
                    'success': False,
                    'error': f'Database schema not found for {database_type}'
                }
            
            schema = self.database_schemas[database_type]
            mappings = self.field_mappings.get(database_type, [])
            
            if page_id:
                # Sync specific page
                pages = [await self._get_notion_page(page_id)]
            else:
                # Sync all pages in database
                pages = await self._get_database_pages(schema.database_id)
            
            synced_records = []
            
            for page in pages:
                if not page:
                    continue
                
                # Transform data from Notion format
                intelligence_os_data = await self._transform_from_notion(page['properties'], mappings)
                
                # Check for conflicts
                conflict = await self._check_for_conflicts(database_type, intelligence_os_data, page)
                
                if conflict:
                    # Handle conflict
                    conflict_result = await self._handle_conflict(conflict)
                    if not conflict_result['resolved']:
                        continue
                    intelligence_os_data = conflict_result['resolved_data']
                
                # Update Intelligence OS data (this would integrate with your data layer)
                update_result = await self._update_intelligence_os_data(database_type, intelligence_os_data)
                
                if update_result['success']:
                    # Record sync operation
                    sync_record = SyncRecord(
                        id=str(uuid.uuid4()),
                        database_type=database_type,
                        record_id=intelligence_os_data.get('id'),
                        notion_page_id=page['id'],
                        direction=SyncDirection.FROM_NOTION,
                        status=SyncStatus.COMPLETED,
                        last_sync=datetime.utcnow()
                    )
                    
                    self.sync_records[sync_record.id] = sync_record
                    synced_records.append(intelligence_os_data)
            
            logger.info("Data synced from Notion", 
                       database_type=database_type,
                       records_synced=len(synced_records))
            
            return {
                'success': True,
                'records_synced': len(synced_records),
                'data': synced_records
            }
            
        except Exception as e:
            logger.error("Sync from Notion failed", error=str(e), database_type=database_type)
            return {
                'success': False,
                'error': str(e)
            }
    
    async def bidirectional_sync(self, database_type: str) -> Dict[str, Any]:
        """
        Perform bidirectional synchronization between Intelligence OS and Notion
        """
        try:
            # First sync from Notion to get latest changes
            from_notion_result = await self.sync_from_notion(database_type)
            
            # Then sync to Notion to push any local changes
            # This would require getting all local records for the database type
            local_records = await self._get_local_records(database_type)
            
            to_notion_results = []
            for record in local_records:
                result = await self.sync_to_notion(database_type, record, record.get('id'))
                to_notion_results.append(result)
            
            successful_to_notion = sum(1 for r in to_notion_results if r.get('success'))
            
            return {
                'success': True,
                'from_notion': from_notion_result,
                'to_notion': {
                    'total_records': len(to_notion_results),
                    'successful': successful_to_notion,
                    'failed': len(to_notion_results) - successful_to_notion
                },
                'sync_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Bidirectional sync failed", error=str(e), database_type=database_type)
            return {
                'success': False,
                'error': str(e)
            }
    
    # Conflict Resolution Methods
    async def _check_for_conflicts(self, database_type: str, intelligence_os_data: Dict[str, Any], 
                                 notion_page: Dict[str, Any]) -> Optional[ConflictRecord]:
        """
        Check for conflicts between Intelligence OS and Notion data
        """
        try:
            record_id = intelligence_os_data.get('id')
            if not record_id:
                return None
            
            # Get local data for comparison
            local_data = await self._get_local_record(database_type, record_id)
            if not local_data:
                return None  # No local record, no conflict
            
            # Get last sync time
            last_sync = await self._get_last_sync_time(database_type, record_id)
            
            # Check if both local and Notion data have been modified since last sync
            local_modified = local_data.get('last_modified')
            notion_modified = datetime.fromisoformat(notion_page['last_edited_time'].replace('Z', '+00:00'))
            
            if (last_sync and local_modified and 
                local_modified > last_sync and notion_modified > last_sync):
                
                # Find conflicting fields
                conflicting_fields = []
                mappings = self.field_mappings.get(database_type, [])
                
                for mapping in mappings:
                    if not mapping.bidirectional:
                        continue
                    
                    local_value = local_data.get(mapping.intelligence_os_field)
                    notion_value = intelligence_os_data.get(mapping.intelligence_os_field)
                    
                    if local_value != notion_value:
                        conflicting_fields.append(mapping.intelligence_os_field)
                
                if conflicting_fields:
                    conflict = ConflictRecord(
                        id=str(uuid.uuid4()),
                        database_type=database_type,
                        record_id=record_id,
                        notion_page_id=notion_page['id'],
                        intelligence_os_data=local_data,
                        notion_data=intelligence_os_data,
                        conflict_fields=conflicting_fields,
                        resolution_strategy=ConflictResolution.LATEST_WINS,  # Default strategy
                        created_at=datetime.utcnow()
                    )
                    
                    self.conflict_records[conflict.id] = conflict
                    return conflict
            
            return None
            
        except Exception as e:
            logger.error("Conflict check failed", error=str(e))
            return None
    
    async def _handle_conflict(self, conflict: ConflictRecord) -> Dict[str, Any]:
        """
        Handle synchronization conflict based on resolution strategy
        """
        try:
            if conflict.resolution_strategy == ConflictResolution.LATEST_WINS:
                # Compare modification times and use latest
                ios_modified = conflict.intelligence_os_data.get('last_modified')
                notion_modified = datetime.utcnow()  # Notion data is being synced now
                
                if notion_modified > ios_modified:
                    resolved_data = conflict.notion_data
                else:
                    resolved_data = conflict.intelligence_os_data
                    
            elif conflict.resolution_strategy == ConflictResolution.NOTION_WINS:
                resolved_data = conflict.notion_data
                
            elif conflict.resolution_strategy == ConflictResolution.INTELLIGENCE_OS_WINS:
                resolved_data = conflict.intelligence_os_data
                
            elif conflict.resolution_strategy == ConflictResolution.MERGE_FIELDS:
                resolved_data = await self._merge_conflicting_fields(conflict)
                
            else:  # MANUAL_REVIEW
                # Mark for manual review
                conflict.resolution_strategy = ConflictResolution.MANUAL_REVIEW
                return {
                    'resolved': False,
                    'requires_manual_review': True,
                    'conflict_id': conflict.id
                }
            
            # Mark conflict as resolved
            conflict.resolved_at = datetime.utcnow()
            conflict.resolution_data = resolved_data
            
            logger.info("Conflict resolved", 
                       conflict_id=conflict.id,
                       strategy=conflict.resolution_strategy.value)
            
            return {
                'resolved': True,
                'resolved_data': resolved_data,
                'strategy': conflict.resolution_strategy.value
            }
            
        except Exception as e:
            logger.error("Conflict resolution failed", error=str(e), conflict_id=conflict.id)
            return {
                'resolved': False,
                'error': str(e)
            }
    
    async def _merge_conflicting_fields(self, conflict: ConflictRecord) -> Dict[str, Any]:
        """
        Merge conflicting fields using intelligent merge strategies
        """
        try:
            merged_data = conflict.intelligence_os_data.copy()
            
            for field in conflict.conflict_fields:
                ios_value = conflict.intelligence_os_data.get(field)
                notion_value = conflict.notion_data.get(field)
                
                # Field-specific merge logic
                if field in ['tags', 'stakeholders', 'participants']:
                    # Merge lists by combining unique values
                    if isinstance(ios_value, list) and isinstance(notion_value, list):
                        merged_data[field] = list(set(ios_value + notion_value))
                    else:
                        merged_data[field] = notion_value  # Use Notion value as fallback
                        
                elif field in ['description', 'notes', 'recommendations']:
                    # Merge text fields by combining with separator
                    if ios_value and notion_value and ios_value != notion_value:
                        merged_data[field] = f"{ios_value}\n\n--- Merged from Notion ---\n{notion_value}"
                    else:
                        merged_data[field] = notion_value or ios_value
                        
                elif field in ['priority', 'status']:
                    # Use Notion value for status fields (assuming Notion is more current)
                    merged_data[field] = notion_value
                    
                else:
                    # Default: use Notion value
                    merged_data[field] = notion_value
            
            return merged_data
            
        except Exception as e:
            logger.error("Field merge failed", error=str(e))
            return conflict.intelligence_os_data 
   
    # Data Transformation Methods
    async def _transform_to_notion(self, data: Dict[str, Any], mappings: List[SyncMapping]) -> Dict[str, Any]:
        """Transform Intelligence OS data to Notion format"""
        try:
            notion_properties = {}
            
            for mapping in mappings:
                value = data.get(mapping.intelligence_os_field)
                if value is None:
                    continue
                
                # Apply transformation function if specified
                if mapping.transformation_function:
                    transformer = self.transformers.get(mapping.transformation_function)
                    if transformer:
                        value = await transformer(value, 'to_notion')
                
                # Format based on property type
                if mapping.property_type == NotionPropertyType.TITLE:
                    notion_properties[mapping.notion_property] = {
                        "title": [{"type": "text", "text": {"content": str(value)[:2000]}}]
                    }
                elif mapping.property_type == NotionPropertyType.RICH_TEXT:
                    if isinstance(value, list):
                        notion_properties[mapping.notion_property] = {"rich_text": value}
                    else:
                        notion_properties[mapping.notion_property] = {
                            "rich_text": [{"type": "text", "text": {"content": str(value)[:2000]}}]
                        }
                elif mapping.property_type == NotionPropertyType.NUMBER:
                    if isinstance(value, (int, float)):
                        notion_properties[mapping.notion_property] = {"number": value}
                elif mapping.property_type == NotionPropertyType.SELECT:
                    notion_properties[mapping.notion_property] = {
                        "select": {"name": str(value)} if value else None
                    }
                elif mapping.property_type == NotionPropertyType.MULTI_SELECT:
                    if isinstance(value, list):
                        notion_properties[mapping.notion_property] = {
                            "multi_select": [{"name": str(item)} for item in value]
                        }
                elif mapping.property_type == NotionPropertyType.DATE:
                    if isinstance(value, dict) and 'start' in value:
                        notion_properties[mapping.notion_property] = {"date": value}
                    elif value:
                        notion_properties[mapping.notion_property] = {
                            "date": {"start": value}
                        }
                elif mapping.property_type == NotionPropertyType.PEOPLE:
                    if isinstance(value, list):
                        notion_properties[mapping.notion_property] = {"people": value}
                elif mapping.property_type == NotionPropertyType.CHECKBOX:
                    notion_properties[mapping.notion_property] = {"checkbox": bool(value)}
                elif mapping.property_type == NotionPropertyType.URL:
                    if value and isinstance(value, str):
                        notion_properties[mapping.notion_property] = {"url": value}
                elif mapping.property_type == NotionPropertyType.RELATION:
                    if isinstance(value, list):
                        notion_properties[mapping.notion_property] = {"relation": value}
                    elif value:
                        notion_properties[mapping.notion_property] = {
                            "relation": [{"id": str(value)}]
                        }
            
            return notion_properties
            
        except Exception as e:
            logger.error("Data transformation to Notion failed", error=str(e))
            return {}
    
    async def _transform_from_notion(self, notion_properties: Dict[str, Any], 
                                   mappings: List[SyncMapping]) -> Dict[str, Any]:
        """Transform Notion data to Intelligence OS format"""
        try:
            intelligence_os_data = {}
            
            for mapping in mappings:
                notion_prop = notion_properties.get(mapping.notion_property)
                if not notion_prop:
                    continue
                
                value = None
                
                # Extract value based on property type
                if mapping.property_type == NotionPropertyType.TITLE:
                    if notion_prop.get('title'):
                        value = ''.join([text['plain_text'] for text in notion_prop['title']])
                elif mapping.property_type == NotionPropertyType.RICH_TEXT:
                    if notion_prop.get('rich_text'):
                        value = ''.join([text['plain_text'] for text in notion_prop['rich_text']])
                elif mapping.property_type == NotionPropertyType.NUMBER:
                    value = notion_prop.get('number')
                elif mapping.property_type == NotionPropertyType.SELECT:
                    select_value = notion_prop.get('select')
                    value = select_value['name'] if select_value else None
                elif mapping.property_type == NotionPropertyType.MULTI_SELECT:
                    multi_select = notion_prop.get('multi_select', [])
                    value = [item['name'] for item in multi_select]
                elif mapping.property_type == NotionPropertyType.DATE:
                    date_value = notion_prop.get('date')
                    if date_value:
                        value = date_value.get('start')
                elif mapping.property_type == NotionPropertyType.PEOPLE:
                    people = notion_prop.get('people', [])
                    value = [person['id'] for person in people]
                elif mapping.property_type == NotionPropertyType.CHECKBOX:
                    value = notion_prop.get('checkbox', False)
                elif mapping.property_type == NotionPropertyType.URL:
                    value = notion_prop.get('url')
                elif mapping.property_type == NotionPropertyType.RELATION:
                    relations = notion_prop.get('relation', [])
                    value = [rel['id'] for rel in relations]
                elif mapping.property_type in [NotionPropertyType.CREATED_TIME, NotionPropertyType.LAST_EDITED_TIME]:
                    value = notion_prop.get(mapping.property_type.value)
                
                # Apply reverse transformation function if specified
                if value is not None and mapping.transformation_function:
                    transformer = self.transformers.get(mapping.transformation_function)
                    if transformer:
                        value = await transformer(value, 'from_notion')
                
                if value is not None:
                    intelligence_os_data[mapping.intelligence_os_field] = value
            
            return intelligence_os_data
            
        except Exception as e:
            logger.error("Data transformation from Notion failed", error=str(e))
            return {}
    
    # Transformation Functions
    async def _datetime_to_notion(self, value: Any, direction: str) -> Any:
        """Transform datetime between formats"""
        if direction == 'to_notion':
            if isinstance(value, datetime):
                return value.isoformat()
            elif isinstance(value, str):
                return value
        else:  # from_notion
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    return value
        return value
    
    async def _notion_to_datetime(self, value: Any, direction: str) -> Any:
        """Reverse datetime transformation"""
        return await self._datetime_to_notion(value, 'from_notion' if direction == 'to_notion' else 'to_notion')
    
    async def _text_to_rich_text(self, value: Any, direction: str) -> Any:
        """Transform text to/from rich text format"""
        if direction == 'to_notion':
            if isinstance(value, str):
                return [{"type": "text", "text": {"content": value[:2000]}}]
        else:  # from_notion
            if isinstance(value, list):
                return ''.join([item.get('plain_text', '') for item in value])
        return value
    
    async def _rich_text_to_text(self, value: Any, direction: str) -> Any:
        """Reverse rich text transformation"""
        return await self._text_to_rich_text(value, 'from_notion' if direction == 'to_notion' else 'to_notion')
    
    async def _list_to_multiselect(self, value: Any, direction: str) -> Any:
        """Transform list to/from multi-select format"""
        if direction == 'to_notion':
            if isinstance(value, list):
                return [{"name": str(item)} for item in value]
        else:  # from_notion
            if isinstance(value, list):
                return [item.get('name', str(item)) for item in value]
        return value
    
    async def _multiselect_to_list(self, value: Any, direction: str) -> Any:
        """Reverse multi-select transformation"""
        return await self._list_to_multiselect(value, 'from_notion' if direction == 'to_notion' else 'to_notion')
    
    async def _name_to_people(self, value: Any, direction: str) -> Any:
        """Transform name to/from people format"""
        if direction == 'to_notion':
            if isinstance(value, str):
                # This would need to resolve names to Notion user IDs
                # For now, return empty list
                return []
        else:  # from_notion
            if isinstance(value, list):
                # Extract names from people objects
                return [person.get('name', person.get('id', '')) for person in value]
        return value
    
    async def _people_to_name(self, value: Any, direction: str) -> Any:
        """Reverse people transformation"""
        return await self._name_to_people(value, 'from_notion' if direction == 'to_notion' else 'to_notion')
    
    async def _list_to_people(self, value: Any, direction: str) -> Any:
        """Transform list to/from people format"""
        if direction == 'to_notion':
            if isinstance(value, list):
                # This would need to resolve names to Notion user IDs
                return []
        else:  # from_notion
            if isinstance(value, list):
                return [person.get('name', person.get('id', '')) for person in value]
        return value
    
    async def _people_to_list(self, value: Any, direction: str) -> Any:
        """Reverse people list transformation"""
        return await self._list_to_people(value, 'from_notion' if direction == 'to_notion' else 'to_notion')
    
    async def _id_to_relation(self, value: Any, direction: str) -> Any:
        """Transform ID to/from relation format"""
        if direction == 'to_notion':
            if value:
                return [{"id": str(value)}]
        else:  # from_notion
            if isinstance(value, list) and value:
                return value[0].get('id')
        return value
    
    async def _relation_to_id(self, value: Any, direction: str) -> Any:
        """Reverse relation transformation"""
        return await self._id_to_relation(value, 'from_notion' if direction == 'to_notion' else 'to_notion')
    
    async def _list_to_relation(self, value: Any, direction: str) -> Any:
        """Transform list to/from relation format"""
        if direction == 'to_notion':
            if isinstance(value, list):
                return [{"id": str(item)} for item in value]
        else:  # from_notion
            if isinstance(value, list):
                return [rel.get('id') for rel in value]
        return value
    
    async def _relation_to_list(self, value: Any, direction: str) -> Any:
        """Reverse relation list transformation"""
        return await self._list_to_relation(value, 'from_notion' if direction == 'to_notion' else 'to_notion')
    
    # Notion API Methods
    async def _create_notion_page(self, database_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new page in Notion database"""
        try:
            payload = {
                "parent": {"database_id": database_id},
                "properties": properties
            }
            
            async with self.session.post(f"{self.base_url}/pages", json=payload) as response:
                if response.status == 200:
                    page_data = await response.json()
                    return {
                        'success': True,
                        'page_id': page_data['id'],
                        'url': page_data['url']
                    }
                else:
                    error_data = await response.json()
                    return {
                        'success': False,
                        'error': error_data.get('message', 'Page creation failed'),
                        'status': response.status
                    }
                    
        except Exception as e:
            logger.error("Notion page creation failed", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _update_notion_page(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing Notion page"""
        try:
            payload = {
                "properties": properties
            }
            
            async with self.session.patch(f"{self.base_url}/pages/{page_id}", json=payload) as response:
                if response.status == 200:
                    page_data = await response.json()
                    return {
                        'success': True,
                        'page_id': page_data['id'],
                        'url': page_data['url']
                    }
                else:
                    error_data = await response.json()
                    return {
                        'success': False,
                        'error': error_data.get('message', 'Page update failed'),
                        'status': response.status
                    }
                    
        except Exception as e:
            logger.error("Notion page update failed", error=str(e))
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_notion_page(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Get a Notion page by ID"""
        try:
            async with self.session.get(f"{self.base_url}/pages/{page_id}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error("Failed to get Notion page", page_id=page_id, status=response.status)
                    return None
                    
        except Exception as e:
            logger.error("Notion page retrieval failed", error=str(e), page_id=page_id)
            return None
    
    async def _get_database_pages(self, database_id: str, page_size: int = 100) -> List[Dict[str, Any]]:
        """Get all pages from a Notion database"""
        try:
            pages = []
            has_more = True
            next_cursor = None
            
            while has_more:
                payload = {
                    "page_size": page_size
                }
                if next_cursor:
                    payload["start_cursor"] = next_cursor
                
                async with self.session.post(f"{self.base_url}/databases/{database_id}/query", 
                                           json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        pages.extend(data.get('results', []))
                        has_more = data.get('has_more', False)
                        next_cursor = data.get('next_cursor')
                    else:
                        logger.error("Failed to query database", database_id=database_id, status=response.status)
                        break
            
            return pages
            
        except Exception as e:
            logger.error("Database query failed", error=str(e), database_id=database_id)
            return []
    
    async def _find_notion_page(self, database_type: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Find a Notion page by record ID"""
        try:
            if database_type not in self.database_schemas:
                return None
            
            schema = self.database_schemas[database_type]
            
            # Query database for page with matching record ID
            payload = {
                "filter": {
                    "property": schema.title_property,
                    "title": {
                        "equals": record_id
                    }
                }
            }
            
            async with self.session.post(f"{self.base_url}/databases/{schema.database_id}/query", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', [])
                    return results[0] if results else None
                else:
                    return None
                    
        except Exception as e:
            logger.error("Notion page search failed", error=str(e))
            return None
    
    # Integration with Intelligence OS Data Layer
    async def _get_local_records(self, database_type: str) -> List[Dict[str, Any]]:
        """Get all local records for a database type"""
        # This would integrate with your actual data layer
        # For now, return empty list
        return []
    
    async def _get_local_record(self, database_type: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific local record"""
        # This would integrate with your actual data layer
        # For now, return None
        return None
    
    async def _update_intelligence_os_data(self, database_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update Intelligence OS data"""
        # This would integrate with your actual data layer
        # For now, return success
        return {'success': True}
    
    async def _get_last_sync_time(self, database_type: str, record_id: str) -> Optional[datetime]:
        """Get the last sync time for a record"""
        for sync_record in self.sync_records.values():
            if (sync_record.database_type == database_type and 
                sync_record.record_id == record_id):
                return sync_record.last_sync
        return None
    
    # Public API Methods
    async def get_sync_status(self, database_type: str = None) -> Dict[str, Any]:
        """Get synchronization status"""
        try:
            if database_type:
                # Get status for specific database type
                records = [r for r in self.sync_records.values() if r.database_type == database_type]
            else:
                # Get status for all database types
                records = list(self.sync_records.values())
            
            status_counts = defaultdict(int)
            for record in records:
                status_counts[record.status.value] += 1
            
            return {
                'database_type': database_type,
                'total_records': len(records),
                'status_breakdown': dict(status_counts),
                'last_sync': max([r.last_sync for r in records]).isoformat() if records else None,
                'conflicts': len([r for r in records if r.status == SyncStatus.CONFLICT])
            }
            
        except Exception as e:
            logger.error("Sync status retrieval failed", error=str(e))
            return {
                'error': str(e)
            }
    
    async def get_conflicts(self, resolved: bool = False) -> List[Dict[str, Any]]:
        """Get conflict records"""
        try:
            conflicts = []
            
            for conflict in self.conflict_records.values():
                if resolved and not conflict.resolved_at:
                    continue
                if not resolved and conflict.resolved_at:
                    continue
                
                conflicts.append({
                    'id': conflict.id,
                    'database_type': conflict.database_type,
                    'record_id': conflict.record_id,
                    'notion_page_id': conflict.notion_page_id,
                    'conflict_fields': conflict.conflict_fields,
                    'resolution_strategy': conflict.resolution_strategy.value,
                    'created_at': conflict.created_at.isoformat(),
                    'resolved_at': conflict.resolved_at.isoformat() if conflict.resolved_at else None
                })
            
            return conflicts
            
        except Exception as e:
            logger.error("Conflicts retrieval failed", error=str(e))
            return []
    
    async def resolve_conflict(self, conflict_id: str, resolution_strategy: ConflictResolution) -> Dict[str, Any]:
        """Manually resolve a conflict"""
        try:
            if conflict_id not in self.conflict_records:
                return {
                    'success': False,
                    'error': 'Conflict not found'
                }
            
            conflict = self.conflict_records[conflict_id]
            conflict.resolution_strategy = resolution_strategy
            
            result = await self._handle_conflict(conflict)
            
            return {
                'success': result['resolved'],
                'conflict_id': conflict_id,
                'resolution_strategy': resolution_strategy.value,
                'resolved_at': datetime.utcnow().isoformat() if result['resolved'] else None
            }
            
        except Exception as e:
            logger.error("Conflict resolution failed", error=str(e), conflict_id=conflict_id)
            return {
                'success': False,
                'error': str(e)
            }

# Global Notion integration service instance
notion_integration_service = NotionIntegrationService()