# Oracle Nexus API Reference

## Overview

The Oracle Nexus API provides comprehensive endpoints for implementing Oracle 9.1 Protocol compliant meeting intelligence systems. All endpoints follow RESTful principles and return JSON responses with consistent error handling.

## Base URL

```
Production: https://api.oracle-nexus.ai/v1
Development: http://localhost:5000/api
```

## Authentication

All API requests require authentication using API keys:

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

## Oracle Analysis Engine

### Analyze Meeting Content

Performs comprehensive Oracle 9.1 Protocol six-dimensional analysis on meeting content.

**Endpoint:** `POST /oracle/analyze`

**Request Body:**
```json
{
  "transcript": "Complete meeting transcript text...",
  "participants": ["Alice Johnson", "Bob Smith", "Charlie Brown"],
  "context": "Strategic planning meeting",
  "meeting_id": "optional-meeting-id",
  "metadata": {
    "duration": 3600,
    "date": "2024-01-15T10:00:00Z",
    "location": "Conference Room A"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-15T11:00:00Z",
    "protocol_version": "9.1",
    "participants": ["Alice Johnson", "Bob Smith", "Charlie Brown"],
    "transcript_length": 1250,
    "analysis": {
      "human_needs": {
        "score": 7.5,
        "insights": "Participants demonstrated strong psychological safety with open communication patterns. High engagement levels observed throughout the discussion.",
        "recommendations": [
          "Enhance active listening practices during decision points",
          "Implement regular check-ins for team emotional state",
          "Create structured feedback mechanisms"
        ],
        "metrics": {
          "psychological_safety": 8.2,
          "engagement_level": 7.8,
          "communication_effectiveness": 7.1
        }
      },
      "strategic_alignment": {
        "score": 8.2,
        "insights": "Strong alignment with organizational objectives. Clear connection between discussed initiatives and strategic priorities.",
        "recommendations": [
          "Continue current strategic direction",
          "Monitor resource allocation efficiency",
          "Establish quarterly alignment reviews"
        ],
        "metrics": {
          "goal_alignment": 8.5,
          "priority_clarity": 8.0,
          "resource_optimization": 7.9
        }
      },
      "pattern_recognition": {
        "score": 6.8,
        "insights": "Recurring themes around innovation and process improvement. Some systemic communication patterns identified.",
        "recommendations": [
          "Establish pattern tracking system",
          "Create feedback loops for continuous improvement",
          "Implement regular pattern review sessions"
        ],
        "patterns_identified": [
          "Innovation-focused discussions increase engagement",
          "Process improvement suggestions often deferred",
          "Technical discussions require more structured facilitation"
        ]
      },
      "decision_tracking": {
        "score": 7.9,
        "insights": "Clear decisions made with appropriate accountability assignments. Good implementation feasibility assessment.",
        "recommendations": [
          "Implement decision tracking dashboard",
          "Establish follow-up protocols",
          "Create decision quality metrics"
        ],
        "decisions": [
          {
            "decision": "Implement new project management system",
            "owner": "Alice Johnson",
            "deadline": "2024-02-15",
            "feasibility": "high"
          }
        ]
      },
      "knowledge_evolution": {
        "score": 7.3,
        "insights": "Significant knowledge sharing observed. Good collaborative learning patterns.",
        "recommendations": [
          "Create knowledge repository",
          "Establish mentoring programs",
          "Implement knowledge transfer protocols"
        ],
        "knowledge_created": [
          "New understanding of customer needs",
          "Improved process efficiency insights",
          "Technical solution alternatives"
        ]
      },
      "organizational_wisdom": {
        "score": 8.1,
        "insights": "Strong collective intelligence demonstrated. Excellent adaptive capacity and cultural health indicators.",
        "recommendations": [
          "Document wisdom patterns",
          "Create organizational learning frameworks",
          "Establish wisdom development metrics"
        ],
        "wisdom_indicators": {
          "collective_intelligence": 8.3,
          "adaptive_capacity": 7.9,
          "cultural_health": 8.1
        }
      }
    },
    "overall_score": 7.6,
    "key_insights": [
      "High level of collaborative engagement across all participants",
      "Strong strategic alignment with organizational objectives",
      "Opportunities for enhanced knowledge management systems",
      "Excellent decision-making processes with clear accountability"
    ],
    "action_items": [
      {
        "item": "Implement Oracle 9.1 Protocol tracking dashboard",
        "owner": "IT Team",
        "priority": "high",
        "deadline": "2024-02-01"
      },
      {
        "item": "Establish regular wisdom development sessions",
        "owner": "HR Team",
        "priority": "medium",
        "deadline": "2024-02-15"
      }
    ],
    "compliance_score": 9.2,
    "processing_time": 2.3
  }
}
```

