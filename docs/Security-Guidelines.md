# Security Guidelines

Comprehensive security guidelines for deploying and maintaining the Multi-Agent Assistant System.

## Security Architecture

### Defense in Depth

The system implements multiple security layers:

1. **Input Validation Layer**: Sanitizes all user inputs
2. **Authentication Layer**: Session-based access control
3. **Authorization Layer**: Role-based permissions
4. **Network Layer**: Rate limiting and firewall protection
5. **Data Layer**: Encrypted storage and secure connections

## Input Security

### Input Validation

All user inputs are validated using a multi-stage approach:

```python
class SecurityValidator:
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS prevention
        r'javascript:',               # JavaScript injection
        r'vbscript:',                # VBScript injection
        r'on\w+\s*=',               # Event handlers
        r'expression\s*\(',         # CSS expression
        r'import\s+os',             # Python imports
        r'subprocess\.',            # Subprocess calls
        r'eval\s*\(',              # Code evaluation
        r'exec\s*\(',              # Code execution
    ]
    
    COMMAND_BLACKLIST = [
        'rm', 'del', 'format', 'fdisk', 'mkfs',
        'dd', 'shutdown', 'reboot', 'halt',
        'passwd', 'su', 'sudo', 'chmod',
        'chown', 'iptables', 'netsh'
    ]
    
    @classmethod
    def validate_input(cls, user_input: str) -> bool:
        """Validate user input for security threats"""
        if not isinstance(user_input, str):
            return False
        
        # Check length
        if len(user_input) > 10000:
            return False
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return False
        
        return True
    
    @classmethod
    def sanitize_command(cls, command: str) -> str:
        """Sanitize shell commands for safe execution"""
        # Remove dangerous commands
        words = command.split()
        safe_words = []
        
        for word in words:
            if word.strip().lower() not in cls.COMMAND_BLACKLIST:
                # Escape shell metacharacters
                safe_word = shlex.quote(word)
                safe_words.append(safe_word)
        
        return ' '.join(safe_words)
```

### Cross-Site Scripting (XSS) Prevention

```python
from markupsafe import escape
from flask import Markup

def safe_render_response(content: str) -> str:
    """Safely render user content to prevent XSS"""
    # Escape HTML characters
    escaped_content = escape(content)
    
    # Allow safe formatting only
    safe_content = escaped_content.replace('\n', '<br>')
    
    return Markup(safe_content)
```

### SQL Injection Prevention

```python
# Always use parameterized queries
def get_user_messages(session_id: str) -> List[ChatMessage]:
    # Good: Parameterized query
    return ChatMessage.query.filter_by(session_id=session_id).all()

# Never use string concatenation
def unsafe_query(session_id: str):
    # BAD: Never do this
    query = f"SELECT * FROM chat_messages WHERE session_id = '{session_id}'"
    return db.session.execute(query)
```

## Authentication and Authorization

### Session Security

```python
class SecureSessionManager:
    def __init__(self, app):
        self.app = app
        self.session_timeout = 3600  # 1 hour
        
        # Configure secure session cookies
        app.config.update(
            SESSION_COOKIE_SECURE=True,     # HTTPS only
            SESSION_COOKIE_HTTPONLY=True,   # No JavaScript access
            SESSION_COOKIE_SAMESITE='Lax',  # CSRF protection
            PERMANENT_SESSION_LIFETIME=self.session_timeout
        )
    
    def create_session(self, session_id: str) -> Dict[str, Any]:
        """Create secure session with metadata"""
        session_data = {
            'session_id': session_id,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        
        # Store in secure session
        session.update(session_data)
        session.permanent = True
        
        return session_data
    
    def validate_session(self) -> bool:
        """Validate session security"""
        if 'session_id' not in session:
            return False
        
        # Check session timeout
        last_activity = session.get('last_activity')
        if last_activity:
            if (datetime.utcnow() - last_activity).seconds > self.session_timeout:
                self.destroy_session()
                return False
        
        # Update last activity
        session['last_activity'] = datetime.utcnow()
        return True
    
    def destroy_session(self):
        """Securely destroy session"""
        session.clear()
```

### API Key Management

```python
class APIKeyManager:
    @staticmethod
    def validate_api_access(request):
        """Validate API access for external integrations"""
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return False
        
        # Validate key format and existence
        if not re.match(r'^[a-zA-Z0-9]{32}$', api_key):
            return False
        
        # Check against stored keys (implement as needed)
        return True
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
```

## Network Security

### Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

