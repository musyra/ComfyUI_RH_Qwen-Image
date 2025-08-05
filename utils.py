"""
Utility functions for Qwen-Image ComfyUI nodes
Includes prompt processing, model management and other auxiliary functions
"""

import re
import os
import json
from typing import Dict, Tuple, Optional

class PromptEnhancer:
    """Prompt enhancer"""
    
    def __init__(self):
        self.positive_magic = {
            "en": "Ultra HD, 4K, cinematic composition, masterpiece, best quality, highly detailed",
            "zh": "超清，4K，电影级构图，杰作，最佳质量，高度详细",
        }
        
        self.negative_magic = {
            "en": "blurry, low quality, distorted, deformed, bad anatomy, worst quality, low resolution",
            "zh": "模糊，低质量，扭曲，变形，解剖错误，最差质量，低分辨率",
        }
    
    def detect_language(self, text: str) -> str:
        """Detect text language"""
        if not text:
            return "en"
        
        # Detect Chinese characters
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        # Detect English letters
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        total_chars = chinese_chars + english_chars
        if total_chars == 0:
            return "en"
        
        chinese_ratio = chinese_chars / total_chars
        return "zh" if chinese_ratio > 0.3 else "en"
    
    def enhance_prompt(self, prompt: str, language: str = "auto", 
                      add_quality: bool = True) -> str:
        """Enhance prompt"""
        if not prompt:
            return prompt
        
        if language == "auto":
            language = self.detect_language(prompt)
        
        enhanced = prompt.strip()
        
        if add_quality and language in self.positive_magic:
            magic = self.positive_magic[language]
            if magic not in enhanced:
                enhanced = f"{enhanced}, {magic}"
        
        return enhanced
    
    def enhance_negative_prompt(self, negative_prompt: str, language: str = "auto") -> str:
        """Enhance negative prompt"""
        if language == "auto":
            language = self.detect_language(negative_prompt) if negative_prompt else "en"
        
        enhanced = negative_prompt.strip() if negative_prompt else ""
        
        if language in self.negative_magic:
            magic = self.negative_magic[language]
            if enhanced:
                enhanced = f"{enhanced}, {magic}"
            else:
                enhanced = magic
        
        return enhanced

class AspectRatioManager:
    """Aspect ratio manager"""
    
    def __init__(self):
        self.ratios = {
            "1:1": (1328, 1328),
            "16:9": (1664, 928),
            "9:16": (928, 1664),
            "4:3": (1472, 1140),
            "3:4": (1140, 1472),
            "21:9": (1792, 768),  # Ultra-wide screen
            "2:3": (1024, 1536),  # Book ratio
            "3:2": (1536, 1024),  # Camera ratio
        }
    
    def get_dimensions(self, ratio_name: str) -> Tuple[int, int]:
        """Get dimensions for specified aspect ratio"""
        return self.ratios.get(ratio_name, (1664, 928))
    
    def get_all_ratios(self) -> Dict[str, Tuple[int, int]]:
        """Get all available aspect ratios"""
        return self.ratios.copy()
    
    def validate_dimensions(self, width: int, height: int) -> Tuple[int, int]:
        """Validate and adjust dimensions to appropriate range"""
        # Ensure dimensions are multiples of 64
        width = max(512, min(2048, (width // 64) * 64))
        height = max(512, min(2048, (height // 64) * 64))
        return width, height

class ModelManager:
    """Model manager"""
    
    def __init__(self):
        self.supported_models = {
            "Qwen/Qwen-Image": {
                "name": "Qwen-Image (Official)",
                "description": "Official Qwen-Image model, 20B parameters",
                "size": "~20GB",
                "features": ["Text rendering", "Image generation", "Chinese optimization"]
            }
        }
    
    def get_model_info(self, model_path: str) -> Dict:
        """Get model information"""
        return self.supported_models.get(model_path, {
            "name": model_path,
            "description": "Custom model",
            "size": "Unknown",
            "features": ["Image generation"]
        })
    
    def is_local_model(self, model_path: str) -> bool:
        """Check if it's a local model"""
        return os.path.exists(model_path) and os.path.isdir(model_path)

class ConfigManager:
    """Configuration manager"""
    
    def __init__(self, config_file: str = "qwen_config.json"):
        self.config_file = config_file
        self.default_config = {
            "default_model": "Qwen/Qwen-Image",
            "default_steps": 50,
            "default_cfg_scale": 4.0,
            "default_aspect_ratio": "16:9",
            "auto_enhance_prompt": True,
            "cache_models": True,
            "low_vram_mode": False
        }
    
    def load_config(self) -> Dict:
        """Load configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge default configuration
                result = self.default_config.copy()
                result.update(config)
                return result
            except Exception as e:
                print(f"Failed to load config file: {e}")
        
        return self.default_config.copy()
    
    def save_config(self, config: Dict) -> bool:
        """Save configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
                    except Exception as e:
                print(f"Failed to save config file: {e}")
                return False

# Global instances
prompt_enhancer = PromptEnhancer()
aspect_ratio_manager = AspectRatioManager()
model_manager = ModelManager()
config_manager = ConfigManager()

def get_device_info():
    """Get device information"""
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            device_name = torch.cuda.get_device_name()
            memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            return {
                "device": device,
                "name": device_name,
                "memory_gb": f"{memory_total:.1f}GB"
            }
        else:
            return {
                "device": "cpu",
                "name": "CPU",
                "memory_gb": "Unknown"
            }
    except:
        return {
            "device": "Unknown",
            "name": "Unknown",
            "memory_gb": "Unknown"
        }