### Voice Processing

Processes real-time voice input and provides intelligent responses using Oracle 9.1 Protocol principles.

**Endpoint:** `POST /oracle/voice-process`

**Request Body:**
```json
{
  "text": "I think we should consider the budget implications of this decision",
  "session_id": "meeting-session-123",
  "participant_id": "alice-johnson",
  "context": {
    "meeting_phase": "decision_making",
    "current_topic": "budget_allocation",
    "participants_present": ["alice", "bob", "charlie"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "meeting-session-123",
    "response": "That's an excellent point about budget implications, Alice. I'm tracking this as a key consideration for the decision. Would you like me to pull up the current budget constraints for this initiative?",
    "response_type": "strategic_guidance",
    "confidence": 0.92,
    "suggested_actions": [
      "Review budget documentation",
      "Schedule budget review meeting",
      "Assign budget analysis task"
    ],
    "analysis": {
      "intent": "budget_concern",
      "sentiment": "constructive",
      "urgency": "medium",
      "strategic_relevance": "high"
    },
    "timestamp": "2024-01-15T10:15:30Z"
  }
}
```

### Meeting Summary Generation

Generates comprehensive meeting summaries with Oracle 9.1 Protocol insights and compliance scoring.

**Endpoint:** `POST /oracle/meeting-summary`

**Request Body:**
```json
{
  "transcript": "Complete meeting transcript...",
  "participants": ["Alice Johnson", "Bob Smith"],
  "title": "Q4 Strategic Planning Meeting",
  "metadata": {
    "duration": 3600,
    "date": "2024-01-15T10:00:00Z",
    "meeting_type": "strategic_planning"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": "# Q4 Strategic Planning Meeting\n\n## Executive Summary\nThis strategic planning meeting demonstrated exceptional collaborative engagement...",
    "meeting_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2024-01-15T11:00:00Z",
    "participants": ["Alice Johnson", "Bob Smith"],
    "key_decisions": [
      {
        "decision": "Approve Q4 marketing budget increase",
        "rationale": "Market opportunity analysis shows 23% growth potential",
        "owner": "Alice Johnson",
        "deadline": "2024-01-30"
      }
    ],
    "action_items": [
      {
        "item": "Prepare detailed budget proposal",
        "owner": "Bob Smith",
        "deadline": "2024-01-22",
        "priority": "high"
      }
    ],
    "oracle_compliance": {
      "score": 8.7,
      "strengths": ["Strong strategic alignment", "Clear decision processes"],
      "improvements": ["Enhance knowledge documentation", "Improve pattern tracking"]
    }
  }
}
```

## System Health and Monitoring

### Health Check

Provides system health status and capability information.

**Endpoint:** `GET /oracle/health`

**Response:**
```json
{
  "status": "healthy",
  "protocol_version": "9.1",
  "timestamp": "2024-01-15T10:00:00Z",
  "capabilities": [
    "six_dimensional_analysis",
    "voice_processing",
    "meeting_summaries",
    "real_time_insights"
  ],
  "system_metrics": {
    "uptime": 86400,
    "requests_per_minute": 45,
    "average_response_time": 1.2,
    "error_rate": 0.001
  }
}
```

