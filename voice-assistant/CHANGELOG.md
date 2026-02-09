# Changelog

All notable changes to Axis Voice Assistant will be documented in this file.

## [1.0.0] - 2026-02-05

### 🎉 Initial Release

#### ✅ Implemented Features

##### Core Modules
- **ThemeManager** - 主题管理系统
  - 自动检测系统主题偏好
  - 支持手动切换深色/浅色主题
  - 主题偏好本地存储
  - 实时主题切换动画

- **ParticleWave** - 粒子波形可视化
  - Canvas 2D 渲染引擎
  - 300个粒子实时动画（60 FPS）
  - 5种状态动画效果（待机/倾听/思考/回复/打断）
  - 音频数据实时可视化
  - 高分屏自适应
  - 响应式布局

- **VoiceController** - 语音控制系统
  - Web Audio API 音频录制
  - 实时音频分析（FFT）
  - VAD 语音活动检测
  - 自动静音检测（1.5秒阈值）
  - ASR 服务集成（Whisper MLX）
  - TTS 服务集成（Qwen3-TTS）
  - 唤醒词检测
  - 打断词检测
  - 性能监控（ASR 延迟）

- **ChatManager** - 对话管理系统
  - WebSocket 连接管理
  - 自动重连机制（5次尝试）
  - 流式响应处理
  - 打字机效果（30ms/字符）
  - 对话历史管理
  - 淡出动画

- **Main** - 主应用入口
  - 模块初始化和协调
  - 事件系统
  - 状态管理
  - 错误处理
  - 调试模式
  - 键盘快捷键

##### User Interface
- 响应式布局设计
- 顶部状态栏
  - Logo 和标题
  - 主题切换按钮
  - ASR 延迟显示
  - 模型信息
- 中央粒子波形可视化区
- 对话气泡显示
  - 用户消息（绿色）
  - AI 回复（蓝色）
  - 打字机效果
  - 历史对话淡出
- 状态指示器
  - 5种颜色状态
  - 动画效果
- 权限请求遮罩
- 错误提示 Toast
- 调试面板（可切换）

##### Interaction
- 点击画布开始录音
- 空格键快捷录音
- Esc 键打断播放
- Ctrl+D 切换调试模式
- 语音唤醒（"你好，源宝"）
- 打断指令（"等等"、"稍等"）
- 自动静音检测

##### Visual Effects
- 粒子呼吸动画（待机）
- 音频反应动画（倾听）
- 快速闪烁动画（思考）
- 流动效果动画（回复）
- 震动效果动画（打断）
- 对话淡入淡出
- 主题切换过渡
- Glow 发光效果

##### Theme System
- 深色主题（默认）
- 浅色主题
- 自动跟随系统
- 手动切换保存
- 颜色变量系统
- 平滑过渡动画

##### Performance
- requestAnimationFrame 优化
- 高分屏适配
- 音频流及时释放
- WebSocket 自动重连
- 延迟监控
- 内存管理

##### Error Handling
- 麦克风权限错误
- ASR/TTS 服务错误
- WebSocket 连接错误
- 空识别结果处理
- 用户友好提示

#### 📦 Project Files

##### Application Files
- `index.html` - 主应用页面
- `test.html` - 系统测试页面
- `css/styles.css` - 样式表（553行）
- `js/theme-manager.js` - 主题管理（119行）
- `js/particle-wave.js` - 粒子渲染（242行）
- `js/voice-controller.js` - 语音控制（410行）
- `js/chat-manager.js` - 对话管理（309行）
- `js/main.js` - 主入口（319行）

##### Documentation
- `README.md` - 使用文档
- `QUICKSTART.md` - 快速开始
- `IMPLEMENTATION.md` - 实现总结
- `CHANGELOG.md` - 本文档
- `spec.md` - 产品规格

##### Scripts
- `start.sh` - 启动脚本

#### 📊 Statistics

- **总代码量**: ~1,950 行
- **JavaScript**: ~1,400 行
- **CSS**: ~550 行
- **文档**: ~1,500 行
- **文件总数**: 15 个

#### 🔧 Configuration

##### Required
- WebSocket URL（需配置）

##### Optional
- ASR/TTS 地址
- 唤醒词列表
- 粒子数量
- VAD 参数
- 打字机速度

#### 🌐 Browser Support

- ✅ Chrome 90+
- ✅ Safari 14+
- ✅ Edge 90+
- ⚠️ Firefox 88+ (部分支持)

#### ⚙️ External Services

- ASR: `http://192.168.31.114:9001` (Whisper MLX)
- TTS: `http://192.168.31.114:5100` (Qwen3-TTS)
- WebSocket: `ws://localhost:8765` (需配置)

#### 🐛 Known Issues

1. **WebSocket 需要配置** - 需要设置 OpenClaw 地址
2. **CORS 限制** - ASR/TTS 可能需要 CORS 配置
3. **麦克风权限** - 需要 HTTPS 或 localhost

#### 📝 Notes

- 所有核心功能已实现
- 测试页面可用于系统检查
- 唯一需要配置的是 WebSocket 地址
- 代码已优化，性能良好
- 文档完整，易于上手

---

## [Unreleased]

### 🎯 Planned Features

#### High Priority
- [ ] OpenClaw WebSocket 实际集成测试
- [ ] 唤醒词模型优化
- [ ] 多语言界面支持

#### Medium Priority
- [ ] 对话历史记录
- [ ] 多轮对话上下文
- [ ] 自定义粒子主题
- [ ] 移动端优化

#### Low Priority
- [ ] 语音指令系统
- [ ] 离线语音识别
- [ ] WebAssembly VAD
- [ ] Web Worker 音频处理

### 🔄 Future Improvements

- 更智能的 VAD
- 更流畅的动画
- 更低的延迟
- 更好的错误恢复
- 更多的主题选项
- 更丰富的可视化效果

---

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。
