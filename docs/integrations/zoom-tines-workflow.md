# Zoom + Tines Workflow Integration for Oracle 9.1 Protocol

## 🎯 **Overview**

The Zoom + Tines integration creates a fully automated workflow that captures meeting data from Zoom, processes it through the Oracle 9.1 Protocol analysis engine, and orchestrates follow-up actions through Tines automation workflows.

## 🏗️ **Integration Architecture**

### **Workflow Components**

#### **1. Zoom Meeting Capture**
```python
class ZoomMeetingCapture:
    def __init__(self, zoom_config: dict):
        self.zoom_config = zoom_config
        self.webhook_handler = ZoomWebhookHandler()
        self.transcript_processor = TranscriptProcessor()
    
    async def setup_zoom_webhook(self):
        """Setup Zoom webhook for automatic meeting capture"""
        webhook_config = {
            "url": f"{self.zoom_config['webhook_base_url']}/api/zoom/webhook",
            "events": [
                "meeting.ended",
                "recording.completed",
                "meeting.participant_joined",
                "meeting.participant_left"
            ],
            "auth_token": self.zoom_config["auth_token"]
        }
        
        return await self._register_webhook(webhook_config)
    
    async def process_meeting_end_event(self, webhook_data: dict):
        """Process meeting end event from Zoom"""
        
        meeting_info = {
            "meeting_id": webhook_data["payload"]["object"]["id"],
            "topic": webhook_data["payload"]["object"]["topic"],
            "start_time": webhook_data["payload"]["object"]["start_time"],
            "duration": webhook_data["payload"]["object"]["duration"],
            "participants": await self._extract_participants(webhook_data),
            "recording_url": webhook_data["payload"]["object"].get("recording_url"),
            "transcript": await self._get_meeting_transcript(webhook_data["payload"]["object"]["id"])
        }
        
        # Send to Tines for Oracle processing
        await self._send_to_tines(meeting_info)
        
        return meeting_info
```

#### **2. Tines Workflow Orchestration**
```python
class TinesWorkflowOrchestrator:
    def __init__(self, tines_config: dict, oracle_service: OracleService):
        self.tines_config = tines_config
        self.oracle_service = oracle_service
        self.workflow_templates = self._load_workflow_templates()
    
    async def process_zoom_meeting(self, meeting_data: dict):
        """Process Zoom meeting through Tines workflow"""
        
        # Create Tines story for meeting processing
        story_config = {
            "name": f"Oracle Analysis - {meeting_data['topic']}",
            "description": f"Automated Oracle 9.1 Protocol analysis for meeting {meeting_data['meeting_id']}",
            "agents": self._create_workflow_agents(meeting_data)
        }
        
        story_id = await self._create_tines_story(story_config)
        
        # Execute Oracle analysis workflow
        oracle_results = await self._execute_oracle_workflow(story_id, meeting_data)
        
        # Execute Tanka debrief workflows
        debrief_results = await self._execute_debrief_workflows(story_id, meeting_data, oracle_results)
        
        # Execute follow-up action workflows
        action_results = await self._execute_action_workflows(story_id, oracle_results, debrief_results)
        
        return {
            "story_id": story_id,
            "oracle_results": oracle_results,
            "debrief_results": debrief_results,
            "action_results": action_results
        }
    
    def _create_workflow_agents(self, meeting_data: dict):
        """Create Tines agents for meeting processing workflow"""
        
        agents = [
            # Oracle Analysis Agent
            {
                "name": "oracle_analysis",
                "type": "webhook",
                "options": {
                    "url": f"{self.oracle_service.base_url}/api/oracle/analyze",
                    "method": "POST",
                    "payload": {
                        "meeting_id": meeting_data["meeting_id"],
                        "transcript": meeting_data["transcript"],
                        "participants": meeting_data["participants"],
                        "metadata": {
                            "topic": meeting_data["topic"],
                            "duration": meeting_data["duration"],
                            "start_time": meeting_data["start_time"]
                        }
                    }
                }
            },
            
            # Tanka Debrief Coordination Agent
            {
                "name": "tanka_debrief_coordinator",
                "type": "webhook",
                "options": {
                    "url": f"{self.oracle_service.base_url}/api/tanka/coordinate-debriefs",
                    "method": "POST",
                    "payload": {
                        "meeting_id": meeting_data["meeting_id"],
                        "participants": meeting_data["participants"],
                        "oracle_analysis": "{{ oracle_analysis.body }}"
                    }
                }
            },
            
            # Action Item Distribution Agent
            {
                "name": "action_distribution",
                "type": "webhook",
                "options": {
                    "url": f"{self.oracle_service.base_url}/api/actions/distribute",
                    "method": "POST",
                    "payload": {
                        "meeting_id": meeting_data["meeting_id"],
                        "oracle_analysis": "{{ oracle_analysis.body }}",
                        "debrief_results": "{{ tanka_debrief_coordinator.body }}"
                    }
                }
            },
            
            # Notification Agent
            {
                "name": "notification_sender",
                "type": "email",
                "options": {
                    "to": [participant["email"] for participant in meeting_data["participants"]],
                    "subject": f"Meeting Analysis Complete: {meeting_data['topic']}",
                    "body": self._generate_notification_template()
                }
            }
        ]
        
        return agents
```

