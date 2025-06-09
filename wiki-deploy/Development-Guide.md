# Development Guide

Comprehensive guide for developers contributing to or extending the Multi-Agent Assistant System.

## Development Environment Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Git
- AWS CLI (optional, for testing Bedrock)
- Code editor with Python support

### Local Development Setup

1. **Clone and Setup**:
```bash
git clone <repository-url>
cd multi-agent-assistant
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Database Setup**:
```bash
# Create development database
sudo -u postgres createdb assistant_dev
sudo -u postgres createuser dev_user --pwprompt
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE assistant_dev TO dev_user;"
```

3. **Environment Configuration**:
```bash
cp .env.example .env.development
# Edit .env.development with your credentials
```

4. **Initialize Database**:
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Project Structure

```
multi-agent-assistant/
├── agents/                 # AI agent implementations
│   ├── __init__.py
│   ├── base_agent.py      # Abstract base class
│   ├── personal_assistant.py
│   ├── calendar_agent.py
│   ├── search_agent.py
│   └── code_assistant.py
├── docs/                  # Documentation (wiki source)
├── graph/                 # Workflow orchestration
│   ├── __init__.py
│   └── workflow.py
├── routes/                # Flask route handlers
│   ├── __init__.py
│   ├── main.py           # Main web routes
│   └── api.py            # API endpoints
├── services/              # External service integrations
│   ├── __init__.py
│   ├── bedrock_service.py
│   ├── perplexity_service.py
│   └── tools_service.py
├── static/                # Static web assets
│   ├── css/
│   ├── js/
│   └── images/
├── templates/             # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   └── chat.html
├── app.py                # Flask application factory
├── config.py             # Configuration management
├── main.py               # Application entry point
├── models.py             # Database models
├── requirements.txt      # Python dependencies
└── pyproject.toml        # Project metadata
```

## Code Style and Standards

### Python Code Style

Follow PEP 8 with these specific guidelines:

```python
# Good: Clear, descriptive names
class CalendarAgent(BaseAgent):
    async def process_scheduling_request(self, user_input: str) -> Dict[str, Any]:
        """Process a calendar scheduling request with conflict detection."""
        pass

# Good: Type hints for all public methods
async def generate_response(
    self, 
    messages: List[Dict[str, str]], 
    max_tokens: int = 1000
) -> str:
    """Generate AI response with specified parameters."""
    pass

# Good: Comprehensive docstrings
class WorkflowEngine:
    """
    Orchestrates multi-agent workflows and manages task delegation.
    
    The WorkflowEngine handles:
    - Agent registration and discovery
    - Task routing and delegation
    - Session state management
    - Error handling and recovery
    
    Example:
        engine = WorkflowEngine()
        engine.register_agent(CalendarAgent())
        result = await engine.process_request("Schedule a meeting")
    """
```

### Code Organization Principles

1. **Single Responsibility**: Each class has one clear purpose
2. **Dependency Injection**: Services passed via constructor
3. **Abstract Interfaces**: Use ABC for agent base classes
4. **Error Handling**: Comprehensive exception handling
5. **Async/Await**: Use async patterns for I/O operations

### Import Organization

```python
# Standard library imports
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

# Third-party imports
import boto3
import requests
from flask import Flask, request, jsonify
from sqlalchemy import Column, Integer, String, DateTime

# Local imports
from config import Config
from models import db, CalendarEvent
from services.bedrock_service import BedrockService
```

## Testing Framework

### Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Pytest configuration
├── test_agents/
│   ├── test_base_agent.py
│   ├── test_calendar_agent.py
│   └── test_search_agent.py
├── test_services/
│   ├── test_bedrock_service.py
│   └── test_perplexity_service.py
├── test_routes/
│   ├── test_api.py
│   └── test_main.py
└── integration/
    ├── test_workflow.py
    └── test_end_to_end.py
```

### Writing Tests

