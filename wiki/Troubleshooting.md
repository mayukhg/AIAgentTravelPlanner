# Troubleshooting Guide

Common issues and solutions for the Multi-Agent Assistant System.

## Quick Diagnostics

### Health Check

First, verify system status:
```bash
curl http://localhost:5000/api/health
```

Expected healthy response:
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "bedrock": "available",
    "perplexity": "available"
  },
  "agents": {
    "personal_assistant": "active",
    "calendar_agent": "active",
    "search_agent": "active",
    "code_assistant": "active"
  }
}
```

## Common Issues

### Application Won't Start

**Error**: `ModuleNotFoundError: No module named 'flask'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Error**: `Port 5000 is already in use`
```bash
# Find process using port
lsof -i :5000
# Kill the process
kill -9 <PID>
# Or use different port
export PORT=5001
python main.py
```

**Error**: `Can't connect to PostgreSQL server`
```bash
# Check PostgreSQL status
sudo systemctl status postgresql
# Start PostgreSQL if stopped
sudo systemctl start postgresql
# Verify connection
psql -h localhost -U assistant_user -d assistant_db
```

### Database Issues

**Error**: `relation "chat_sessions" does not exist`
```python
# Create database tables
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

**Error**: `FATAL: password authentication failed`
```bash
# Reset PostgreSQL password
sudo -u postgres psql
ALTER USER assistant_user PASSWORD 'new_password';
# Update DATABASE_URL in .env file
```

**Error**: `too many connections`
```python
# Reduce connection pool size in config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 5,
    "max_overflow": 10,
    "pool_recycle": 300
}
```

### AWS Bedrock Issues

**Error**: `UnauthorizedOperation: You are not authorized to perform this operation`
```bash
# Check AWS credentials
aws sts get-caller-identity
# Verify Bedrock model access in AWS Console
```

**Error**: `AccessDeniedException: User is not authorized to perform: bedrock:InvokeModel`
```json
// Add to IAM policy
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

**Error**: `ValidationException: The model 'anthropic.claude-3-5-sonnet-20241022-v2:0' is not supported`
```bash
# Check model availability in your AWS region
aws bedrock list-foundation-models --region us-east-1
# Request model access in Bedrock console
```

### Perplexity API Issues

**Error**: `401 Unauthorized`
```bash
# Verify API key
curl -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
     https://api.perplexity.ai/chat/completions
```

**Error**: `429 Too Many Requests`
```python
# Implement rate limiting in search_agent.py
import time
time.sleep(1)  # Add delay between requests
```

### Agent Not Responding

**Issue**: Agent selection not working properly
```python
# Debug agent selection
@app.route('/debug/agents')
def debug_agents():
    return jsonify({
        agent_type: {
            'capabilities': agent.get_capabilities(),
            'can_handle_test': agent.can_handle("test message", {})
        }
        for agent_type, agent in workflow_engine.agents.items()
    })
```

**Issue**: Agent timeout
```python
# Increase timeout in config.py
AGENT_TIMEOUT = 60  # Increase from 30 to 60 seconds
```

### Session Management Issues

**Issue**: Session data not persisting
```python
# Check session creation
session = ChatSession.query.filter_by(session_id='test').first()
if not session:
    print("Session not found in database")
```

**Issue**: Memory usage growing
```python
# Implement session cleanup
def cleanup_old_sessions():
    cutoff = datetime.utcnow() - timedelta(hours=24)
    old_sessions = ChatSession.query.filter(
        ChatSession.created_at < cutoff
    ).all()
    for session in old_sessions:
        db.session.delete(session)
    db.session.commit()
```

## Performance Issues

### Slow Response Times

**Check database query performance**:
```sql
-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
SELECT pg_reload_conf();

-- Monitor slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

**Optimize agent processing**:
```python
# Add performance monitoring
import time

class PerformanceMonitor:
    def __init__(self):
        self.timings = {}
    
    def time_operation(self, operation_name):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                self.timings[operation_name] = duration
                return result
            return wrapper
        return decorator
```

### Memory Usage

**Monitor memory usage**:
```python
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

# Log memory usage periodically
@app.before_request
def log_memory():
    if app.debug:
        memory_mb = get_memory_usage()
        if memory_mb > 500:  # Alert if over 500MB
            app.logger.warning(f"High memory usage: {memory_mb:.1f}MB")
```

## Debugging Tools

### Enable Debug Logging

```python
# In main.py or app.py
import logging

if app.debug:
    logging.basicConfig(level=logging.DEBUG)
    
    # Enable SQLAlchemy query logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    # Enable detailed agent logging
    logging.getLogger('agents').setLevel(logging.DEBUG)
    logging.getLogger('services').setLevel(logging.DEBUG)
