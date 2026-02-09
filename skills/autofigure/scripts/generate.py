#!/usr/bin/env python3
"""
AutoFigure Skill - 论文插图生成
Usage: /autofigure/generate "method text" [output_name] [--reference path]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# 配置
AUTOFIGURE_DIR = Path("/home/neardws/User_Services/autofigure-edit")
OUTPUT_BASE_DIR = AUTOFIGURE_DIR / "outputs"
VENV_PYTHON = AUTOFIGURE_DIR / "venv/bin/python"

def load_env():
    """加载 .env 文件"""
    env_paths = [
        Path.home() / ".env",
        Path.home() / ".openclaw" / ".env",
        Path.home() / "clawd" / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, val = line.strip().split('=', 1)
                        os.environ.setdefault(key, val)
            break

def generate(method_text: str, output_name: str = None, reference: str = None) -> dict:
    """生成论文插图"""
    load_env()
    
    # 优先使用 OpenRouter (支持中国访问)
    api_key = os.getenv("OPENROUTER_API_KEY")
    provider = "openrouter"
    
    # 如果没有 OpenRouter，尝试 Gemini (需代理)
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        provider = "gemini"
    
    if not api_key:
        return {
            "success": False,
            "error": "未配置 API Key。请在 ~/.env 中添加:\n\n# 方案1: OpenRouter (推荐，支持中国访问)\nOPENROUTER_API_KEY=sk-or-v1-...\n\n# 方案2: Gemini (需要代理)\nGEMINI_API_KEY=your_key\n\n获取 OpenRouter Key: https://openrouter.ai/keys\n获取 Gemini Key: https://aistudio.google.com/app/apikey"
        }
    
    if not output_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"figure_{timestamp}"
    
    output_dir = OUTPUT_BASE_DIR / output_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存方法文本
    method_file = output_dir / "method.txt"
    method_file.write_text(method_text, encoding="utf-8")
    
    print(f"🎨 生成插图: {output_name}", file=sys.stderr)
    print(f"📁 输出目录: {output_dir}", file=sys.stderr)
    print("⏳ 生成中，请稍候 (~1-2分钟)...", file=sys.stderr)
    
    # 构建命令
    cmd = [
        str(VENV_PYTHON),
        str(AUTOFIGURE_DIR / "autofigure2.py"),
        "--method_file", str(method_file),
        "--output_dir", str(output_dir),
        "--provider", provider,
        "--api_key", api_key,
        "--sam_prompt", "icon,diagram,arrow",
        "--placeholder_mode", "label",
        "--optimize_iterations", "0",
    ]
    
    if reference and Path(reference).exists():
        cmd.extend(["--reference_image_path", reference])
    
    import subprocess
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(AUTOFIGURE_DIR))
    
    # 收集输出文件
    files = {}
    if (output_dir / "final.svg").exists():
        files["final_svg"] = str(output_dir / "final.svg")
    if (output_dir / "figure.png").exists():
        files["original_png"] = str(output_dir / "figure.png")
    
    icons_dir = output_dir / "icons"
    if icons_dir.exists():
        icons = list(icons_dir.glob("*_nobg.png"))
        if icons:
            files["icons"] = [str(f) for f in icons]
    
    return {
        "success": result.returncode == 0,
        "output_name": output_name,
        "output_dir": str(output_dir),
        "files": files,
    }

def main():
    parser = argparse.ArgumentParser(description="AutoFigure Skill")
    parser.add_argument("method_text", help="论文方法文本")
    parser.add_argument("output_name", nargs="?", help="输出名称")
    parser.add_argument("--reference", help="参考图片路径")
    args = parser.parse_args()
    
    result = generate(args.method_text, args.output_name, args.reference)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