#### **3. Oracle Integration Webhook Handler**
```python
class OracleZoomTinesHandler:
    def __init__(self, oracle_service: OracleService, tanka_service: TankaService):
        self.oracle = oracle_service
        self.tanka = tanka_service
        self.processing_queue = asyncio.Queue()
    
    async def handle_tines_webhook(self, webhook_data: dict):
        """Handle incoming webhook from Tines with Zoom meeting data"""
        
        try:
            # Validate webhook data
            validated_data = self._validate_webhook_data(webhook_data)
            
            # Process through Oracle 9.1 Protocol
            oracle_analysis = await self.oracle.analyze_meeting_comprehensive(
                meeting_id=validated_data["meeting_id"],
                transcript=validated_data["transcript"],
                participants=validated_data["participants"],
                metadata=validated_data["metadata"]
            )
            
            # Store analysis results
            await self._store_analysis_results(validated_data["meeting_id"], oracle_analysis)
            
            # Trigger Tanka debriefs for each participant
            debrief_tasks = []
            for participant in validated_data["participants"]:
                task = self.tanka.conduct_post_meeting_debrief(
                    validated_data["meeting_id"], 
                    participant["user_id"]
                )
                debrief_tasks.append(task)
            
            debrief_results = await asyncio.gather(*debrief_tasks)
            
            # Process discrepancies and generate follow-up actions
            discrepancy_analysis = await self._analyze_discrepancies(debrief_results)
            follow_up_actions = await self._generate_follow_up_actions(
                oracle_analysis, debrief_results, discrepancy_analysis
            )
            
            # Return results to Tines for further workflow processing
            return {
                "status": "success",
                "oracle_analysis": oracle_analysis,
                "debrief_results": debrief_results,
                "discrepancy_analysis": discrepancy_analysis,
                "follow_up_actions": follow_up_actions,
                "next_actions": self._determine_next_actions(discrepancy_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error processing Tines webhook: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "retry_recommended": True
            }
```

## 🔄 **Complete Workflow Process**

