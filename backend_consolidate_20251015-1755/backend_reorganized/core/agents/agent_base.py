# core/app/agents/agent_base.py (mejoras)
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
import json
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class AgentBase(ABC):
    """Base class for all AI agents using DeepSeek API - IMPROVED VERSION"""
    
    def __init__(self, name: str):
        self.name = name
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        self.max_retries = 3
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def call_deepseek(self, messages: list, temperature: float = 0.7, max_tokens: int = 4000, 
                     response_format: Optional[Dict] = None) -> str:
        """Make API call to DeepSeek with retries and structured output support"""
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        # Support for structured output
        if response_format:
            payload["response_format"] = response_format
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions", 
                json=payload, 
                headers=headers, 
                timeout=120  # Increased timeout for complex projects
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract token usage for metrics
            token_usage = result.get("usage", {})
            self.log_activity(f"Token usage: {token_usage.get('total_tokens', 0)} tokens")
            
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.Timeout:
            logger.error(f"DeepSeek API timeout for {self.name}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API request error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {self.name}: {e}")
            raise
    
    def generate_structured_response(self, prompt: str, context: str = "", 
                                  schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate AI response with optional JSON schema enforcement"""
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        
        messages.append({"role": "user", "content": prompt})
        
        response_format = {"type": "json_object"} if schema else None
        
        response = self.call_deepseek(
            messages, 
            temperature=0.3,  # Lower temperature for structured data
            response_format=response_format
        )
        
        try:
            return json.loads(response) if schema else response
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON response from {self.name}")
            # Fallback: try to extract JSON from text
            return self._extract_json_from_text(response)
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Fallback method to extract JSON from text response"""
        try:
            # Look for JSON pattern in the text
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = text[start:end]
                return json.loads(json_str)
        except:
            pass
        return {"raw_response": text}
    
    @abstractmethod
    def run(self, project_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method for the agent"""
        pass
        
    def log_activity(self, message: str, level: str = "info"):
        """Enhanced logging with levels"""
        log_method = getattr(logger, level, logger.info)
        log_method(f"[{self.name}] {message}")