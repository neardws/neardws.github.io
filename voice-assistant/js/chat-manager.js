/**
 * ChatManager - 对话管理模块
 * 处理与 OpenClaw WebSocket 的通信和打字机效果
 */

class ChatManager {
    constructor(particleWave, voiceController) {
        this.particleWave = particleWave;
        this.voiceController = voiceController;
        
        // WebSocket
        this.ws = null;
        this.wsUrl = 'ws://localhost:8765'; // 需要配置
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        
        // 对话状态
        this.currentUserText = '';
        this.currentAiText = '';
        this.isTyping = false;
        this.typingSpeed = 30; // ms per character
        
        // DOM 元素
        this.userTextEl = document.getElementById('user-text');
        this.aiTextEl = document.getElementById('ai-text');
        this.dialogueHistoryEl = document.getElementById('dialogue-history');
        
        // 回调
        this.onResponse = null;
        this.onError = null;
    }

    /**
     * 连接 WebSocket
     */
    connect() {
        try {
            console.log('[ChatManager] 连接 WebSocket:', this.wsUrl);
            this.ws = new WebSocket(this.wsUrl);
            
            this.ws.onopen = () => {
                console.log('[ChatManager] WebSocket 连接成功');
                this.reconnectAttempts = 0;
            };
            
            this.ws.onmessage = (event) => {
                this.handleMessage(event.data);
            };
            
            this.ws.onerror = (error) => {
                console.error('[ChatManager] WebSocket 错误:', error);
                if (this.onError) {
                    this.onError('连接失败，请检查 OpenClaw 服务');
                }
            };
            
            this.ws.onclose = () => {
                console.log('[ChatManager] WebSocket 连接关闭');
                this.attemptReconnect();
            };
            
        } catch (error) {
            console.error('[ChatManager] 连接失败:', error);
            if (this.onError) {
                this.onError('无法连接到 AI 服务');
            }
        }
    }

    /**
     * 尝试重连
     */
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`[ChatManager] ${this.reconnectDelay}ms 后尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        } else {
            console.error('[ChatManager] 重连失败，已达到最大尝试次数');
            if (this.onError) {
                this.onError('无法连接到 AI 服务，请刷新页面');
            }
        }
    }

    /**
     * 发送消息
     */
    sendMessage(text) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            console.error('[ChatManager] WebSocket 未连接');
            if (this.onError) {
                this.onError('连接已断开，正在重连...');
            }
            this.connect();
            return;
        }
        
        console.log('[ChatManager] 发送消息:', text);
        
        // 显示用户消息
        this.displayUserMessage(text);
        
        // 发送到 WebSocket
        const message = {
            type: 'chat',
            content: text,
            timestamp: Date.now()
        };
        
        this.ws.send(JSON.stringify(message));
        
        // 切换到思考状态
        this.particleWave.setState('thinking');
    }

    /**
     * 处理 WebSocket 消息
     */
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            
            switch (message.type) {
                case 'response':
                    // 流式响应
                    this.handleStreamResponse(message.content);
                    break;
                    
                case 'complete':
                    // 响应完成
                    this.handleResponseComplete();
                    break;
                    
                case 'error':
                    console.error('[ChatManager] 服务器错误:', message.error);
                    if (this.onError) {
                        this.onError(message.error);
                    }
                    this.particleWave.setState('idle');
                    break;
                    
                default:
                    console.warn('[ChatManager] 未知消息类型:', message.type);
            }
        } catch (error) {
            console.error('[ChatManager] 消息解析错误:', error);
        }
    }

    /**
     * 处理流式响应
     */
    handleStreamResponse(content) {
        this.currentAiText += content;
        
        // 使用打字机效果显示
        if (!this.isTyping) {
            this.startTypewriter();
        }
    }

    /**
     * 处理响应完成
     */
    handleResponseComplete() {
        console.log('[ChatManager] 响应完成');
        
        // 等待打字机效果完成
        const waitForTyping = setInterval(() => {
            if (!this.isTyping) {
                clearInterval(waitForTyping);
                
                // 发送到 TTS
                if (this.currentAiText.trim()) {
                    this.voiceController.playTTS(this.currentAiText.trim());
                }
                
                // 触发回调
                if (this.onResponse) {
                    this.onResponse(this.currentAiText);
                }
            }
        }, 100);
    }

    /**
     * 显示用户消息
     */
    displayUserMessage(text) {
        // 将旧对话移到历史
        this.moveToHistory();
        
        // 显示新消息
        this.currentUserText = text;
        this.userTextEl.textContent = text;
        this.userTextEl.style.display = 'block';
        
        // 清空 AI 文本
        this.currentAiText = '';
        this.aiTextEl.textContent = '';
        this.aiTextEl.style.display = 'none';
    }

    /**
     * 打字机效果
     */
    startTypewriter() {
        this.isTyping = true;
        this.aiTextEl.style.display = 'block';
        this.aiTextEl.classList.add('typing');
        
        let displayedText = '';
        let index = 0;
        
        const typeNextChar = () => {
            if (index < this.currentAiText.length) {
                displayedText += this.currentAiText[index];
                this.aiTextEl.textContent = displayedText;
                index++;
                setTimeout(typeNextChar, this.typingSpeed);
            } else {
                // 打字完成
                this.aiTextEl.classList.remove('typing');
                this.isTyping = false;
            }
        };
        
        typeNextChar();
    }

    /**
     * 将当前对话移到历史
     */
    moveToHistory() {
        if (!this.currentUserText && !this.currentAiText) return;
        
        // 创建历史记录
        const historyItem = document.createElement('div');
        historyItem.className = 'dialogue-history-item';
        
        if (this.currentUserText) {
            const userDiv = document.createElement('div');
            userDiv.className = 'user-text';
            userDiv.textContent = this.currentUserText;
            historyItem.appendChild(userDiv);
        }
        
        if (this.currentAiText) {
            const aiDiv = document.createElement('div');
            aiDiv.className = 'ai-text';
            aiDiv.textContent = this.currentAiText;
            historyItem.appendChild(aiDiv);
        }
        
        this.dialogueHistoryEl.appendChild(historyItem);
        
        // 添加淡出动画
        setTimeout(() => {
            historyItem.classList.add('fade-out');
            
            // 动画完成后移除
            setTimeout(() => {
                historyItem.remove();
            }, 1000);
        }, 100);
    }

    /**
     * 清空当前对话
     */
    clearDialogue() {
        this.currentUserText = '';
        this.currentAiText = '';
        this.userTextEl.textContent = '';
        this.aiTextEl.textContent = '';
        this.userTextEl.style.display = 'none';
        this.aiTextEl.style.display = 'none';
        this.isTyping = false;
        
        console.log('[ChatManager] 对话已清空');
    }

    /**
     * 设置 WebSocket URL
     */
    setWebSocketUrl(url) {
        this.wsUrl = url;
    }

    /**
     * 断开连接
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatManager;
}
