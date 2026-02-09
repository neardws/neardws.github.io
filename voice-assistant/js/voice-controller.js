/**
 * VoiceController - 语音控制模块
 * 处理麦克风录音、VAD、ASR、TTS、语音唤醒和打断
 */

class VoiceController {
    constructor(particleWave) {
        this.particleWave = particleWave;
        
        // Web Audio API
        this.audioContext = null;
        this.mediaStream = null;
        this.microphone = null;
        this.analyser = null;
        this.recorder = null;
        this.audioChunks = [];
        
        // 播放
        this.audioElement = null;
        this.currentPlayback = null;
        
        // 配置 - 使用 localhost 避免 CORS 和 HTTPS 问题
        this.ASR_URL = 'http://localhost:9001/transcribe';
        this.TTS_URL = 'http://localhost:5100/tts';
        this.VOICE_ID = 'wangyuan';
        
        // 唤醒词和打断词
        this.WAKE_WORDS = ['你好源宝', '你好，源宝', '源宝'];
        this.INTERRUPT_WORDS = ['等等', '稍等', '打断一下', '停止'];
        
        // 状态
        this.isRecording = false;
        this.isListening = false;
        this.listenTimeout = null;
        this.LISTEN_TIMEOUT_MS = 30000; // 30秒
        
        // VAD
        this.silenceThreshold = 0.01;
        this.silenceDelay = 1500; // 1.5秒静音后停止
        this.silenceStart = null;
        this.isSpeaking = false;
        
        // 性能追踪
        this.asrStartTime = 0;
        
        // 回调
        this.onTranscript = null;
        this.onInterrupt = null;
        this.onError = null;
        this.onLatencyUpdate = null;
    }

    /**
     * 初始化麦克风权限
     */
    async init() {
        try {
            // 创建音频上下文
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // 请求麦克风权限
            this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            // 设置音频分析
            this.setupAudioAnalysis();
            
            console.log('[VoiceController] 麦克风初始化成功');
            return true;
        } catch (error) {
            console.error('[VoiceController] 麦克风初始化失败:', error);
            if (this.onError) {
                this.onError('麦克风权限被拒绝，请检查浏览器设置');
            }
            return false;
        }
    }

    /**
     * 设置音频分析
     */
    setupAudioAnalysis() {
        // 创建分析器
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 256;
        this.analyser.smoothingTimeConstant = 0.8;
        
        // 连接麦克风
        this.microphone = this.audioContext.createMediaStreamSource(this.mediaStream);
        this.microphone.connect(this.analyser);
        
        // 创建录音器
        this.recorder = new MediaRecorder(this.mediaStream, {
            mimeType: 'audio/webm;codecs=opus'
        });
        
        this.recorder.ondataavailable = (e) => {
            if (e.data.size > 0) {
                this.audioChunks.push(e.data);
            }
        };
        
        this.recorder.onstop = () => {
            this.sendToASR();
        };
        
        // 开始音频可视化循环
        this.startAudioVisualization();
    }

    /**
     * 开始音频可视化
     */
    startAudioVisualization() {
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const updateVisual = () => {
            requestAnimationFrame(updateVisual);
            
            this.analyser.getByteFrequencyData(dataArray);
            this.particleWave.updateAudioData(dataArray);
            
            // VAD: 检测静音
            if (this.isRecording) {
                const volume = this.getAverageVolume(dataArray);
                this.detectSilence(volume);
            }
        };
        
        updateVisual();
    }

    /**
     * 获取平均音量
     */
    getAverageVolume(dataArray) {
        const sum = dataArray.reduce((a, b) => a + b, 0);
        return sum / dataArray.length / 255;
    }

    /**
     * 检测静音（VAD）
     */
    detectSilence(volume) {
        if (volume > this.silenceThreshold) {
            // 有声音
            this.isSpeaking = true;
            this.silenceStart = null;
        } else if (this.isSpeaking) {
            // 从说话转为静音
            if (this.silenceStart === null) {
                this.silenceStart = Date.now();
            } else if (Date.now() - this.silenceStart > this.silenceDelay) {
                // 静音超过阈值，停止录音
                console.log('[VoiceController] 检测到静音，停止录音');
                this.stopRecording();
            }
        }
    }

    /**
     * 开始录音
     */
    startRecording() {
        if (this.isRecording) return;
        
        console.log('[VoiceController] 开始录音');
        this.isRecording = true;
        this.isListening = true;
        this.isSpeaking = false;
        this.silenceStart = null;
        this.audioChunks = [];
        
        this.recorder.start();
        this.particleWave.setState('listening');
        
        // 设置超时
        this.listenTimeout = setTimeout(() => {
            if (this.isListening) {
                console.log('[VoiceController] 监听超时');
                this.stopRecording();
            }
        }, this.LISTEN_TIMEOUT_MS);
    }

    /**
     * 停止录音
     */
    stopRecording() {
        if (!this.isRecording) return;
        
        console.log('[VoiceController] 停止录音');
        this.isRecording = false;
        this.isListening = false;
        
        if (this.listenTimeout) {
            clearTimeout(this.listenTimeout);
            this.listenTimeout = null;
        }
        
        this.recorder.stop();
    }