### **1. Meeting Lifecycle Automation**
```python
class MeetingLifecycleAutomation:
    def __init__(self, zoom_service, tines_service, oracle_service, tanka_service):
        self.zoom = zoom_service
        self.tines = tines_service
        self.oracle = oracle_service
        self.tanka = tanka_service
    
    async def handle_complete_meeting_lifecycle(self, meeting_id: str):
        """Handle complete meeting lifecycle from start to follow-up"""
        
        lifecycle_results = {
            "meeting_id": meeting_id,
            "phases": {},
            "timeline": []
        }
        
        # Phase 1: Pre-Meeting Setup
        pre_meeting_setup = await self._setup_pre_meeting_context(meeting_id)
        lifecycle_results["phases"]["pre_meeting"] = pre_meeting_setup
        lifecycle_results["timeline"].append({
            "phase": "pre_meeting",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        })
        
        # Phase 2: Meeting Monitoring (if real-time processing enabled)
        if self.zoom.real_time_monitoring_enabled:
            monitoring_results = await self._monitor_meeting_realtime(meeting_id)
            lifecycle_results["phases"]["monitoring"] = monitoring_results
        
        # Phase 3: Post-Meeting Processing
        meeting_data = await self.zoom.get_meeting_data(meeting_id)
        
        # Oracle 9.1 Protocol Analysis
        oracle_analysis = await self.oracle.analyze_meeting_comprehensive(
            meeting_id=meeting_id,
            transcript=meeting_data["transcript"],
            participants=meeting_data["participants"],
            metadata=meeting_data["metadata"]
        )
        
        lifecycle_results["phases"]["oracle_analysis"] = oracle_analysis
        lifecycle_results["timeline"].append({
            "phase": "oracle_analysis",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        })
        
        # Phase 4: Individual Tanka Debriefs
        debrief_results = {}
        for participant in meeting_data["participants"]:
            debrief_result = await self.tanka.conduct_post_meeting_debrief(
                meeting_id, participant["user_id"]
            )
            debrief_results[participant["user_id"]] = debrief_result
        
        lifecycle_results["phases"]["tanka_debriefs"] = debrief_results
        lifecycle_results["timeline"].append({
            "phase": "tanka_debriefs",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        })
        
        # Phase 5: Discrepancy Analysis and Resolution
        discrepancy_analysis = await self._analyze_cross_participant_discrepancies(
            oracle_analysis, debrief_results
        )
        
        lifecycle_results["phases"]["discrepancy_analysis"] = discrepancy_analysis
        
        # Phase 6: Action Item Generation and Distribution
        action_items = await self._generate_and_distribute_action_items(
            oracle_analysis, debrief_results, discrepancy_analysis
        )
        
        lifecycle_results["phases"]["action_items"] = action_items
        lifecycle_results["timeline"].append({
            "phase": "action_items",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        })
        
        # Phase 7: Follow-up Workflow Initiation
        follow_up_workflows = await self._initiate_follow_up_workflows(
            meeting_id, lifecycle_results
        )
        
        lifecycle_results["phases"]["follow_up"] = follow_up_workflows
        lifecycle_results["timeline"].append({
            "phase": "follow_up",
            "timestamp": datetime.now().isoformat(),
            "status": "initiated"
        })
        
        return lifecycle_results
```