class RateLimitManager:
    def __init__(self, app):
        self.limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["1000 per hour"]
        )
        
        # Apply specific limits to endpoints
        self.configure_limits()
    
    def configure_limits(self):
        """Configure rate limits for different endpoints"""
        
        @self.limiter.limit("60 per minute")
        @app.route('/api/chat', methods=['POST'])
        def rate_limited_chat():
            pass
        
        @self.limiter.limit("120 per minute")
        @app.route('/api/health')
        def rate_limited_health():
            pass
        
        @self.limiter.limit("10 per minute")
        @app.route('/api/admin/*')
        def rate_limited_admin():
            pass
```

### Request Filtering

```python
class RequestFilter:
    BLOCKED_USER_AGENTS = [
        'badbot', 'scanner', 'crawler'  # Add known malicious agents
    ]
    
    BLOCKED_IPS = [
        # Add known malicious IPs
    ]
    
    @staticmethod
    def filter_request(request) -> bool:
        """Filter malicious requests"""
        
        # Check user agent
        user_agent = request.headers.get('User-Agent', '').lower()
        if any(blocked in user_agent for blocked in RequestFilter.BLOCKED_USER_AGENTS):
            return False
        
        # Check IP address
        if request.remote_addr in RequestFilter.BLOCKED_IPS:
            return False
        
        # Check request size
        if request.content_length and request.content_length > 10 * 1024 * 1024:  # 10MB
            return False
        
        return True
```

## Data Security

### Encryption at Rest

```python
from cryptography.fernet import Fernet
import base64

class DataEncryption:
    def __init__(self):
        # Generate or load encryption key
        self.key = self._get_or_generate_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_generate_key(self) -> bytes:
        """Get existing key or generate new one"""
        key_env = os.environ.get('ENCRYPTION_KEY')
        if key_env:
            return base64.urlsafe_b64decode(key_env)
        else:
            # Generate new key (store securely)
            key = Fernet.generate_key()
            # Save to secure location
            return key
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data before storage"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data after retrieval"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

### Secure Database Connections

```python
# Database connection with SSL
DATABASE_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL'),
    'SQLALCHEMY_ENGINE_OPTIONS': {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'sslmode': 'require',
            'sslcert': '/path/to/client-cert.pem',
            'sslkey': '/path/to/client-key.pem',
            'sslrootcert': '/path/to/ca-cert.pem'
        }
    }
}
```

## External Service Security

### AWS Bedrock Security

```python
class BedrockSecurityManager:
    def __init__(self):
        self.session = boto3.Session()
        self.configure_security()
    
    def configure_security(self):
        """Configure secure AWS access"""
        
        # Use IAM roles instead of access keys when possible
        # Implement least privilege principle
        self.required_permissions = [
            'bedrock:InvokeModel',
            'bedrock:ListFoundationModels'
        ]
    
    def validate_model_access(self, model_id: str) -> bool:
        """Validate access to specific model"""
        allowed_models = [
            'anthropic.claude-3-5-sonnet-20241022-v2:0'
        ]
        return model_id in allowed_models
    
    def sanitize_model_input(self, input_data: Dict) -> Dict:
        """Sanitize input before sending to model"""
        sanitized = {}
        
        # Validate and sanitize each field
        if 'messages' in input_data:
            sanitized['messages'] = [
                {
                    'role': msg.get('role', 'user'),
                    'content': self._sanitize_content(msg.get('content', ''))
                }
                for msg in input_data['messages']
                if isinstance(msg, dict)
            ]
        
        # Limit token count
        sanitized['max_tokens'] = min(input_data.get('max_tokens', 1000), 4000)
        
        return sanitized
    
    def _sanitize_content(self, content: str) -> str:
        """Sanitize message content"""
        # Remove potential prompt injection attempts
        dangerous_phrases = [
            'ignore previous instructions',
            'forget your role',
            'act as if you are',
            'pretend to be'
        ]
        
        sanitized_content = content
        for phrase in dangerous_phrases:
            sanitized_content = sanitized_content.replace(phrase, '[FILTERED]')
        
        return sanitized_content[:5000]  # Limit length
```

### Perplexity API Security

```python
class PerplexitySecurityManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.rate_limiter = RateLimiter(requests_per_minute=60)
    
    def secure_search_request(self, query: str) -> Dict:
        """Make secure search request"""
        
        # Sanitize search query
        sanitized_query = self._sanitize_search_query(query)
        
        # Apply rate limiting
        if not self.rate_limiter.allow_request():
            raise Exception("Rate limit exceeded")
        
        # Make request with proper headers
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Assistant-System/1.0'
        }
        
        return {
            'query': sanitized_query,
            'headers': headers,
            'timeout': 30
        }
    
    def _sanitize_search_query(self, query: str) -> str:
        """Sanitize search query"""
        # Remove potential injection attempts
        sanitized = re.sub(r'[<>"\']', '', query)
        return sanitized[:500]  # Limit length
```