    /**
     * 发送音频到 ASR
     */
    async sendToASR() {
        if (this.audioChunks.length === 0) {
            console.warn('[VoiceController] 没有录音数据');
            return;
        }
        
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        this.audioChunks = [];
        
        console.log('[VoiceController] 发送到 ASR，大小:', audioBlob.size);
        this.particleWave.setState('thinking');
        this.asrStartTime = Date.now();
        
        try {
            const formData = new FormData();
            formData.append('file', audioBlob, 'audio.webm');
            
            const response = await fetch(this.ASR_URL, {
                method: 'POST',
                body: formData
            });
            
            const latency = Date.now() - this.asrStartTime;
            console.log('[VoiceController] ASR 延迟:', latency, 'ms');
            
            if (this.onLatencyUpdate) {
                this.onLatencyUpdate('asr', latency);
            }
            
            if (!response.ok) {
                throw new Error(`ASR 请求失败: ${response.status}`);
            }
            
            const result = await response.json();
            const text = result.text || result.transcription || '';
            
            console.log('[VoiceController] ASR 结果:', text);
            
            // 检查是否为唤醒词
            if (this.isWakeWord(text)) {
                console.log('[VoiceController] 检测到唤醒词');
                this.startRecording();
                return;
            }
            
            // 检查是否为打断词
            if (this.isInterruptWord(text)) {
                console.log('[VoiceController] 检测到打断词');
                this.interrupt();
                return;
            }
            
            // 传递转录结果
            if (this.onTranscript && text.trim()) {
                this.onTranscript(text.trim());
            } else {
                console.warn('[VoiceController] 未识别到有效文本');
                this.particleWave.setState('idle');
            }
            
        } catch (error) {
            console.error('[VoiceController] ASR 错误:', error);
            if (this.onError) {
                this.onError('语音识别失败: ' + error.message);
            }
            this.particleWave.setState('idle');
        }
    }

    /**
     * 判断是否为唤醒词
     */
    isWakeWord(text) {
        const normalized = text.replace(/[，。！？\s]/g, '').toLowerCase();
        return this.WAKE_WORDS.some(word => 
            normalized.includes(word.replace(/[，。！？\s]/g, '').toLowerCase())
        );
    }

    /**
     * 判断是否为打断词
     */
    isInterruptWord(text) {
        const normalized = text.replace(/[，。！？\s]/g, '').toLowerCase();
        return this.INTERRUPT_WORDS.some(word => 
            normalized.includes(word.replace(/[，。！？\s]/g, '').toLowerCase())
        );
    }

    /**
     * 播放 TTS 音频
     */
    async playTTS(text) {
        console.log('[VoiceController] 请求 TTS:', text);
        this.particleWave.setState('speaking');
        
        try {
            const response = await fetch(this.TTS_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `text=${encodeURIComponent(text)}&voice_id=${this.VOICE_ID}`
            });
            
            if (!response.ok) {
                throw new Error(`TTS 请求失败: ${response.status}`);
            }
            
            // 获取音频数据
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            
            // 播放音频
            this.audioElement = new Audio(audioUrl);
            this.currentPlayback = this.audioElement;
            
            this.audioElement.onended = () => {
                console.log('[VoiceController] TTS 播放完成');
                this.particleWave.setState('idle');
                URL.revokeObjectURL(audioUrl);
                this.currentPlayback = null;
            };
            
            this.audioElement.onerror = (error) => {
                console.error('[VoiceController] TTS 播放错误:', error);
                this.particleWave.setState('idle');
                URL.revokeObjectURL(audioUrl);
                this.currentPlayback = null;
            };
            
            await this.audioElement.play();
            console.log('[VoiceController] TTS 开始播放');
            
        } catch (error) {
            console.error('[VoiceController] TTS 错误:', error);
            if (this.onError) {
                this.onError('语音合成失败: ' + error.message);
            }
            this.particleWave.setState('idle');
        }
    }

    /**
     * 打断当前播放
     */
    interrupt() {
        console.log('[VoiceController] 打断');
        
        // 停止播放
        if (this.currentPlayback) {
            this.currentPlayback.pause();
            this.currentPlayback.currentTime = 0;
            this.currentPlayback = null;
        }
        
        // 停止录音
        if (this.isRecording) {
            this.recorder.stop();
            this.isRecording = false;
            this.isListening = false;
            this.audioChunks = [];
        }
        
        // 更新状态
        this.particleWave.setState('interrupted');
        
        // 触发回调
        if (this.onInterrupt) {
            this.onInterrupt();
        }
        
        // 3秒后恢复
        setTimeout(() => {
            this.particleWave.setState('idle');
        }, 3000);
    }

    /**
     * 销毁
     */
    destroy() {
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
        if (this.currentPlayback) {
            this.currentPlayback.pause();
        }
    }
}

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceController;
}
