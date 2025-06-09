# Configuration Guide

Complete configuration reference for the Multi-Agent Assistant System.

## Environment Variables

### Required Configuration

| Variable | Description | Example Value | Required |
|----------|-------------|---------------|----------|
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` | Yes |
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIAIOSFODNN7EXAMPLE` | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` | Yes |
| `PERPLEXITY_API_KEY` | Perplexity API key | `pplx-abc123def456...` | Yes |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` | Yes |
| `SESSION_SECRET` | Flask session secret | `your-secure-secret-key` | Yes |

### Optional Configuration

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `BEDROCK_MODEL_ID` | Claude model identifier | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| `PERPLEXITY_MODEL` | Perplexity model name | `llama-3.1-sonar-small-128k-online` |
| `FLASK_DEBUG` | Enable debug mode | `True` |
| `MAX_AGENT_ITERATIONS` | Maximum agent processing loops | `10` |
| `AGENT_TIMEOUT` | Agent processing timeout (seconds) | `30` |

## Configuration Files

### Environment File (.env)

Create a `.env` file in the project root:

```env
# Amazon Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Perplexity AI Configuration
PERPLEXITY_API_KEY=your_perplexity_api_key_here
PERPLEXITY_MODEL=llama-3.1-sonar-small-128k-online

# Database Configuration
DATABASE_URL=postgresql://assistant_user:password@localhost:5432/assistant_db

# Flask Configuration
SESSION_SECRET=your-super-secret-session-key-change-in-production
FLASK_DEBUG=True

# Performance Configuration
MAX_AGENT_ITERATIONS=10
AGENT_TIMEOUT=30
```

### Application Configuration (config.py)

The system uses a centralized configuration class:

```python
import os

class Config:
    # AWS and Bedrock Configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
    
    # Perplexity Configuration
    PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')
    PERPLEXITY_MODEL = 'llama-3.1-sonar-small-128k-online'
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///assistant.db')
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Agent Configuration
    MAX_AGENT_ITERATIONS = int(os.environ.get('MAX_AGENT_ITERATIONS', '10'))
    AGENT_TIMEOUT = int(os.environ.get('AGENT_TIMEOUT', '30'))
```

## Service-Specific Configuration

### Amazon Bedrock

**Model Configuration**:
- **Model ID**: `anthropic.claude-3-5-sonnet-20241022-v2:0`
- **Max Tokens**: 1000-4000 (configurable per request)
- **Temperature**: 0.1-0.7 (lower for focused responses)
- **Top P**: 0.95 (enhanced token sampling)
- **Top K**: 50 (optimized for Claude 3.5 Sonnet v4)

**Region Support**:
- Primary: `us-east-1`
- Secondary: `us-west-2`, `eu-west-1`

**IAM Permissions Required**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

### Perplexity AI

**API Configuration**:
- **Base URL**: `https://api.perplexity.ai`
- **Model**: `llama-3.1-sonar-small-128k-online`
- **Rate Limits**: 60 requests/minute (standard plan)
- **Timeout**: 30 seconds per request

**Request Parameters**:
```python
{
    "model": "llama-3.1-sonar-small-128k-online",
    "temperature": 0.2,
    "top_p": 0.9,
    "max_tokens": 1000,
    "search_recency_filter": "month",
    "return_images": False,
    "return_related_questions": False
}
```

### PostgreSQL Database

**Connection Configuration**:
```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20
}
```

**Required Database Setup**:
```sql
-- Create database and user
CREATE DATABASE assistant_db;
CREATE USER assistant_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE assistant_db TO assistant_user;

-- Connect to the database
\c assistant_db

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO assistant_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO assistant_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO assistant_user;
```

## Agent-Specific Configuration

### Personal Assistant Agent

```python
PERSONAL_ASSISTANT_CONFIG = {
    'delegation_threshold': 0.7,  # Confidence threshold for delegation
    'max_conversation_history': 50,  # Messages to retain in context
    'response_timeout': 30,  # Seconds before timeout
    'fallback_enabled': True  # Enable direct response fallback
}
```

### Calendar Agent

```python
CALENDAR_AGENT_CONFIG = {
    'default_event_duration': 60,  # Minutes
    'conflict_detection': True,
    'time_zone': 'UTC',
    'business_hours': {
        'start': '09:00',
        'end': '17:00',
        'days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    },
    'max_events_per_day': 20
}
```

### Search Agent

