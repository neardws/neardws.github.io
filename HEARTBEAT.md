# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

## 每日晨报（09:00 Asia/Shanghai）

每天上午 9 点发一次"今日计划"到 #heartbeat 频道（id: 1468239674865614920）。

内容格式：
1. 读取 `/home/neardws/clawd/tasks.json` 获取当前任务列表
2. 检查 `/home/neardws/clawd/daily-plan-last.txt` 是否包含今天的日期（格式 YYYY-MM-DD）
3. 如果今天已发过，跳过；否则：
   - 发送晨报消息到 #heartbeat（包含：日期、进行中任务摘要、待处理提醒）
   - 将今天的日期写入 `/home/neardws/clawd/daily-plan-last.txt` 覆盖旧内容
4. 发送完毕后回复 HEARTBEAT_OK
