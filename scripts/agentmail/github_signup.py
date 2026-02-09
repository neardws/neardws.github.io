#!/usr/bin/env python3
"""
GitHub 注册脚本 - 修复版
Axis ⚡ - 2026-02-04

注意：GitHub 有 CAPTCHA 验证，可能需要人工干预
"""

from playwright.sync_api import sync_playwright
import time
import secrets
import string

EMAIL = "axis-ai@agentmail.to"
USERNAME = "axis-ai-bot"
PASSWORD = ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%") for _ in range(16))

def main():
    print(f"📧 邮箱: {EMAIL}")
    print(f"👤 用户名: {USERNAME}")
    print(f"🔑 密码: {PASSWORD}")
    print()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Step 1: 访问注册页面
        print("📍 Step 1: 访问 GitHub 注册页面...")
        page.goto("https://github.com/signup")
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # Step 2: 输入邮箱
        print("📧 Step 2: 输入邮箱...")
        email_input = page.locator('input#email')
        email_input.fill(EMAIL)
        time.sleep(1)
        
        # 点击 Continue 按钮（精确定位，避免点到 Google）
        page.locator('button[data-continue-to="password-container"]').click()
        time.sleep(2)
        page.screenshot(path="/tmp/github_step2.png")
        print("📸 截图: /tmp/github_step2.png")
        
        # Step 3: 输入密码
        print("🔑 Step 3: 输入密码...")
        password_input = page.locator('input#password')
        if password_input.count() > 0:
            password_input.fill(PASSWORD)
            time.sleep(1)
            page.locator('button[data-continue-to="username-container"]').click()
            time.sleep(2)
        page.screenshot(path="/tmp/github_step3.png")
        print("📸 截图: /tmp/github_step3.png")
        
        # Step 4: 输入用户名
        print("👤 Step 4: 输入用户名...")
        username_input = page.locator('input#login')
        if username_input.count() > 0:
            username_input.fill(USERNAME)
            time.sleep(1)
            page.locator('button[data-continue-to="opt-in-container"]').click()
            time.sleep(2)
        page.screenshot(path="/tmp/github_step4.png")
        print("📸 截图: /tmp/github_step4.png")
        
        # Step 5: 处理 opt-in (是否接收邮件)
        print("📬 Step 5: 处理邮件订阅...")
        opt_in = page.locator('input#opt_in')
        if opt_in.count() > 0:
            # 不订阅
            pass
        # 点击继续
        continue_btn = page.locator('button[data-continue-to="captcha-and-submit-container"]')
        if continue_btn.count() > 0:
            continue_btn.click()
            time.sleep(2)
        page.screenshot(path="/tmp/github_step5.png")
        print("📸 截图: /tmp/github_step5.png")
        
        # Step 6: CAPTCHA 验证
        print("🔐 Step 6: CAPTCHA 验证...")
        print("⚠️ GitHub 需要人工验证 CAPTCHA，无法自动完成")
        time.sleep(5)
        page.screenshot(path="/tmp/github_step6.png")
        print("📸 截图: /tmp/github_step6.png")
        
        print(f"\n📄 当前页面 URL: {page.url}")
        print(f"📄 页面标题: {page.title()}")
        
        browser.close()
        print("\n🏁 完成")
        print(f"\n⚠️ 请保存密码: {PASSWORD}")
        print("⚠️ 需要手动完成 CAPTCHA 验证")

if __name__ == "__main__":
    main()
