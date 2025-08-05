# ComfyUI Qwen-Image 节点

这是一个用于ComfyUI的Qwen-Image图像生成节点，基于阿里巴巴通义千问团队发布的Qwen-Image模型实现，专门针对高质量图像生成和文本渲染进行了优化。

## ⚠️ 重要注意事项

- **系统配置要求**: 当前运行环境需要 **24GB GPU显存** 和 **64GB以上内存**，可能还需要打开虚拟内存以确保最佳性能。
- **MMGP优化问题**: 目前我们对MMGP的使用还存在一些优化空间，可能导致显存不能完全释放，多次连续运行时可能出现问题。我们正在积极寻找解决方案，进一步优化这个问题。

## ✨ 特性

- 🎨 **高质量图像生成**: 基于20B参数的MMDiT架构
- 📝 **优秀的文本渲染**: 特别擅长中文文本渲染和复杂文本布局
- 🎯 **多种宽高比支持**: 预设1:1、16:9、9:16、4:3、3:4等比例
- 🌐 **多语言支持**: 自动检测中英文并应用相应的增强提示词
- ⚙️ **丰富的参数控制**: 支持CFG scale、推理步数、种子等精细控制
- 🚀 **批量生成**: 支持一次生成多张变体图像
- 🔧 **提示词增强**: 自动优化和增强用户输入的提示词
- 📊 **实时进度条**: 推理过程中显示详细进度信息和时间估计
- 💾 **内存优化**: 24G显存能运行 支持VAE tiling、CPU offload、MMGP优化等

## 🔧 节点列表

### 核心节点
- **Qwen-Image模型加载器**: 专门的模型加载和优化节点
- **RH_Qwen-Image生成器**: 高效的图像生成器，支持实时进度条显示
- **RH_Qwen-Image提示词增强器**: 高级提示词预处理和增强工具

## 🚀 快速安装

### 步骤1：安装节点
```bash
# 进入ComfyUI的custom_nodes目录
cd ComfyUI/custom_nodes

# 克隆仓库
git clone https://github.com/HM-RunningHub/ComfyUI_RH_Qwen-Image
# 安装依赖
cd ComfyUI_RH_Qwen-Image
pip install -r requirements.txt
```

### 步骤2：下载模型
```bash
# 进入ComfyUI/models目录
cd ../../models

# 下载Qwen-Image模型到本地
git lfs clone https://huggingface.co/Qwen/Qwen-Image

# 重启ComfyUI
```

### 步骤3：验证安装
```bash
# 验证本地模型设置
cd custom_nodes/ComfyUI_RH_Qwen-Image
python verify_model.py
```

## 📖 使用方法

### 推荐工作流（优化版）

1. **添加模型加载器**：
   - 在ComfyUI中添加 "Qwen-Image模型加载器"
   - 保持默认设置
   - 根据显卡配置优化选项

2. **添加生成器**：
   - 添加 "RH_Qwen-Image生成器"
   - 连接模型加载器的 `pipeline` 输出
   - 配置生成参数

3. **基础工作流**：
   ```
   [模型加载器] → [生成器] → [保存图像]
   ```

### 示例提示词

#### 中文示例
```
一只可爱的小猫咪坐在窗台上，阳光透过窗户洒在它身上，旁边放着一杯热咖啡，咖啡杯上写着"通义千问"
```

#### 英文示例
```
A coffee shop entrance features a chalkboard sign reading "Qwen Coffee 😊 $2 per cup," with a neon light beside it displaying "通义千问"
```

## 📐 预设宽高比

- **1:1**: 1328x1328 (正方形)
- **16:9**: 1664x928 (横屏)
- **9:16**: 928x1664 (竖屏)
- **4:3**: 1472x1140 (传统横屏)
- **3:4**: 1140x1472 (传统竖屏)
- **custom**: 使用自定义width和height

## 🛠️ 技术细节

- 基于Diffusers库实现
- 支持CUDA和CPU推理
- 自动应用语言相关的增强提示词
- 支持bf16精度以提升性能
- 支持MMGP高级内存优化

## ⚠️ 系统要求

- **性能要求**: 建议使用CUDA环境，GPU显存24GB+，内存64GB+
- **依赖要求**: 需要最新版本的diffusers库支持

## 📁 本地模型优势

- ✅ 无需网络连接
- ✅ 加载速度更快
- ✅ 完全离线使用
- ✅ 避免重复下载
- ✅ 数据隐私保护

## 🔧 故障排除

### 常见问题1: "module diffusers has no attribute QwenImagePipeline"

这个错误表示diffusers版本过旧。解决方案：

```bash
# 卸载旧版本
pip uninstall diffusers -y

# 安装最新版本
pip install git+https://github.com/huggingface/diffusers

# 重启ComfyUI
```

### 常见问题2: 模型下载失败

- 检查网络连接
- 确保可以访问HuggingFace Hub
- 确保有足够硬盘空间（约20GB）

### 常见问题3: GPU内存不足

- 关闭其他占用GPU的程序
- 使用较小的图像尺寸
- 降低批量生成数量
- 在模型加载器中启用CPU offload
- 启用VAE tiling优化

## 📄 许可证

遵循Apache 2.0许可证，与原始Qwen-Image项目保持一致。

## 🔗 参考链接

- [Qwen-Image HuggingFace](https://huggingface.co/Qwen/Qwen-Image)
- [Qwen-Image GitHub](https://github.com/QwenLM/Qwen-Image)
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

## 🤝 贡献

欢迎贡献代码！请随时提交问题和拉取请求。

## ⭐ Star历史

如果您觉得这个项目有帮助，请考虑给它一个star！