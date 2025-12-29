#!/usr/bin/env python3
"""
AI Content Auto-Generator - Main Orchestrator

Distributed AI content generation system with multi-API orchestration,
smart limits management, and self-optimization.
"""

import yaml
import asyncio
from typing import List, Dict, Optional
from pathlib import Path
from loguru import logger

from api_manager import APIManager
from text_generator import TextGenerator
from image_generator import ImageGenerator
from cache_manager import CacheManager
from analytics import AnalyticsEngine
from optimizer import ContentOptimizer


class ContentGenerator:
    """
    Main content generation orchestrator.
    
    Coordinates multiple AI services, manages limits, implements caching,
    and optimizes content based on user metrics.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the content generator."""
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.api_manager = APIManager(self.config)
        self.text_gen = TextGenerator(self.api_manager)
        self.image_gen = ImageGenerator(self.api_manager)
        self.cache = CacheManager(self.config.get('cache', {}))
        self.analytics = AnalyticsEngine(self.config.get('ab_testing', {}))
        self.optimizer = ContentOptimizer(self.config.get('optimization', {}))
        
        logger.info("ContentGenerator initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    async def generate_text(self, 
                           prompt: str, 
                           context: Optional[Dict] = None,
                           use_cache: bool = True) -> str:
        """
        Generate text content with automatic API selection.
        
        Args:
            prompt: Text generation prompt
            context: Additional context (page type, style, etc.)
            use_cache: Whether to use semantic caching
            
        Returns:
            Generated text content
        """
        # Check cache first
        if use_cache:
            cached = await self.cache.get_similar(prompt)
            if cached:
                logger.info(f"Cache hit for prompt: {prompt[:50]}...")
                return cached
        
        # Generate new content
        try:
            result = await self.text_gen.generate(
                prompt=prompt,
                context=context,
                strategy=self.config['distribution']['mode']
            )
            
            # Cache result
            if use_cache:
                await self.cache.store(prompt, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            # Fallback strategy
            return await self._handle_fallback('text', prompt)
    
    async def generate_images(self,
                            prompts: List[str],
                            style: str = "photorealistic",
                            use_cache: bool = True) -> List[str]:
        """
        Generate multiple images with distributed API calls.
        
        Args:
            prompts: List of image generation prompts
            style: Image style (photorealistic, artistic, etc.)
            use_cache: Whether to use caching
            
        Returns:
            List of image URLs or paths
        """
        results = []
        
        for prompt in prompts:
            # Check cache
            if use_cache:
                cached = await self.cache.get_similar(f"img:{prompt}")
                if cached:
                    results.append(cached)
                    continue
            
            # Generate new image
            try:
                image_url = await self.image_gen.generate(
                    prompt=prompt,
                    style=style,
                    strategy=self.config['distribution']['mode']
                )
                
                results.append(image_url)
                
                # Cache result
                if use_cache:
                    await self.cache.store(f"img:{prompt}", image_url)
                    
            except Exception as e:
                logger.error(f"Image generation failed for '{prompt}': {e}")
                # Fallback
                fallback = await self._handle_fallback('image', prompt)
                results.append(fallback)
        
        return results
    
    async def generate_batch(self,
                           pages: List[str],
                           mode: str = "auto") -> Dict:
        """
        Generate content for multiple pages in batch.
        
        Args:
            pages: List of page identifiers
            mode: Generation mode (auto, parallel, sequential)
            
        Returns:
            Dictionary with generation results per page
        """
        logger.info(f"Starting batch generation for {len(pages)} pages")
        
        results = {}
        
        if mode == "parallel":
            # Generate all pages concurrently
            tasks = [self._generate_page(page) for page in pages]
            page_results = await asyncio.gather(*tasks)
            results = dict(zip(pages, page_results))
        else:
            # Sequential generation with API rotation
            for page in pages:
                results[page] = await self._generate_page(page)
        
        logger.info(f"Batch generation completed: {len(results)} pages")
        return results
    
    async def _generate_page(self, page_id: str) -> Dict:
        """Generate all content for a single page."""
        # Load page config
        page_config = self._load_page_config(page_id)
        
        result = {
            'page_id': page_id,
            'text': {},
            'images': {},
            'meta': {}
        }
        
        # Generate texts
        for text_key, prompt in page_config.get('texts', {}).items():
            result['text'][text_key] = await self.generate_text(prompt)
        
        # Generate images
        image_prompts = list(page_config.get('images', {}).values())
        if image_prompts:
            images = await self.generate_images(image_prompts)
            result['images'] = dict(zip(page_config['images'].keys(), images))
        
        # Generate SEO meta
        if self.config['seo']['auto_meta_generation']:
            result['meta'] = await self._generate_seo_meta(page_config)
        
        return result
    
    def _load_page_config(self, page_id: str) -> Dict:
        """Load page configuration from templates."""
        # TODO: Implement proper page config loading
        return {
            'texts': {},
            'images': {},
            'style': 'default'
        }
    
    async def _generate_seo_meta(self, page_config: Dict) -> Dict:
        """Generate SEO metadata for a page."""
        # TODO: Implement SEO generation
        return {
            'title': '',
            'description': '',
            'keywords': []
        }
    
    async def _handle_fallback(self, content_type: str, prompt: str) -> str:
        """Handle fallback when primary generation fails."""
        fallback_order = self.config['fallback']['cascade']
        
        for fallback in fallback_order[1:]:  # Skip primary
            if fallback == 'cache':
                cached = await self.cache.get_similar(prompt, threshold=0.7)
                if cached:
                    return cached
            elif fallback == 'template':
                # Return placeholder content
                return f"[{content_type.upper()}_PLACEHOLDER]"
        
        return ""
    
    def enable_cache(self, similarity_threshold: float = 0.85):
        """Enable semantic caching with custom threshold."""
        self.cache.set_threshold(similarity_threshold)
        logger.info(f"Cache enabled with threshold {similarity_threshold}")
    
    def create_ab_test(self, page: str, variants: int, metric: str):
        """Create A/B test for a page."""
        self.analytics.create_test(
            page_id=page,
            num_variants=variants,
            success_metric=metric
        )
        logger.info(f"A/B test created for {page} with {variants} variants")
    
    def enable_optimization(self, metrics: List[str], optimization_interval: str):
        """Enable auto-optimization based on metrics."""
        self.optimizer.enable(
            metrics=metrics,
            interval=optimization_interval
        )
        logger.info(f"Optimization enabled with metrics: {metrics}")


if __name__ == "__main__":
    # Example usage
    generator = ContentGenerator()
    
    # Generate single text
    text = asyncio.run(generator.generate_text(
        "Write a compelling restaurant description"
    ))
    print(f"Generated text: {text}")
    
    # Generate images
    images = asyncio.run(generator.generate_images([
        "modern restaurant interior",
        "delicious food plating"
    ]))
    print(f"Generated images: {images}")