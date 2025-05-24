import { auth } from '../utils/auth'

// 路由守卫
export function setupRouterGuards(router) {
  // 全局前置守卫
  router.beforeEach((to, from, next) => {
    const isAuthenticated = auth.isAuthenticated()
    
    // 如果要去登录页且已经登录，重定向到首页
    if (to.name === 'Login' && isAuthenticated) {
      next({ name: 'Dashboard' })
      return
    }
    
    // 如果要去需要认证的页面且未登录，重定向到登录页
    if (to.meta.requiresAuth && !isAuthenticated) {
      next({ name: 'Login' })
      return
    }
    
    next()
  })
}