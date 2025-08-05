from .model_loader import QwenImageModelLoader
from .optimized_nodes import RH_QwenImageGenerator, RH_QwenImagePromptEnhancer

# 节点映射 - 核心节点
NODE_CLASS_MAPPINGS = {
    "QwenImageModelLoader": QwenImageModelLoader,
    "RH_QwenImageGenerator": RH_QwenImageGenerator,
    "RH_QwenImagePromptEnhancer": RH_QwenImagePromptEnhancer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenImageModelLoader": "Qwen-Image模型加载器",
    "RH_QwenImageGenerator": "RH_Qwen-Image",
    "RH_QwenImagePromptEnhancer": "RH_Qwen-Image提示词增强器",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']