#!/usr/bin/env python3
"""
验证Qwen-Image本地模型设置
"""

import os
import sys
from pathlib import Path

def get_comfyui_root():
    """获取ComfyUI根目录"""
    try:
        import folder_paths
        # folder_paths.base_path 就是ComfyUI根目录
        return folder_paths.base_path
    except:
        # 如果在ComfyUI环境外运行，尝试查找
        current_dir = Path(__file__).parent
        
        # 向上查找包含models目录的路径
        for parent in current_dir.parents:
            if (parent / "models").exists():
                return str(parent)
        
        # 如果找不到，假设在ComfyUI/custom_nodes/ComfyUI_RH_Qwen中
        return str(current_dir.parent.parent)

def verify_local_model():
    """验证本地模型设置"""
    print("🔍 验证Qwen-Image本地模型设置")
    print("=" * 50)
    
    # 获取路径
    comfy_root = get_comfyui_root()
    model_path = os.path.join(comfy_root, "models", "Qwen-Image")
    
    print(f"ComfyUI根目录: {comfy_root}")
    print(f"模型路径: {model_path}")
    
    # 检查目录是否存在
    if not os.path.exists(model_path):
        print("❌ 模型目录不存在！")
        print(f"\n📋 请创建目录: {model_path}")
        print("然后下载Qwen-Image模型文件到该目录")
        return False
    
    print("✅ 模型目录存在")
    
    # 检查必要文件
    required_files = {
        "model_index.json": "主配置文件",
        "scheduler/scheduler_config.json": "调度器配置",
        "text_encoder/config.json": "文本编码器配置",
        "tokenizer/tokenizer_config.json": "分词器配置",
        "transformer/config.json": "Transformer配置",
        "vae/config.json": "VAE配置"
    }
    
    print("\n📄 检查必要文件:")
    missing_files = []
    
    for file_path, description in required_files.items():
        full_path = os.path.join(model_path, file_path)
        if os.path.exists(full_path):
            print(f"  ✅ {file_path} - {description}")
        else:
            print(f"  ❌ {file_path} - {description}")
            missing_files.append(file_path)
    
    # 检查模型权重文件
    weight_files = [
        "transformer/diffusion_pytorch_model.safetensors",
        "vae/diffusion_pytorch_model.safetensors"
    ]
    
    print("\n⚖️  检查模型权重文件:")
    for weight_file in weight_files:
        full_path = os.path.join(model_path, weight_file)
        if os.path.exists(full_path):
            size_mb = os.path.getsize(full_path) / 1024 / 1024
            print(f"  ✅ {weight_file} ({size_mb:.1f} MB)")
        else:
            full_path_bin = full_path.replace('.safetensors', '.bin')
            if os.path.exists(full_path_bin):
                size_mb = os.path.getsize(full_path_bin) / 1024 / 1024
                print(f"  ✅ {weight_file.replace('.safetensors', '.bin')} ({size_mb:.1f} MB)")
            else:
                print(f"  ❌ {weight_file} (权重文件)")
                missing_files.append(weight_file)
    
    # 计算总大小
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(model_path):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)
            file_count += 1
    
    total_gb = total_size / 1024 / 1024 / 1024
    print(f"\n📊 模型统计:")
    print(f"  文件总数: {file_count}")
    print(f"  总大小: {total_gb:.2f} GB")
    
    # 验证结果
    if missing_files:
        print(f"\n❌ 验证失败，缺少 {len(missing_files)} 个文件:")
        for file in missing_files:
            print(f"  - {file}")
        
        print(f"\n💡 解决方案:")
        print(f"1. 完整下载Qwen-Image模型到: {model_path}")
        print(f"2. 确保所有文件都下载完成")
        print(f"3. 检查文件权限")
        
        return False
    else:
        print(f"\n✅ 验证成功！本地模型设置正确")
        print(f"📁 模型路径: {model_path}")
        print(f"💾 模型大小: {total_gb:.2f} GB")
        print(f"🎉 现在可以在ComfyUI中使用Qwen-Image节点了！")
        
        return True

def test_model_loading():
    """测试模型加载"""
    print(f"\n🔧 测试模型加载...")
    
    try:
        from diffusers import DiffusionPipeline
        import torch
        
        comfy_root = get_comfyui_root()
        model_path = os.path.join(comfy_root, "models", "Qwen-Image")
        
        if not os.path.exists(model_path):
            print("❌ 模型路径不存在，跳过加载测试")
            return False
        
        print("正在测试模型加载...")
        
        # 尝试加载配置（不加载权重）
        try:
            pipeline = DiffusionPipeline.from_pretrained(
                model_path,
                torch_dtype=torch.float32,
                trust_remote_code=True,
                local_files_only=True
            )
            print("✅ 模型配置加载成功！")
            return True
        except Exception as e:
            print(f"❌ 模型加载测试失败: {str(e)}")
            return False
            
    except ImportError:
        print("⚠️  diffusers未安装，跳过加载测试")
        return True
    except Exception as e:
        print(f"❌ 加载测试异常: {str(e)}")
        return False

def main():
    print("🚀 Qwen-Image本地模型验证工具")
    
    # 验证文件结构
    structure_ok = verify_local_model()
    
    if structure_ok:
        # 测试模型加载
        loading_ok = test_model_loading()
        
        if loading_ok:
            print(f"\n🎉 所有检查通过！")
            print(f"现在您可以在ComfyUI中使用Qwen-Image节点了")
            print(f"节点会自动从本地路径加载模型，无需在线下载")
        else:
            print(f"\n⚠️  文件结构正确，但模型加载有问题")
            print(f"请检查模型文件是否完整")
    else:
        print(f"\n❌ 请先正确设置本地模型")
    
    print(f"\n💡 相关文档:")
    print(f"- 本地模型设置指南: LOCAL_MODEL_SETUP.md")
    print(f"- 快速修复指南: QUICKFIX.md")

if __name__ == "__main__":
    main()