#!/usr/bin/env python3
"""
AgentMail 安全邮件处理器
Axis ⚡ - 2026-02-04
"""

import sys
sys.path.insert(0, '/home/neardws/clawd/scripts/agentmail')

from agentmail import AgentMail
from config import AGENTMAIL_API_KEY, INBOX_ID, SECURITY
from safety import check_email_safety


def get_client():
    return AgentMail(api_key=AGENTMAIL_API_KEY)


def check_inbox():
    """检查收件箱并安全处理邮件"""
    client = get_client()
    messages = client.inboxes.messages.list(inbox_id=INBOX_ID)
    
    results = []
    for msg in messages.messages:
        # 跳过自己发的邮件
        if INBOX_ID in str(msg.from_):
            continue
            
        # 获取完整邮件
        full = client.inboxes.messages.get(
            inbox_id=INBOX_ID, 
            message_id=msg.message_id
        )
        content = full.text or full.html or ""
        
        # 安全检查
        safety = check_email_safety(
            sender=str(full.from_),
            subject=full.subject or "",
            content=content
        )
        
        results.append({
            "from": str(full.from_),
            "subject": full.subject,
            "safety": safety,
            "message_id": msg.message_id
        })
    
    return results


def print_safe_email(result: dict):
    """安全地打印邮件信息"""
    safety = result["safety"]
    
    status = "✅ 安全" if safety.is_safe else "⚠️ 警告"
    sender_status = "✓" if safety.sender_trusted else "✗"
    content_status = "✓" if safety.content_safe else "✗"
    
    print(f"\n{'='*50}")
    print(f"📧 {result['subject']}")
    print(f"From: {result['from']}")
    print(f"状态: {status}")
    print(f"  发件人白名单: {sender_status}")
    print(f"  内容安全: {content_status}")
    
    if safety.warnings:
        print(f"\n⚠️ 警告:")
        for w in safety.warnings:
            print(f"  - {w}")
    
    if safety.is_safe and safety.sanitized_content:
        print(safety.sanitized_content)


if __name__ == "__main__":
    print("🔍 检查 Axis 邮箱...")
    results = check_inbox()
    
    if not results:
        print("📭 没有新邮件")
    else:
        for r in results:
            print_safe_email(r)
