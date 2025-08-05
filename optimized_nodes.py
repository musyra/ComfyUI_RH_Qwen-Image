"""
Refactored Qwen-Image generation node
Uses separate model loader for optimized performance and memory usage
"""

import torch
import numpy as np
from PIL import Image
import random
import comfy.utils

class RH_QwenImageGenerator:
    """
    Qwen-Image Generator (Refactored Version)
    Uses pre-loaded pipeline for image generation
    """
    
    def __init__(self):
        pass
        
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "pipeline": ("QWEN_PIPELINE",),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "A cute little kitten sitting on a windowsill, with sunlight streaming through the window onto it."
                }),
                "width": ("INT", {
                    "default": 1664,
                    "min": 512,
                    "max": 2048,
                    "step": 64
                }),
                "height": ("INT", {
                    "default": 928,
                    "min": 512,
                    "max": 2048,
                    "step": 64
                }),
                "num_inference_steps": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 100,
                    "step": 1
                }),
                "true_cfg_scale": ("FLOAT", {
                    "default": 4.0,
                    "min": 1.0,
                    "max": 20.0,
                    "step": 0.1
                }),
                "seed": ("INT", {
                    "default": 42,
                    "min": 0,
                    "max": 0xffffffffffffffff
                }),
                "language": (["auto", "zh", "en"], {
                    "default": "auto"
                }),
                "aspect_ratio": (["custom", "1:1", "16:9", "9:16", "4:3", "3:4"], {
                    "default": "16:9"
                }),
            },
            "optional": {
                "negative_prompt": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "enhance_prompt": ("BOOLEAN", {
                    "default": True
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    CATEGORY = "RunningHub/ImageGenerator"
    
    def get_positive_magic(self, language):
        """Get language-related enhancement prompts"""
        positive_magic = {
            "en": "Ultra HD, 4K, cinematic composition.",
            "zh": "超清，4K，电影级构图",
        }
        return positive_magic.get(language, positive_magic["en"])
    
    def detect_language(self, prompt):
        """Simple language detection"""
        # Detect Chinese characters
        chinese_chars = sum(1 for char in prompt if '\u4e00' <= char <= '\u9fff')
        total_chars = len([char for char in prompt if char.isalnum()])
        
        if total_chars == 0:
            return "en"
        
        chinese_ratio = chinese_chars / total_chars
        return "zh" if chinese_ratio > 0.3 else "en"
    
    def get_aspect_ratio_dimensions(self, aspect_ratio):
        """Get dimensions based on aspect ratio presets"""
        aspect_ratios = {
            "1:1": (1328, 1328),
            "16:9": (1664, 928),
            "9:16": (928, 1664),
            "4:3": (1472, 1140),
            "3:4": (1140, 1472)
        }
        return aspect_ratios.get(aspect_ratio, (1664, 928))
    
    def update_progress(self, step=1):
        """Update ComfyUI progress bar"""
        if hasattr(self, 'pbar'):
            self.pbar.update(step)
    
    def generate_image(self, pipeline, prompt, width, height, num_inference_steps, 
                      true_cfg_scale, seed, language, aspect_ratio, 
                      negative_prompt="", enhance_prompt=True):
        """Main function for image generation"""
        try:
            # If a preset aspect ratio is selected, use preset dimensions
            if aspect_ratio != "custom":
                width, height = self.get_aspect_ratio_dimensions(aspect_ratio)
            
            # Language detection and prompt enhancement
            if language == "auto":
                detected_lang = self.detect_language(prompt)
            else:
                detected_lang = language
            
            # Add enhancement prompts
            if enhance_prompt:
                positive_magic = self.get_positive_magic(detected_lang)
                enhanced_prompt = f"{prompt} {positive_magic}"
            else:
                enhanced_prompt = prompt
            
            print(f"🎨 Starting image generation:")
            print(f"  Prompt: {enhanced_prompt}")
            print(f"  Negative prompt: {negative_prompt}")
            print(f"  Dimensions: {width}x{height}")
            print(f"  Inference steps: {num_inference_steps}")
            print(f"  CFG Scale: {true_cfg_scale}")
            print(f"  Seed: {seed}")
            print(f"  Language: {detected_lang}")
            
            # Set random seed
            device = "cuda" if torch.cuda.is_available() else "cpu"
            generator = torch.Generator(device=device).manual_seed(seed)
            
            # Create ComfyUI progress bar
            self.pbar = comfy.utils.ProgressBar(num_inference_steps)
            
            # Generate image
            print("🚀 Starting image generation...")
            
            # Try using pipeline callback function with ComfyUI progress bar
            def diffusers_callback(step, timestep, latents):
                self.update_progress(1)
            
            try:
                # Try using callback method
                result = pipeline(
                    prompt=enhanced_prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    true_cfg_scale=true_cfg_scale,
                    generator=generator,
                    callback=diffusers_callback,
                    callback_steps=1
                )
            except TypeError:
                # If callback is not supported, use simulated progress
                print("⚠️ Pipeline doesn't support callback, using simulated progress bar")
                self.update_progress(1)
                
                result = pipeline(
                    prompt=enhanced_prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    true_cfg_scale=true_cfg_scale,
                    generator=generator
                )
                
                # Generation completed, update remaining progress
                self.update_progress(num_inference_steps - 1)
            
            image = result.images[0]
            print("✅ Image generation completed!")
            
            # Convert to ComfyUI format
            image_np = np.array(image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]
            
            return (image_tensor,)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error occurred during image generation: {error_msg}")
            
            # Check if it's a CUDA out of memory error
            if "CUDA out of memory" in error_msg or "out of memory" in error_msg.lower():
                print("💡 Suggested solutions:")
                print("  1. Reduce image resolution (width/height)")
                print("  2. Reduce inference steps (num_inference_steps)")
                print("  3. Enable CPU Offload in model loader")
                print("  4. Enable VAE Tiling in model loader")
                print("  5. Use float16 or bfloat16 data type")
                print("  6. If MMGP optimization is available, enable it")
                # Throw exception for out of memory, don't return blank image
                raise RuntimeError(f"🚫 CUDA out of memory: {error_msg}")
            
            # Other types of errors should also throw exceptions
            raise RuntimeError(f"🚫 Image generation failed: {error_msg}")

class RH_QwenImagePromptEnhancer:
    """
    Qwen-Image Prompt Enhancer (Refactored Version)
    Specialized for prompt preprocessing and enhancement
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "a little cat"
                }),
                "language": (["auto", "zh", "en"], {
                    "default": "auto"
                }),
                "style": (["none", "realistic", "anime", "artistic", "cinematic", "photographic"], {
                    "default": "none"
                }),
                "quality_level": (["basic", "high", "ultra"], {
                    "default": "high"
                }),
            },
            "optional": {
                "custom_style": ("STRING", {
                    "default": ""
                }),
                "custom_quality": ("STRING", {
                    "default": ""
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("enhanced_prompt", "detected_language")
    FUNCTION = "enhance_prompt"
    CATEGORY = "RunningHub/ImageGenerator"
    
    def detect_language(self, prompt):
        """Detect language"""
        chinese_chars = sum(1 for char in prompt if '\u4e00' <= char <= '\u9fff')
        total_chars = len([char for char in prompt if char.isalnum()])
        
        if total_chars == 0:
            return "en"
        
        chinese_ratio = chinese_chars / total_chars
        return "zh" if chinese_ratio > 0.3 else "en"
    
    def get_style_tags(self, style, language):
        """Get style tags"""
        style_tags = {
            "realistic": {
                "zh": "写实风格，真实感，高质量摄影",
                "en": "realistic style, photorealistic, high quality photography"
            },
            "anime": {
                "zh": "动漫风格，二次元，精美插画",
                "en": "anime style, 2D illustration, beautiful artwork"
            },
            "artistic": {
                "zh": "艺术风格，绘画作品，创意表现",
                "en": "artistic style, painting, creative expression"
            },
            "cinematic": {
                "zh": "电影风格，戏剧性光影，电影镜头",
                "en": "cinematic style, dramatic lighting, movie scene"
            },
            "photographic": {
                "zh": "专业摄影，商业摄影，精细细节",
                "en": "professional photography, commercial photography, fine details"
            }
        }
        
        if style == "none":
            return ""
        
        return style_tags.get(style, {}).get(language, "")
    
    def get_quality_tags(self, quality_level, language):
        """Get quality tags"""
        quality_tags = {
            "basic": {
                "zh": "高质量",
                "en": "high quality"
            },
            "high": {
                "zh": "杰作，最佳质量，高度详细",
                "en": "masterpiece, best quality, highly detailed"
            },
            "ultra": {
                "zh": "杰作，最佳质量，超高分辨率，极致细节，完美构图，专业级",
                "en": "masterpiece, best quality, ultra high resolution, extreme detail, perfect composition, professional grade"
            }
        }
        
        return quality_tags.get(quality_level, quality_tags["high"]).get(language, "")
    
    def enhance_prompt(self, prompt, language, style, quality_level, 
                      custom_style="", custom_quality=""):
        """Enhance prompt"""
        try:
            # Language detection
            if language == "auto":
                detected_lang = self.detect_language(prompt)
            else:
                detected_lang = language
            
            enhanced = prompt.strip()
            
            # Add styles
            style_tags = self.get_style_tags(style, detected_lang)
            if style_tags:
                enhanced = f"{enhanced}, {style_tags}"
            
            if custom_style.strip():
                enhanced = f"{enhanced}, {custom_style.strip()}"
            
            # Add quality tags
            if custom_quality.strip():
                quality_tags = custom_quality.strip()
            else:
                quality_tags = self.get_quality_tags(quality_level, detected_lang)
            
            if quality_tags:
                enhanced = f"{enhanced}, {quality_tags}"
            
            print(f"✨ Prompt enhancement completed:")
            print(f"  Original: {prompt}")
            print(f"  Enhanced: {enhanced}")
            print(f"  Language: {detected_lang}")
            
            return (enhanced, detected_lang)
            
        except Exception as e:
            print(f"Prompt enhancement failed: {str(e)}")
            return (prompt, language if language != "auto" else "en")

NODE_CLASS_MAPPINGS = {
    "RH_QwenImageGenerator": RH_QwenImageGenerator,
    "RH_QwenImagePromptEnhancer": RH_QwenImagePromptEnhancer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RH_QwenImageGenerator": "RH_Qwen-Image",
    "RH_QwenImagePromptEnhancer": "RH_Qwen-ImagePromptEnhancer",
}