/**
 * ThemeManager - 主题管理模块
 * 自动检测和切换系统深色/浅色主题
 */

class ThemeManager {
    constructor() {
        this.currentTheme = 'dark';
        this.mediaQuery = window.matchMedia('(prefers-color-scheme: light)');
        this.init();
    }

    init() {
        // 检测系统主题
        this.detectSystemTheme();
        
        // 监听系统主题变化
        this.watchSystemTheme();
        
        // 绑定主题切换按钮
        this.bindToggleButton();
        
        console.log('[ThemeManager] 初始化完成，当前主题:', this.currentTheme);
    }

    /**
     * 检测系统主题偏好
     */
    detectSystemTheme() {
        const savedTheme = localStorage.getItem('axis-theme');
        
        if (savedTheme) {
            // 使用用户保存的主题
            this.applyTheme(savedTheme);
        } else {
            // 跟随系统主题
            const isLight = this.mediaQuery.matches;
            this.applyTheme(isLight ? 'light' : 'dark');
        }
    }

    /**
     * 监听系统主题变化
     */
    watchSystemTheme() {
        this.mediaQuery.addEventListener('change', (e) => {
            // 只有在没有手动设置时才自动切换
            if (!localStorage.getItem('axis-theme')) {
                this.applyTheme(e.matches ? 'light' : 'dark');
            }
        });
    }

    /**
     * 应用主题
     */
    applyTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        
        // 更新图标
        const icon = document.getElementById('theme-icon');
        if (icon) {
            icon.textContent = theme === 'light' ? '☀️' : '🌙';
        }
        
        // 触发主题变化事件
        window.dispatchEvent(new CustomEvent('themechange', { 
            detail: { theme } 
        }));
        
        console.log('[ThemeManager] 主题已切换为:', theme);
    }

    /**
     * 切换主题
     */
    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
        localStorage.setItem('axis-theme', newTheme);
    }

    /**
     * 绑定切换按钮
     */
    bindToggleButton() {
        const btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.addEventListener('click', () => this.toggleTheme());
        }
    }

    /**
     * 获取当前主题
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * 获取当前主题下的颜色值
     */
    getColor(emotion) {
        const colors = {
            idle: this.currentTheme === 'dark' ? '#00d4ff' : '#0088cc',
            listening: this.currentTheme === 'dark' ? '#00ff88' : '#00cc66',
            thinking: this.currentTheme === 'dark' ? '#7b2cbf' : '#5a1d8f',
            speaking: this.currentTheme === 'dark' ? '#ff6b35' : '#cc5522',
            interrupted: this.currentTheme === 'dark' ? '#ff3366' : '#cc2244'
        };
        return colors[emotion] || colors.idle;
    }
}

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}