## Logging and Monitoring

### Security Event Logging

```python
import logging
from datetime import datetime

class SecurityLogger:
    def __init__(self):
        self.security_logger = logging.getLogger('security')
        handler = logging.FileHandler('security.log')
        formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.security_logger.addHandler(handler)
        self.security_logger.setLevel(logging.WARNING)
    
    def log_suspicious_activity(self, event_type: str, details: Dict):
        """Log security events"""
        self.security_logger.warning(
            f"{event_type}: {json.dumps(details)}"
        )
    
    def log_authentication_failure(self, ip_address: str, user_agent: str):
        """Log authentication failures"""
        self.log_suspicious_activity('AUTH_FAILURE', {
            'ip_address': ip_address,
            'user_agent': user_agent,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_rate_limit_exceeded(self, ip_address: str, endpoint: str):
        """Log rate limit violations"""
        self.log_suspicious_activity('RATE_LIMIT_EXCEEDED', {
            'ip_address': ip_address,
            'endpoint': endpoint,
            'timestamp': datetime.utcnow().isoformat()
        })
```

### Intrusion Detection

```python
class IntrusionDetectionSystem:
    def __init__(self):
        self.failed_attempts = defaultdict(int)
        self.blocked_ips = set()
        self.alert_threshold = 5
        self.block_duration = 3600  # 1 hour
    
    def check_request(self, request) -> bool:
        """Check request for malicious patterns"""
        ip_address = request.remote_addr
        
        # Check if IP is already blocked
        if ip_address in self.blocked_ips:
            return False
        
        # Analyze request patterns
        if self._detect_attack_patterns(request):
            self.failed_attempts[ip_address] += 1
            
            if self.failed_attempts[ip_address] >= self.alert_threshold:
                self._block_ip(ip_address)
                return False
        
        return True
    
    def _detect_attack_patterns(self, request) -> bool:
        """Detect common attack patterns"""
        patterns = [
            r'\.\./',           # Directory traversal
            r'<script',         # XSS
            r'union.*select',   # SQL injection
            r'exec.*\(',        # Code injection
        ]
        
        # Check URL and parameters
        full_url = str(request.url)
        for pattern in patterns:
            if re.search(pattern, full_url, re.IGNORECASE):
                return True
        
        return False
    
    def _block_ip(self, ip_address: str):
        """Block malicious IP address"""
        self.blocked_ips.add(ip_address)
        
        # Schedule unblock (implement with task queue)
        # schedule_task('unblock_ip', ip_address, delay=self.block_duration)
        
        # Log the block
        SecurityLogger().log_suspicious_activity('IP_BLOCKED', {
            'ip_address': ip_address,
            'reason': 'Attack pattern detected'
        })
```

## Deployment Security

### Environment Security

```bash
# Secure file permissions
chmod 600 .env
chmod 600 /path/to/ssl/certs/*
chmod 700 /path/to/application/

# Secure database files
chmod 600 /var/lib/postgresql/data/*
chown postgres:postgres /var/lib/postgresql/data/
```

### SSL/TLS Configuration

```python
# HTTPS enforcement
class HTTPSRedirect:
    def __init__(self, app):
        @app.before_request
        def force_https():
            if not request.is_secure and app.env != 'development':
                return redirect(request.url.replace('http://', 'https://'))
```

### Security Headers

```python
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
```

## Security Checklist

### Pre-Deployment

- [ ] All environment variables use secure values
- [ ] Database connections use SSL/TLS
- [ ] API keys are properly secured
- [ ] Input validation is implemented
- [ ] Rate limiting is configured
- [ ] Security headers are enabled
- [ ] Logging is configured for security events
- [ ] Backup strategy includes encryption

### Post-Deployment

- [ ] Monitor security logs regularly
- [ ] Update dependencies for security patches
- [ ] Review access logs for suspicious activity
- [ ] Test security controls periodically
- [ ] Maintain incident response procedures
- [ ] Regular security assessments

### Incident Response

1. **Detection**: Monitor logs and alerts
2. **Containment**: Block malicious traffic
3. **Eradication**: Remove threats and vulnerabilities
4. **Recovery**: Restore normal operations
5. **Lessons Learned**: Update security measures

This security framework provides comprehensive protection for the multi-agent assistant system across all layers of the application stack.