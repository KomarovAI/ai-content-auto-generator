#!/usr/bin/env python3
"""
Text Generator - AI-powered text content generation
"""

import asyncio
from typing import Dict, Optional
from loguru import logger


class TextGenerator:
    """Generate text content using multiple AI APIs."""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        logger.info("TextGenerator initialized")
    
    async def generate(self,
                      prompt: str,
                      context: Optional[Dict] = None,
                      strategy: str = 'round_robin') -> str:
        """
        Generate text content.
        
        Args:
            prompt: Text generation prompt
            context: Additional context (page type, style, etc.)
            strategy: API selection strategy
            
        Returns:
            Generated text
        """
        # Select API
        api_name = self.api_manager.get_available_api('text', strategy)
        
        if not api_name:
            raise Exception("No text generation APIs available")
        
        # Prepare payload
        payload = self._prepare_payload(prompt, context, api_name)
        
        # Call API
        response = await self.api_manager.call_api(api_name, 'text', payload)
        
        # Extract text from response
        text = self._extract_text(response, api_name)
        
        logger.info(f"Generated {len(text)} characters using {api_name}")
        return text
    
    def _prepare_payload(self, prompt: str, context: Optional[Dict], api_name: str) -> Dict:
        """Prepare API-specific payload."""
        base_payload = {'prompt': prompt}
        
        if context:
            base_payload['context'] = context
        
        # API-specific formatting
        if api_name == 'openai':
            return {
                'model': 'gpt-4',
                'messages': [{'role': 'user', 'content': prompt}]
            }
        elif api_name == 'gemini':
            return {
                'model': 'gemini-flash',
                'prompt': prompt
            }
        elif api_name == 'anthropic':
            return {
                'model': 'claude-3-sonnet',
                'messages': [{'role': 'user', 'content': prompt}]
            }
        
        return base_payload
    
    def _extract_text(self, response: Dict, api_name: str) -> str:
        """Extract text from API-specific response."""
        # TODO: Implement proper extraction for each API
        return response.get('data', '')