### **2. Tines Story Templates**
```json
{
  "name": "Oracle 9.1 Protocol - Complete Meeting Analysis",
  "description": "Automated workflow for comprehensive meeting analysis using Oracle 9.1 Protocol with Tanka.ai integration",
  "agents": [
    {
      "name": "zoom_webhook_receiver",
      "type": "webhook",
      "description": "Receives meeting data from Zoom webhook",
      "options": {
        "secret": "{{ CREDENTIAL.zoom_webhook_secret }}",
        "verbs": ["post"],
        "path": "zoom-meeting-ended"
      }
    },
    {
      "name": "oracle_analysis_trigger",
      "type": "webhook",
      "description": "Triggers Oracle 9.1 Protocol analysis",
      "options": {
        "url": "{{ CREDENTIAL.oracle_api_base_url }}/api/oracle/analyze",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer {{ CREDENTIAL.oracle_api_token }}",
          "Content-Type": "application/json"
        },
        "payload": {
          "meeting_id": "{{ zoom_webhook_receiver.body.payload.object.id }}",
          "transcript": "{{ zoom_webhook_receiver.body.payload.object.transcript }}",
          "participants": "{{ zoom_webhook_receiver.body.payload.object.participants }}",
          "metadata": {
            "topic": "{{ zoom_webhook_receiver.body.payload.object.topic }}",
            "start_time": "{{ zoom_webhook_receiver.body.payload.object.start_time }}",
            "duration": "{{ zoom_webhook_receiver.body.payload.object.duration }}"
          }
        }
      }
    },
    {
      "name": "tanka_debrief_coordinator",
      "type": "webhook",
      "description": "Coordinates individual Tanka debriefs for all participants",
      "options": {
        "url": "{{ CREDENTIAL.oracle_api_base_url }}/api/tanka/coordinate-debriefs",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer {{ CREDENTIAL.oracle_api_token }}",
          "Content-Type": "application/json"
        },
        "payload": {
          "meeting_id": "{{ zoom_webhook_receiver.body.payload.object.id }}",
          "participants": "{{ zoom_webhook_receiver.body.payload.object.participants }}",
          "oracle_analysis": "{{ oracle_analysis_trigger.body }}"
        }
      }
    },
    {
      "name": "discrepancy_analyzer",
      "type": "webhook",
      "description": "Analyzes discrepancies between Oracle analysis and individual debriefs",
      "options": {
        "url": "{{ CREDENTIAL.oracle_api_base_url }}/api/analysis/discrepancies",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer {{ CREDENTIAL.oracle_api_token }}",
          "Content-Type": "application/json"
        },
        "payload": {
          "meeting_id": "{{ zoom_webhook_receiver.body.payload.object.id }}",
          "oracle_analysis": "{{ oracle_analysis_trigger.body }}",
          "debrief_results": "{{ tanka_debrief_coordinator.body }}"
        }
      }
    },
    {
      "name": "action_item_generator",
      "type": "webhook",
      "description": "Generates and distributes action items based on analysis",
      "options": {
        "url": "{{ CREDENTIAL.oracle_api_base_url }}/api/actions/generate",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer {{ CREDENTIAL.oracle_api_token }}",
          "Content-Type": "application/json"
        },
        "payload": {
          "meeting_id": "{{ zoom_webhook_receiver.body.payload.object.id }}",
          "oracle_analysis": "{{ oracle_analysis_trigger.body }}",
          "debrief_results": "{{ tanka_debrief_coordinator.body }}",
          "discrepancy_analysis": "{{ discrepancy_analyzer.body }}"
        }
      }
    },
    {
      "name": "notification_sender",
      "type": "email",
      "description": "Sends completion notification to all participants",
      "options": {
        "to": "{{ zoom_webhook_receiver.body.payload.object.participants | map: 'email' | join: ',' }}",
        "subject": "Meeting Analysis Complete: {{ zoom_webhook_receiver.body.payload.object.topic }}",
        "body": "Your meeting analysis is complete. Oracle insights, individual debriefs, and action items are now available in your dashboard.\n\nMeeting: {{ zoom_webhook_receiver.body.payload.object.topic }}\nDate: {{ zoom_webhook_receiver.body.payload.object.start_time }}\nDuration: {{ zoom_webhook_receiver.body.payload.object.duration }} minutes\n\nView your personalized insights and action items in the Oracle Intelligence dashboard."
      }
    },
    {
      "name": "follow_up_scheduler",
      "type": "webhook",
      "description": "Schedules follow-up workflows based on analysis results",
      "options": {
        "url": "{{ CREDENTIAL.oracle_api_base_url }}/api/workflows/schedule-follow-up",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer {{ CREDENTIAL.oracle_api_token }}",
          "Content-Type": "application/json"
        },
        "payload": {
          "meeting_id": "{{ zoom_webhook_receiver.body.payload.object.id }}",
          "action_items": "{{ action_item_generator.body }}",
          "discrepancies": "{{ discrepancy_analyzer.body }}",
          "follow_up_schedule": {
            "check_in_days": 3,
            "review_days": 7,
            "assessment_days": 14
          }
        }
      }
    }
  ]
}
```

## 🔧 **Implementation Components**

### **1. Zoom Integration Service**
```python
# src/backend/src/integrations/zoom_integration.py
import asyncio
import aiohttp
from typing import Dict, List, Optional
import logging

class ZoomIntegrationService:
    def __init__(self, zoom_config: dict):
        self.config = zoom_config
        self.session = None
        self.webhook_handlers = {}
    
    async def initialize(self):
        """Initialize Zoom integration service"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config['access_token']}",
                "Content-Type": "application/json"
            }
        )
        
        # Register webhook handlers
        await self._register_webhook_handlers()
    
    async def _register_webhook_handlers(self):
        """Register webhook handlers for Zoom events"""
        webhook_config = {
            "url": f"{self.config['webhook_base_url']}/api/zoom/webhook",
            "events": [
                "meeting.ended",
                "recording.completed",
                "meeting.participant_joined",
                "meeting.participant_left"
            ]
        }
        
        async with self.session.post(
            f"{self.config['api_base_url']}/webhooks",
            json=webhook_config
        ) as response:
            if response.status == 201:
                webhook_data = await response.json()
                self.webhook_handlers["main"] = webhook_data
                logging.info("Zoom webhook registered successfully")
            else:
                logging.error(f"Failed to register Zoom webhook: {response.status}")
    
    async def get_meeting_transcript(self, meeting_id: str) -> Optional[str]:
        """Get meeting transcript from Zoom"""
        try:
            async with self.session.get(
                f"{self.config['api_base_url']}/meetings/{meeting_id}/recordings"
            ) as response:
                if response.status == 200:
                    recording_data = await response.json()
                    
                    # Find transcript file
                    for recording_file in recording_data.get("recording_files", []):
                        if recording_file.get("file_type") == "TRANSCRIPT":
                            transcript_url = recording_file.get("download_url")
                            return await self._download_transcript(transcript_url)
                    
                    return None
                else:
                    logging.error(f"Failed to get meeting recordings: {response.status}")
                    return None
        except Exception as e:
            logging.error(f"Error getting meeting transcript: {e}")
            return None
    
    async def _download_transcript(self, transcript_url: str) -> str:
        """Download transcript content from URL"""
        try:
            async with self.session.get(transcript_url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logging.error(f"Failed to download transcript: {response.status}")
                    return ""
        except Exception as e:
            logging.error(f"Error downloading transcript: {e}")
            return ""
```

