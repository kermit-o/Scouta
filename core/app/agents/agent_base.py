import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)

class AgentBase(ABC):
    """Base class for all AI agents using DeepSeek API"""
    
    def __init__(self, name: str):
        self.name = name
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        
    def call_deepseek(self, messages: list, temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """Make API call to DeepSeek"""
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
        
        try:
            response = requests.post(f"{self.api_base}/chat/completions", 
                                   json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            raise
    
    @abstractmethod
    def run(self, project_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method for the agent"""
        pass
        
    def log_activity(self, message: str):
        """Log agent activity"""
        logger.info(f"[{self.name}] {message}")

    def generate_ai_response(self, prompt: str, context: str = "", temperature: float = 0.7) -> str:
        """Helper method to generate AI responses"""
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        
        return self.call_deepseek(messages, temperature)
