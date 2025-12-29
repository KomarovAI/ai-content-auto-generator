#!/usr/bin/env python3
"""
Image Generator - AI-powered image generation with Hugging Face primary
"""

import asyncio
import os
import base64
import aiohttp
from typing import Optional
from loguru import logger


class ImageGenerator:
    """Generate images using multiple AI APIs with HF priority."""
    
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.hf_api_key = os.getenv('HUGGINGFACE_FULLAPI')
        self.hf_models = [
            'stabilityai/stable-diffusion-xl-base-1.0',
            'black-forest-labs/FLUX.1-dev',
            'prompthero/openjourney-v4'
        ]
        logger.info("ImageGenerator initialized with Hugging Face")
    
    async def generate(self,
                      prompt: str,
                      style: str = 'photorealistic',
                      strategy: str = 'round_robin') -> str:
        """
        Generate image with HF primary + fallback chain.
        
        Args:
            prompt: Image generation prompt
            style: Image style
            strategy: API selection strategy
            
        Returns:
            Image URL or base64 data
        """
        enhanced_prompt = self._enhance_prompt(prompt, style)
        
        # Try Hugging Face first (free, unlimited)
        if self.hf_api_key:
            try:
                return await self._generate_hf(enhanced_prompt)
            except Exception as e:
                logger.warning(f"HF generation failed: {e}, falling back to other APIs")
        
        # Fallback to managed APIs
        api_name = self.api_manager.get_available_api('image', strategy)
        
        if not api_name:
            raise Exception("No image generation APIs available")
        
        payload = self._prepare_payload(enhanced_prompt, api_name)
        response = await self.api_manager.call_api(api_name, 'image', payload)
        image_url = self._extract_url(response, api_name)
        
        logger.info(f"Generated image using {api_name}: {image_url}")
        return image_url
    
    async def _generate_hf(self, prompt: str, model_index: int = 0) -> str:
        """
        Generate image using Hugging Face Inference API.
        
        Tries multiple models with exponential backoff.
        """
        if model_index >= len(self.hf_models):
            raise Exception("All HF models exhausted")
        
        model = self.hf_models[model_index]
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        headers = {
            'Authorization': f'Bearer {self.hf_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {'inputs': prompt}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=payload, timeout=60) as resp:
                    if resp.status == 503:
                        # Model loading, wait and retry
                        logger.info(f"HF model {model} loading, waiting 20s...")
                        await asyncio.sleep(20)
                        return await self._generate_hf(prompt, model_index)
                    
                    if resp.status == 429:
                        # Rate limit, try next model
                        logger.warning(f"HF rate limit on {model}, trying next")
                        return await self._generate_hf(prompt, model_index + 1)
                    
                    if resp.status != 200:
                        error = await resp.text()
                        raise Exception(f"HF API error {resp.status}: {error}")
                    
                    # Get image bytes
                    image_bytes = await resp.read()
                    
                    # Convert to base64 for storage/display
                    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                    
                    logger.info(f"✅ Generated image via HF ({model}, {len(image_bytes)} bytes)")
                    return f"data:image/png;base64,{image_b64}"
        
        except asyncio.TimeoutError:
            logger.warning(f"HF timeout on {model}, trying next")
            return await self._generate_hf(prompt, model_index + 1)
        except Exception as e:
            logger.error(f"HF generation error: {e}")
            raise
    
    def _prepare_payload(self, prompt: str, api_name: str) -> dict:
        """Prepare API-specific payload."""
        if api_name == 'openai':
            return {
                'model': 'dall-e-3',
                'prompt': prompt,
                'size': '1024x1024',
                'quality': 'standard'
            }
        elif api_name == 'imagen':
            return {
                'prompt': prompt,
                'aspectRatio': '1:1',
                'sampleCount': 1
            }
        elif api_name == 'stability':
            return {
                'text_prompts': [{'text': prompt, 'weight': 1}],
                'cfg_scale': 7,
                'samples': 1,
                'steps': 30
            }
        elif api_name == 'adobe_firefly':
            return {
                'prompt': prompt,
                'contentClass': 'photo',
                'size': {'width': 1024, 'height': 1024}
            }
        
        return {'prompt': prompt}
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt with style modifiers."""
        style_modifiers = {
            'photorealistic': ', highly detailed, photorealistic, sharp focus, 8k uhd, professional photography',
            'artistic': ', artistic interpretation, creative, expressive, stylized artwork',
            'minimalist': ', clean composition, minimalist design, simple elegance',
            'professional': ', professional quality, corporate style, polished, modern design',
            'vibrant': ', vibrant colors, high contrast, dynamic composition, eye-catching',
            'cinematic': ', cinematic lighting, dramatic atmosphere, movie-like quality'
        }
        
        modifier = style_modifiers.get(style, '')
        return f"{prompt}{modifier}"
    
    def _extract_url(self, response: dict, api_name: str) -> str:
        """Extract image URL from API response."""
        if api_name == 'openai':
            return response.get('data', [{}])[0].get('url', '')
        elif api_name == 'imagen':
            return response.get('predictions', [{}])[0].get('bytesBase64Encoded', '')
        elif api_name == 'stability':
            return response.get('artifacts', [{}])[0].get('base64', '')
        elif api_name == 'adobe_firefly':
            return response.get('outputs', [{}])[0].get('image', {}).get('url', '')
        
        return response.get('data', 'https://placeholder.com/1024x1024.png')
