#!/usr/bin/env python3
"""
Image Generator - Hugging Face Inference API only
"""

import asyncio
import os
import base64
import aiohttp
from typing import Optional
from loguru import logger


class ImageGenerator:
    """Generate images using Hugging Face Inference API exclusively."""
    
    def __init__(self, api_manager=None):
        self.hf_api_key = os.getenv('HUGGINGFACE_FULLAPI')
        
        if not self.hf_api_key:
            raise ValueError("HUGGINGFACE_FULLAPI environment variable required")
        
        # Available HF models for rotation
        self.hf_models = [
            'stabilityai/stable-diffusion-xl-base-1.0',
            'black-forest-labs/FLUX.1-dev',
            'prompthero/openjourney-v4',
            'runwayml/stable-diffusion-v1-5',
            'CompVis/stable-diffusion-v1-4'
        ]
        
        logger.info(f"ImageGenerator initialized with {len(self.hf_models)} HF models")
    
    async def generate(self,
                      prompt: str,
                      style: str = 'photorealistic',
                      model_index: int = 0) -> str:
        """
        Generate image using Hugging Face.
        
        Args:
            prompt: Image generation prompt
            style: Image style (adds modifiers)
            model_index: Starting model index for rotation
            
        Returns:
            Base64 encoded image data URI
        """
        enhanced_prompt = self._enhance_prompt(prompt, style)
        
        try:
            return await self._generate_hf(enhanced_prompt, model_index)
        except Exception as e:
            logger.error(f"All HF models failed: {e}")
            raise Exception("Image generation failed: all HF models exhausted")
    
    async def _generate_hf(self, prompt: str, model_index: int = 0) -> str:
        """
        Generate image using HF Inference API with model rotation.
        
        Automatically rotates through models on rate limits/errors.
        """
        if model_index >= len(self.hf_models):
            raise Exception(f"All {len(self.hf_models)} HF models exhausted")
        
        model = self.hf_models[model_index]
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        headers = {
            'Authorization': f'Bearer {self.hf_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {'inputs': prompt}
        
        logger.info(f"Generating with HF model [{model_index + 1}/{len(self.hf_models)}]: {model}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=payload, timeout=60) as resp:
                    # Model loading (cold start)
                    if resp.status == 503:
                        error_data = await resp.json()
                        wait_time = error_data.get('estimated_time', 20)
                        logger.warning(f"Model {model} loading, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        return await self._generate_hf(prompt, model_index)
                    
                    # Rate limit - try next model
                    if resp.status == 429:
                        logger.warning(f"Rate limit on {model}, rotating to next model")
                        await asyncio.sleep(2)
                        return await self._generate_hf(prompt, model_index + 1)
                    
                    # Other errors - try next model
                    if resp.status != 200:
                        error = await resp.text()
                        logger.error(f"HF API error {resp.status} on {model}: {error}")
                        await asyncio.sleep(2)
                        return await self._generate_hf(prompt, model_index + 1)
                    
                    # Success - get image bytes
                    image_bytes = await resp.read()
                    
                    if len(image_bytes) < 1000:
                        raise Exception(f"Invalid image size: {len(image_bytes)} bytes")
                    
                    # Convert to base64 data URI
                    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                    
                    logger.info(f"✅ Generated image via {model} ({len(image_bytes)} bytes)")
                    return f"data:image/png;base64,{image_b64}"
        
        except asyncio.TimeoutError:
            logger.warning(f"Timeout on {model}, rotating to next model")
            return await self._generate_hf(prompt, model_index + 1)
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error on {model}: {e}")
            await asyncio.sleep(2)
            return await self._generate_hf(prompt, model_index + 1)
        
        except Exception as e:
            logger.error(f"Unexpected error on {model}: {e}")
            return await self._generate_hf(prompt, model_index + 1)
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt with style modifiers for better quality."""
        style_modifiers = {
            'photorealistic': ', highly detailed, photorealistic, sharp focus, 8k uhd, dslr, professional photography',
            'artistic': ', artistic interpretation, creative, expressive, stylized artwork, painterly',
            'minimalist': ', clean composition, minimalist design, simple elegance, negative space',
            'professional': ', professional quality, corporate style, polished, modern design, clean',
            'vibrant': ', vibrant colors, high contrast, dynamic composition, eye-catching, saturated',
            'cinematic': ', cinematic lighting, dramatic atmosphere, movie-like quality, film grain',
            'anime': ', anime style, manga art, cel shaded, vibrant anime colors',
            'digital_art': ', digital art, concept art, artstation trending, detailed illustration'
        }
        
        modifier = style_modifiers.get(style, '')
        
        # Add quality boosters
        quality_boost = ', high quality, masterpiece, best quality'
        
        return f"{prompt}{modifier}{quality_boost}"
    
    def get_available_models(self) -> list:
        """Return list of available HF models."""
        return self.hf_models.copy()
    
    def get_model_info(self, model_name: str) -> dict:
        """Get information about a specific model."""
        model_descriptions = {
            'stabilityai/stable-diffusion-xl-base-1.0': {
                'name': 'Stable Diffusion XL',
                'quality': 'High',
                'speed': 'Medium (8-12s)',
                'style': 'Photorealistic, versatile'
            },
            'black-forest-labs/FLUX.1-dev': {
                'name': 'FLUX.1 Dev',
                'quality': 'Very High',
                'speed': 'Slow (15-25s)',
                'style': 'Photorealistic, artistic'
            },
            'prompthero/openjourney-v4': {
                'name': 'OpenJourney v4',
                'quality': 'High',
                'speed': 'Fast (5-8s)',
                'style': 'Midjourney-like, artistic'
            },
            'runwayml/stable-diffusion-v1-5': {
                'name': 'Stable Diffusion 1.5',
                'quality': 'Medium',
                'speed': 'Fast (3-5s)',
                'style': 'General purpose'
            },
            'CompVis/stable-diffusion-v1-4': {
                'name': 'Stable Diffusion 1.4',
                'quality': 'Medium',
                'speed': 'Fast (3-5s)',
                'style': 'General purpose'
            }
        }
        
        return model_descriptions.get(model_name, {'name': model_name, 'info': 'No description'})


if __name__ == "__main__":
    # Test image generator
    async def test():
        generator = ImageGenerator()
        
        print("Available models:")
        for model in generator.get_available_models():
            info = generator.get_model_info(model)
            print(f"  - {info['name']}: {info.get('quality', 'N/A')} quality, {info.get('speed', 'N/A')}")
        
        print("\nGenerating test image...")
        try:
            result = await generator.generate(
                prompt="A serene mountain landscape at sunset",
                style="photorealistic"
            )
            print(f"✅ Success! Image data length: {len(result)} chars")
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    asyncio.run(test())