```

### Debug Endpoints

Add these endpoints for development debugging:

```python
@app.route('/debug/sessions')
def debug_sessions():
    sessions = ChatSession.query.limit(10).all()
    return jsonify([{
        'session_id': s.session_id,
        'created_at': s.created_at.isoformat(),
        'message_count': len(s.messages)
    } for s in sessions])

@app.route('/debug/agents/<agent_type>')
def debug_agent(agent_type):
    agent = workflow_engine.agents.get(agent_type)
    if not agent:
        return jsonify({'error': 'Agent not found'}), 404
    
    return jsonify({
        'agent_type': agent.agent_type,
        'capabilities': agent.get_capabilities(),
        'system_prompt': agent.get_system_prompt()
    })

@app.route('/debug/database')
def debug_database():
    try:
        result = db.session.execute('SELECT version()')
        version = result.fetchone()[0]
        
        tables = db.session.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """).fetchall()
        
        return jsonify({
            'database_version': version,
            'tables': [t[0] for t in tables],
            'connection_status': 'healthy'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'connection_status': 'failed'
        }), 500
```

### Log Analysis

**Analyze application logs**:
```bash
# View recent errors
tail -f app.log | grep ERROR

# Count error types
grep ERROR app.log | cut -d'-' -f4 | sort | uniq -c

# Monitor agent performance
grep "Agent.*completed" app.log | tail -20
```

**Monitor database connections**:
```sql
-- Current connections
SELECT pid, usename, application_name, client_addr, state 
FROM pg_stat_activity 
WHERE datname = 'assistant_db';

-- Connection statistics
SELECT sum(numbackends) as total_connections,
       max(numbackends) as max_connections
FROM pg_stat_database 
WHERE datname = 'assistant_db';
```

## Error Recovery

### Automatic Recovery

```python
class ErrorRecoveryManager:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
    
    async def with_retry(self, operation, *args, **kwargs):
        """Execute operation with automatic retry on failure"""
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                
                wait_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(wait_time)
                logger.warning(f"Retrying operation after {wait_time}s, attempt {attempt + 1}")
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, operation, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await operation(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
            
            raise
```

## Prevention Strategies

### Health Monitoring

```python
class HealthMonitor:
    def __init__(self):
        self.checks = []
    
    def add_check(self, name, check_function):
        self.checks.append((name, check_function))
    
    async def run_health_checks(self):
        results = {}
        overall_status = 'healthy'
        
        for name, check_function in self.checks:
            try:
                result = await check_function()
                results[name] = {'status': 'healthy', 'details': result}
            except Exception as e:
                results[name] = {'status': 'unhealthy', 'error': str(e)}
                overall_status = 'unhealthy'
        
        return {'overall_status': overall_status, 'checks': results}

# Usage
health_monitor = HealthMonitor()
health_monitor.add_check('database', check_database_connection)
health_monitor.add_check('bedrock', check_bedrock_availability)
health_monitor.add_check('perplexity', check_perplexity_api)
```

### Monitoring and Alerting

```python
# Simple alerting system
class AlertManager:
    def __init__(self):
        self.alert_thresholds = {
            'response_time': 5.0,  # seconds
            'error_rate': 0.1,     # 10%
            'memory_usage': 1000   # MB
        }
    
    def check_and_alert(self, metric_name, value):
        threshold = self.alert_thresholds.get(metric_name)
        if threshold and value > threshold:
            self.send_alert(f"{metric_name} exceeded threshold: {value} > {threshold}")
    
    def send_alert(self, message):
        # Implement your alerting mechanism
        logger.critical(f"ALERT: {message}")
```

## Getting Help

### Before Seeking Help

1. Check application logs for specific error messages
2. Verify all environment variables are set correctly
3. Test individual components (database, APIs) separately
4. Try with a clean database and fresh session

### Information to Include

When reporting issues, include:

- Error messages (full stack traces)
- Environment details (OS, Python version, dependency versions)
- Configuration (sanitized, no secrets)
- Steps to reproduce the issue
- Expected vs actual behavior

### Log Collection

```bash
# Collect system information
python --version
pip list
env | grep -E "(AWS|PERPLEXITY|DATABASE|FLASK)" | sed 's/=.*/=***/'

# Collect application logs
tail -100 app.log

# Collect database status
psql -d assistant_db -c "\l"
psql -d assistant_db -c "\dt"
```

This troubleshooting guide covers the most common issues and provides systematic approaches to diagnosing and resolving problems in the multi-agent assistant system.