### Analytics Dashboard

Retrieves analytics data for dashboard display.

**Endpoint:** `GET /oracle/analytics`

**Query Parameters:**
- `timeframe`: `day`, `week`, `month`, `quarter`
- `metric_type`: `engagement`, `decisions`, `wisdom`, `all`

**Response:**
```json
{
  "success": true,
  "data": {
    "timeframe": "week",
    "metrics": {
      "total_meetings": 47,
      "total_participants": 156,
      "average_oracle_score": 7.8,
      "decisions_tracked": 89,
      "action_items_completed": 67,
      "wisdom_development_score": 8.2
    },
    "trends": {
      "engagement_trend": "increasing",
      "decision_quality_trend": "stable",
      "collaboration_trend": "improving"
    }
  }
}
```

## Error Handling

All API endpoints use consistent error response format:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Transcript is required for analysis",
    "details": {
      "field": "transcript",
      "expected": "string",
      "received": "null"
    },
    "timestamp": "2024-01-15T10:00:00Z",
    "request_id": "req_123456789"
  }
}
```

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_REQUEST` | Request validation failed | 400 |
| `UNAUTHORIZED` | Authentication required | 401 |
| `FORBIDDEN` | Insufficient permissions | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `RATE_LIMITED` | Too many requests | 429 |
| `INTERNAL_ERROR` | Server error | 500 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |

## Rate Limiting

API requests are rate limited to ensure fair usage:

- **Free Tier**: 100 requests per hour
- **Pro Tier**: 1,000 requests per hour
- **Enterprise**: Custom limits

Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

## Webhooks

Oracle Nexus supports webhooks for real-time notifications:

### Webhook Events

- `meeting.started` - Meeting session initiated
- `meeting.ended` - Meeting session completed
- `analysis.completed` - Oracle analysis finished
- `decision.made` - New decision tracked
- `insight.generated` - New insight available

### Webhook Payload

```json
{
  "event": "analysis.completed",
  "timestamp": "2024-01-15T10:00:00Z",
  "data": {
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "meeting_id": "meeting-123",
    "overall_score": 7.6,
    "participants": ["Alice", "Bob"],
    "key_insights": ["High engagement", "Strong alignment"]
  }
}
```

## SDK and Libraries

Official SDKs are available for popular programming languages:

- **Python**: `pip install oracle-nexus-sdk`
- **JavaScript/Node.js**: `npm install oracle-nexus-sdk`
- **Java**: Maven/Gradle dependency available
- **C#/.NET**: NuGet package available

### Python SDK Example

```python
from oracle_nexus import OracleClient

client = OracleClient(api_key="your-api-key")

# Analyze meeting
result = client.analyze_meeting(
    transcript="Meeting transcript...",
    participants=["Alice", "Bob"],
    context="Strategic planning"
)

print(f"Oracle Score: {result.overall_score}")
```

### JavaScript SDK Example

```javascript
import { OracleClient } from 'oracle-nexus-sdk';

const client = new OracleClient({ apiKey: 'your-api-key' });

// Process voice input
const response = await client.processVoice({
  text: "I think we should consider the budget",
  sessionId: "meeting-123"
});

console.log(response.data.response);
```

## Testing

### Test Environment

Use the test environment for development and testing:

```
Base URL: https://api-test.oracle-nexus.ai/v1
API Key: test_key_123456789
```

### Mock Data

Test endpoints provide mock data for development:

```http
GET /oracle/mock/meeting-data
GET /oracle/mock/analysis-result
GET /oracle/mock/voice-response
```

## Support

- **Documentation**: [https://docs.oracle-nexus.ai](https://docs.oracle-nexus.ai)
- **API Status**: [https://status.oracle-nexus.ai](https://status.oracle-nexus.ai)
- **Support Email**: api-support@oracle-nexus.ai
- **GitHub Issues**: [Repository Issues](https://github.com/oracle-nexus/api/issues)

