"""
Input Validation Manager for Intelligence OS
Handles input sanitization and validation
"""

import re
import html
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import logging
import structlog

logger = structlog.get_logger(__name__)

class InputValidator:
    """Input validation and sanitization manager"""
    
    def __init__(self):
        # Common validation patterns
        self.patterns = {
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'phone': re.compile(r'^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'),
            'uuid': re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'),
            'alphanumeric': re.compile(r'^[a-zA-Z0-9]+$'),
            'safe_string': re.compile(r'^[a-zA-Z0-9\s\-_.,!?]+$'),
            'sql_injection': re.compile(r'(union|select|insert|update|delete|drop|create|alter|exec|execute)', re.IGNORECASE),
            'xss': re.compile(r'<script|javascript:|on\w+\s*=', re.IGNORECASE)
        }
        
        # Maximum lengths for different field types
        self.max_lengths = {
            'short_text': 100,
            'medium_text': 500,
            'long_text': 5000,
            'description': 2000,
            'title': 200,
            'name': 100,
            'email': 254,
            'phone': 20,
            'url': 2048
        }
    
    def validate_text(self, text: str, field_type: str = 'medium_text', 
                     allow_html: bool = False, required: bool = True) -> Dict[str, Any]:
        """Validate and sanitize text input"""
        result = {
            'valid': True,
            'sanitized': text,
            'errors': []
        }
        
        try:
            # Check if required
            if required and (not text or not text.strip()):
                result['valid'] = False
                result['errors'].append('Field is required')
                return result
            
            if not text:
                return result
            
            # Check length
            max_length = self.max_lengths.get(field_type, 500)
            if len(text) > max_length:
                result['valid'] = False
                result['errors'].append(f'Text exceeds maximum length of {max_length} characters')
            
            # Check for SQL injection attempts
            if self.patterns['sql_injection'].search(text):
                result['valid'] = False
                result['errors'].append('Potentially malicious SQL content detected')
            
            # Check for XSS attempts
            if self.patterns['xss'].search(text):
                result['valid'] = False
                result['errors'].append('Potentially malicious script content detected')
            
            # Sanitize HTML if not allowed
            if not allow_html:
                result['sanitized'] = html.escape(text)
            
            # Additional sanitization
            result['sanitized'] = result['sanitized'].strip()
            
        except Exception as e:
            logger.error("Text validation failed", error=str(e))
            result['valid'] = False
            result['errors'].append('Validation error occurred')
        
        return result
    
    def validate_email(self, email: str, required: bool = True) -> Dict[str, Any]:
        """Validate email address"""
        result = {
            'valid': True,
            'sanitized': email.lower().strip() if email else '',
            'errors': []
        }
        
        try:
            if required and not email:
                result['valid'] = False
                result['errors'].append('Email is required')
                return result
            
            if not email:
                return result
            
            # Check format
            if not self.patterns['email'].match(email):
                result['valid'] = False
                result['errors'].append('Invalid email format')
            
            # Check length
            if len(email) > self.max_lengths['email']:
                result['valid'] = False
                result['errors'].append('Email address too long')
                
        except Exception as e:
            logger.error("Email validation failed", error=str(e))
            result['valid'] = False
            result['errors'].append('Email validation error')
        
        return result
    
    def validate_json(self, json_str: str, required: bool = True) -> Dict[str, Any]:
        """Validate JSON string"""
        result = {
            'valid': True,
            'sanitized': json_str,
            'parsed': None,
            'errors': []
        }
        
        try:
            if required and not json_str:
                result['valid'] = False
                result['errors'].append('JSON is required')
                return result
            
            if not json_str:
                return result
            
            # Try to parse JSON
            try:
                result['parsed'] = json.loads(json_str)
            except json.JSONDecodeError as e:
                result['valid'] = False
                result['errors'].append(f'Invalid JSON format: {str(e)}')
                
        except Exception as e:
            logger.error("JSON validation failed", error=str(e))
            result['valid'] = False
            result['errors'].append('JSON validation error')
        
        return result
    
    def validate_uuid(self, uuid_str: str, required: bool = True) -> Dict[str, Any]:
        """Validate UUID string"""
        result = {
            'valid': True,
            'sanitized': uuid_str.lower().strip() if uuid_str else '',
            'errors': []
        }
        
        try:
            if required and not uuid_str:
                result['valid'] = False
                result['errors'].append('UUID is required')
                return result
            
            if not uuid_str:
                return result
            
            # Check format
            if not self.patterns['uuid'].match(uuid_str.lower()):
                result['valid'] = False
                result['errors'].append('Invalid UUID format')
                
        except Exception as e:
            logger.error("UUID validation failed", error=str(e))
            result['valid'] = False
            result['errors'].append('UUID validation error')
        
        return result
    
    def validate_meeting_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate meeting data structure"""
        result = {
            'valid': True,
            'sanitized': {},
            'errors': []
        }
        
        try:
            # Validate title
            if 'title' in data:
                title_result = self.validate_text(data['title'], 'title', required=True)
                if not title_result['valid']:
                    result['valid'] = False
                    result['errors'].extend([f"Title: {error}" for error in title_result['errors']])
                else:
                    result['sanitized']['title'] = title_result['sanitized']
            
            # Validate participants
            if 'participants' in data:
                if not isinstance(data['participants'], list):
                    result['valid'] = False
                    result['errors'].append('Participants must be a list')
                else:
                    sanitized_participants = []
                    for participant in data['participants']:
                        if isinstance(participant, str):
                            participant_result = self.validate_text(participant, 'name')
                            if participant_result['valid']:
                                sanitized_participants.append(participant_result['sanitized'])
                    result['sanitized']['participants'] = sanitized_participants
            
            # Validate agenda
            if 'agenda' in data:
                if isinstance(data['agenda'], list):
                    sanitized_agenda = []
                    for item in data['agenda']:
                        if isinstance(item, str):
                            item_result = self.validate_text(item, 'description')
                            if item_result['valid']:
                                sanitized_agenda.append(item_result['sanitized'])
                    result['sanitized']['agenda'] = sanitized_agenda
                elif isinstance(data['agenda'], str):
                    agenda_result = self.validate_text(data['agenda'], 'long_text')
                    if agenda_result['valid']:
                        result['sanitized']['agenda'] = agenda_result['sanitized']
            
            # Validate context
            if 'context' in data:
                if isinstance(data['context'], dict):
                    result['sanitized']['context'] = data['context']
                elif isinstance(data['context'], str):
                    context_result = self.validate_json(data['context'], required=False)
                    if context_result['valid'] and context_result['parsed']:
                        result['sanitized']['context'] = context_result['parsed']
                    else:
                        context_text_result = self.validate_text(data['context'], 'long_text')
                        if context_text_result['valid']:
                            result['sanitized']['context'] = {'description': context_text_result['sanitized']}
            
        except Exception as e:
            logger.error("Meeting data validation failed", error=str(e))
            result['valid'] = False
            result['errors'].append('Meeting data validation error')
        
        return result
    
    def validate_nlu_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate NLU processing input"""
        result = {
            'valid': True,
            'sanitized': {},
            'errors': []
        }
        
        try:
            # Validate text
            if 'text' not in data:
                result['valid'] = False
                result['errors'].append('Text is required for NLU processing')
                return result
            
            text_result = self.validate_text(data['text'], 'long_text', required=True)
            if not text_result['valid']:
                result['valid'] = False
                result['errors'].extend([f"Text: {error}" for error in text_result['errors']])
            else:
                result['sanitized']['text'] = text_result['sanitized']
            
            # Validate session_id
            if 'session_id' in data:
                session_result = self.validate_text(data['session_id'], 'short_text')
                if session_result['valid']:
                    result['sanitized']['session_id'] = session_result['sanitized']
            
            # Validate meeting_context
            if 'meeting_context' in data:
                if isinstance(data['meeting_context'], dict):
                    context_validation = self.validate_meeting_data(data['meeting_context'])
                    if context_validation['valid']:
                        result['sanitized']['meeting_context'] = context_validation['sanitized']
                    else:
                        result['errors'].extend([f"Meeting context: {error}" for error in context_validation['errors']])
            
        except Exception as e:
            logger.error("NLU input validation failed", error=str(e))
            result['valid'] = False
            result['errors'].append('NLU input validation error')
        
        return result
    
    def sanitize_for_storage(self, data: Any) -> Any:
        """Sanitize data for safe storage"""
        try:
            if isinstance(data, str):
                # Remove null bytes and control characters
                sanitized = data.replace('\x00', '').replace('\r', '').replace('\n', ' ')
                # Limit length
                if len(sanitized) > 10000:  # Max storage length
                    sanitized = sanitized[:10000] + '...'
                return sanitized
            elif isinstance(data, dict):
                return {key: self.sanitize_for_storage(value) for key, value in data.items()}
            elif isinstance(data, list):
                return [self.sanitize_for_storage(item) for item in data]
            else:
                return data
        except Exception as e:
            logger.error("Data sanitization failed", error=str(e))
            return str(data)[:1000]  # Fallback to string representation

# Global input validator instance
input_validator = InputValidator()