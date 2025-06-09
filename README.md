# Multi-Agent Assistant System

A sophisticated AI-powered assistant system built with Flask and LangGraph, featuring coordinated specialized agents for calendar management, web search, and code assistance. The system uses Amazon Bedrock for LLM inference and Perplexity for real-time web search capabilities.

## 🏗️ System Architecture

The system follows a multi-agent architecture pattern where specialized AI agents work together under the coordination of a Personal Assistant Agent. Each agent has specific capabilities and can be invoked based on the user's request.

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface (Flask)                    │
├─────────────────────────────────────────────────────────────┤
│                   API Layer (REST API)                     │
├─────────────────────────────────────────────────────────────┤
│              Multi-Agent Workflow Engine                   │
│                    (LangGraph-inspired)                    │
├─────────────────────────────────────────────────────────────┤
│ Personal Assistant Agent (Coordinator)                     │
│ ├── Calendar Agent                                         │
│ ├── Search Agent                                           │
│ └── Code Assistant Agent                                   │
├─────────────────────────────────────────────────────────────┤
│                   Service Layer                            │
│ ├── Amazon Bedrock Service (LLM)                          │
│ ├── Perplexity Service (Web Search)                       │
│ └── Tools Service (Python, Shell, Editor, Journal)       │
├─────────────────────────────────────────────────────────────┤
│                  Data Persistence                          │
│ └── SQLite Database (Calendar Events, Chat History)       │
└─────────────────────────────────────────────────────────────┘
```

## 🤖 Agent Overview

### Personal Assistant Agent (Coordinator)
- **Purpose**: Main orchestrator that analyzes user requests and delegates to appropriate specialized agents
- **Capabilities**: Task analysis, delegation, conversation management, general assistance
- **Decision Making**: Uses LLM to determine which specialized agent should handle specific requests

### Calendar Agent
- **Purpose**: Manages scheduling and calendar operations
- **Capabilities**: 
  - Event creation and management
  - Conflict detection
  - Free time finding
  - Natural language date/time parsing
- **Storage**: SQLite database for persistent calendar data

### Search Agent
- **Purpose**: Provides current information through web search
- **Capabilities**:
  - Real-time web search via Perplexity API
  - Information research and fact-finding
  - Source citation and verification
  - Current events and market data
- **Intelligence**: Determines when web search is needed vs. direct LLM response

### Code Assistant Agent
- **Purpose**: Programming assistance and development tools
- **Capabilities**:
  - Code generation and review
  - Debugging assistance
  - Programming concept explanations
  - Integration with built-in development tools
- **Tools**: Python REPL, file editor, shell access, persistent journal

## 🔧 Technical Components

### Workflow Engine (`graph/workflow.py`)
LangGraph-inspired orchestration system that:
- Manages agent states and conversation history
- Coordinates inter-agent communication
- Handles workflow persistence and recovery
- Provides health monitoring and status tracking

### Service Layer
- **Bedrock Service**: Amazon Bedrock integration for LLM inference
- **Perplexity Service**: Web search capabilities with citation support
- **Tools Service**: Built-in development tools (Python REPL, editor, shell, journal)

### Database Models (`models.py`)
- **CalendarEvent**: Persistent calendar data storage
- **ChatSession**: Conversation session management
- **ChatMessage**: Message history with agent attribution
- **AgentState**: Agent state persistence

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Amazon Bedrock access (AWS credentials)
- Perplexity API key (for web search)

### Installation

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd multi-agent-assistant
   ```

2. **Environment Configuration**
   Create a `.env` file with required API keys:
   ```env
   # Amazon Bedrock Configuration
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
   
   # Perplexity API (for web search)
   PERPLEXITY_API_KEY=your_perplexity_api_key
   
   # Flask Configuration
   SESSION_SECRET=your-secret-key-here
   FLASK_DEBUG=True
   
   # Database (PostgreSQL)
   DATABASE_URL=postgresql://username:password@host:port/database
   # Note: DATABASE_URL is automatically configured when using the database tool
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```
   The application will be available at `http://localhost:5000`

### Alternative: Using Gunicorn (Production)
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## 📱 Usage Examples

### Calendar Management
```
User: "Schedule a meeting with the team tomorrow at 2 PM"
→ Calendar Agent creates event, checks for conflicts

User: "What's on my schedule for today?"
→ Calendar Agent lists today's events

User: "When am I free this week?"
→ Calendar Agent finds available time slots
```

### Web Search & Research
```
User: "What's the latest news about AI developments?"
→ Search Agent performs web search, provides current information with sources

User: "What's the current price of Bitcoin?"
→ Search Agent fetches real-time market data

User: "Research the benefits of renewable energy"
→ Search Agent compiles information from multiple sources
```

### Code Assistance
```
User: "Write a Python function to calculate Fibonacci numbers"
→ Code Assistant generates optimized code with explanations

User: "Debug this error: NameError: name 'x' is not defined"
→ Code Assistant analyzes error and provides solutions

User: "Run this Python code: print('Hello, World!')"
→ Code Assistant executes code using Python REPL tool
```

### General Assistance
```
User: "Help me plan a project"
→ Personal Assistant provides direct guidance

User: "Explain quantum computing"
→ Personal Assistant or Search Agent (depending on need for current info)
```

