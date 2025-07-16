import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMem0Manager:
    def __init__(self, neo4j_driver=None, redis_client=None):
        self.neo4j_driver = neo4j_driver
        self.redis_client = redis_client
        self.memory = {}  # In-memory fallback for demonstration
        self.neo4j_driver_connected = neo4j_driver is not None
        self.redis_client_connected = redis_client is not None
        logger.info(f"Mem0Manager initialized. Neo4j connected: {self.neo4j_driver_connected}, Redis connected: {self.redis_client_connected}")

        # Initialize with Impact Launchpad team members and their psychological profiles
        self._initialize_team_profiles()

    def _initialize_team_profiles(self):
        """Initializes the memory with predefined Impact Launchpad team profiles."""
        team_members = [
            {"user_id": "troy", "name": "Troy", "role": "CEO", "last_active": "2025-07-03T10:00:00Z",
             "tanka_profile": {"mbti": "ENTJ", "disc": "D", "big_five": {"openness": 0.8, "conscientiousness": 0.9, "extraversion": 0.7, "agreeableness": 0.5, "neuroticism": 0.3}, "communication_style": "direct", "focus_areas": ["strategy", "growth"], "project_expertise": ["100% Project", "SPARK"]},
             "performance_metrics": {"meeting_participation": 0.9, "action_item_completion": 0.95, "strategic_contribution": 0.9, "collaboration_score": 0.85}},
            {"user_id": "daniel", "name": "Daniel", "role": "Managing Partner", "last_active": "2025-07-03T09:30:00Z",
             "tanka_profile": {"mbti": "INTP", "disc": "C", "big_five": {"openness": 0.9, "conscientiousness": 0.8, "extraversion": 0.4, "agreeableness": 0.6, "neuroticism": 0.4}, "communication_style": "analytical", "focus_areas": ["innovation", "technology"], "project_expertise": ["Ecoco", "TreeGens"]},
             "performance_metrics": {"meeting_participation": 0.7, "action_item_completion": 0.85, "strategic_contribution": 0.8, "collaboration_score": 0.75}},
            {"user_id": "sarah", "name": "Sarah", "role": "Partner", "last_active": "2025-07-03T11:15:00Z",
             "tanka_profile": {"mbti": "ESFJ", "disc": "S", "big_five": {"openness": 0.6, "conscientiousness": 0.85, "extraversion": 0.8, "agreeableness": 0.9, "neuroticism": 0.2}, "communication_style": "supportive", "focus_areas": ["client relations", "team building"], "project_expertise": ["100% Project"]},
             "performance_metrics": {"meeting_participation": 0.85, "action_item_completion": 0.9, "strategic_contribution": 0.7, "collaboration_score": 0.9}},
            {"user_id": "david", "name": "David", "role": "Partner", "last_active": "2025-07-03T08:45:00Z",
             "tanka_profile": {"mbti": "ISTP", "disc": "I", "big_five": {"openness": 0.7, "conscientiousness": 0.7, "extraversion": 0.6, "agreeableness": 0.7, "neuroticism": 0.5}, "communication_style": "practical", "focus_areas": ["operations", "problem-solving"], "project_expertise": ["SPARK"]},
             "performance_metrics": {"meeting_participation": 0.75, "action_item_completion": 0.8, "strategic_contribution": 0.75, "collaboration_score": 0.8}},
            {"user_id": "emily", "name": "Emily", "role": "Associate", "last_active": "2025-07-03T10:30:00Z",
             "tanka_profile": {"mbti": "ENFP", "disc": "I", "big_five": {"openness": 0.95, "conscientiousness": 0.6, "extraversion": 0.9, "agreeableness": 0.8, "neuroticism": 0.4}, "communication_style": "enthusiastic", "focus_areas": ["marketing", "creativity"], "project_expertise": ["Ecoco"]},
             "performance_metrics": {"meeting_participation": 0.8, "action_item_completion": 0.75, "strategic_contribution": 0.65, "collaboration_score": 0.85}},
            {"user_id": "michael", "name": "Michael", "role": "Associate", "last_active": "2025-07-03T09:00:00Z",
             "tanka_profile": {"mbti": "INTJ", "disc": "C", "big_five": {"openness": 0.85, "conscientiousness": 0.9, "extraversion": 0.5, "agreeableness": 0.4, "neuroticism": 0.3}, "communication_style": "logical", "focus_areas": ["research", "analytics"], "project_expertise": ["TreeGens"]},
             "performance_metrics": {"meeting_participation": 0.65, "action_item_completion": 0.88, "strategic_contribution": 0.85, "collaboration_score": 0.7}},
            {"user_id": "olivia", "name": "Olivia", "role": "Consultant", "last_active": "2025-07-03T11:00:00Z",
             "tanka_profile": {"mbti": "ISFJ", "disc": "S", "big_five": {"openness": 0.5, "conscientiousness": 0.9, "extraversion": 0.6, "agreeableness": 0.95, "neuroticism": 0.25}, "communication_style": "harmonious", "focus_areas": ["project management", "details"], "project_expertise": ["100% Project"]},
             "performance_metrics": {"meeting_participation": 0.8, "action_item_completion": 0.92, "strategic_contribution": 0.7, "collaboration_score": 0.9}},
            {"user_id": "william", "name": "William", "role": "Consultant", "last_active": "2025-07-03T09:45:00Z",
             "tanka_profile": {"mbti": "ESTP", "disc": "D", "big_five": {"openness": 0.7, "conscientiousness": 0.6, "extraversion": 0.85, "agreeableness": 0.6, "neuroticism": 0.5}, "communication_style": "action-oriented", "focus_areas": ["sales", "negotiation"], "project_expertise": ["SPARK"]},
             "performance_metrics": {"meeting_participation": 0.7, "action_item_completion": 0.8, "strategic_contribution": 0.75, "collaboration_score": 0.8}},
            {"user_id": "sophia", "name": "Sophia", "role": "Analyst", "last_active": "2025-07-03T10:15:00Z",
             "tanka_profile": {"mbti": "INFJ", "disc": "C", "big_five": {"openness": 0.8, "conscientiousness": 0.85, "extraversion": 0.4, "agreeableness": 0.8, "neuroticism": 0.35}, "communication_style": "insightful", "focus_areas": ["data analysis", "strategy"], "project_expertise": ["Ecoco", "TreeGens"]},
             "performance_metrics": {"meeting_participation": 0.75, "action_item_completion": 0.88, "strategic_contribution": 0.8, "collaboration_score": 0.85}}
        ]
        for member in team_members:
            self.memory[f"user_profile:{member['user_id']}"] = member
            logger.info(f"Initialized profile for {member['user_id']}")

    async def create_or_update_user_profile(self, user_data: Dict[str, Any]) -> bool:
        user_id = user_data["user_id"]
        key = f"user_profile:{user_id}"
        user_data["updated_at"] = datetime.now().isoformat()
        self.memory[key] = user_data
        logger.info(f"User profile for {user_id} updated in memory.")
        return True

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        key = f"user_profile:{user_id}"
        profile = self.memory.get(key)
        if profile:
            logger.info(f"User profile for {user_id} fetched from in-memory fallback.")
        return profile

    async def get_all_team_profiles(self) -> List[Dict[str, Any]]:
        team_profiles = []
        for key, value in self.memory.items():
            if key.startswith("user_profile:"):
                team_profiles.append(value)
        logger.info("All team profiles fetched from in-memory fallback.")
        return team_profiles

    async def create_meeting(self, meeting_data: Dict[str, Any]) -> str:
        meeting_id = meeting_data["meeting_id"]
        key = f"meeting:{meeting_id}"
        meeting_data["created_at"] = datetime.now().isoformat()
        self.memory[key] = meeting_data
        logger.info(f"Meeting {meeting_id} created in memory.")
        return meeting_id

    async def get_meeting(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        key = f"meeting:{meeting_id}"
        meeting = self.memory.get(key)
        if meeting:
            logger.info(f"Meeting {meeting_id} fetched from in-memory fallback.")
        return meeting

    async def collect_debrief(self, meeting_id: str, participants: List[str], debrief_type: str) -> Dict[str, Any]:
        """Simulates collecting debrief information and generating insights."""
        meeting = await self.get_meeting(meeting_id)
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found for debrief.")

        insights = [
            f"Debrief for meeting '{meeting.get('title', 'N/A')}' ({meeting_id}) of type '{debrief_type}' collected.",
            f"Key discussion points from transcript: {meeting.get('transcript', 'No transcript available')[:100]}...",
            f"Participants involved: {', '.join(participants)}."
        ]

        for participant_id in participants:
            profile = await self.get_user_profile(participant_id)
            if profile and profile.get('tanka_profile'):
                tanka = profile['tanka_profile']
                insights.append(f"Participant {profile['name']} (MBTI: {tanka.get('mbti', 'N/A')}, DISC: {tanka.get('disc', 'N/A')}) contributed with a {tanka.get('communication_style', 'N/A')} style.")
        
        debrief_result = {
            "meeting_id": meeting_id,
            "debrief_type": debrief_type,
            "timestamp": datetime.now().isoformat(),
            "generated_insights": insights
        }

        debrief_key = f"debrief:{meeting_id}:{debrief_type}"
        self.memory[debrief_key] = debrief_result
        return debrief_result

    async def search_insights(self, query: str, user_id: Optional[str] = None, top_k: int = 5) -> List[str]:
        """Simulates searching for insights based on a query."""
        all_insights = []
        for key, value in self.memory.items():
            if key.startswith("debrief:"):
                all_insights.extend(value.get("generated_insights", []))
            elif key.startswith("meeting:"):
                all_insights.append(value.get("transcript", ""))
        
        relevant_insights = [
            insight for insight in all_insights if query.lower() in insight.lower()
        ]
        return relevant_insights[:top_k]

    async def record_decision_vote(self, decision_id: str, user_id: str, vote: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Records a decision vote and updates consensus."""
        key = f"decision:{decision_id}"
        decision_data = self.memory.get(key, {"decision_id": decision_id, "votes": {}, "status": "pending"})
        
        decision_data["votes"][user_id] = {"vote": vote, "reason": reason, "timestamp": datetime.now().isoformat()}
        
        total_votes = len(decision_data["votes"])
        approve_count = sum(1 for v in decision_data["votes"].values() if v["vote"] == "approve")
        reject_count = sum(1 for v in decision_data["votes"].values() if v["vote"] == "reject")
        
        consensus_percentage = (approve_count / total_votes) * 100 if total_votes > 0 else 0
        
        if consensus_percentage >= 75:
            decision_data["status"] = "approved"
        elif reject_count > total_votes * 0.25:
            decision_data["status"] = "rejected"
        else:
            decision_data["status"] = "pending"

        self.memory[key] = decision_data
        logger.info(f"Vote for decision {decision_id} recorded by {user_id}. Status: {decision_data['status']}")
        return {"consensus_percentage": consensus_percentage, "status": decision_data["status"]}

    async def resolve_conflict(self, conflict_id: str, parties: List[str], description: str, proposed_solution: Optional[str] = None) -> Dict[str, Any]:
        """Simulates conflict resolution process."""
        key = f"conflict:{conflict_id}"
        conflict_data = {
            "conflict_id": conflict_id,
            "parties": parties,
            "description": description,
            "proposed_solution": proposed_solution,
            "status": "in_progress",
            "timestamp": datetime.now().isoformat()
        }

        resolution_steps = [f"Conflict '{conflict_id}' involving {', '.join(parties)} initiated."]
        for party_id in parties:
            profile = await self.get_user_profile(party_id)
            if profile and profile.get('tanka_profile'):
                tanka = profile['tanka_profile']
                resolution_steps.append(f"Understanding {profile['name']} (MBTI: {tanka.get('mbti', 'N/A')}, DISC: {tanka.get('disc', 'N/A')}) perspective is crucial.")
        
        if proposed_solution:
            resolution_steps.append(f"Proposed solution: '{proposed_solution}'. Assessing its alignment with all parties' communication styles and focus areas.")
            conflict_data["status"] = "solution_proposed"
        else:
            resolution_steps.append("No solution proposed yet. Facilitating dialogue based on psychological profiles to find common ground.")
            conflict_data["status"] = "dialogue_needed"

        if len(parties) > 1 and proposed_solution:
            conflict_data["status"] = "resolved"
            resolution_steps.append("Conflict resolved successfully (simulated).")
        elif len(parties) == 1:
            conflict_data["status"] = "resolved"
            resolution_steps.append("Single-party conflict addressed (simulated).")
        else:
            conflict_data["status"] = "unresolved"
            resolution_steps.append("Conflict remains unresolved (simulated). Further intervention may be needed.")

        conflict_data["resolution_log"] = resolution_steps
        self.memory[key] = conflict_data
        logger.info(f"Conflict {conflict_id} resolution status: {conflict_data['status']}")
        return conflict_data

