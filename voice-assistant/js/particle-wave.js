/**
 * ParticleWave - 粒子波形可视化模块
 * 使用 Canvas API 渲染抽象粒子线，支持情绪色彩映射
 */

class ParticleWave {
    constructor(canvasId, themeManager) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.themeManager = themeManager;
        
        // 状态
        this.state = 'idle'; // idle | listening | thinking | speaking | interrupted
        this.emotionColor = this.themeManager.getColor('idle');
        
        // 粒子配置
        this.particleCount = 300;
        this.particles = [];
        this.audioData = null;
        this.breathPhase = 0; // 呼吸动画相位
        
        // 动画
        this.animationId = null;
        
        this.init();
    }

    init() {
        this.resizeCanvas();
        this.createParticles();
        this.startAnimation();
        
        // 监听窗口大小变化
        window.addEventListener('resize', () => this.resizeCanvas());
        
        // 监听主题变化
        window.addEventListener('themechange', () => {
            this.emotionColor = this.themeManager.getColor(this.state);
        });
        
        console.log('[ParticleWave] 初始化完成，粒子数:', this.particleCount);
    }

    /**
     * 调整 Canvas 尺寸
     */
    resizeCanvas() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width * window.devicePixelRatio;
        this.canvas.height = rect.height * window.devicePixelRatio;
        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = rect.height + 'px';
        this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        
        // 重新创建粒子
        this.createParticles();
    }

    /**
     * 创建粒子
     */
    createParticles() {
        this.particles = [];
        const width = this.canvas.width / window.devicePixelRatio;
        const height = this.canvas.height / window.devicePixelRatio;
        
        for (let i = 0; i < this.particleCount; i++) {
            this.particles.push({
                x: (i / this.particleCount) * width,
                baseY: height / 2,
                y: height / 2,
                size: Math.random() * 2 + 1,
                speed: Math.random() * 0.02 + 0.01,
                offset: Math.random() * Math.PI * 2
            });
        }
    }

    /**
     * 设置状态
     */
    setState(state) {
        this.state = state;
        this.emotionColor = this.themeManager.getColor(state);
        console.log('[ParticleWave] 状态切换:', state, '颜色:', this.emotionColor);
    }

    /**
     * 更新音频数据
     */
    updateAudioData(frequencyData) {
        this.audioData = frequencyData;
    }

    /**
     * 设置情绪颜色
     */
    setEmotionColor(color) {
        this.emotionColor = color;
    }

    /**
     * 开始动画
     */
    startAnimation() {
        const animate = () => {
            this.render();
            this.animationId = requestAnimationFrame(animate);
        };
        animate();
    }

    /**
     * 停止动画
     */
    stopAnimation() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    /**
     * 渲染粒子波形
     */
    render() {
        const width = this.canvas.width / window.devicePixelRatio;
        const height = this.canvas.height / window.devicePixelRatio;
        
        // 清空画布
        this.ctx.clearRect(0, 0, width, height);
        
        // 更新呼吸相位
        this.breathPhase += 0.02;
        
        // 根据状态更新粒子位置
        this.particles.forEach((particle, i) => {
            let amplitude = 0;
            
            switch (this.state) {
                case 'idle':
                    // 呼吸动画 - 5秒周期
                    amplitude = Math.sin(this.breathPhase + particle.offset) * 20;
                    break;
                    
                case 'listening':
                    // 随音频跳动
                    if (this.audioData && this.audioData.length > 0) {
                        const dataIndex = Math.floor((i / this.particleCount) * this.audioData.length);
                        const audioValue = this.audioData[dataIndex] / 255;
                        amplitude = audioValue * height * 0.3;
                    } else {
                        // 无音频数据时的默认动画
                        amplitude = Math.sin(this.breathPhase * 2 + particle.offset) * 30;
                    }
                    break;
                    
                case 'thinking':
                    // 快速闪烁
                    amplitude = Math.sin(this.breathPhase * 5 + particle.offset) * 40 * 
                               (0.5 + Math.random() * 0.5);
                    break;
                    
                case 'speaking':
                    // 流动效果
                    if (this.audioData && this.audioData.length > 0) {
                        const dataIndex = Math.floor((i / this.particleCount) * this.audioData.length);
                        const audioValue = this.audioData[dataIndex] / 255;
                        amplitude = audioValue * height * 0.25;
                    } else {
                        amplitude = Math.sin(this.breathPhase * 3 + particle.offset + i * 0.1) * 35;
                    }
                    break;
                    
                case 'interrupted':
                    // 震动效果
                    amplitude = Math.sin(this.breathPhase * 10 + particle.offset) * 60 * 
                               Math.abs(Math.sin(this.breathPhase * 2));
                    break;
            }
            
            particle.y = particle.baseY + amplitude;
        });
        
        // 绘制粒子
        this.drawParticles();
        
        // 绘制连接线
        this.drawConnections();
    }

    /**
     * 绘制粒子
     */
    drawParticles() {
        this.ctx.fillStyle = this.emotionColor;
        this.ctx.shadowBlur = 10;
        this.ctx.shadowColor = this.emotionColor;
        
        this.particles.forEach(particle => {
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fill();
        });
        
        this.ctx.shadowBlur = 0;
    }

    /**
     * 绘制连接线
     */
    drawConnections() {
        this.ctx.strokeStyle = this.emotionColor;
        this.ctx.lineWidth = 1;
        this.ctx.globalAlpha = 0.3;
        
        this.ctx.beginPath();
        this.particles.forEach((particle, i) => {
            if (i === 0) {
                this.ctx.moveTo(particle.x, particle.y);
            } else {
                this.ctx.lineTo(particle.x, particle.y);
            }
        });
        this.ctx.stroke();
        
        this.ctx.globalAlpha = 1;
    }

    /**
     * 销毁
     */
    destroy() {
        this.stopAnimation();
        window.removeEventListener('resize', this.resizeCanvas);
    }
}

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ParticleWave;
}
