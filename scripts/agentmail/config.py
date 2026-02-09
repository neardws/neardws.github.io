# AgentMail 安全配置
# Axis ⚡ - 2026-02-04

# API 配置
AGENTMAIL_API_KEY = "am_f01b634d50f42a0d35d78594736d829b73d338db00af0b3d79df13770fe6aa18"
INBOX_ID = "axis-ai@agentmail.to"

# 发件人白名单 - 只处理这些邮箱发来的邮件
TRUSTED_SENDERS = [
    "neard.ws@gmail.com",
    "xc.xu@uestc.edu.cn",
    "neardws@qq.com",
]

# 安全设置
SECURITY = {
    # 是否只处理白名单发件人
    "whitelist_only": True,
    # 是否记录被拒绝的邮件
    "log_rejected": True,
    # 最大邮件内容长度（防止超长攻击）
    "max_content_length": 10000,
    # 是否启用内容清洗
    "sanitize_content": True,
}
