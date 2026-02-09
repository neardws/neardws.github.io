# Axis Voice Assistant ⚡

一个运行在 Mac Mini 上的语音交互助手，采用抽象粒子波形可视化，支持语音唤醒、流式对话和情绪色彩反馈。

## 功能特性

- 🎙️ **语音唤醒**: 说"你好，源宝"开始对话
- 🌊 **粒子波形可视化**: 实时音频反馈
- 🎨 **情绪色彩映射**: 不同状态显示不同颜色
- 💬 **流式对话**: 打字机效果显示 AI 回复
- 🌓 **主题切换**: 自动跟随系统主题
- 🔌 **WebSocket 集成**: 连接 OpenClaw/Kimi

## 系统要求

### 运行环境
- **主机**: Mac Mini M4 (192.168.31.114) 或任意支持的浏览器
- **浏览器**: Chrome/Safari/Edge (需支持 Web Audio API)
- **网络**: 本地局域网访问

### 外部服务依赖

| 服务 | 地址 | 状态 |
|------|------|------|
| ASR (Whisper MLX) | `http://192.168.31.114:9001` | ✅ 必需 |
| TTS (Qwen3-TTS) | `http://192.168.31.114:5100` | ✅ 必需 |
| OpenClaw WebSocket | `ws://localhost:8765` | ⚙️ 需配置 |

## 快速开始

### 1. 启动本地服务器

在项目根目录下运行：

```bash
# 使用 Python (推荐)
python3 -m http.server 3000

# 或使用 Node.js
npx serve -p 3000
```

### 2. 配置 WebSocket 地址

编辑 `js/chat-manager.js`，修改第 12 行：

```javascript
this.wsUrl = 'ws://localhost:8765'; // 修改为你的 OpenClaw WebSocket 地址
```

### 3. 访问应用

打开浏览器访问：

```
http://localhost:3000
```

### 4. 授权麦克风

首次访问时会弹出麦克风权限请求，点击"授权使用"。

## 使用说明

### 语音交互

1. **唤醒助手**:
   - 点击画布中央的粒子波形
   - 或说"你好，源宝"
   - 或按下**空格键**

2. **开始对话**:
   - 唤醒后说出你的问题
   - 系统会自动检测静音并停止录音

3. **打断对话**:
   - 说"等等"、"稍等"或"打断一下"
   - 或按下 **Esc 键**

### 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| **空格键** | 开始/停止录音 |
| **Esc** | 打断当前播放 |
| **Ctrl + D** | 切换调试模式 |

### 调试模式

在 URL 中添加 `?debug=true` 参数：

```
http://localhost:3000?debug=true
```

或在运行时按 **Ctrl + D** 切换。

## 状态指示

### 粒子颜色

| 颜色 | 状态 | 描述 |
|------|------|------|
| 🔵 科技蓝 | 待机 | 呼吸状态，5秒周期缓慢浮动 |
| 🟢 活力绿 | 倾听 | 随音量跳动，密度随音量变化 |
| 🟣 神秘紫 | 思考 | 快速闪烁，AI 正在思考 |
| 🟠 温暖橙 | 回复 | 配合打字机效果流动 |
| 🔴 警示红 | 打断 | 闪烁3秒后恢复 |

### 状态栏信息

- **主题图标**: 🌙 深色 / ☀️ 浅色
- **ASR延迟**: 语音识别响应时间
- **模型**: 当前使用的 AI 模型

## 项目结构

```
voice-assistant/
├── index.html              # 主页面
├── README.md               # 本文档
├── spec.md                 # 产品规格文档
├── css/
│   └── styles.css          # 样式文件
├── js/
│   ├── main.js             # 主入口
│   ├── particle-wave.js    # 粒子波形可视化
│   ├── voice-controller.js # 语音控制
│   ├── chat-manager.js     # 对话管理
│   └── theme-manager.js    # 主题管理
└── assets/
    └── sounds/             # 音效资源（可选）
```

## 配置说明

### 修改 ASR 地址

编辑 `js/voice-controller.js`，修改第 19 行：

```javascript
this.ASR_URL = 'http://192.168.31.114:9001/transcribe';
```

### 修改 TTS 地址

编辑 `js/voice-controller.js`，修改第 20 行：

```javascript
this.TTS_URL = 'http://192.168.31.114:5100/tts';
```

### 修改唤醒词

编辑 `js/voice-controller.js`，修改第 24-25 行：

```javascript
this.WAKE_WORDS = ['你好源宝', '你好，源宝', '源宝'];
this.INTERRUPT_WORDS = ['等等', '稍等', '打断一下', '停止'];
```

### 调整 VAD 参数

编辑 `js/voice-controller.js`，修改第 32-34 行：

```javascript
this.silenceThreshold = 0.01;  // 静音阈值 (0-1)
this.silenceDelay = 1500;       // 静音延迟 (ms)
```

### 调整打字机速度

编辑 `js/chat-manager.js`，修改第 19 行：

```javascript
this.typingSpeed = 30; // 每个字符的延迟 (ms)
```

## 故障排查

### 麦克风无法使用

1. 确保使用 HTTPS 或 localhost
2. 检查浏览器权限设置
3. 尝试刷新页面重新授权

### ASR/TTS 连接失败

1. 检查服务是否运行：
   ```bash
   curl http://192.168.31.114:9001/health
   curl http://192.168.31.114:5100/health
   ```
2. 检查网络连接
3. 查看浏览器控制台错误信息

### WebSocket 连接失败

1. 确认 OpenClaw 服务已启动
2. 检查 WebSocket 地址配置
3. 查看调试面板日志

### 粒子动画卡顿

1. 降低粒子数量（修改 `particle-wave.js` 第 14 行）
2. 关闭硬件加速
3. 使用性能更好的浏览器

## 开发计划

- [x] 基础框架
- [x] 粒子波形渲染
- [x] 语音录音和 ASR
- [x] TTS 播放
- [x] 对话管理
- [ ] OpenClaw WebSocket 集成（待配置）
- [ ] 唤醒词优化
- [ ] 多语言支持
- [ ] 移动端适配

## 技术栈

- **前端**: HTML5 + CSS3 + Vanilla JavaScript
- **音频**: Web Audio API
- **可视化**: Canvas API
- **通信**: WebSocket
- **ASR**: Whisper MLX
- **TTS**: Qwen3-TTS
- **LLM**: OpenClaw (Kimi)

## 许可证

MIT License

---

*文档生成时间: 2026-02-05*
*版本: v1.0*