**Unit Tests Example**:
```python
import pytest
from unittest.mock import Mock, AsyncMock
from agents.calendar_agent import CalendarAgent

class TestCalendarAgent:
    @pytest.fixture
    def calendar_agent(self):
        mock_bedrock = Mock()
        return CalendarAgent(mock_bedrock)
    
    def test_can_handle_scheduling_request(self, calendar_agent):
        # Test positive cases
        assert calendar_agent.can_handle("Schedule a meeting tomorrow", {})
        assert calendar_agent.can_handle("Book an appointment at 2 PM", {})
        
        # Test negative cases
        assert not calendar_agent.can_handle("What's the weather?", {})
        assert not calendar_agent.can_handle("Write Python code", {})
    
    @pytest.mark.asyncio
    async def test_process_task_creates_event(self, calendar_agent):
        # Mock database operations
        with patch('models.CalendarEvent') as mock_event:
            result = await calendar_agent.process_task(
                "Schedule team meeting tomorrow at 2 PM",
                {"session_id": "test_session"}
            )
            
            assert result['status'] == 'success'
            assert 'event_id' in result['metadata']
            mock_event.assert_called_once()
```

**Integration Tests Example**:
```python
import pytest
from app import create_app, db
from config import TestConfig

class TestWorkflowIntegration:
    @pytest.fixture
    def app(self):
        app = create_app(TestConfig)
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    def test_chat_endpoint_routing(self, client):
        response = client.post('/api/chat', json={
            'message': 'Schedule a meeting for tomorrow',
            'context': {'session_id': 'test_session'}
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['agent_type'] == 'calendar_agent'
        assert 'response' in data
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agents/test_calendar_agent.py

# Run tests with debugging
pytest -v -s

# Run integration tests only
pytest tests/integration/
```

## Adding New Agents

### Agent Development Process

1. **Create Agent Class**:
```python
# agents/new_agent.py
from agents.base_agent import BaseAgent
from typing import Dict, List, Any

class NewAgent(BaseAgent):
    def __init__(self, bedrock_service, tools_service=None):
        super().__init__('new_agent', bedrock_service, tools_service)
        self.keywords = ['keyword1', 'keyword2', 'keyword3']
    
    def get_system_prompt(self) -> str:
        return """
        You are a specialized agent for handling [specific domain] tasks.
        Your capabilities include:
        - Capability 1
        - Capability 2
        - Capability 3
        
        Always respond with structured, helpful information.
        """
    
    def can_handle(self, task: str, context: Dict[str, Any]) -> bool:
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in self.keywords)
    
    async def process_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Analyze the task
            analysis = await self._analyze_task(task, context)
            
            # Process based on analysis
            if analysis['task_type'] == 'type1':
                return await self._handle_type1(task, context, analysis)
            elif analysis['task_type'] == 'type2':
                return await self._handle_type2(task, context, analysis)
            else:
                return await self._handle_general(task, context)
                
        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            return self.format_error(f"Failed to process request: {str(e)}")
    
    async def _analyze_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the task to determine processing approach"""
        # Implementation here
        pass
    
    def get_capabilities(self) -> List[str]:
        return [
            "Capability 1 description",
            "Capability 2 description",
            "Capability 3 description"
        ]
```

2. **Register Agent**:
```python
# In graph/workflow.py or main initialization
def initialize_agents(bedrock_service, tools_service):
    # Existing agents
    personal_assistant = PersonalAssistantAgent(bedrock_service, tools_service)
    calendar_agent = CalendarAgent(bedrock_service, tools_service)
    
    # New agent
    new_agent = NewAgent(bedrock_service, tools_service)
    
    # Register with coordinator
    personal_assistant.register_agent(calendar_agent)
    personal_assistant.register_agent(new_agent)  # Add this line
    
    return personal_assistant
```

