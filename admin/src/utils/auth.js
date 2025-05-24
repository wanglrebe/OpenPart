const TOKEN_KEY = 'openpart_admin_token'
const USER_KEY = 'openpart_admin_user'

export const auth = {
  // 获取token
  getToken() {
    return localStorage.getItem(TOKEN_KEY)
  },

  // 设置token
  setToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
  },

  // 移除token
  removeToken() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },

  // 获取用户信息
  getUser() {
    const user = localStorage.getItem(USER_KEY)
    return user ? JSON.parse(user) : null
  },

  // 设置用户信息
  setUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },

  // 检查是否已登录
  isAuthenticated() {
    return !!this.getToken()
  },

  // 登出
  logout() {
    this.removeToken()
    // 可以在这里添加其他登出逻辑
  }
}