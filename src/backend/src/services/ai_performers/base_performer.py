"""
Base AI Performer for Intelligence OS
Provides foundation for specialized AI performers
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
import json
import openai
import structlog

from .message_handlers import BasePerformerMessageHandler

logger = structlog.get_logger(__name__)

class BaseAIPerformer(ABC):
    """Base class for all AI performers"""
    
    def __init__(self, performer_id: str, name: str, dimension: str):
        self.performer_id = performer_id
        self.name = name
        self.dimension = dimension
        self.openai_client = None
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '4000'))
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.2'))
        
        # Performance tracking
        self.total_tasks_processed = 0
        self.successful_tasks = 0
        self.failed_tasks = 0
        self.total_processing_time = 0.0
        self.last_activity = None
        
        # Capabilities and configuration
        self.capabilities = self._get_capabilities()
        self.system_prompt = self._get_system_prompt()
        
        # Communication capabilities
        self.message_handler = None
        self.communication_hub = None
    
    async def initialize(self):
        """Initialize the AI performer"""
        try:
            # Initialize OpenAI client
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
                logger.info(f"{self.name} initialized with OpenAI", performer_id=self.performer_id)
            else:
                logger.warning(f"{self.name} initialized without OpenAI", performer_id=self.performer_id)
            
            # Additional initialization
            await self._initialize_resources()
            
            logger.info(f"{self.name} initialized successfully", performer_id=self.performer_id)
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name}", performer_id=self.performer_id, error=str(e))
            raise
    
    async def _initialize_resources(self):
        """Initialize additional resources (to be overridden by subclasses)"""
        pass
    
    @abstractmethod
    def _get_capabilities(self) -> Dict[str, Any]:
        """Get performer capabilities (to be implemented by subclasses)"""
        pass
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get system prompt for the performer (to be implemented by subclasses)"""
        pass
    
    @abstractmethod
    async def _generate_user_prompt(self, input_data: Dict[str, Any]) -> str:
        """Generate user prompt based on input data (to be implemented by subclasses)"""
        pass
    
    @abstractmethod
    async def _process_response(self, response_text: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI response (to be implemented by subclasses)"""
        pass
    
    async def process_task(self, task_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task with the AI performer"""
        start_time = datetime.utcnow()
        self.last_activity = start_time
        
        try:
            logger.info(f"{self.name} processing task", 
                       performer_id=self.performer_id,
                       task_id=task_id,
                       dimension=self.dimension)
            
            # Generate result using AI
            if self.openai_client:
                result = await self._process_with_openai(input_data)
            else:
                result = await self._process_with_fallback(input_data)
            
            # Add metadata
            result['task_id'] = task_id
            result['performer_id'] = self.performer_id
            result['dimension'] = self.dimension
            result['processing_time'] = (datetime.utcnow() - start_time).total_seconds()
            
            # Update performance metrics
            self.total_tasks_processed += 1
            self.successful_tasks += 1
            self.total_processing_time += result['processing_time']
            
            logger.info(f"{self.name} completed task successfully", 
                       performer_id=self.performer_id,
                       task_id=task_id,
                       processing_time=result['processing_time'])
            
            return result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.total_tasks_processed += 1
            self.failed_tasks += 1
            self.total_processing_time += processing_time
            
            logger.error(f"{self.name} task processing failed", 
                        performer_id=self.performer_id,
                        task_id=task_id,
                        error=str(e))
            
            # Return error result
            return {
                'task_id': task_id,
                'performer_id': self.performer_id,
                'dimension': self.dimension,
                'error': str(e),
                'status': 'failed',
                'processing_time': processing_time,
                'confidence': 0.0
            }
    
    async def _process_with_openai(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process task using OpenAI"""
        try:
            # Generate user prompt
            user_prompt = await self._generate_user_prompt(input_data)
            
            # Call OpenAI API
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Get response text
            response_text = response.choices[0].message.content
            
            # Process response
            result = await self._process_response(response_text, input_data)
            result['processing_method'] = 'openai'
            result['model_used'] = self.model
            
            return result
            
        except Exception as e:
            logger.error(f"OpenAI processing failed for {self.name}", 
                        performer_id=self.performer_id,
                        error=str(e))
            
            # Try fallback
            return await self._process_with_fallback(input_data)
    
    async def _process_with_fallback(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process task using fallback method when AI is unavailable"""
        try:
            # Implement basic fallback processing
            result = await self._fallback_processing(input_data)
            result['processing_method'] = 'fallback'
            
            return result
            
        except Exception as e:
            logger.error(f"Fallback processing failed for {self.name}", 
                        performer_id=self.performer_id,
                        error=str(e))
            
            raise
    
    @abstractmethod
    async def _fallback_processing(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback processing implementation (to be implemented by subclasses)"""
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Get performer status and metrics"""
        return {
            'performer_id': self.performer_id,
            'name': self.name,
            'dimension': self.dimension,
            'status': 'ready',
            'capabilities': self.capabilities,
            'metrics': {
                'total_tasks_processed': self.total_tasks_processed,
                'successful_tasks': self.successful_tasks,
                'failed_tasks': self.failed_tasks,
                'success_rate': self.successful_tasks / self.total_tasks_processed if self.total_tasks_processed > 0 else 1.0,
                'average_processing_time': self.total_processing_time / self.total_tasks_processed if self.total_tasks_processed > 0 else 0.0,
                'last_activity': self.last_activity.isoformat() if self.last_activity else None
            },
            'configuration': {
                'model': self.model,
                'temperature': self.temperature,
                'max_tokens': self.max_tokens
            }
        }
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text response"""
        try:
            # Try to find JSON in the response
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = text[json_start:json_end]
                return json.loads(json_str)
            
            # If no JSON found, try to parse the entire text
            return json.loads(text)
            
        except Exception as e:
            logger.error(f"JSON extraction failed for {self.name}", 
                        performer_id=self.performer_id,
                        error=str(e))
            
            # Return empty dict if parsing fails
            return {}