3. **Add Tests**:
```python
# tests/test_agents/test_new_agent.py
import pytest
from agents.new_agent import NewAgent

class TestNewAgent:
    @pytest.fixture
    def new_agent(self):
        mock_bedrock = Mock()
        return NewAgent(mock_bedrock)
    
    def test_can_handle_relevant_tasks(self, new_agent):
        assert new_agent.can_handle("task with keyword1", {})
        assert not new_agent.can_handle("unrelated task", {})
    
    @pytest.mark.asyncio
    async def test_process_task_success(self, new_agent):
        result = await new_agent.process_task("valid task", {})
        assert result['status'] == 'success'
```

## Database Development

### Adding New Models

```python
# In models.py
class NewModel(db.Model):
    __tablename__ = 'new_table'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
```

### Database Migrations

```bash
# Initialize migrations (first time only)
flask db init

# Create migration
flask db migrate -m "Add new model for feature X"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

## API Development

### Adding New Endpoints

```python
# In routes/api.py
from flask import Blueprint, request, jsonify

api_bp = Blueprint('api', __name__)

@api_bp.route('/new-endpoint', methods=['POST'])
def new_endpoint():
    """
    New API endpoint for specific functionality.
    
    Expected JSON payload:
    {
        "parameter1": "value",
        "parameter2": "value"
    }
    
    Returns:
    {
        "result": "data",
        "status": "success|error"
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'parameter1' not in data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Missing required parameter1'
            }), 400
        
        # Process request
        result = process_new_functionality(data)
        
        return jsonify({
            'result': result,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in new endpoint: {str(e)}")
        return jsonify({
            'error': 'processing_error',
            'message': 'Failed to process request'
        }), 500
```

## Performance Optimization

### Profiling

```python
# Add to development dependencies
# pip install pytest-profiling memory-profiler

# Profile specific functions
@profile
def expensive_function():
    # Function implementation
    pass

# Memory profiling
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Function implementation
    pass
```

### Optimization Techniques

1. **Database Query Optimization**:
```python
# Use eager loading for relationships
events = CalendarEvent.query.options(
    joinedload(CalendarEvent.attendees)
).filter_by(date=today).all()

# Use pagination for large result sets
events = CalendarEvent.query.paginate(
    page=page, per_page=20, error_out=False
).items
```

2. **Caching Implementation**:
```python
from functools import lru_cache
import redis

# Memory caching
@lru_cache(maxsize=128)
def expensive_computation(param):
    # Expensive operation
    return result

# Redis caching
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cached_api_call(key, api_function, *args, **kwargs):
    cached_result = redis_client.get(key)
    if cached_result:
        return json.loads(cached_result)
    
    result = api_function(*args, **kwargs)
    redis_client.setex(key, 1800, json.dumps(result))  # 30 min cache
    return result
```

## Debugging

### Logging Best Practices

```python
import logging

# Configure logger for your module
logger = logging.getLogger(__name__)

class MyAgent(BaseAgent):
    def process_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Processing task for session: {context.get('session_id')}")
        logger.debug(f"Task content: {task[:100]}...")  # Log first 100 chars
        
        try:
            result = self._do_processing(task, context)
            logger.info(f"Task completed successfully")
            return result
        except Exception as e:
            logger.error(f"Task processing failed: {str(e)}", exc_info=True)
            raise
```

### Debug Mode Features

```python
# In development environment
if app.debug:
    # Enable SQL query logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    # Add debug endpoints
    @app.route('/debug/agents')
    def debug_agents():
        return jsonify({
            agent_type: agent.get_capabilities()
            for agent_type, agent in workflow_engine.agents.items()
        })
```

## Deployment

### Production Checklist

- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] Security headers configured
- [ ] Logging configured
- [ ] Health checks working
- [ ] Rate limiting enabled
- [ ] Error monitoring setup

### Docker Development

```dockerfile
# Dockerfile for development
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--reload", "main:app"]
```

```yaml
# docker-compose.yml for development
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/assistant_dev
    depends_on:
      - db
    volumes:
      - .:/app
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=assistant_dev
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Contributing Guidelines

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes with tests
4. Run test suite: `pytest`
5. Update documentation if needed
6. Commit with clear messages
7. Push and create pull request

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Error handling implemented
- [ ] Logging added where appropriate