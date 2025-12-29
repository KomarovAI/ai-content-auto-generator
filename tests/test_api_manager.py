#!/usr/bin/env python3
"""
Tests for API Manager
"""

import pytest
import asyncio
from scripts.api_manager import APIManager


@pytest.fixture
def api_config():
    """Test configuration."""
    return {
        'api_keys': {
            'openai': 'test-key-1',
            'gemini': 'test-key-2',
            'anthropic': 'test-key-3'
        },
        'limits': {
            'openai': {'text': 100, 'image': 50},
            'gemini': {'flash': 150, 'pro': 50},
            'anthropic': {'text': 100}
        },
        'distribution': {
            'retry_attempts': 3,
            'timeout': 30
        }
    }


@pytest.fixture
def api_manager(api_config):
    """Create API manager instance."""
    return APIManager(api_config)


class TestAPIManager:
    """Test API Manager functionality."""
    
    def test_initialization(self, api_manager):
        """Test API manager initialization."""
        assert api_manager is not None
        assert len(api_manager.text_apis) > 0
        assert len(api_manager.image_apis) > 0
    
    def test_round_robin_selection(self, api_manager):
        """Test round-robin API selection."""
        # Get multiple APIs
        api1 = api_manager.get_available_api('text', 'round_robin')
        api2 = api_manager.get_available_api('text', 'round_robin')
        api3 = api_manager.get_available_api('text', 'round_robin')
        
        # Should rotate through APIs
        assert api1 is not None
        assert api2 is not None
        assert api3 is not None
    
    def test_quota_checking(self, api_manager):
        """Test quota management."""
        api_name = 'openai'
        
        # Initially should have quota
        assert api_manager._has_quota(api_name, 'text')
        
        # Record usage up to limit
        limit = api_manager.limits['openai']['text']
        api_manager.record_usage(api_name, limit)
        
        # Should be exhausted
        assert not api_manager._has_quota(api_name, 'text')
    
    def test_usage_stats(self, api_manager):
        """Test usage statistics."""
        stats = api_manager.get_usage_stats()
        
        assert isinstance(stats, dict)
        assert 'openai' in stats
        assert 'used' in stats['openai']
        assert 'limit' in stats['openai']
        assert 'remaining' in stats['openai']
    
    def test_priority_selection(self, api_manager):
        """Test priority-based selection."""
        api = api_manager.get_available_api('text', 'priority')
        
        # Should select highest priority API with quota
        assert api is not None
        assert api in api_manager.text_apis
    
    def test_cost_optimized_selection(self, api_manager):
        """Test cost-optimized selection."""
        api = api_manager.get_available_api('text', 'cost_optimized')
        
        # Should select cheapest API with quota
        assert api is not None
        assert api in api_manager.text_apis
    
    @pytest.mark.asyncio
    async def test_api_call(self, api_manager):
        """Test API call with retry logic."""
        result = await api_manager.call_api(
            'openai',
            'text',
            {'prompt': 'test'}
        )
        
        assert result is not None
        assert 'success' in result or 'data' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])