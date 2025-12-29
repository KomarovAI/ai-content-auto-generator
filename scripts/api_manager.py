#!/usr/bin/env python3
"""
API Manager - Multi-API Orchestration & Limits Management

Handles API key rotation, quota tracking, and intelligent request distribution.
"""

import time
from typing import Dict, List, Optional
from collections import defaultdict
from loguru import logger
import asyncio


class APIManager:
    """
    Manages multiple AI API connections with smart limits tracking.
    
    Features:
    - Automatic API rotation
    - Quota management
    - Rate limiting
    - Failover handling
    - Hugging Face priority for images
    """
    
    def __init__(self, config: Dict):
        """Initialize API manager with configuration."""
        self.config = config
        self.api_keys = config.get('api_keys', {})
        self.limits = config.get('limits', {})
        
        # Track usage per API
        self.usage = defaultdict(lambda: {'count': 0, 'reset_time': self._get_reset_time()})
        
        # Available APIs by type
        self.text_apis = ['openai', 'gemini', 'anthropic']
        # HF not in list - handled directly in ImageGenerator
        self.image_apis = ['imagen', 'openai', 'stability', 'adobe_firefly']
        
        # Current rotation index
        self.text_index = 0
        self.image_index = 0
        
        logger.info("APIManager initialized with {} text and {} image APIs (+HF)".format(
            len(self.text_apis), len(self.image_apis)
        ))
    
    def _get_reset_time(self) -> float:
        """Get next daily reset time (midnight)."""
        now = time.time()
        day_seconds = 86400
        seconds_since_midnight = now % day_seconds
        return now + (day_seconds - seconds_since_midnight)
    
    def _check_and_reset_usage(self, api_name: str):
        """Reset usage counter if daily limit has reset."""
        current_time = time.time()
        if current_time >= self.usage[api_name]['reset_time']:
            self.usage[api_name]['count'] = 0
            self.usage[api_name]['reset_time'] = self._get_reset_time()
            logger.info(f"Usage counter reset for {api_name}")
    
    def get_available_api(self, api_type: str, strategy: str = 'round_robin') -> Optional[str]:
        """
        Get next available API based on strategy and limits.
        
        Args:
            api_type: 'text' or 'image'
            strategy: 'round_robin', 'priority', 'cost_optimized'
            
        Returns:
            API name or None if all exhausted
        """
        api_list = self.text_apis if api_type == 'text' else self.image_apis
        
        if strategy == 'round_robin':
            return self._round_robin_select(api_list, api_type)
        elif strategy == 'priority':
            return self._priority_select(api_list)
        elif strategy == 'cost_optimized':
            return self._cost_optimized_select(api_list)
        else:
            return api_list[0] if api_list else None
    
    def _round_robin_select(self, api_list: List[str], api_type: str) -> Optional[str]:
        """Select API using round-robin with quota checking."""
        attempts = 0
        max_attempts = len(api_list)
        
        while attempts < max_attempts:
            # Get current index
            if api_type == 'text':
                index = self.text_index
                self.text_index = (self.text_index + 1) % len(api_list)
            else:
                index = self.image_index
                self.image_index = (self.image_index + 1) % len(api_list)
            
            api_name = api_list[index]
            
            # Check if API has quota remaining
            if self._has_quota(api_name, api_type):
                logger.debug(f"Selected API: {api_name} (round-robin)")
                return api_name
            
            attempts += 1
        
        logger.warning(f"All {api_type} APIs exhausted")
        return None
    
    def _priority_select(self, api_list: List[str]) -> Optional[str]:
        """Select highest priority API with available quota."""
        # Priority order: cheaper/free APIs first
        priority_order = {
            'gemini': 1,      # Cheap
            'openai': 2,      # Mid-cost
            'anthropic': 3,   # Expensive
            'imagen': 1,      # Free (within limits)
            'stability': 2,
            'adobe_firefly': 3
        }
        
        sorted_apis = sorted(api_list, key=lambda x: priority_order.get(x, 999))
        
        for api_name in sorted_apis:
            if self._has_quota(api_name, 'any'):
                logger.debug(f"Selected API: {api_name} (priority)")
                return api_name
        
        return None
    
    def _cost_optimized_select(self, api_list: List[str]) -> Optional[str]:
        """Select cheapest API with available quota."""
        # Cost per request (approximate USD)
        cost_map = {
            'gemini': 0.00005,     # Flash 2.0
            'openai': 0.002,       # GPT-4o mini
            'anthropic': 0.003,    # Claude
            'imagen': 0.0,         # Free tier
            'stability': 0.004,
            'adobe_firefly': 0.0   # Free tier
        }
        
        sorted_apis = sorted(api_list, key=lambda x: cost_map.get(x, 999))
        
        for api_name in sorted_apis:
            if self._has_quota(api_name, 'any'):
                logger.debug(f"Selected API: {api_name} (cost-optimized)")
                return api_name
        
        return None
    
    def _has_quota(self, api_name: str, api_type: str) -> bool:
        """Check if API has remaining quota."""
        self._check_and_reset_usage(api_name)
        
        # Check unlimited APIs
        if api_name == 'imagen' and self.limits.get('imagen', {}).get('unlimited'):
            return True
        
        # Get limit for this API
        api_limits = self.limits.get(api_name, {})
        
        if api_type == 'text':
            limit = api_limits.get('text', api_limits.get('flash', 0))
        elif api_type == 'image':
            limit = api_limits.get('image', api_limits.get('daily', 0))
        else:
            # Get max of all limits
            limit = max(api_limits.values()) if api_limits else 0
        
        current_usage = self.usage[api_name]['count']
        has_quota = current_usage < limit
        
        if not has_quota:
            logger.warning(f"{api_name} quota exhausted: {current_usage}/{limit}")
        
        return has_quota
    
    def record_usage(self, api_name: str, count: int = 1):
        """Record API usage."""
        self.usage[api_name]['count'] += count
        logger.debug(f"{api_name} usage: {self.usage[api_name]['count']}")
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics for all APIs."""
        stats = {}
        
        for api_name in set(self.text_apis + self.image_apis):
            self._check_and_reset_usage(api_name)
            
            api_limits = self.limits.get(api_name, {})
            max_limit = max(api_limits.values()) if api_limits else 0
            
            stats[api_name] = {
                'used': self.usage[api_name]['count'],
                'limit': max_limit,
                'remaining': max(0, max_limit - self.usage[api_name]['count']),
                'reset_in': int(self.usage[api_name]['reset_time'] - time.time())
            }
        
        return stats
    
    async def call_api(self, 
                       api_name: str, 
                       api_type: str,
                       payload: Dict) -> Dict:
        """
        Make API call with retry logic.
        
        Args:
            api_name: Name of the API to call
            api_type: 'text' or 'image'
            payload: Request payload
            
        Returns:
            API response
        """
        max_retries = self.config.get('distribution', {}).get('retry_attempts', 3)
        
        for attempt in range(max_retries):
            try:
                # TODO: Implement actual API calls
                logger.info(f"Calling {api_name} API (attempt {attempt + 1}/{max_retries})")
                
                # Simulate API call
                await asyncio.sleep(0.1)
                
                # Record usage
                self.record_usage(api_name)
                
                return {'success': True, 'data': 'Generated content'}
                
            except Exception as e:
                logger.error(f"{api_name} API call failed: {e}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
        
        raise Exception(f"All retry attempts failed for {api_name}")


if __name__ == "__main__":
    # Test API manager
    config = {
        'api_keys': {'openai': 'test', 'gemini': 'test', 'huggingface': 'test'},
        'limits': {
            'openai': {'text': 1000, 'image': 50},
            'gemini': {'flash': 1500},
            'imagen': {'daily': 100}
        },
        'distribution': {
            'retry_attempts': 3,
            'timeout': 30
        }
    }
    
    manager = APIManager(config)
    
    # Test API selection
    for i in range(10):
        api = manager.get_available_api('text', 'round_robin')
        print(f"Request {i+1}: {api}")
        if api:
            manager.record_usage(api)
    
    # Print stats
    print("\nUsage Stats:")
    for api, stats in manager.get_usage_stats().items():
        print(f"{api}: {stats}")
