from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import json
import time
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional

# Import mem0 for memory management
try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    logging.warning("mem0 not available. Install with: pip install mem0ai")

# Import other infrastructure components
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available. Install with: pip install redis")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available. Install with: pip install openai")

# Create blueprint
oracle_ai_bp = Blueprint('oracle_ai', __name__, url_prefix='/api/oracle')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OracleMemoryManager:
    """Memory manager for Oracle 9.1 Protocol with mem0 integration"""
    
    def __init__(self):
        self.memory = None
        self.redis_client = None
        self.openai_client = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize mem0, Redis, and OpenAI components"""
        
        # Initialize OpenAI
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            logger.info("OpenAI client initialized")
        
        # Initialize Redis
        if REDIS_AVAILABLE:
            try:
                redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                logger.info("Redis client initialized")
            except Exception as e:
                logger.warning(f"Redis initialization failed: {e}")
                self.redis_client = None
        
        # Initialize mem0
        if MEM0_AVAILABLE and self.openai_client:
            try:
                memory_config = self._get_memory_config()
                self.memory = Memory.from_config(memory_config)
                logger.info("Mem0 memory initialized")
            except Exception as e:
                logger.warning(f"Mem0 initialization failed: {e}")
                self.memory = None
    
    def _get_memory_config(self) -> Dict[str, Any]:
        """Get mem0 configuration"""
        return {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4o-mini",
                    "temperature": 0.1,
                    "max_tokens": 1000
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            },
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "host": os.getenv('QDRANT_HOST', 'localhost'),
                    "port": int(os.getenv('QDRANT_PORT', '6333')),
                    "collection_name": "oracle_memory"
                }
            } if os.getenv('QDRANT_HOST') else {
                "provider": "chroma",
                "config": {
                    "collection_name": "oracle_memory",
                    "path": "./chroma_db"
                }
            }
        }
    
    def store_meeting_context(self, meeting_data: Dict[str, Any], user_id: str, session_id: str) -> bool:
        """Store meeting context in working memory"""
        if not self.memory:
            return False
        
        try:
            messages = [
                {"role": "system", "content": "Store meeting context and participant information for Oracle 9.1 Protocol analysis"},
                {"role": "user", "content": f"Meeting context: {json.dumps(meeting_data)}"}
            ]
            
            self.memory.add(
                messages=messages,
                user_id=user_id,
                session_id=session_id,
                metadata={
                    "type": "working_memory",
                    "meeting_id": meeting_data.get("meeting_id"),
                    "timestamp": meeting_data.get("timestamp", datetime.now().isoformat()),
                    "participants": meeting_data.get("participants", []),
                    "oracle_protocol_version": "9.1"
                }
            )
            
            logger.info(f"Stored meeting context for user {user_id}, session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store meeting context: {e}")
            return False
    
    def store_user_preferences(self, user_data: Dict[str, Any], user_id: str) -> bool:
        """Store user preferences in factual memory"""
        if not self.memory:
            return False
        
        try:
            messages = [
                {"role": "system", "content": "Store user preferences and behavioral patterns for Oracle 9.1 Protocol personalization"},
                {"role": "user", "content": f"User profile and preferences: {json.dumps(user_data)}"}
            ]
            
            self.memory.add(
                messages=messages,
                user_id=user_id,
                metadata={
                    "type": "factual_memory",
                    "category": "user_preferences",
                    "permanent": True,
                    "oracle_dimension": "human_needs_analysis",
                    "last_updated": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Stored user preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store user preferences: {e}")
            return False
    
    def store_analysis_results(self, analysis_data: Dict[str, Any], user_id: str, meeting_id: str) -> bool:
        """Store Oracle 9.1 analysis results in episodic memory"""
        if not self.memory:
            return False
        
        try:
            messages = [
                {"role": "system", "content": "Store Oracle 9.1 Protocol analysis results and insights"},
                {"role": "user", "content": f"Analysis results: {json.dumps(analysis_data)}"}
            ]
            
            self.memory.add(
                messages=messages,
                user_id=user_id,
                metadata={
                    "type": "episodic_memory",
                    "category": "analysis_results",
                    "meeting_id": meeting_id,
                    "oracle_dimensions": analysis_data.get("dimensions", {}),
                    "compliance_score": analysis_data.get("compliance_score", 0),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Stored analysis results for user {user_id}, meeting {meeting_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store analysis results: {e}")
            return False
    
    def store_organizational_wisdom(self, wisdom_data: Dict[str, Any], organization_id: str) -> bool:
        """Store organizational insights in semantic memory"""
        if not self.memory:
            return False
        
        try:
            messages = [
                {"role": "system", "content": "Store organizational wisdom and collective intelligence insights"},
                {"role": "user", "content": f"Organizational wisdom: {json.dumps(wisdom_data)}"}
            ]
            
            self.memory.add(
                messages=messages,
                user_id=f"org_{organization_id}",
                metadata={
                    "type": "semantic_memory",
                    "category": "organizational_wisdom",
                    "scope": "organization",
                    "wisdom_type": wisdom_data.get("type", "general"),
                    "confidence_score": wisdom_data.get("confidence", 0.8),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Stored organizational wisdom for organization {organization_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store organizational wisdom: {e}")
            return False
    
    def retrieve_relevant_context(self, query: str, user_id: str, context_type: str = "all", limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve relevant context for Oracle 9.1 analysis"""
        if not self.memory:
            return []
        
        try:
            filters = {"type": context_type} if context_type != "all" else None
            
            search_results = self.memory.search(
                query=query,
                user_id=user_id,
                limit=limit,
                filters=filters
            )
            
            return search_results.get("results", [])
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []
    
    def get_six_dimensional_context(self, user_id: str, meeting_context: str, organization_id: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get context for all six Oracle 9.1 Protocol dimensions"""
        contexts = {}
        
        if not self.memory:
            return contexts
        
        try:
            # Human Needs Analysis context
            contexts["human_needs"] = self.retrieve_relevant_context(
                f"user preferences communication style engagement psychological safety {meeting_context}",
                user_id,
                "factual_memory",
                limit=5
            )
            
            # Strategic Alignment context
            org_user_id = f"org_{organization_id}" if organization_id else user_id
            contexts["strategic_alignment"] = self.retrieve_relevant_context(
                f"organizational goals priorities strategic alignment objectives {meeting_context}",
                org_user_id,
                "semantic_memory",
                limit=5
            )
            
            # Pattern Recognition context
            contexts["pattern_recognition"] = self.retrieve_relevant_context(
                f"behavioral patterns successful approaches recurring themes {meeting_context}",
                user_id,
                "episodic_memory",
                limit=5
            )
            
            # Decision Tracking context
            contexts["decision_tracking"] = self.retrieve_relevant_context(
                f"past decisions outcomes implementation success failure {meeting_context}",
                user_id,
                "episodic_memory",
                limit=5
            )
            
            # Knowledge Evolution context
            contexts["knowledge_evolution"] = self.retrieve_relevant_context(
                f"learning progression skill development knowledge transfer growth {meeting_context}",
                user_id,
                "factual_memory",
                limit=5
            )
            
            # Organizational Wisdom context
            contexts["organizational_wisdom"] = self.retrieve_relevant_context(
                f"collective intelligence collaboration patterns organizational culture {meeting_context}",
                org_user_id,
                "semantic_memory",
                limit=5
            )
            
            logger.info(f"Retrieved six-dimensional context for user {user_id}")
            return contexts
            
        except Exception as e:
            logger.error(f"Failed to get six-dimensional context: {e}")
            return {}
    
    def cache_result(self, key: str, data: Any, ttl: int = 3600) -> bool:
        """Cache result in Redis"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.setex(key, ttl, json.dumps(data))
            return True
        except Exception as e:
            logger.error(f"Failed to cache result: {e}")
            return False
    
    def get_cached_result(self, key: str) -> Optional[Any]:
        """Get cached result from Redis"""
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get cached result: {e}")
            return None

# Initialize memory manager
memory_manager = OracleMemoryManager()

class Oracle91AnalysisEngine:
    """Oracle 9.1 Protocol Analysis Engine with mem0 integration"""
    
    def __init__(self, memory_manager: OracleMemoryManager):
        self.memory = memory_manager
        self.openai_client = memory_manager.openai_client
    
    def analyze_with_memory(self, meeting_data: Dict[str, Any], user_id: str, organization_id: str = None) -> Dict[str, Any]:
        """Perform Oracle 9.1 analysis with memory context"""
        
        # Check cache first
        cache_key = f"oracle_analysis:{user_id}:{meeting_data.get('meeting_id', 'unknown')}"
        cached_result = self.memory.get_cached_result(cache_key)
        if cached_result:
            logger.info(f"Returning cached analysis for {cache_key}")
            return cached_result
        
        try:
            # Get relevant memory context for all six dimensions
            memory_contexts = self.memory.get_six_dimensional_context(
                user_id, 
                meeting_data.get("context", ""),
                organization_id
            )
            
            # Perform analysis with memory context
            analysis_result = self._perform_six_dimensional_analysis_with_memory(
                meeting_data, 
                memory_contexts
            )
            
            # Store analysis results in memory
            self.memory.store_analysis_results(
                analysis_result, 
                user_id, 
                meeting_data.get("meeting_id", "unknown")
            )
            
            # Cache the result
            self.memory.cache_result(cache_key, analysis_result, ttl=1800)  # 30 minutes
            
            logger.info(f"Completed Oracle 9.1 analysis for user {user_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return self._get_fallback_analysis()
    
    def _perform_six_dimensional_analysis_with_memory(self, meeting_data: Dict[str, Any], memory_contexts: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Perform six-dimensional analysis incorporating memory context"""
        
        if not self.openai_client:
            return self._get_fallback_analysis()
        
        # Build analysis prompt with memory context
        system_prompt = self._build_analysis_prompt_with_memory(memory_contexts)
        
        # Prepare meeting data for analysis
        meeting_content = json.dumps(meeting_data, indent=2)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this meeting data according to the Oracle 9.1 Protocol:\\n\\n{meeting_content}"}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse and structure the analysis
            return self._structure_analysis_result(analysis_text, meeting_data)
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            return self._get_fallback_analysis()
    
    def _build_analysis_prompt_with_memory(self, memory_contexts: Dict[str, List[Dict[str, Any]]]) -> str:
        """Build analysis prompt incorporating memory context"""
        
        prompt = """
You are the Oracle 9.1 Protocol Analysis Engine. Perform comprehensive six-dimensional analysis 
incorporating the following memory contexts from previous interactions:

HUMAN NEEDS ANALYSIS CONTEXT:
{human_needs_context}

STRATEGIC ALIGNMENT CONTEXT:
{strategic_context}

PATTERN RECOGNITION CONTEXT:
{pattern_context}

DECISION TRACKING CONTEXT:
{decision_context}

KNOWLEDGE EVOLUTION CONTEXT:
{knowledge_context}

ORGANIZATIONAL WISDOM CONTEXT:
{wisdom_context}

Based on this historical context and the current meeting data, provide analysis across all six dimensions:

1. HUMAN NEEDS ANALYSIS (25 points)
   - Psychological safety assessment
   - Individual engagement levels
   - Communication effectiveness
   - Emotional intelligence indicators

2. STRATEGIC ALIGNMENT ASSESSMENT (25 points)
   - Goal alignment with organizational objectives
   - Resource allocation effectiveness
   - Priority alignment
   - Strategic coherence

3. PATTERN RECOGNITION & INSIGHTS (20 points)
   - Behavioral patterns identified
   - Systemic patterns
   - Recurring themes
   - Predictive insights

4. DECISION TRACKING & VALIDATION (15 points)
   - Decision quality assessment
   - Implementation feasibility
   - Stakeholder buy-in
   - Success probability

5. KNOWLEDGE EVOLUTION MAPPING (10 points)
   - Learning opportunities identified
   - Knowledge transfer effectiveness
   - Skill development areas
   - Capability growth

6. ORGANIZATIONAL WISDOM DEVELOPMENT (5 points)
   - Collective intelligence insights
   - Cultural alignment
   - Wisdom accumulation
   - Long-term organizational learning

Provide specific scores (0-100) for each dimension and an overall Oracle 9.1 Protocol compliance score.
Include actionable recommendations based on the memory context and current analysis.

Use the memory context to provide more accurate, personalized, and contextually aware analysis.
Reference specific patterns, preferences, and historical insights where relevant.
""".format(
            human_needs_context=self._format_memory_context(memory_contexts.get("human_needs", [])),
            strategic_context=self._format_memory_context(memory_contexts.get("strategic_alignment", [])),
            pattern_context=self._format_memory_context(memory_contexts.get("pattern_recognition", [])),
            decision_context=self._format_memory_context(memory_contexts.get("decision_tracking", [])),
            knowledge_context=self._format_memory_context(memory_contexts.get("knowledge_evolution", [])),
            wisdom_context=self._format_memory_context(memory_contexts.get("organizational_wisdom", []))
        )
        
        return prompt
    
    def _format_memory_context(self, memories: List[Dict[str, Any]]) -> str:
        """Format memory context for prompt inclusion"""
        if not memories:
            return "No relevant historical context available."
        
        formatted_memories = []
        for memory in memories[:3]:  # Limit to top 3 most relevant
            memory_text = memory.get("memory", "")
            timestamp = memory.get("created_at", "")
            formatted_memories.append(f"- {memory_text} (from {timestamp})")
        
        return "\\n".join(formatted_memories)
    
    def _structure_analysis_result(self, analysis_text: str, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure the analysis result into a standardized format"""
        
        # This is a simplified parser - in production, you'd want more robust parsing
        result = {
            "meeting_id": meeting_data.get("meeting_id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "oracle_protocol_version": "9.1",
            "analysis_text": analysis_text,
            "dimensions": {
                "human_needs_analysis": {"score": 75, "insights": []},
                "strategic_alignment": {"score": 80, "insights": []},
                "pattern_recognition": {"score": 70, "insights": []},
                "decision_tracking": {"score": 85, "insights": []},
                "knowledge_evolution": {"score": 65, "insights": []},
                "organizational_wisdom": {"score": 78, "insights": []}
            },
            "overall_compliance_score": 75.5,
            "recommendations": [],
            "memory_enhanced": True
        }
        
        # In production, implement proper parsing of the analysis_text
        # to extract scores, insights, and recommendations
        
        return result
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Provide fallback analysis when main analysis fails"""
        return {
            "meeting_id": "unknown",
            "timestamp": datetime.now().isoformat(),
            "oracle_protocol_version": "9.1",
            "analysis_text": "Analysis temporarily unavailable. Please try again.",
            "dimensions": {
                "human_needs_analysis": {"score": 0, "insights": ["Analysis unavailable"]},
                "strategic_alignment": {"score": 0, "insights": ["Analysis unavailable"]},
                "pattern_recognition": {"score": 0, "insights": ["Analysis unavailable"]},
                "decision_tracking": {"score": 0, "insights": ["Analysis unavailable"]},
                "knowledge_evolution": {"score": 0, "insights": ["Analysis unavailable"]},
                "organizational_wisdom": {"score": 0, "insights": ["Analysis unavailable"]}
            },
            "overall_compliance_score": 0,
            "recommendations": ["Please check system configuration and try again"],
            "memory_enhanced": False,
            "error": "Analysis engine temporarily unavailable"
        }

# Initialize analysis engine
analysis_engine = Oracle91AnalysisEngine(memory_manager)

# API Routes

@oracle_ai_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "mem0": MEM0_AVAILABLE and memory_manager.memory is not None,
            "redis": REDIS_AVAILABLE and memory_manager.redis_client is not None,
            "openai": OPENAI_AVAILABLE and memory_manager.openai_client is not None
        }
    }
    
    return jsonify(status)

@oracle_ai_bp.route('/analyze', methods=['POST'])
@cross_origin()
def analyze_meeting():
    """Perform Oracle 9.1 Protocol analysis with memory integration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract required parameters
        meeting_data = data.get('meeting_data', {})
        user_id = data.get('user_id', 'anonymous')
        organization_id = data.get('organization_id')
        
        # Store meeting context in memory
        if meeting_data:
            session_id = meeting_data.get('session_id', f"session_{int(time.time())}")
            memory_manager.store_meeting_context(meeting_data, user_id, session_id)
        
        # Perform analysis with memory context
        analysis_result = analysis_engine.analyze_with_memory(
            meeting_data, 
            user_id, 
            organization_id
        )
        
        return jsonify({
            "success": True,
            "analysis": analysis_result,
            "memory_enhanced": analysis_result.get("memory_enhanced", False)
        })
        
    except Exception as e:
        logger.error(f"Analysis endpoint error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "analysis": analysis_engine._get_fallback_analysis()
        }), 500

@oracle_ai_bp.route('/memory/store', methods=['POST'])
@cross_origin()
def store_memory():
    """Store data in memory system"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        memory_type = data.get('type', 'factual')
        user_id = data.get('user_id', 'anonymous')
        content = data.get('content', {})
        
        success = False
        
        if memory_type == 'user_preferences':
            success = memory_manager.store_user_preferences(content, user_id)
        elif memory_type == 'organizational_wisdom':
            organization_id = data.get('organization_id', 'default')
            success = memory_manager.store_organizational_wisdom(content, organization_id)
        else:
            return jsonify({"error": f"Unsupported memory type: {memory_type}"}), 400
        
        return jsonify({
            "success": success,
            "message": f"Memory stored successfully" if success else "Failed to store memory"
        })
        
    except Exception as e:
        logger.error(f"Memory store endpoint error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@oracle_ai_bp.route('/memory/search', methods=['POST'])
@cross_origin()
def search_memory():
    """Search memory system"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        query = data.get('query', '')
        user_id = data.get('user_id', 'anonymous')
        context_type = data.get('context_type', 'all')
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        results = memory_manager.retrieve_relevant_context(
            query, user_id, context_type, limit
        )
        
        return jsonify({
            "success": True,
            "results": results,
            "count": len(results)
        })
        
    except Exception as e:
        logger.error(f"Memory search endpoint error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "results": []
        }), 500

@oracle_ai_bp.route('/memory/context', methods=['POST'])
@cross_origin()
def get_dimensional_context():
    """Get six-dimensional context for analysis"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_id = data.get('user_id', 'anonymous')
        meeting_context = data.get('meeting_context', '')
        organization_id = data.get('organization_id')
        
        contexts = memory_manager.get_six_dimensional_context(
            user_id, meeting_context, organization_id
        )
        
        return jsonify({
            "success": True,
            "contexts": contexts
        })
        
    except Exception as e:
        logger.error(f"Dimensional context endpoint error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "contexts": {}
        }), 500

@oracle_ai_bp.route('/voice-process', methods=['POST'])
@cross_origin()
def process_voice():
    """Process voice input with memory context"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # This would integrate with speech-to-text services
        # For now, return a mock response
        
        return jsonify({
            "success": True,
            "transcription": "Voice processing with memory integration",
            "confidence": 0.95,
            "memory_enhanced": True
        })
        
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@oracle_ai_bp.route('/meeting-summary', methods=['POST'])
@cross_origin()
def generate_meeting_summary():
    """Generate meeting summary with memory integration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        meeting_data = data.get('meeting_data', {})
        user_id = data.get('user_id', 'anonymous')
        
        # Get memory context for summary generation
        memory_contexts = memory_manager.get_six_dimensional_context(
            user_id, 
            meeting_data.get("context", ""),
            data.get('organization_id')
        )
        
        # Generate summary (simplified for demo)
        summary = {
            "meeting_id": meeting_data.get("meeting_id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "summary": "Meeting summary generated with memory context",
            "key_points": [
                "Point 1 enhanced with historical context",
                "Point 2 informed by user preferences",
                "Point 3 aligned with organizational patterns"
            ],
            "action_items": [
                "Action item 1 based on past successful patterns",
                "Action item 2 tailored to user preferences"
            ],
            "oracle_insights": [
                "Insight 1 from six-dimensional analysis",
                "Insight 2 from organizational wisdom"
            ],
            "memory_enhanced": True,
            "context_sources": len([ctx for ctx in memory_contexts.values() if ctx])
        }
        
        # Store summary in episodic memory
        memory_manager.store_analysis_results(
            {"summary": summary}, 
            user_id, 
            meeting_data.get("meeting_id", "unknown")
        )
        
        return jsonify({
            "success": True,
            "summary": summary
        })
        
    except Exception as e:
        logger.error(f"Meeting summary error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Error handlers
@oracle_ai_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@oracle_ai_bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