### **2. Tines Integration Service**
```python
# src/backend/src/integrations/tines_integration.py
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional
import logging

class TinesIntegrationService:
    def __init__(self, tines_config: dict):
        self.config = tines_config
        self.session = None
        self.active_stories = {}
    
    async def initialize(self):
        """Initialize Tines integration service"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config['api_token']}",
                "Content-Type": "application/json"
            }
        )
    
    async def create_meeting_analysis_story(self, meeting_data: dict) -> str:
        """Create Tines story for meeting analysis workflow"""
        
        story_template = await self._load_story_template("oracle_meeting_analysis")
        
        # Customize story for specific meeting
        story_config = {
            "name": f"Oracle Analysis - {meeting_data['topic']}",
            "description": f"Automated Oracle 9.1 Protocol analysis for meeting {meeting_data['meeting_id']}",
            "agents": self._customize_agents_for_meeting(story_template["agents"], meeting_data)
        }
        
        try:
            async with self.session.post(
                f"{self.config['api_base_url']}/stories",
                json=story_config
            ) as response:
                if response.status == 201:
                    story_data = await response.json()
                    story_id = story_data["id"]
                    self.active_stories[meeting_data["meeting_id"]] = story_id
                    
                    # Trigger story execution
                    await self._trigger_story_execution(story_id, meeting_data)
                    
                    return story_id
                else:
                    logging.error(f"Failed to create Tines story: {response.status}")
                    return None
        except Exception as e:
            logging.error(f"Error creating Tines story: {e}")
            return None
    
    async def _trigger_story_execution(self, story_id: str, meeting_data: dict):
        """Trigger execution of Tines story with meeting data"""
        
        trigger_payload = {
            "meeting_data": meeting_data,
            "timestamp": datetime.now().isoformat(),
            "source": "zoom_integration"
        }
        
        try:
            async with self.session.post(
                f"{self.config['api_base_url']}/stories/{story_id}/trigger",
                json=trigger_payload
            ) as response:
                if response.status == 200:
                    logging.info(f"Tines story {story_id} triggered successfully")
                else:
                    logging.error(f"Failed to trigger Tines story: {response.status}")
        except Exception as e:
            logging.error(f"Error triggering Tines story: {e}")
```

## 🎯 **Integration Benefits**

### **1. Complete Automation**
- **Zero Manual Intervention**: Meetings automatically trigger comprehensive analysis
- **Real-time Processing**: Analysis begins immediately after meeting ends
- **Intelligent Routing**: Different meeting types trigger appropriate workflows
- **Error Handling**: Robust error handling and retry mechanisms

### **2. Scalable Workflow Management**
- **Parallel Processing**: Multiple meetings processed simultaneously
- **Resource Optimization**: Intelligent resource allocation based on meeting complexity
- **Workflow Customization**: Different workflows for different meeting types
- **Performance Monitoring**: Comprehensive monitoring and alerting

### **3. Enhanced Organizational Intelligence**
- **Continuous Learning**: Every meeting contributes to organizational knowledge
- **Pattern Recognition**: Identifies trends across meetings and teams
- **Predictive Insights**: Anticipates needs based on meeting patterns
- **Strategic Alignment**: Ensures all meetings contribute to organizational objectives

---

**The Zoom + Tines integration transforms meeting management from a manual, reactive process into an intelligent, proactive system that automatically captures, analyzes, and acts on organizational intelligence.**

