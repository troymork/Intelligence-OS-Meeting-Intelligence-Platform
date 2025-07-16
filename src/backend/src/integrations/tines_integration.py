#!/usr/bin/env python3
"""
Tines Integration for Oracle Intelligence System
Processes Zoom meeting data from Tines automation
"""

from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TinesWebhookData(BaseModel):
    meeting_id: str
    meeting_title: str
    start_time: str
    duration_minutes: int
    participants: List[str]
    transcript: str
    zoom_meeting_id: Optional[str] = None
    recording_url: Optional[str] = None
    meeting_type: Optional[str] = "strategic_session"

class TinesBatchData(BaseModel):
    meetings: List[TinesWebhookData]
    batch_id: str
    total_meetings: int

async def process_tines_meeting(webhook_data: TinesWebhookData, mem0_manager):
    """Process a single meeting from Tines"""
    try:
        # Create meeting in Oracle system
        meeting_data = {
            "meeting_id": webhook_data.meeting_id,
            "title": webhook_data.meeting_title,
            "date": webhook_data.start_time,
            "transcript": webhook_data.transcript,
            "participants": webhook_data.participants,
            "duration_minutes": webhook_data.duration_minutes
        }
        
        # Store meeting
        meeting_result = await mem0_manager.create_meeting(meeting_data)
        
        # Generate psychological insights
        debrief_result = await mem0_manager.collect_debrief(
            meeting_id=webhook_data.meeting_id,
            participants=webhook_data.participants,
            debrief_type="psychological_analysis"
        )
        
        logger.info(f"Successfully processed meeting {webhook_data.meeting_id}")
        return {
            "meeting_id": webhook_data.meeting_id,
            "status": "success",
            "insights_generated": True,
            "meeting_result": meeting_result,
            "debrief_result": debrief_result
        }
        
    except Exception as e:
        logger.error(f"Error processing meeting {webhook_data.meeting_id}: {e}")
        return {
            "meeting_id": webhook_data.meeting_id,
            "status": "error",
            "error": str(e)
        }

async def process_tines_batch(batch_data: TinesBatchData, mem0_manager):
    """Process multiple meetings from Tines batch"""
    results = []
    
    for meeting in batch_data.meetings:
        result = await process_tines_meeting(meeting, mem0_manager)
        results.append(result)
    
    # Generate batch summary
    successful = len([r for r in results if r["status"] == "success"])
    failed = len([r for r in results if r["status"] == "error"])
    
    return {
        "batch_id": batch_data.batch_id,
        "total_meetings": batch_data.total_meetings,
        "processed": len(results),
        "successful": successful,
        "failed": failed,
        "results": results
    }

def create_sample_meeting_data():
    """Create sample meeting data for testing"""
    return TinesWebhookData(
        meeting_id="impact_launchpad_20250706_001",
        meeting_title="Impact Launchpad Strategic Planning - January 2025",
        start_time="2025-01-15T10:00:00Z",
        duration_minutes=90,
        participants=["Troy Mork", "Daniel Matalon", "Kristie Thompson", "Sarah Johnson", "David Chen"],
        transcript="""Troy Mork: Welcome everyone to our strategic planning session for Q1 2025. Today we're focusing on SPARK project development and the Agreement Economy framework. Let's start with project updates.

Daniel Matalon: Thanks Troy. I've been analyzing our user engagement data and the metrics are very promising. The SPARK platform is showing 40% month-over-month growth in active users. Our innovation pipeline is strong, particularly in the AI-driven consensus mechanisms.

Kristie Thompson: From an operational perspective, our team coordination has been excellent. We've streamlined our project management processes and are seeing improved collaboration across all initiatives. The 100% Project is gaining significant momentum with three new enterprise clients.

Sarah Johnson: I want to highlight our client relations improvements. We've implemented new feedback loops that are helping us understand user needs better. The psychological profiling features are particularly well-received by our enterprise customers.

David Chen: On the technical side, we've made significant progress on the TreeGens integration. The environmental impact tracking is now fully automated, and we're seeing strong adoption from sustainability-focused organizations.

Troy Mork: Excellent updates everyone. Let's discuss our strategic priorities for the next quarter. I think we need to focus on scaling our Agreement Economy platform while maintaining our innovation edge.

Daniel Matalon: I agree. The data suggests we should prioritize user experience improvements and expand our AI capabilities. The psychological insights feature is becoming a key differentiator.

Kristie Thompson: We should also consider expanding our team. The current workload is manageable, but if we want to scale effectively, we'll need additional resources in both development and client success.

Sarah Johnson: I'd like to propose a new initiative around team dynamics optimization. Based on our internal usage of the Oracle system, I think there's a market opportunity for enterprise team intelligence solutions.

David Chen: That's interesting. We could leverage our existing psychological profiling technology and create a standalone product for organizational development.

Troy Mork: Great ideas. Let's prioritize these initiatives and create action items. Daniel, can you prepare a detailed analysis of our scaling requirements? Kristie, please draft a resource plan for Q1 expansion.

Daniel Matalon: Absolutely. I'll have the analysis ready by Friday, including user growth projections and technical infrastructure needs.

Kristie Thompson: I'll coordinate with HR on the hiring plan and create a timeline for onboarding new team members.

Troy Mork: Perfect. This has been a productive session. Our team dynamics are strong, and I'm confident about our strategic direction. Let's reconvene next week to review the detailed plans.""",
        zoom_meeting_id="123456789",
        recording_url="https://zoom.us/rec/share/sample_recording_url",
        meeting_type="strategic_planning"
    )