```python
SEARCH_AGENT_CONFIG = {
    'max_search_results': 10,
    'result_synthesis': True,
    'source_validation': True,
    'cache_results': True,
    'cache_duration': 1800,  # 30 minutes
    'recency_filter': 'month'
}
```

### Code Assistant Agent

```python
CODE_ASSISTANT_CONFIG = {
    'supported_languages': [
        'python', 'javascript', 'java', 'c++', 'sql', 'html', 'css'
    ],
    'code_execution': False,  # Security consideration
    'max_code_length': 5000,  # Characters
    'include_examples': True,
    'explain_complexity': True
}
```

## Security Configuration

### Input Validation

```python
SECURITY_CONFIG = {
    'validate_user_input': True,
    'sanitize_commands': True,
    'block_dangerous_patterns': True,
    'max_message_length': 10000,
    'rate_limiting': {
        'chat_endpoint': 60,  # requests per minute
        'api_endpoints': 120  # requests per minute
    }
}
```

### Session Management

```python
SESSION_CONFIG = {
    'session_timeout': 3600,  # 1 hour
    'secure_cookies': True,
    'session_regeneration': True,
    'csrf_protection': True
}
```

## Performance Configuration

### Connection Pooling

```python
CONNECTION_POOL_CONFIG = {
    'database': {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 300,
        'pool_pre_ping': True
    },
    'bedrock': {
        'max_connections': 5,
        'connection_timeout': 30,
        'read_timeout': 60
    }
}
```

### Caching Configuration

```python
CACHE_CONFIG = {
    'llm_responses': {
        'enabled': True,
        'ttl': 1800,  # 30 minutes
        'max_size': 1000
    },
    'search_results': {
        'enabled': True,
        'ttl': 900,  # 15 minutes
        'max_size': 500
    }
}
```

## Logging Configuration

### Log Levels and Outputs

```python
import logging

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'formatter': 'detailed'
        }
    },
    'loggers': {
        'agents': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'services': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}
```

## Environment-Specific Configuration

### Development Environment

```env
# Development (.env.development)
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
CACHE_ENABLED=False
RATE_LIMITING_ENABLED=False
DATABASE_URL=postgresql://dev_user:dev_pass@localhost:5432/assistant_dev
```

### Testing Environment

```env
# Testing (.env.testing)
FLASK_DEBUG=False
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/assistant_test
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
CACHE_ENABLED=False
```

### Production Environment

```env
# Production (.env.production)
FLASK_DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=postgresql://prod_user:secure_pass@prod-host:5432/assistant_prod
SESSION_SECRET=production-grade-secret-key-256-bits
RATE_LIMITING_ENABLED=True
CACHE_ENABLED=True
```

## Configuration Validation

### Startup Validation

```python
class ConfigValidator:
    @staticmethod
    def validate_required_config():
        """Validate that all required configuration is present"""
        required_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'PERPLEXITY_API_KEY',
            'DATABASE_URL',
            'SESSION_SECRET'
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    @staticmethod
    def validate_aws_credentials():
        """Validate AWS credentials and region"""
        try:
            import boto3
            client = boto3.client('bedrock-runtime')
            # Test connection
            client.list_foundation_models()
            return True
        except Exception as e:
            raise ValueError(f"AWS configuration invalid: {str(e)}")
```

## Dynamic Configuration Updates

### Runtime Configuration Changes

```python
class ConfigManager:
    def __init__(self):
        self.config_watchers = []
    
    def update_agent_config(self, agent_type: str, config_updates: Dict):
        """Update agent configuration at runtime"""
        current_config = getattr(self, f'{agent_type.upper()}_CONFIG', {})
        current_config.update(config_updates)
        
        # Notify watchers
        for watcher in self.config_watchers:
            watcher.on_config_change(agent_type, config_updates)
    
    def register_config_watcher(self, watcher):
        """Register callback for configuration changes"""
        self.config_watchers.append(watcher)
```

## Configuration Best Practices

### Security Best Practices

1. **Never commit secrets to version control**
2. **Use strong, unique secrets for production**
3. **Rotate API keys regularly**
4. **Use environment-specific configuration files**
5. **Validate configuration at startup**

### Performance Best Practices

1. **Tune connection pool sizes based on load**
2. **Enable caching for appropriate data**
3. **Set appropriate timeouts**
4. **Monitor and adjust rate limits**
5. **Use proper logging levels in production**

### Maintenance Best Practices

1. **Document all configuration changes**
2. **Test configuration in staging before production**
3. **Monitor configuration-related errors**
4. **Backup configuration files**
5. **Use configuration management tools for production**