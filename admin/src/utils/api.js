import axios from 'axios'
import { auth } from './auth'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器 - 添加token
api.interceptors.request.use(
  config => {
    const token = auth.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          auth.logout()
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('权限不足')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(data.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误')
    }
    
    return Promise.reject(error)
  }
)

// API方法
export const authAPI = {
  // 登录
  login(credentials) {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    
    return api.post('/auth/token', formData)
  },

  // 获取当前用户信息
  getCurrentUser() {
    return api.get('/auth/users/me')
  },

  // 获取用户列表
  getUsers(params = {}) {
    return api.get('/auth/users', { params })
  },

  // 创建用户
  createUser(userData) {
    return api.post('/auth/users', userData)
  }
}

export const partsAPI = {
  // 获取零件列表（管理员）
  getParts(params = {}) {
    return api.get('/admin/parts/', { params })
  },

  // 获取零件详情
  getPart(id) {
    return api.get(`/admin/parts/${id}`)
  },

  // 创建零件
  createPart(partData) {
    return api.post('/admin/parts/', partData)
  },

  // 更新零件
  updatePart(id, partData) {
    return api.put(`/admin/parts/${id}`, partData)
  },

  // 删除零件
  deletePart(id) {
    return api.delete(`/admin/parts/${id}`)
  }
}

export default api