const TOKEN_KEY = 'openpart_admin_token'
const USER_KEY = 'openpart_admin_user'
const LAST_ACTIVITY_KEY = 'openpart_last_activity'

// 配置项
const AUTH_CONFIG = {
  SESSION_TIMEOUT: 30 * 60 * 1000, // 30分钟无活动自动登出
  TOKEN_CHECK_INTERVAL: 5 * 60 * 1000, // 每5分钟检查一次token有效性
  ACTIVITY_UPDATE_INTERVAL: 60 * 1000 // 每分钟更新活动时间
}

class AuthManager {
  constructor() {
    this.tokenCheckTimer = null
    this.activityUpdateTimer = null
    this.isCheckingToken = false
    this.setupActivityMonitoring()
  }

  // 获取token
  getToken() {
    return localStorage.getItem(TOKEN_KEY)
  }

  // 设置token
  setToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
    this.updateLastActivity()
  }

  // 移除token和相关数据
  removeToken() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem(LAST_ACTIVITY_KEY)
    this.stopMonitoring()
  }

  // 获取用户信息
  getUser() {
    const user = localStorage.getItem(USER_KEY)
    return user ? JSON.parse(user) : null
  }

  // 设置用户信息
  setUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  }

  // 检查是否已登录（仅检查token存在）
  isAuthenticated() {
    return !!this.getToken()
  }

  // 🆕 验证token有效性（发送API请求验证）
  async validateToken() {
    if (!this.getToken()) {
      return false
    }

    // 防止重复验证
    if (this.isCheckingToken) {
      return true
    }

    try {
      this.isCheckingToken = true
      
      // 发送验证请求 - 使用最轻量级的API
      const response = await fetch('/api/auth/users/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getToken()}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        this.updateLastActivity()
        return true
      } else if (response.status === 401) {
        // token无效
        console.log('Token验证失败：未授权')
        return false
      } else {
        // 其他错误，暂时认为token有效，避免频繁登出
        console.warn('Token验证请求失败：', response.status)
        return true
      }
    } catch (error) {
      // 网络错误等，暂时认为token有效
      console.warn('Token验证网络错误：', error.message)
      return true
    } finally {
      this.isCheckingToken = false
    }
  }

  // 🆕 检查会话是否超时
  isSessionExpired() {
    const lastActivity = localStorage.getItem(LAST_ACTIVITY_KEY)
    if (!lastActivity) {
      return false
    }

    const timeSinceActivity = Date.now() - parseInt(lastActivity)
    return timeSinceActivity > AUTH_CONFIG.SESSION_TIMEOUT
  }

  // 🆕 更新最后活动时间
  updateLastActivity() {
    localStorage.setItem(LAST_ACTIVITY_KEY, Date.now().toString())
  }

  // 🆕 设置活动监控
  setupActivityMonitoring() {
    // 监听用户活动
    const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click']
    
    const updateActivity = () => {
      if (this.isAuthenticated()) {
        this.updateLastActivity()
      }
    }

    // 添加事件监听器
    activityEvents.forEach(event => {
      document.addEventListener(event, updateActivity, { passive: true })
    })

    // 定期检查会话超时
    this.activityUpdateTimer = setInterval(() => {
      if (this.isAuthenticated()) {
        if (this.isSessionExpired()) {
          console.log('会话超时，自动登出')
          this.logout()
          // 显示超时消息
          if (window.ElMessage) {
            window.ElMessage.warning('会话已超时，请重新登录')
          }
          // 跳转到登录页
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
        }
      }
    }, AUTH_CONFIG.ACTIVITY_UPDATE_INTERVAL)
  }

  // 🆕 停止监控
  stopMonitoring() {
    if (this.tokenCheckTimer) {
      clearInterval(this.tokenCheckTimer)
      this.tokenCheckTimer = null
    }
    if (this.activityUpdateTimer) {
      clearInterval(this.activityUpdateTimer)
      this.activityUpdateTimer = null
    }
  }

  // 🆕 增强的登出方法
  logout() {
    console.log('用户登出')
    
    // 清理存储的数据
    this.removeToken()
    
    // 停止所有监控
    this.stopMonitoring()
    
    // 清理可能的用户数据缓存
    if (window.sessionStorage) {
      sessionStorage.clear()
    }
  }

  // 🆕 获取会话信息（用于调试）
  getSessionInfo() {
    const lastActivity = localStorage.getItem(LAST_ACTIVITY_KEY)
    const token = this.getToken()
    
    return {
      hasToken: !!token,
      lastActivity: lastActivity ? new Date(parseInt(lastActivity)).toLocaleString() : null,
      sessionTimeRemaining: lastActivity ? 
        Math.max(0, AUTH_CONFIG.SESSION_TIMEOUT - (Date.now() - parseInt(lastActivity))) : 0,
      isSessionExpired: this.isSessionExpired()
    }
  }
}

// 创建单例实例
export const auth = new AuthManager()

// 🆕 开发环境调试工具
if (process.env.NODE_ENV === 'development') {
  window.authDebug = {
    getSessionInfo: () => auth.getSessionInfo(),
    forceLogout: () => auth.logout(),
    checkToken: () => auth.validateToken(),
    config: AUTH_CONFIG
  }
  console.log('🔐 Auth Debug工具已加载到 window.authDebug')
}