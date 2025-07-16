from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import logging
import os
from datetime import datetime

# Import our enhanced Mem0 manager
from EnhancedMem0Manager import EnhancedMem0Manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Oracle Intelligence API",
    description="Advanced psychological AI system for team intelligence and decision support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the enhanced Mem0 manager
mem0_manager = EnhancedMem0Manager()

# Pydantic models for request/response
class UserProfileRequest(BaseModel):
    user_id: str
    name: str
    role: str
    preferences: Optional[Dict[str, Any]] = {}
    tanka_profile: Optional[Dict[str, Any]] = {}
    performance_metrics: Optional[Dict[str, Any]] = {}

class MeetingRequest(BaseModel):
    meeting_id: str
    title: str
    date: str
    transcript: str
    participants: List[str]
    duration_minutes: Optional[int] = 60
    meeting_type: Optional[str] = "general"

class DebriefRequest(BaseModel):
    meeting_id: str
    participants: List[str]
    debrief_type: str

class InsightSearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    top_k: Optional[int] = 5

class DecisionVoteRequest(BaseModel):
    decision_id: str
    user_id: str
    vote: str  # "approve", "reject", "abstain"
    reason: Optional[str] = None

class ConflictResolutionRequest(BaseModel):
    conflict_id: str
    parties: List[str]
    description: str
    proposed_solution: Optional[str] = None

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# User profile management endpoints
@app.post("/api/users/profile")
async def create_or_update_user_profile(request: UserProfileRequest):
    try:
        user_data = request.dict()
        success = await mem0_manager.create_or_update_user_profile(user_data)
        if success:
            return {"message": f"User profile for {request.user_id} updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update user profile")
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/profile/{user_id}")
async def get_user_profile(user_id: str):
    try:
        profile = await mem0_manager.get_user_profile(user_id)
        if profile:
            return profile
        else:
            raise HTTPException(status_code=404, detail=f"User profile for {user_id} not found")
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/profiles")
async def get_all_team_profiles():
    try:
        profiles = await mem0_manager.get_all_team_profiles()
        return {"profiles": profiles, "count": len(profiles)}
    except Exception as e:
        logger.error(f"Error fetching team profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Meeting management endpoints
@app.post("/api/meetings")
async def create_meeting(request: MeetingRequest):
    try:
        meeting_data = request.dict()
        meeting_id = await mem0_manager.create_meeting(meeting_data)
        return {"message": f"Meeting {meeting_id} created successfully", "meeting_id": meeting_id}
    except Exception as e:
        logger.error(f"Error creating meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/meetings/{meeting_id}")
async def get_meeting(meeting_id: str):
    try:
        meeting = await mem0_manager.get_meeting(meeting_id)
        if meeting:
            return meeting
        else:
            raise HTTPException(status_code=404, detail=f"Meeting {meeting_id} not found")
    except Exception as e:
        logger.error(f"Error fetching meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Intelligence and analysis endpoints
@app.post("/api/debrief/collect")
async def collect_debrief(request: DebriefRequest):
    try:
        debrief_result = await mem0_manager.collect_debrief(
            request.meeting_id, 
            request.participants, 
            request.debrief_type
        )
        return debrief_result
    except Exception as e:
        logger.error(f"Error collecting debrief: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/insights/search")
async def search_insights(request: InsightSearchRequest):
    try:
        insights = await mem0_manager.search_insights(
            request.query, 
            request.user_id, 
            request.top_k
        )
        return {"insights": insights, "query": request.query, "count": len(insights)}
    except Exception as e:
        logger.error(f"Error searching insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Decision support endpoints
@app.post("/api/decisions/vote")
async def record_decision_vote(request: DecisionVoteRequest):
    try:
        result = await mem0_manager.record_decision_vote(
            request.decision_id,
            request.user_id,
            request.vote,
            request.reason
        )
        return result
    except Exception as e:
        logger.error(f"Error recording decision vote: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conflicts/resolve")
async def resolve_conflict(request: ConflictResolutionRequest):
    try:
        result = await mem0_manager.resolve_conflict(
            request.conflict_id,
            request.parties,
            request.description,
            request.proposed_solution
        )
        return result
    except Exception as e:
        logger.error(f"Error resolving conflict: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard and analytics endpoints
@app.get("/api/dashboard/overview")
async def get_dashboard_overview():
    try:
        # Get team profiles for overview
        profiles = await mem0_manager.get_all_team_profiles()
        
        # Calculate team statistics
        total_members = len(profiles)
        roles = {}
        mbti_distribution = {}
        avg_performance = {
            "meeting_participation": 0,
            "action_item_completion": 0,
            "strategic_contribution": 0,
            "collaboration_score": 0
        }
        
        for profile in profiles:
            # Count roles
            role = profile.get('role', 'Unknown')
            roles[role] = roles.get(role, 0) + 1
            
            # Count MBTI types
            if profile.get('tanka_profile') and profile['tanka_profile'].get('mbti'):
                mbti = profile['tanka_profile']['mbti']
                mbti_distribution[mbti] = mbti_distribution.get(mbti, 0) + 1
            
            # Calculate average performance metrics
            if profile.get('performance_metrics'):
                metrics = profile['performance_metrics']
                for key in avg_performance:
                    if key in metrics:
                        avg_performance[key] += metrics[key]
        
        # Calculate averages
        if total_members > 0:
            for key in avg_performance:
                avg_performance[key] = round(avg_performance[key] / total_members, 2)
        
        return {
            "team_overview": {
                "total_members": total_members,
                "roles_distribution": roles,
                "mbti_distribution": mbti_distribution,
                "average_performance": avg_performance
            },
            "system_status": {
                "api_status": "operational",
                "memory_system": "active",
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error generating dashboard overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/team-dynamics")
async def get_team_dynamics():
    try:
        profiles = await mem0_manager.get_all_team_profiles()
        
        # Analyze team dynamics based on psychological profiles
        dynamics = {
            "communication_styles": {},
            "focus_areas": {},
            "collaboration_patterns": [],
            "potential_conflicts": [],
            "synergy_opportunities": []
        }
        
        for profile in profiles:
            if profile.get('tanka_profile'):
                tanka = profile['tanka_profile']
                
                # Communication styles
                style = tanka.get('communication_style', 'Unknown')
                dynamics["communication_styles"][style] = dynamics["communication_styles"].get(style, 0) + 1
                
                # Focus areas
                for area in tanka.get('focus_areas', []):
                    dynamics["focus_areas"][area] = dynamics["focus_areas"].get(area, 0) + 1
        
        # Generate insights based on team composition
        dynamics["collaboration_patterns"] = [
            "High strategic focus with strong analytical support",
            "Balanced mix of direct and supportive communication styles",
            "Strong project management and detail orientation"
        ]
        
        dynamics["synergy_opportunities"] = [
            "Pair analytical thinkers with creative team members",
            "Leverage supportive communicators for team building",
            "Combine strategic and operational expertise for project success"
        ]
        
        return dynamics
    except Exception as e:
        logger.error(f"Error analyzing team dynamics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API information endpoint
@app.get("/api/info")
async def get_api_info():
    return {
        "name": "Oracle Intelligence API",
        "version": "1.0.0",
        "description": "Advanced psychological AI system for team intelligence and decision support",
        "features": [
            "User profile management with psychological insights",
            "Meeting analysis and debrief collection",
            "Intelligent insight search and retrieval",
            "Decision support with consensus tracking",
            "Conflict resolution with psychological analysis",
            "Team dynamics and performance analytics"
        ],
        "endpoints": {
            "users": "/api/users/*",
            "meetings": "/api/meetings/*",
            "intelligence": "/api/debrief/*, /api/insights/*",
            "decisions": "/api/decisions/*",
            "conflicts": "/api/conflicts/*",
            "dashboard": "/api/dashboard/*"
        }
    }

if __name__ == "__main__":
    import uvicorn
    # This is for local development outside of Docker.
    # In Docker, uvicorn is run via Gunicorn in Dockerfile.api
    uvicorn.run(app, host="0.0.0.0", port=8001)

