# Feishu Minutes (飞书妙记) Skill

查询和管理飞书妙记内容。

## 触发词
飞书妙记、会议记录、妙记、minutes、feishu minutes

## 前置条件
- 飞书应用凭证配置在 `~/User_Services/feishu/.env`
- 已开通 `minutes:minute:readonly` 等权限

## 使用方法

### 获取妙记列表
```bash
~/clawd/skills/feishu-minutes/scripts/minutes.sh list
```

### 获取妙记详情
```bash
~/clawd/skills/feishu-minutes/scripts/minutes.sh get <minute_token>
```

### 获取妙记转写文本
```bash
~/clawd/skills/feishu-minutes/scripts/minutes.sh transcript <minute_token>
```

## 环境变量
从 `~/User_Services/feishu/.env` 加载：
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
