# Axis Voice Assistant - 快速开始 🚀

## 5分钟上手指南

### 第 1 步：启动服务器

```bash
cd /home/neardws/clawd/voice-assistant
./start.sh
```

或者手动启动：

```bash
python3 -m http.server 3000
```

### 第 2 步：测试系统

打开浏览器访问：

```
http://localhost:3000/test.html
```

检查所有项目是否为绿色 ✅

### 第 3 步：配置 WebSocket

编辑 `js/chat-manager.js` 第 12 行：

```javascript
this.wsUrl = 'ws://localhost:8765'; // 改为你的 WebSocket 地址
```

### 第 4 步：启动应用

访问：

```
http://localhost:3000
```

### 第 5 步：开始对话

1. 点击"授权使用"允许麦克风访问
2. 点击画布或按**空格键**开始录音
3. 说出你的问题
4. 等待 AI 回复和语音播放

## 快捷键

| 按键 | 功能 |
|------|------|
| **空格** | 开始/停止录音 |
| **Esc** | 打断播放 |
| **Ctrl+D** | 调试模式 |

## 唤醒词

- **开始**: "你好，源宝"
- **打断**: "等等"、"稍等"、"打断一下"

## 状态颜色

- 🔵 蓝色 = 待机
- 🟢 绿色 = 监听中
- 🟣 紫色 = 思考中
- 🟠 橙色 = 回复中
- 🔴 红色 = 已打断

## 故障排查

### 麦克风无法使用？

1. 检查浏览器权限设置
2. 确保使用 localhost 或 HTTPS
3. 刷新页面重新授权

### ASR/TTS 连接失败？

检查服务是否运行：

```bash
curl http://192.168.31.114:9001
curl http://192.168.31.114:5100
```

### WebSocket 无法连接？

1. 确认 OpenClaw 服务已启动
2. 检查 `js/chat-manager.js` 中的地址
3. 查看浏览器控制台日志（F12）

## 需要帮助？

- 查看 `README.md` 详细文档
- 查看 `IMPLEMENTATION.md` 技术细节
- 查看 `spec.md` 产品规格
- 打开浏览器控制台（F12）查看日志

---

**Enjoy! ⚡**
