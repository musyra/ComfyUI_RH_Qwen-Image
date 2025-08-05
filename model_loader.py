"""
Qwen-Image Model Loader Node
Specialized for loading and optimizing Qwen-Image pipeline
"""

import torch
import os
from contextlib import contextmanager
from diffusers import DiffusionPipeline

@contextmanager
def preserve_default_device():
    """Context manager to protect default device settings"""
    prev_device = torch._C._get_default_device()
    try:
        yield
    finally:
        torch.set_default_device(prev_device)

class QwenImageModelLoader:
    """
    Qwen-Image Model Loader
    Responsible for loading models and applying various optimizations
    """
    
    def __init__(self):
        self.cached_pipeline = None
        self.cached_model_path = None
        
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "torch_dtype": (["bfloat16", "float16", "float32"], {
                    "default": "bfloat16"
                }),
                "device": (["auto", "cuda", "cpu"], {
                    "default": "auto"
                }),
            },
            "optional": {
                "enable_vae_tiling": ("BOOLEAN", {
                    "default": True
                }),
                "enable_attention_slicing": ("BOOLEAN", {
                    "default": False
                }),
                "enable_cpu_offload": ("BOOLEAN", {
                    "default": True
                }),
                "enable_mmgp_optimization": ("BOOLEAN", {
                    "default": True
                }),
                "force_reload": ("BOOLEAN", {
                    "default": False
                }),
            }
        }
    
    RETURN_TYPES = ("QWEN_PIPELINE",)
    RETURN_NAMES = ("pipeline",)
    FUNCTION = "load_model"
    CATEGORY = "RunningHub/ImageGenerator"
    
    @staticmethod
    def get_local_model_path():
        """Get local model path"""
        try:
            import folder_paths
            # folder_paths.base_path is the ComfyUI root directory
            comfy_root = folder_paths.base_path
            local_model_path = os.path.join(comfy_root, "models", "Qwen-Image")
            return local_model_path
        except:
            # If folder_paths cannot be obtained, use relative path
            return os.path.join("models", "Qwen-Image")
    
    @staticmethod
    def check_local_model_exists():
        """Check if local model exists"""
        local_path = QwenImageModelLoader.get_local_model_path()
        
        # Check if directory exists
        if not os.path.exists(local_path):
            return False, f"Local model directory does not exist: {local_path}"
        
        # Check required model files
        required_files = [
            "model_index.json",
            "scheduler/scheduler_config.json"
        ]
        
        missing_files = []
        for file in required_files:
            file_path = os.path.join(local_path, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if missing_files:
            return False, f"Missing required files: {', '.join(missing_files)}"
        
        return True, local_path
    
    def get_torch_dtype(self, dtype_str):
        """Get torch data type"""
        dtype_map = {
            "bfloat16": torch.bfloat16,
            "float16": torch.float16,
            "float32": torch.float32
        }
        return dtype_map.get(dtype_str, torch.bfloat16)
    
    def get_device(self, device_str):
        """Get device"""
        if device_str == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device_str
    
    def apply_optimizations(self, pipeline, enable_vae_tiling, enable_attention_slicing, 
                          enable_cpu_offload, enable_mmgp_optimization):
        """Apply various optimizations"""
        print("🔧 Applying pipeline optimizations...")
        
        # VAE Tiling - Reduce VRAM usage
        if enable_vae_tiling:
            pipeline.enable_vae_tiling()
            print("  ✅ VAE Tiling enabled")
        
        # Attention Slicing - Reduce VRAM usage
        if enable_attention_slicing:
            pipeline.enable_attention_slicing()
            print("  ✅ Attention Slicing enabled")
        
        # CPU Offload - Automatically offload to CPU
        if enable_cpu_offload:
            pipeline.enable_model_cpu_offload()
            print("  ✅ Model CPU Offload enabled")
        
        # MMGP optimization (if available)
        if enable_mmgp_optimization:
            try:
                from mmgp import offload, profile_type
                
                if not getattr(pipeline, '_mmgp_profiled', False):
                    pipeline._mmgp_profiled = True
                    print("  🚀 Applying MMGP memory optimization...")
                    
                    with preserve_default_device():
                        components = {}
                        if hasattr(pipeline, 'transformer'):
                            components["transformer"] = pipeline.transformer
                        if hasattr(pipeline, 'vae'):
                            components["vae"] = pipeline.vae
                        
                        if components:
                            offload.profile(components, profile_type.LowRAM_LowVRAM)
                            print("  ✅ MMGP optimization applied")
                        else:
                            print("  ⚠️  No optimizable components found")
                else:
                    print("  ✅ MMGP optimization already exists")
                    
            except ImportError:
                print("  ⚠️  MMGP library not installed, skipping optimization")
            except Exception as e:
                print(f"  ⚠️  MMGP optimization failed: {e}")
    
    def load_model(self, torch_dtype, device, enable_vae_tiling=True, 
                   enable_attention_slicing=False, enable_cpu_offload=True, 
                   enable_mmgp_optimization=True, force_reload=False):
        """Main function for loading the model"""
        try:
            # Use fixed local model path
            model_path = "local"
            
            # Check local model
            model_exists, actual_path = self.check_local_model_exists()
            if not model_exists:
                error_msg = f"❌ Local model check failed: {actual_path}\n\n📋 Please follow these steps:\n1. Create directory in ComfyUI root: models/Qwen-Image/\n2. Download Qwen-Image model files to that directory\n3. Ensure directory structure is correct\n\n💡 Local model path: {self.get_local_model_path()}"
                print(error_msg)
                raise FileNotFoundError(error_msg)
            actual_model_path = actual_path
            print(f"✅ Local model detected: {actual_model_path}")
            
            # Check if reload is needed
            cache_key = f"{actual_model_path}_{torch_dtype}_{device}"
            if (not force_reload and 
                self.cached_pipeline is not None and 
                self.cached_model_path == cache_key):
                print("✅ Using cached model pipeline")
                return (self.cached_pipeline,)
            
            print(f"🚀 Starting to load Qwen-Image model...")
            print(f"  Model path: {actual_model_path}")
            print(f"  Data type: {torch_dtype}")
            print(f"  Device: {device}")
            
            # Get actual torch type and device
            actual_torch_dtype = self.get_torch_dtype(torch_dtype)
            actual_device = self.get_device(device)
            
            # Check diffusers version
            try:
                import diffusers
                print(f"  Diffusers version: {diffusers.__version__}")
            except:
                print("  Cannot get diffusers version information")
            
            # Display device information
            if actual_device == "cuda" and torch.cuda.is_available():
                print(f"  CUDA device: {torch.cuda.get_device_name()}")
                print(f"  VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
            else:
                print(f"  Using CPU device")
            
            # Load pipeline
            is_local = os.path.exists(actual_model_path)
            if is_local:
                print("📁 Loading model weights from local...")
            else:
                print("🌐 Downloading/loading model weights from online...")
            
            pipeline = DiffusionPipeline.from_pretrained(
                actual_model_path,
                torch_dtype=actual_torch_dtype,
                trust_remote_code=True,
                use_safetensors=True,
                local_files_only=is_local
            )
            
            print("🔧 Model weights loaded, applying optimizations...")
            
            # 应用优化
            self.apply_optimizations(
                pipeline, 
                enable_vae_tiling, 
                enable_attention_slicing, 
                enable_cpu_offload, 
                enable_mmgp_optimization
            )
            
            # 缓存pipeline
            self.cached_pipeline = pipeline
            self.cached_model_path = cache_key
            
            print(f"✅ Qwen-Image model loading completed!")
            print(f"  Device: {actual_device}")
            print(f"  Optimizations: VAE Tiling({enable_vae_tiling}), CPU Offload({enable_cpu_offload})")
            
            return (pipeline,)
            
        except FileNotFoundError as e:
            print(str(e))
            raise e
        except ImportError as e:
            error_msg = f"Import error: {str(e)}\nPlease ensure you have installed the latest version of diffusers: pip install git+https://github.com/huggingface/diffusers"
            print(error_msg)
            raise ImportError(error_msg)
        except Exception as e:
            error_msg = f"Loading Qwen-Image model failed: {str(e)}\n\nSolutions:\n1. Check if local model files are complete\n2. Upgrade diffusers: pip install git+https://github.com/huggingface/diffusers\n3. Ensure sufficient GPU memory"
            print(error_msg)
            raise Exception(error_msg)

# Node registration
NODE_CLASS_MAPPINGS = {
    "QwenImageModelLoader": QwenImageModelLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenImageModelLoader": "Qwen-Image Model Loader",
}