def create_sample_batch_data():
    """Create sample batch data for testing"""
    meetings = []
    
    # Meeting 1: Strategic Planning
    meetings.append(create_sample_meeting_data())
    
    # Meeting 2: SPARK Development Review
    meetings.append(TinesWebhookData(
        meeting_id="impact_launchpad_20250706_002",
        meeting_title="SPARK Development Review - Technical Deep Dive",
        start_time="2025-01-22T14:00:00Z",
        duration_minutes=75,
        participants=["Daniel Matalon", "David Chen", "Michael Rodriguez", "Emily Watson"],
        transcript="""Daniel Matalon: Let's dive into the technical architecture review for SPARK. David, can you walk us through the latest infrastructure updates?

David Chen: Certainly. We've implemented the new microservices architecture, which has improved our system scalability by 60%. The Agreement Economy consensus engine is now processing 10,000 transactions per minute with sub-second response times.

Michael Rodriguez: The analytics pipeline is performing exceptionally well. We're capturing detailed user behavior patterns and the psychological profiling algorithms are showing 95% accuracy in personality type detection.

Emily Watson: From a user experience perspective, the new interface is getting positive feedback. The creative elements we added are helping users engage more naturally with the consensus-building features.

Daniel Matalon: Excellent. What about the integration challenges we discussed last week?

David Chen: We've resolved the TreeGens API integration issues. The environmental impact calculations are now real-time, and we're seeing strong adoption from our sustainability-focused clients.

Michael Rodriguez: The data visualization improvements are also complete. Users can now see their team dynamics in real-time, which is driving higher engagement with the psychological insights features.

Emily Watson: I've been working on the mobile optimization. The responsive design is now fully functional, and we're seeing 40% of our traffic coming from mobile devices.

Daniel Matalon: Great progress everyone. Let's discuss the next sprint priorities. I think we should focus on the enterprise features that Sarah mentioned in the strategic session.

David Chen: Agreed. The enterprise dashboard requirements are clear, and we have the technical foundation to deliver them quickly.

Michael Rodriguez: I'll continue optimizing the analytics engine. There's still room for improvement in the real-time processing capabilities.

Emily Watson: I'll work on the enterprise UI components. The feedback from our pilot customers suggests they want more customization options.

Daniel Matalon: Perfect. This team's technical collaboration is outstanding. Our innovation pipeline is strong, and we're well-positioned for the Q1 scaling goals.""",
        zoom_meeting_id="123456790",
        recording_url="https://zoom.us/rec/share/sample_recording_url_2",
        meeting_type="technical_review"
    ))
    
    # Meeting 3: Client Success Review
    meetings.append(TinesWebhookData(
        meeting_id="impact_launchpad_20250706_003",
        meeting_title="Client Success & Market Analysis",
        start_time="2025-01-29T11:00:00Z",
        duration_minutes=60,
        participants=["Sarah Johnson", "Olivia Martinez", "William Thompson", "Sophia Chen"],
        transcript="""Sarah Johnson: Welcome to our client success review. Let's start with the Q4 performance metrics and client feedback analysis.

Olivia Martinez: Our client retention rate is at 94%, which is excellent. The 100% Project clients are particularly satisfied with the project management features and team coordination tools.

William Thompson: From a sales perspective, we're seeing strong interest in the psychological profiling capabilities. Enterprise clients are specifically requesting team dynamics analysis and conflict resolution features.

Sophia Chen: The data analysis shows clear patterns in client usage. Organizations with remote teams are getting the most value from our collaboration insights, while in-person teams prefer the decision-making consensus tools.

Sarah Johnson: That's valuable insight. How are clients responding to the Agreement Economy framework?

Olivia Martinez: Very positively. The consensus-building features are reducing meeting times by an average of 30%, and clients report higher satisfaction with decision outcomes.

William Thompson: We're also seeing expansion opportunities. Several clients have asked about scaling the system to larger teams and multiple departments.

Sophia Chen: The usage analytics support this. Power users are engaging with advanced features like psychological team matching and conflict prediction algorithms.

Sarah Johnson: Excellent. What about the challenges and improvement areas?

Olivia Martinez: The main feedback is around customization. Enterprise clients want more control over the psychological assessment parameters and reporting formats.

William Thompson: There's also demand for integration with existing HR systems and project management tools. This could be a significant growth opportunity.

Sophia Chen: From a data perspective, clients want more detailed analytics on team performance trends and predictive insights about team dynamics.

Sarah Johnson: These are all actionable insights. Let's prioritize the customization features for the next development cycle. Our client success metrics are strong, and the market feedback is very encouraging.""",
        zoom_meeting_id="123456791",
        recording_url="https://zoom.us/rec/share/sample_recording_url_3",
        meeting_type="client_review"
    ))
    
    return TinesBatchData(
        meetings=meetings,
        batch_id="impact_launchpad_historical_batch_001",
        total_meetings=len(meetings)
    )

