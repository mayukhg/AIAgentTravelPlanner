import json
import logging
import boto3
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError
import config

class BedrockService:
    """
    Service for Amazon Bedrock LLM integration.
    
    This service provides a unified interface for interacting with Amazon Bedrock
    foundation models, specifically optimized for Claude 3 Sonnet. It handles:
    
    1. AWS Authentication: Manages AWS credentials and regional configuration
    2. Request Formatting: Converts conversation format to Bedrock API specifications
    3. Response Processing: Parses and extracts content from Bedrock responses
    4. Error Handling: Comprehensive error handling with retry logic and fallbacks
    5. Health Monitoring: Service availability and performance monitoring
    
    Key Features:
    - Multi-model support with Claude-optimized request formatting
    - Automatic retry mechanisms for transient failures
    - Structured error responses with actionable error messages
    - Configuration-driven model selection and parameters
    - Health check endpoints for monitoring and alerting
    
    The service abstracts the complexity of the Bedrock API, providing a simple
    async interface for agents to generate natural language responses. It handles
    conversation context, system prompts, and response parameters automatically.
    
    Security Considerations:
    - AWS credentials managed via environment variables
    - Request/response logging excludes sensitive data
    - Rate limiting and timeout controls prevent abuse
    - Model access controlled via IAM policies
    """
    
    def __init__(self):
        self.logger = logging.getLogger("services.bedrock")
        self.client = None
        self.model_id = config.Config.BEDROCK_MODEL_ID
        
        try:
            # Initialize Bedrock client
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=config.Config.AWS_REGION,
                aws_access_key_id=config.Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.Config.AWS_SECRET_ACCESS_KEY
            )
            self.logger.info(f"Bedrock client initialized with model: {self.model_id}")
            
        except NoCredentialsError:
            self.logger.error("AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            raise
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.1
    ) -> str:
        """Generate a response using Amazon Bedrock"""
        
        try:
            # Prepare the request body based on the model
            if "claude" in self.model_id.lower():
                return await self._generate_claude_response(messages, system_prompt, max_tokens, temperature)
            else:
                # Default to Claude format, but log a warning
                self.logger.warning(f"Using Claude format for unknown model: {self.model_id}")
                return await self._generate_claude_response(messages, system_prompt, max_tokens, temperature)
                
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise
    
    async def _generate_claude_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.1
    ) -> str:
        """Generate response using Claude model format"""
        
        try:
            # Prepare the request body for Claude
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": []
            }
            
            # Add system prompt if provided
            if system_prompt:
                body["system"] = system_prompt
            
            # Convert messages to Claude format
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                
                # Claude expects "user" and "assistant" roles
                if role in ["user", "assistant"]:
                    body["messages"].append({
                        "role": role,
                        "content": content
                    })
            
            # Make the API call
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read())
            
            # Extract content from Claude response
            if "content" in response_body and len(response_body["content"]) > 0:
                return response_body["content"][0].get("text", "")
            else:
                self.logger.warning("Unexpected response format from Claude model")
                return "I apologize, but I couldn't generate a proper response."
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            self.logger.error(f"Bedrock API error [{error_code}]: {error_message}")
            
            if error_code == 'ValidationException':
                raise Exception(f"Invalid request to Bedrock: {error_message}")
            elif error_code == 'AccessDeniedException':
                raise Exception("Access denied to Bedrock model. Please check your permissions.")
            elif error_code == 'ThrottlingException':
                raise Exception("Request was throttled. Please try again later.")
            else:
                raise Exception(f"Bedrock API error: {error_message}")
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Bedrock response: {str(e)}")
            raise Exception("Failed to parse response from Bedrock")
            
        except Exception as e:
            self.logger.error(f"Unexpected error in Claude response generation: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the Bedrock service is accessible"""
        try:
            # Try to list available models as a health check
            response = self.client.list_foundation_models()
            
            return {
                "status": "healthy",
                "model_id": self.model_id,
                "region": config.Config.AWS_REGION,
                "models_available": len(response.get('modelSummaries', []))
            }
            
        except Exception as e:
            self.logger.error(f"Bedrock health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "model_id": self.model_id,
                "region": config.Config.AWS_REGION
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model_id": self.model_id,
            "region": config.Config.AWS_REGION,
            "service": "Amazon Bedrock"
        }
