/**
 * Main - 主入口文件
 * 初始化所有模块并协调交互
 */

class AxisVoiceAssistant {
    constructor() {
        // 模块实例
        this.themeManager = null;
        this.particleWave = null;
        this.voiceController = null;
        this.chatManager = null;
        
        // DOM 元素
        this.statusText = document.getElementById('status-text');
        this.statusIndicator = document.getElementById('status-indicator');
        this.asrLatencyEl = document.getElementById('asr-latency');
        this.errorToast = document.getElementById('error-toast');
        this.errorMessage = document.getElementById('error-message');
        this.permissionOverlay = document.getElementById('permission-overlay');
        this.grantPermissionBtn = document.getElementById('grant-permission');
        this.debugPanel = document.getElementById('debug-panel');
        this.debugContent = document.getElementById('debug-content');
        this.debugCloseBtn = document.getElementById('debug-close');
        
        // 状态
        this.isInitialized = false;
        this.debugMode = false;
        
        this.init();
    }

    /**
     * 初始化
     */
    async init() {
        console.log('[Axis] 初始化 Voice Assistant...');
        
        // 1. 初始化主题管理
        this.themeManager = new ThemeManager();
        
        // 2. 初始化粒子波形
        this.particleWave = new ParticleWave('particle-canvas', this.themeManager);
        
        // 3. 初始化语音控制
        this.voiceController = new VoiceController(this.particleWave);
        
        // 4. 初始化对话管理
        this.chatManager = new ChatManager(this.particleWave, this.voiceController);
        
        // 5. 绑定事件
        this.bindEvents();
        
        // 6. 检测调试模式
        if (window.location.search.includes('debug=true')) {
            this.enableDebugMode();
        }
        
        // 7. 请求麦克风权限
        this.showPermissionOverlay();
        
        console.log('[Axis] 初始化完成');
    }

