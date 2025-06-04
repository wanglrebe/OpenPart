import { auth } from '../utils/auth'

// 路由守卫配置
const GUARD_CONFIG = {
  VALIDATION_TIMEOUT: 5000, // token验证超时时间（5秒）
  RETRY_ATTEMPTS: 2, // 验证失败重试次数
  SKIP_VALIDATION_PATHS: ['/login'], // 跳过验证的路径
}

// 🆕 验证结果缓存（避免频繁验证）
const validationCache = {
  lastValidation: 0,
  isValid: false,
  cacheTimeout: 2 * 60 * 1000, // 2分钟缓存
  
  isValidCached() {
    const now = Date.now()
    return (now - this.lastValidation) < this.cacheTimeout && this.isValid
  },
  
  updateCache(isValid) {
    this.lastValidation = Date.now()
    this.isValid = isValid
  },
  
  clearCache() {
    this.lastValidation = 0
    this.isValid = false
  }
}

// 🆕 路由守卫增强功能
export function setupRouterGuards(router) {
  // 全局前置守卫
  router.beforeEach(async (to, from, next) => {
    const startTime = Date.now()
    
    try {
      // 如果要去登录页且已经登录，重定向到首页
      if (to.name === 'Login' && auth.isAuthenticated()) {
        console.log('👤 已登录用户访问登录页，重定向到仪表板')
        next({ name: 'Dashboard' })
        return
      }
      
      // 如果页面不需要认证，直接通过
      if (!to.meta.requiresAuth) {
        next()
        return
      }
      
      // 检查基础认证状态
      const hasToken = auth.isAuthenticated()
      if (!hasToken) {
        console.log('❌ 未登录用户尝试访问受保护页面，重定向到登录页')
        next({ name: 'Login' })
        return
      }
      
      // 🆕 检查会话是否超时
      if (auth.isSessionExpired()) {
        console.log('⏰ 会话已超时，自动登出')
        auth.logout()
        if (window.ElMessage) {
          window.ElMessage.warning('会话已超时，请重新登录')
        }
        next({ name: 'Login' })
        return
      }
      
      // 🆕 使用缓存避免频繁验证
      if (validationCache.isValidCached()) {
        console.log('✅ 使用缓存的验证结果')
        next()
        return
      }
      
      // 🆕 验证token有效性
      console.log('🔐 验证token有效性...')
      const isValidToken = await validateTokenWithRetry()
      
      if (isValidToken) {
        // 验证成功，更新缓存
        validationCache.updateCache(true)
        console.log(`✅ Token验证成功 (${Date.now() - startTime}ms)`)
        next()
      } else {
        // 验证失败，清理并跳转登录
        console.log('❌ Token验证失败，清理登录状态')
        validationCache.clearCache()
        auth.logout()
        
        if (window.ElMessage) {
          window.ElMessage.error('登录已失效，请重新登录')
        }
        
        next({ name: 'Login' })
      }
      
    } catch (error) {
      console.error('🚨 路由守卫异常:', error)
      
      // 异常情况下的处理策略
      if (to.name === 'Login') {
        // 如果目标是登录页，直接放行
        next()
      } else {
        // 其他页面，为了安全起见跳转到登录页
        if (window.ElMessage) {
          window.ElMessage.error('系统异常，请重新登录')
        }
        next({ name: 'Login' })
      }
    }
  })
  
  // 🆕 全局后置守卫（用于记录和分析）
  router.afterEach((to, from, failure) => {
    if (failure) {
      console.error('🚨 路由跳转失败:', failure)
      return
    }
    
    // 记录页面访问（可用于分析用户行为）
    console.log(`📄 页面跳转: ${from.name || 'Unknown'} → ${to.name || 'Unknown'}`)
    
    // 🆕 更新用户活动时间
    if (to.meta.requiresAuth && auth.isAuthenticated()) {
      auth.updateLastActivity()
    }
    
    // 🆕 清理过期的验证缓存
    if (to.name === 'Login') {
      validationCache.clearCache()
    }
  })
  
  // 🆕 路由错误处理
  router.onError((error) => {
    console.error('🚨 路由系统错误:', error)
    
    // 如果是认证相关错误，跳转到登录页
    if (error.message.includes('401') || error.message.includes('unauthorized')) {
      auth.logout()
      router.push('/login')
    }
  })
}

// 🆕 带重试机制的token验证
async function validateTokenWithRetry() {
  let attempts = 0
  
  while (attempts < GUARD_CONFIG.RETRY_ATTEMPTS) {
    try {
      // 设置验证超时
      const validationPromise = auth.validateToken()
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Validation timeout')), GUARD_CONFIG.VALIDATION_TIMEOUT)
      })
      
      const isValid = await Promise.race([validationPromise, timeoutPromise])
      
      if (isValid) {
        return true
      } else {
        console.log(`❌ Token验证失败 (尝试 ${attempts + 1}/${GUARD_CONFIG.RETRY_ATTEMPTS})`)
        attempts++
        
        // 如果不是最后一次尝试，等待一下再重试
        if (attempts < GUARD_CONFIG.RETRY_ATTEMPTS) {
          await new Promise(resolve => setTimeout(resolve, 1000))
        }
      }
    } catch (error) {
      console.warn(`⚠️ Token验证异常 (尝试 ${attempts + 1}/${GUARD_CONFIG.RETRY_ATTEMPTS}):`, error.message)
      attempts++
      
      // 超时或网络错误，如果不是最后一次尝试，等待后重试
      if (attempts < GUARD_CONFIG.RETRY_ATTEMPTS) {
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
    }
  }
  
  // 所有尝试都失败了
  console.error('❌ Token验证最终失败')
  return false
}

// 🆕 开发环境调试工具
if (process.env.NODE_ENV === 'development') {
  window.guardDebug = {
    validationCache,
    config: GUARD_CONFIG,
    forceValidation: () => {
      validationCache.clearCache()
      return auth.validateToken()
    },
    clearCache: () => validationCache.clearCache()
  }
  console.log('🛡️ Guard Debug工具已加载到 window.guardDebug')
}