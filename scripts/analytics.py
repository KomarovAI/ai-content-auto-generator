#!/usr/bin/env python3
"""
Analytics Engine - A/B testing and metrics tracking
"""

from typing import List, Dict
from loguru import logger
import random


class AnalyticsEngine:
    """A/B testing and analytics tracking."""
    
    def __init__(self, config: dict):
        self.config = config
        self.tests = {}
        
        logger.info("AnalyticsEngine initialized")
    
    def create_test(self, page_id: str, num_variants: int, success_metric: str):
        """Create new A/B test."""
        test_id = f"{page_id}_{success_metric}"
        
        self.tests[test_id] = {
            'page_id': page_id,
            'variants': num_variants,
            'metric': success_metric,
            'results': {i: {'views': 0, 'conversions': 0} for i in range(num_variants)},
            'winner': None
        }
        
        logger.info(f"A/B test created: {test_id} with {num_variants} variants")
    
    def get_variant(self, page_id: str) -> int:
        """Get variant for user (random assignment)."""
        # Find test for this page
        test = None
        for test_id, t in self.tests.items():
            if t['page_id'] == page_id:
                test = t
                break
        
        if not test:
            return 0
        
        # Random assignment
        return random.randint(0, test['variants'] - 1)
    
    def record_event(self, page_id: str, variant: int, event_type: str):
        """Record analytics event."""
        # Find test
        for test in self.tests.values():
            if test['page_id'] == page_id:
                if event_type == 'view':
                    test['results'][variant]['views'] += 1
                elif event_type == 'conversion':
                    test['results'][variant]['conversions'] += 1
                break
    
    def analyze_test(self, page_id: str) -> Dict:
        """Analyze test results and determine winner."""
        # Find test
        test = None
        for t in self.tests.values():
            if t['page_id'] == page_id:
                test = t
                break
        
        if not test:
            return {}
        
        # Calculate conversion rates
        rates = {}
        for variant, results in test['results'].items():
            views = results['views']
            conversions = results['conversions']
            rate = conversions / views if views > 0 else 0
            rates[variant] = rate
        
        # Find winner
        winner = max(rates, key=rates.get)
        test['winner'] = winner
        
        logger.info(f"Test analysis for {page_id}: Winner is variant {winner}")
        
        return {
            'winner': winner,
            'rates': rates,
            'results': test['results']
        }