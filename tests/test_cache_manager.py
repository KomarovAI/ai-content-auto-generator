#!/usr/bin/env python3
"""
Tests for Cache Manager
"""

import pytest
import asyncio
from scripts.cache_manager import CacheManager


@pytest.fixture
def cache_config():
    """Test cache configuration."""
    return {
        'enabled': True,
        'similarity_threshold': 0.85,
        'backend': 'memory'
    }


@pytest.fixture
def cache_manager(cache_config):
    """Create cache manager instance."""
    return CacheManager(cache_config)


class TestCacheManager:
    """Test Cache Manager functionality."""
    
    def test_initialization(self, cache_manager):
        """Test cache initialization."""
        assert cache_manager is not None
        assert cache_manager.enabled is True
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve(self, cache_manager):
        """Test storing and retrieving from cache."""
        query = "test query"
        content = "test content"
        
        # Store
        await cache_manager.store(query, content)
        
        # Retrieve exact match
        result = await cache_manager.get_similar(query)
        assert result == content
    
    @pytest.mark.asyncio
    async def test_cache_miss(self, cache_manager):
        """Test cache miss."""
        result = await cache_manager.get_similar("nonexistent query")
        assert result is None
    
    def test_set_threshold(self, cache_manager):
        """Test threshold update."""
        new_threshold = 0.9
        cache_manager.set_threshold(new_threshold)
        assert cache_manager.threshold == new_threshold
    
    def test_clear_cache(self, cache_manager):
        """Test cache clearing."""
        cache_manager.cache['test'] = 'data'
        cache_manager.clear()
        assert len(cache_manager.cache) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])