    /**
     * 显示权限请求遮罩
     */
    showPermissionOverlay() {
        this.permissionOverlay.classList.remove('hidden');
        
        this.grantPermissionBtn.onclick = async () => {
            const success = await this.voiceController.init();
            
            if (success) {
                this.permissionOverlay.classList.add('hidden');
                this.isInitialized = true;
                this.updateStatus('点击或说"你好，源宝"开始对话');
                
                // 连接 WebSocket
                this.chatManager.connect();
            } else {
                this.showError('无法获取麦克风权限，请检查浏览器设置');
            }
        };
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 语音控制事件
        this.voiceController.onTranscript = (text) => {
            this.handleTranscript(text);
        };
        
        this.voiceController.onInterrupt = () => {
            this.handleInterrupt();
        };
        
        this.voiceController.onError = (error) => {
            this.showError(error);
        };
        
        this.voiceController.onLatencyUpdate = (type, latency) => {
            this.updateLatency(type, latency);
        };
        
        // 对话管理事件
        this.chatManager.onResponse = (text) => {
            this.log('AI 响应:', text);
        };
        
        this.chatManager.onError = (error) => {
            this.showError(error);
        };
        
        // 点击画布开始录音
        const canvas = document.getElementById('particle-canvas');
        canvas.addEventListener('click', () => {
            if (!this.isInitialized) return;
            
            if (!this.voiceController.isRecording) {
                this.voiceController.startRecording();
                this.updateStatus('正在监听...');
                this.statusIndicator.classList.add('active');
            }
        });
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (!this.isInitialized) return;
            
            // 空格键：开始/停止录音
            if (e.code === 'Space' && !e.repeat) {
                e.preventDefault();
                if (!this.voiceController.isRecording) {
                    this.voiceController.startRecording();
                    this.updateStatus('正在监听...');
                    this.statusIndicator.classList.add('active');
                } else {
                    this.voiceController.stopRecording();
                }
            }
            
            // Escape：打断
            if (e.code === 'Escape') {
                this.voiceController.interrupt();
            }
            
            // Ctrl + D：切换调试模式
            if (e.ctrlKey && e.code === 'KeyD') {
                e.preventDefault();
                this.toggleDebugMode();
            }
        });
        
        // 调试面板关闭
        if (this.debugCloseBtn) {
            this.debugCloseBtn.onclick = () => {
                this.debugPanel.classList.add('hidden');
            };
        }
    }

    /**
     * 处理转录结果
     */
    handleTranscript(text) {
        console.log('[Axis] 转录结果:', text);
        this.log('用户输入:', text);
        
        this.updateStatus('思考中...');
        this.statusIndicator.classList.remove('active');
        this.statusIndicator.classList.add('thinking');
        
        // 发送到对话管理
        this.chatManager.sendMessage(text);
        
        // 监听播放完成后恢复状态
        const checkPlayback = setInterval(() => {
            if (this.particleWave.state === 'idle') {
                clearInterval(checkPlayback);
                this.updateStatus('点击或说"你好，源宝"开始对话');
                this.statusIndicator.classList.remove('thinking', 'speaking');
            } else if (this.particleWave.state === 'speaking') {
                this.updateStatus('播放中...');
                this.statusIndicator.classList.remove('thinking');
                this.statusIndicator.classList.add('speaking');
            }
        }, 100);
    }

    /**
     * 处理打断
     */
    handleInterrupt() {
        console.log('[Axis] 已打断');
        this.log('打断', '检测到打断指令');
        
        this.chatManager.clearDialogue();
        this.updateStatus('已打断');
        this.statusIndicator.classList.add('interrupted');
        
        setTimeout(() => {
            this.updateStatus('点击或说"你好，源宝"开始对话');
            this.statusIndicator.classList.remove('interrupted');
        }, 3000);
    }

    /**
     * 更新状态文本
     */
    updateStatus(text) {
        if (this.statusText) {
            this.statusText.textContent = text;
        }
    }

    /**
     * 更新延迟显示
     */
    updateLatency(type, latency) {
        if (type === 'asr' && this.asrLatencyEl) {
            this.asrLatencyEl.textContent = `⏱️ ${latency}ms`;
        }
    }

    /**
     * 显示错误提示
     */
    showError(message) {
        console.error('[Axis] 错误:', message);
        this.log('错误', message);
        
        if (this.errorToast && this.errorMessage) {
            this.errorMessage.textContent = message;
            this.errorToast.classList.remove('hidden');
            
            setTimeout(() => {
                this.errorToast.classList.add('hidden');
            }, 5000);
        }
    }

    /**
     * 日志输出
     */
    log(title, content = '') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = `[${timestamp}] ${title}: ${content}`;
        
        if (this.debugMode && this.debugContent) {
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.innerHTML = `<span class="log-time">${timestamp}</span><span>${title}: ${content}</span>`;
            this.debugContent.appendChild(entry);
            
            // 自动滚动到底部
            this.debugContent.scrollTop = this.debugContent.scrollHeight;
        }
        
        console.log(logEntry);
    }

    /**
     * 启用调试模式
     */
    enableDebugMode() {
        this.debugMode = true;
        if (this.debugPanel) {
            this.debugPanel.classList.remove('hidden');
        }
        console.log('[Axis] 调试模式已启用');
    }

    /**
     * 切换调试模式
     */
    toggleDebugMode() {
        this.debugMode = !this.debugMode;
        
        if (this.debugPanel) {
            if (this.debugMode) {
                this.debugPanel.classList.remove('hidden');
            } else {
                this.debugPanel.classList.add('hidden');
            }
        }
        
        console.log('[Axis] 调试模式:', this.debugMode ? '开启' : '关闭');
    }

    /**
     * 销毁
     */
    destroy() {
        if (this.voiceController) {
            this.voiceController.destroy();
        }
        if (this.particleWave) {
            this.particleWave.destroy();
        }
        if (this.chatManager) {
            this.chatManager.disconnect();
        }
    }
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', () => {
    window.axisApp = new AxisVoiceAssistant();
});

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
    if (window.axisApp) {
        window.axisApp.destroy();
    }
});
