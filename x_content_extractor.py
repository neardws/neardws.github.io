#!/usr/bin/env python3
"""
X Smart Digest - 内容提取与总结
从截图中提取推文内容，使用 AI 总结后发送文字报告
"""

import os
import sys
import base64
import requests
from pathlib import Path
from datetime import datetime

# 配置
CLAWDBOT_API_TOKEN = "b1b693ff60a1320bae4abcab1f99722b24e576318ef53d0aada23ebd08310cff"
CLAWDBOT_GATEWAY = "http://192.168.31.211:18789"
LOG_DIR = Path("/Users/neardws/clawphone/logs")
WEBHOOK = "https://discord.com/api/webhooks/1470696274775769205/Tp6q93PwB2MVowcv3YCbAkdBIL_FvnaXZSIzJGwnhTdfeDGzEV1ZdbHIORb3oZXgL2HD"

def encode_image(image_path):
    """将图片转为 base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_image_with_vision(image_path):
    """使用 vision 模型提取推文内容"""
    base64_image = encode_image(image_path)
    
    # 通过 Clawdbot Gateway 调用 vision 模型
    headers = {
        "Authorization": f"Bearer {CLAWDBOT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "你是一个专门提取 X (Twitter) 推文内容的助手。请从截图中提取所有可见的推文内容，包括：\n1. 发推人用户名\n2. 推文正文\n3. 关键数据（点赞、转发、评论数等）\n4. 时间戳\n\n按时间顺序列出每条推文，格式简洁。"
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请提取这张 X 截图中的所有推文内容："},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(
            f"{CLAWDBOT_GATEWAY}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Vision analysis error: {e}")
        return None

def summarize_content(all_tweets):
    """使用 AI 总结推文内容"""
    headers = {
        "Authorization": f"Bearer {CLAWDBOT_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "kimi/kimi-k2-0711",
        "messages": [
            {
                "role": "system",
                "content": "你是一个 X (Twitter) 内容总结助手。请将以下提取的推文内容进行智能总结：\n\n1. 识别重要话题和趋势\n2. 提取有价值的观点和信息\n3. 按主题分类整理\n4. 突出值得关注的内容\n\n输出格式：\n📊 X Smart Digest - 总结报告\n\n🔥 热门话题\n- ...\n\n💡 有价值观点\n- ...\n\n📰 重要资讯\n- ...\n\n🎯 值得关注\n- ..."
            },
            {
                "role": "user",
                "content": f"请总结以下 X 推文内容：\n\n{all_tweets}"
            }
        ],
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(
            f"{CLAWDBOT_GATEWAY}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Summarization error: {e}")
        return None

def send_to_discord(content):
    """发送文字到 Discord"""
    # 分割长消息
    max_length = 1900
    chunks = []
    
    while len(content) > max_length:
        # 找到最后一个换行符
        split_point = content[:max_length].rfind('\n')
        if split_point == -1:
            split_point = max_length
        chunks.append(content[:split_point])
        content = content[split_point:].strip()
    chunks.append(content)
    
    for i, chunk in enumerate(chunks):
        if i == 0:
            payload = {"content": f"📱 X Smart Digest - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{chunk}"}
        else:
            payload = {"content": chunk}
        
        try:
            response = requests.post(WEBHOOK, json=payload, timeout=30)
            response.raise_for_status()
        except Exception as e:
            print(f"Discord send error: {e}")

def main():
    # 获取最新的3张截图
    screenshots = sorted(LOG_DIR.glob("x_*.png"), reverse=True)[:3]
    
    if not screenshots:
        print("No screenshots found")
        sys.exit(1)
    
    print(f"Found {len(screenshots)} screenshots to analyze")
    
    # 提取每张截图的内容
    all_extracted = []
    for screenshot in screenshots:
        print(f"Analyzing {screenshot.name}...")
        content = analyze_image_with_vision(str(screenshot))
        if content:
            all_extracted.append(f"=== {screenshot.name} ===\n{content}\n")
    
    if not all_extracted:
        print("Failed to extract content from screenshots")
        sys.exit(1)
    
    # 合并所有内容
    combined_content = "\n".join(all_extracted)
    
    # 保存提取的原始内容（用于调试）
    debug_file = LOG_DIR / f"extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    debug_file.write_text(combined_content)
    print(f"Saved extracted content to {debug_file}")
    
    # 总结内容
    print("Summarizing content...")
    summary = summarize_content(combined_content)
    
    if summary:
        # 发送到 Discord
        print("Sending to Discord...")
        send_to_discord(summary)
        print("Done!")
    else:
        print("Failed to generate summary")
        # 发送原始提取内容作为 fallback
        send_to_discord("📱 X Smart Digest - 总结失败，原始内容：\n\n" + combined_content[:1500])

if __name__ == "__main__":
    main()
