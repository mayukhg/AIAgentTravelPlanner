import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional
import config

class PerplexityService:
    """Service for Perplexity API integration"""
    
    def __init__(self):
        self.logger = logging.getLogger("services.perplexity")
        self.api_key = config.Config.PERPLEXITY_API_KEY
        self.model = config.Config.PERPLEXITY_MODEL
        self.base_url = "https://api.perplexity.ai/chat/completions"
        
        if not self.api_key:
            self.logger.warning("Perplexity API key not found. Search functionality will be limited.")
    
    async def search(
        self,
        query: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = 1000,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """Perform a search using Perplexity API"""
        
        if not self.api_key:
            return {
                "success": False,
                "error": "Perplexity API key not configured",
                "content": "I'm unable to perform web searches at the moment. Please provide your search query and I'll do my best to help with the information I have."
            }
        
        try:
            # Prepare messages
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user", 
                "content": query
            })
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "return_images": False,
                "return_related_questions": False,
                "search_recency_filter": "month",
                "top_k": 0,
                "stream": False,
                "presence_penalty": 0,
                "frequency_penalty": 1
            }
            
            # Make the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_perplexity_response(data)
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Perplexity API error {response.status}: {error_text}")
                        
                        return {
                            "success": False,
                            "error": f"API request failed with status {response.status}",
                            "content": "I encountered an error while searching for information. Please try again later."
                        }
                        
        except asyncio.TimeoutError:
            self.logger.error("Perplexity API request timed out")
            return {
                "success": False,
                "error": "Request timed out",
                "content": "The search request timed out. Please try again with a more specific query."
            }
            
        except Exception as e:
            self.logger.error(f"Error making Perplexity API request: {str(e)}")
            return {
                "success": False,
                "error": f"Request failed: {str(e)}",
                "content": "I encountered an error while searching. Please try rephrasing your query."
            }
    
    def _parse_perplexity_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the response from Perplexity API"""
        try:
            choices = data.get('choices', [])
            if not choices:
                return {
                    "success": False,
                    "error": "No response choices returned",
                    "content": "I didn't receive a proper response from the search service."
                }
            
            # Get the main response content
            message = choices[0].get('message', {})
            content = message.get('content', '')
            
            # Get citations if available
            citations = data.get('citations', [])
            
            # Get usage information
            usage = data.get('usage', {})
            
            return {
                "success": True,
                "content": content,
                "citations": citations,
                "usage": usage,
                "model": data.get('model', self.model)
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing Perplexity response: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to parse response: {str(e)}",
                "content": "I received a response but couldn't parse it properly."
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the Perplexity service is accessible"""
        if not self.api_key:
            return {
                "status": "unhealthy",
                "error": "API key not configured",
                "service": "Perplexity"
            }
        
        try:
            # Simple test query
            result = await self.search(
                "What is 2+2?",
                system_prompt="Respond with just the answer.",
                max_tokens=50
            )
            
            if result.get('success'):
                return {
                    "status": "healthy",
                    "model": self.model,
                    "service": "Perplexity"
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": result.get('error', 'Unknown error'),
                    "service": "Perplexity"
                }
                
        except Exception as e:
            self.logger.error(f"Perplexity health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "service": "Perplexity"
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the Perplexity service"""
        return {
            "service": "Perplexity",
            "model": self.model,
            "api_configured": bool(self.api_key),
            "base_url": self.base_url
        }
