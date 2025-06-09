import os

class Config:
    # AWS Bedrock Configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    
    # Bedrock Model Configuration
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