## 🏗️ Project Structure

```
multi-agent-assistant/
├── agents/                    # AI Agent implementations
│   ├── __init__.py           # Agent exports
│   ├── base_agent.py         # Abstract base agent class
│   ├── personal_assistant.py # Main coordinator agent
│   ├── calendar_agent.py     # Calendar management agent
│   ├── search_agent.py       # Web search agent
│   └── code_assistant.py     # Programming assistance agent
├── graph/                     # Workflow orchestration
│   ├── __init__.py           # Graph exports
│   ├── state.py              # State management classes
│   └── workflow.py           # Multi-agent workflow engine
├── services/                  # External service integrations
│   ├── __init__.py           # Service exports
│   ├── bedrock_service.py    # Amazon Bedrock LLM service
│   ├── perplexity_service.py # Perplexity web search service
│   └── tools_service.py      # Built-in development tools
├── routes/                    # Flask route handlers
│   ├── __init__.py           # Route exports
│   ├── main.py               # Main web routes
│   └── api.py                # REST API endpoints
├── templates/                 # HTML templates
│   ├── base.html             # Base template with navigation
│   ├── index.html            # Landing page
│   └── chat.html             # Chat interface
├── static/                    # Static web assets
│   ├── css/style.css         # Custom styles
│   └── js/chat.js            # Chat interface JavaScript
├── app.py                     # Flask application factory
├── main.py                    # Application entry point
├── config.py                  # Configuration management
├── models.py                  # Database models
└── README.md                  # This documentation
```

## 🔒 Security & Guardrails

### AI Agent Guardrails
- **Content Filtering**: Agents avoid generating harmful or inappropriate content
- **Tool Access Control**: Built-in tools have security restrictions (e.g., dangerous shell commands blocked)
- **File System Protection**: File operations restricted to current directory
- **API Rate Limiting**: Reasonable timeout and retry mechanisms
- **Input Validation**: All user inputs are validated and sanitized

### Security Measures
- **Environment Variables**: Sensitive credentials stored as environment variables
- **SQL Injection Protection**: Using SQLAlchemy ORM with parameterized queries
- **XSS Prevention**: HTML escaping in web interface
- **CSRF Protection**: Flask session management
- **Command Injection**: Shell command filtering and validation

## 🔍 API Endpoints

### Chat API
- **POST** `/api/chat` - Send message to multi-agent system
- **GET** `/api/workflow/status/<session_id>` - Get workflow status
- **DELETE** `/api/clear/<session_id>` - Clear session data

### System Monitoring
- **GET** `/api/health` - Comprehensive system health check
- **GET** `/api/agents` - List available agents and capabilities
- **GET** `/health` - Simple health check

## 🧪 Built-in Development Tools

The Code Assistant Agent provides access to several built-in tools:

### Python REPL
- Execute Python code snippets
- Safe execution environment with timeout
- Output capture and error handling

### File Editor
- Read, write, and modify files
- Restricted to current directory for security
- Support for various file operations

### Shell Access
- Execute system commands
- Security filtering prevents dangerous operations
- Timeout protection for long-running commands

### Persistent Journal
- Keep notes and logs across sessions
- Timestamped entries
- Read, write, and clear operations

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required |
| `BEDROCK_MODEL_ID` | Bedrock model identifier | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| `PERPLEXITY_API_KEY` | Perplexity API key | Required for search |
| `DATABASE_URL` | Database connection string | `sqlite:///assistant.db` |
| `SESSION_SECRET` | Flask session secret | `dev-secret-key-change-in-production` |
| `FLASK_DEBUG` | Enable debug mode | `True` |
| `MAX_AGENT_ITERATIONS` | Max workflow iterations | `10` |
| `AGENT_TIMEOUT` | Agent timeout in seconds | `30` |

## 🐛 Troubleshooting

### Common Issues

1. **AWS Bedrock Access Denied**
   - Verify AWS credentials are correct
   - Ensure Bedrock access is enabled in your AWS account
   - Check IAM permissions for Bedrock API access

2. **Perplexity API Errors**
   - Verify API key is valid and active
   - Check API usage limits and billing status
   - Ensure internet connectivity for API calls

3. **Database Issues**
   - Check SQLite database file permissions
   - Verify DATABASE_URL configuration
   - Run database migrations if needed

4. **Agent Communication Failures**
   - Check system health endpoint `/api/health`
   - Review application logs for specific errors
   - Verify all required services are running

### Health Monitoring

The system provides comprehensive health monitoring:
- Service status (Bedrock, Perplexity)
- Agent availability and capabilities
- Active workflow count
- Database connectivity

Access health information at `/api/health` or through the web interface.

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   - Set production environment variables
   - Use strong SESSION_SECRET
   - Configure production database (PostgreSQL recommended)

2. **Web Server**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
   ```

3. **Reverse Proxy** (Nginx example)
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangGraph**: Inspiration for multi-agent workflow orchestration
- **Amazon Bedrock**: LLM inference capabilities
- **Perplexity AI**: Real-time web search and information retrieval
- **Flask**: Web framework foundation
- **Bootstrap**: UI component library