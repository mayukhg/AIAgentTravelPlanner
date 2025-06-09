# API Reference

Complete REST API documentation for the Multi-Agent Assistant System.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, the API uses session-based authentication. No API keys are required for local development.

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send message to multi-agent system |
| GET | `/workflow/status` | Get workflow execution status |
| GET | `/agents` | List available agents and capabilities |
| GET | `/health` | Comprehensive system health check |
| DELETE | `/clear` | Clear session data |

---

## Chat API

### Send Message

Send a message to the multi-agent assistant system.

**Endpoint:** `POST /api/chat`

**Request Body:**
```json
{
  "message": "string",
  "context": {
    "session_id": "string (optional)",
    "agent_preference": "string (optional)"
  }
}
```

**Response:**
```json
{
  "response": "string",
  "agent_type": "string",
  "session_id": "string",
  "metadata": {
    "processing_time": "float",
    "agent_confidence": "float",
    "sources": ["array of strings (if applicable)"]
  },
  "status": "success|error"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Schedule a meeting for tomorrow at 2 PM",
    "context": {
      "session_id": "abc123"
    }
  }'
```

**Example Response:**
```json
{
  "response": "I've scheduled a meeting for tomorrow at 2:00 PM. The event has been added to your calendar with ID cal_001.",
  "agent_type": "calendar_agent",
  "session_id": "abc123",
  "metadata": {
    "processing_time": 1.2,
    "agent_confidence": 0.95,
    "event_id": "cal_001"
  },
  "status": "success"
}
```

---

## Workflow Status API

### Get Workflow Status

Retrieve current workflow execution status and agent activity.

**Endpoint:** `GET /api/workflow/status`

**Query Parameters:**
- `session_id` (optional): Filter by session ID

**Response:**
```json
{
  "status": "idle|processing|error",
  "active_agents": ["array of agent types"],
  "session_count": "integer",
  "uptime": "float (seconds)",
  "last_activity": "ISO timestamp"
}
```

**Example Request:**
```bash
curl http://localhost:5000/api/workflow/status?session_id=abc123
```

---

## Agents API

### List Available Agents

Get information about all available agents and their capabilities.

**Endpoint:** `GET /api/agents`

**Response:**
```json
{
  "agents": [
    {
      "type": "personal_assistant",
      "name": "Personal Assistant",
      "description": "Main coordinator agent",
      "capabilities": [
        "Task delegation",
        "Conversation management",
        "General assistance"
      ],
      "status": "active"
    },
    {
      "type": "calendar_agent",
      "name": "Calendar Agent",
      "description": "Schedule and event management",
      "capabilities": [
        "Event creation",
        "Schedule viewing",
        "Conflict detection",
        "Meeting scheduling"
      ],
      "status": "active"
    }
  ]
}
```

---

## Health Check API

### System Health Check

Comprehensive health check for all system components.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "ISO timestamp",
  "services": {
    "database": "connected|disconnected",
    "bedrock": "available|unavailable",
    "perplexity": "available|unavailable"
  },
  "agents": {
    "personal_assistant": "active|inactive",
    "calendar_agent": "active|inactive",
    "search_agent": "active|inactive",
    "code_assistant": "active|inactive"
  },
  "metrics": {
    "response_time_ms": "float",
    "memory_usage_mb": "float",
    "active_sessions": "integer"
  }
}
```

---

## Session Management API

### Clear Session

Clear all session data and conversation history.

**Endpoint:** `DELETE /api/clear`

**Query Parameters:**
- `session_id` (optional): Specific session to clear

**Response:**
```json
{
  "message": "Session cleared successfully",
  "session_id": "string",
  "status": "success"
}
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "error_code",
  "message": "Human readable error message",
  "details": "Additional error details (optional)",
  "status": "error"
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `invalid_request` | Malformed request body | 400 |
| `agent_unavailable` | Requested agent is not available | 503 |
| `processing_timeout` | Request processing timeout | 504 |
| `service_unavailable` | External service (Bedrock/Perplexity) unavailable | 503 |
| `database_error` | Database connection or query error | 500 |
| `authentication_required` | Session authentication required | 401 |

---

## Rate Limiting

- **Chat API**: 60 requests per minute per session
- **Other APIs**: 120 requests per minute per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

---

## WebSocket API

Real-time communication for streaming responses.

**Endpoint:** `ws://localhost:5000/ws/chat`

**Message Format:**
```json
{
  "type": "message|status|error",
  "data": {
    "message": "string",
    "session_id": "string"
  }
}
```

**Example Usage:**
```javascript
const ws = new WebSocket('ws://localhost:5000/ws/chat');

ws.onopen = function() {
  ws.send(JSON.stringify({
    type: 'message',
    data: {
      message: 'Hello, assistant!',
      session_id: 'abc123'
    }
  }));
};

ws.onmessage = function(event) {
  const response = JSON.parse(event.data);
  console.log('Agent response:', response);
};
```

---

## SDK Examples

### Python SDK

```python
import requests

class AssistantAPI:
    def __init__(self, base_url="http://localhost:5000/api"):
        self.base_url = base_url
        self.session_id = None
    
    def chat(self, message):
        response = requests.post(f"{self.base_url}/chat", json={
            "message": message,
            "context": {"session_id": self.session_id}
        })
        data = response.json()
        self.session_id = data.get("session_id")
        return data
    
    def health_check(self):
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# Usage
api = AssistantAPI()
result = api.chat("What's the weather like today?")
print(result["response"])
```

### JavaScript SDK

```javascript
class AssistantAPI {
  constructor(baseUrl = 'http://localhost:5000/api') {
    this.baseUrl = baseUrl;
    this.sessionId = null;
  }
  
  async chat(message) {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        context: { session_id: this.sessionId }
      })
    });
    
    const data = await response.json();
    this.sessionId = data.session_id;
    return data;
  }
  
  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/health`);
    return response.json();
  }
}

// Usage
const api = new AssistantAPI();
api.chat('Schedule a meeting for tomorrow')
  .then(result => console.log(result.response));
```