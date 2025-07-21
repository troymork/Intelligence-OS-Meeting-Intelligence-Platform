"""
Zapier Webhook API Routes
Handles incoming webhooks from Zapier for automated transcript processing
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
import structlog
import json

from ..services.zapier_integration_service import zapier_integration_service

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/zapier", tags=["zapier-integration"])

# Request/Response Models
class WebhookResponse(BaseModel):
    """Response model for webhook reception"""
    webhook_id: str
    status: str
    message: Optional[str] = None
    timestamp: str
    estimated_processing_time: Optional[str] = None
    error: Optional[str] = None

class WebhookStatusResponse(BaseModel):
    """Response model for webhook status"""
    webhook_id: str
    status: str
    source: Optional[str] = None
    timestamp: Optional[str] = None
    format: Optional[str] = None
    priority: Optional[str] = None
    retry_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ProcessingStatsResponse(BaseModel):
    """Response model for processing statistics"""
    total_received: int
    total_processed: int
    total_failed: int
    success_rate: float
    average_processing_time_seconds: float
    queue_size: int
    failed_webhooks_count: int
    last_processed: Optional[str] = None
    supported_platforms: List[str]
    supported_formats: List[str]

class RetryResponse(BaseModel):
    """Response model for webhook retry"""
    webhook_id: str
    status: str
    message: Optional[str] = None
    error: Optional[str] = None

# Webhook Reception Endpoints
@router.post("/webhook/{source}")
async def receive_webhook(
    source: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Receive webhook from Zapier for a specific platform source
    
    Supported sources:
    - zoom: Zoom meeting transcripts
    - teams: Microsoft Teams transcripts
    - google_meet: Google Meet transcripts
    - webex: Cisco Webex transcripts
    - generic: Generic platform transcripts
    """
    try:
        # Get headers
        headers = dict(request.headers)
        
        # Get payload
        try:
            payload = await request.json()
        except Exception as e:
            logger.error("Invalid JSON payload", error=str(e), source=source)
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Log webhook reception
        logger.info("Webhook received", source=source, headers_count=len(headers))
        
        # Process webhook
        result = await zapier_integration_service.receive_webhook(source, headers, payload)
        
        # Start background processing if webhook was accepted
        if result.get('status') == 'received':
            background_tasks.add_task(start_webhook_processing)
        
        # Return response based on status
        if result.get('status') == 'rejected':
            return JSONResponse(
                status_code=400,
                content=result
            )
        elif result.get('status') == 'error':
            return JSONResponse(
                status_code=500,
                content=result
            )
        else:
            return JSONResponse(
                status_code=200,
                content=result
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Webhook reception failed", error=str(e), source=source)
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@router.post("/webhook/generic")
async def receive_generic_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Receive webhook from generic source (fallback endpoint)
    """
    return await receive_webhook("generic", request, background_tasks)

# Webhook Status and Management Endpoints
@router.get("/webhook/{webhook_id}/status", response_model=WebhookStatusResponse)
async def get_webhook_status(webhook_id: str):
    """
    Get the status of a specific webhook by ID
    """
    try:
        status = await zapier_integration_service.get_webhook_status(webhook_id)
        
        if status.get('status') == 'not_found':
            raise HTTPException(status_code=404, detail=f"Webhook '{webhook_id}' not found")
        
        return JSONResponse(content=status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Webhook status retrieval failed", webhook_id=webhook_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get webhook status: {str(e)}")

@router.get("/webhooks/statistics", response_model=ProcessingStatsResponse)
async def get_processing_statistics():
    """
    Get processing statistics for all webhooks
    """
    try:
        stats = await zapier_integration_service.get_processing_statistics()
        
        if 'error' in stats:
            raise HTTPException(status_code=500, detail=stats['error'])
        
        return JSONResponse(content=stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Statistics retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.post("/webhook/{webhook_id}/retry", response_model=RetryResponse)
async def retry_failed_webhook(webhook_id: str, background_tasks: BackgroundTasks):
    """
    Manually retry a failed webhook
    """
    try:
        result = await zapier_integration_service.retry_failed_webhook(webhook_id)
        
        if result.get('status') == 'not_found':
            raise HTTPException(status_code=404, detail=f"Failed webhook '{webhook_id}' not found")
        
        # Start background processing if webhook was requeued
        if result.get('status') == 'requeued':
            background_tasks.add_task(start_webhook_processing)
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Webhook retry failed", webhook_id=webhook_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retry webhook: {str(e)}")

@router.get("/webhooks/failed")
async def get_failed_webhooks():
    """
    Get list of failed webhooks
    """
    try:
        failed_webhooks = []
        
        for webhook_id, failure_result in zapier_integration_service.failed_webhooks.items():
            if webhook_id in zapier_integration_service.webhook_history:
                webhook = zapier_integration_service.webhook_history[webhook_id]
                failed_webhooks.append({
                    'webhook_id': webhook_id,
                    'source': webhook.source,
                    'timestamp': webhook.timestamp.isoformat(),
                    'retry_count': webhook.retry_count,
                    'error_message': failure_result.error_message,
                    'next_retry_at': failure_result.next_retry_at.isoformat() if failure_result.next_retry_at else None,
                    'metadata': {
                        'meeting_title': webhook.metadata.meeting_title,
                        'participant_count': webhook.metadata.participant_count,
                        'duration_minutes': webhook.metadata.duration_minutes
                    }
                })
        
        return JSONResponse(content={
            'failed_webhooks': failed_webhooks,
            'total_count': len(failed_webhooks),
            'retrieved_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Failed webhooks retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get failed webhooks: {str(e)}")

# Configuration and Information Endpoints
@router.get("/platforms")
async def get_supported_platforms():
    """
    Get list of supported platforms and their configurations
    """
    try:
        platforms = []
        
        for platform_id, config in zapier_integration_service.platform_configs.items():
            platforms.append({
                'id': platform_id,
                'name': config['name'],
                'supported_formats': [fmt.value for fmt in config['supported_formats']],
                'webhook_endpoint': f"/api/zapier/webhook/{platform_id}",
                'metadata_fields': config['metadata_fields']
            })
        
        return JSONResponse(content={
            'platforms': platforms,
            'total_count': len(platforms),
            'default_platform': 'generic'
        })
        
    except Exception as e:
        logger.error("Platform information retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get platform information: {str(e)}")

@router.get("/formats")
async def get_supported_formats():
    """
    Get list of supported transcript formats
    """
    try:
        from ..services.zapier_integration_service import TranscriptFormat
        
        formats = []
        for fmt in TranscriptFormat:
            formats.append({
                'id': fmt.value,
                'name': fmt.value.title(),
                'description': f'{fmt.value.title()} format transcript'
            })
        
        return JSONResponse(content={
            'formats': formats,
            'total_count': len(formats)
        })
        
    except Exception as e:
        logger.error("Format information retrieval failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get format information: {str(e)}")

# Webhook Testing and Validation Endpoints
@router.post("/webhook/test")
async def test_webhook_endpoint(
    source: str = "generic",
    test_payload: Dict[str, Any] = None
):
    """
    Test webhook endpoint with sample data
    """
    try:
        # Default test payload if none provided
        if not test_payload:
            test_payload = {
                "meeting_id": "test_meeting_123",
                "meeting_title": "Test Meeting",
                "start_time": datetime.utcnow().isoformat(),
                "duration": 30,
                "participants": ["Test User 1", "Test User 2"],
                "transcript": "Test User 1: Hello everyone, welcome to our test meeting.\nTest User 2: Thanks for organizing this test session.\nTest User 1: Let's discuss our test agenda items."
            }
        
        # Test headers
        test_headers = {
            'content-type': 'application/json',
            'x-webhook-signature': 'test_signature',
            'x-webhook-timestamp': str(int(datetime.utcnow().timestamp())),
            'user-agent': 'Zapier-Test/1.0'
        }
        
        # Process test webhook (but don't actually trigger Oracle analysis)
        with patch.object(zapier_integration_service, '_trigger_oracle_analysis') as mock_oracle:
            mock_oracle.return_value = {'success': True, 'analysis_id': 'test_analysis_123'}
            
            result = await zapier_integration_service.receive_webhook(source, test_headers, test_payload)
        
        return JSONResponse(content={
            'test_result': result,
            'test_payload': test_payload,
            'test_headers': test_headers,
            'message': 'Test webhook processed successfully'
        })
        
    except Exception as e:
        logger.error("Webhook test failed", error=str(e), source=source)
        raise HTTPException(status_code=500, detail=f"Webhook test failed: {str(e)}")

@router.post("/webhook/validate")
async def validate_webhook_payload(payload: Dict[str, Any]):
    """
    Validate a webhook payload without processing it
    """
    try:
        # Extract content
        content_result = await zapier_integration_service._extract_content(payload)
        
        if not content_result['valid']:
            return JSONResponse(
                status_code=400,
                content={
                    'valid': False,
                    'error': content_result['error'],
                    'suggestions': [
                        'Ensure payload contains one of: transcript, content, text, body, data',
                        'Check that content is not empty',
                        'Verify content format is supported (text, json, markdown, html, xml)'
                    ]
                }
            )
        
        # Extract metadata
        metadata = await zapier_integration_service._extract_metadata(
            content_result['content'],
            content_result['format'],
            'generic',
            payload
        )
        
        return JSONResponse(content={
            'valid': True,
            'content_format': content_result['format'].value,
            'content_length': len(content_result['content']),
            'extracted_metadata': {
                'meeting_id': metadata.meeting_id,
                'meeting_title': metadata.meeting_title,
                'meeting_date': metadata.meeting_date.isoformat() if metadata.meeting_date else None,
                'duration_minutes': metadata.duration_minutes,
                'participant_count': metadata.participant_count,
                'participants': metadata.participants[:5] if metadata.participants else [],  # First 5 participants
                'confidence_score': metadata.confidence_score,
                'source_platform': metadata.source_platform
            },
            'validation_timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Payload validation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Payload validation failed: {str(e)}")

# Background Processing Management
async def start_webhook_processing():
    """
    Start background webhook processing
    """
    try:
        # This would typically be handled by a background task manager
        # For now, we'll just log that processing should start
        logger.info("Background webhook processing requested")
        
        # In a production environment, this might:
        # 1. Start a background worker process
        # 2. Add tasks to a job queue (Redis, Celery, etc.)
        # 3. Trigger a serverless function
        # 4. Send a message to a message queue
        
    except Exception as e:
        logger.error("Background processing start failed", error=str(e))

@router.post("/processing/start")
async def start_processing_manually():
    """
    Manually start webhook processing (for testing/debugging)
    """
    try:
        queue_size = zapier_integration_service.processing_queue.qsize()
        
        if queue_size == 0:
            return JSONResponse(content={
                'message': 'No webhooks in queue to process',
                'queue_size': 0,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Start processing (this would be handled differently in production)
        await start_webhook_processing()
        
        return JSONResponse(content={
            'message': f'Processing started for {queue_size} webhooks',
            'queue_size': queue_size,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error("Manual processing start failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")

# Health Check Endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint for Zapier integration service
    """
    try:
        stats = await zapier_integration_service.get_processing_statistics()
        
        service_status = {
            'service': 'zapier_integration',
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'components': {
                'webhook_queue_size': stats.get('queue_size', 0),
                'total_processed': stats.get('total_processed', 0),
                'success_rate': stats.get('success_rate', 0),
                'supported_platforms': len(stats.get('supported_platforms', [])),
                'supported_formats': len(stats.get('supported_formats', []))
            },
            'endpoints': {
                'webhook_reception': '/api/zapier/webhook/{source}',
                'status_check': '/api/zapier/webhook/{webhook_id}/status',
                'statistics': '/api/zapier/webhooks/statistics',
                'retry': '/api/zapier/webhook/{webhook_id}/retry'
            }
        }
        
        return JSONResponse(content=service_status)
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                'service': 'zapier_integration',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        )

# Import patch for testing
try:
    from unittest.mock import patch
except ImportError:
    # Fallback for production environments
    def patch(*args, **kwargs):
        def decorator(func):
            return func
        return decorator