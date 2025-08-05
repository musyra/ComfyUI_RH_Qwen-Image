# ComfyUI Qwen-Image Node

A custom node for ComfyUI that integrates Alibaba's Qwen-Image model for high-quality image generation with exceptional text rendering capabilities.

## ⚠️ Important Notes

- **System Requirements**: Current operation requires **24GB GPU memory** and **64GB+ RAM**. Virtual memory may need to be enabled for optimal performance.
- **MMGP Optimization**: We are aware that our MMGP implementation may have optimization issues that prevent proper VRAM release, potentially causing problems with multiple consecutive runs. We are actively working on further optimizations to resolve this issue.

## ✨ Features

- 🎨 **High-Quality Image Generation**: Powered by 20B parameter MMDiT architecture
- 📝 **Superior Text Rendering**: Especially excels at Chinese text rendering and complex text layouts
- 🎯 **Multiple Aspect Ratios**: Preset ratios including 1:1, 16:9, 9:16, 4:3, 3:4
- 🌐 **Multi-Language Support**: Auto-detection of Chinese/English with language-specific prompt enhancement
- ⚙️ **Rich Parameter Control**: CFG scale, inference steps, seed control and more
- 🚀 **Batch Generation**: Generate multiple image variants in one run
- 🔧 **Prompt Enhancement**: Automatic prompt optimization and enhancement
- 📊 **Real-Time Progress**: Detailed progress bars with time estimation during inference
- 💾 **Memory Optimization**: VAE tiling, CPU offload, MMGP optimization support

## 🔧 Node List

### Core Nodes
- **Qwen-Image Model Loader**: Specialized model loading and optimization node
- **RH_Qwen-Image Generator**: Efficient image generator with real-time progress display
- **RH_Qwen-Image Prompt Enhancer**: Advanced prompt preprocessing and enhancement

## 🚀 Quick Installation

### Step 1: Install the Node
```bash
# Navigate to ComfyUI custom_nodes directory
cd ComfyUI/custom_nodes

# Clone the repository
git clone https://github.com/HM-RunningHub/ComfyUI_RH_Qwen-Image

# Install dependencies
cd ComfyUI_RH_Qwen-Image
pip install -r requirements.txt
```

### Step 2: Download the Model
```bash
# Navigate to ComfyUI models directory
cd ../../models

# Download Qwen-Image model locally
git lfs clone https://huggingface.co/Qwen/Qwen-Image

# Restart ComfyUI
```

### Step 3: Verify Installation
```bash
# Verify local model setup
cd custom_nodes/ComfyUI_RH_Qwen-Image
python verify_model.py
```

## 📖 Usage

### Recommended Workflow (Optimized)

1. **Add Model Loader**:
   - Add "Qwen-Image Model Loader" node in ComfyUI
   - Keep `model_path` as default `"local"`
   - Configure optimization options based on your GPU

2. **Add Generator**:
   - Add "RH_Qwen-Image Generator" node
   - Connect the `pipeline` output from model loader
   - Configure generation parameters

3. **Basic Workflow**:
   ```
   [Model Loader] → [RH Generator] → [Save Image]
   ```

### Example Prompts

#### English Example
```
A coffee shop entrance features a chalkboard sign reading "Qwen Coffee 😊 $2 per cup," with a neon light beside it displaying "通义千问"
```

#### Chinese Example
```
一只可爱的小猫咪坐在窗台上，阳光透过窗户洒在它身上，旁边放着一杯热咖啡，咖啡杯上写着"通义千问"
```

## 📐 Aspect Ratio Presets

- **1:1**: 1328x1328 (Square)
- **16:9**: 1664x928 (Landscape)
- **9:16**: 928x1664 (Portrait)
- **4:3**: 1472x1140 (Traditional Landscape)
- **3:4**: 1140x1472 (Traditional Portrait)
- **custom**: Use custom width and height

## 🛠️ Technical Details

- Built on Diffusers library
- Supports CUDA and CPU inference
- Automatic language-specific prompt enhancement
- Support for bf16 precision for improved performance
- Advanced memory optimization with MMGP support

## ⚠️ Requirements

- **Storage**: ~20GB disk space for local model
- **Performance**: CUDA environment recommended, 24GB+ GPU memory, 64GB+ RAM
- **Dependencies**: Latest version of diffusers library required
- **Special Feature**: Optimized for Chinese text rendering



## 📁 Local Model Advantages

- ✅ No internet connection required
- ✅ Faster loading times
- ✅ Complete offline usage
- ✅ Avoid repeated downloads
- ✅ Data privacy protection

## 🔧 Troubleshooting

### Common Issue 1: "module diffusers has no attribute QwenImagePipeline"

This error indicates an outdated diffusers version. Solution:

```bash
# Uninstall old version
pip uninstall diffusers -y

# Install latest version
pip install git+https://github.com/huggingface/diffusers

# Restart ComfyUI
```

### Common Issue 2: Model Download Failed

- Check network connection
- Ensure access to HuggingFace Hub
- Verify sufficient disk space (~20GB)

### Common Issue 3: GPU Out of Memory

- Close other GPU-intensive programs
- Use smaller image dimensions
- Reduce batch generation count
- Enable CPU offload in model loader
- Enable VAE tiling optimization

## 📄 License

Licensed under Apache 2.0, consistent with the original Qwen-Image project.

## 🔗 References

- [Qwen-Image HuggingFace](https://huggingface.co/Qwen/Qwen-Image)
- [Qwen-Image GitHub](https://github.com/QwenLM/Qwen-Image)
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## ⭐ Star History

If you find this project helpful, please consider giving it a star!