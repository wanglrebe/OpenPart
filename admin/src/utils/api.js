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

// 认证API
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

// 零件API
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

// 兼容性规则管理API
export const compatibilityRules = {
  // 获取规则列表
  list(params = {}) {
    return api.get('/admin/compatibility/rules', { params })
  },

  // 获取单个规则详情
  get(id) {
    return api.get(`/admin/compatibility/rules/${id}`)
  },

  // 创建规则
  create(data) {
    return api.post('/admin/compatibility/rules', data)
  },

  // 更新规则
  update(id, data) {
    return api.put(`/admin/compatibility/rules/${id}`, data)
  },

  // 删除规则
  delete(id) {
    return api.delete(`/admin/compatibility/rules/${id}`)
  },

  // 验证表达式安全性
  validate(expression) {
    return api.post('/admin/compatibility/rules/validate', { expression })
  },

  // 测试规则执行
  test(id, testData) {
    return api.post(`/admin/compatibility/rules/${id}/test`, testData)
  }
}

// 兼容性经验管理API
export const compatibilityExperiences = {
  // 获取经验列表
  list(params = {}) {
    return api.get('/admin/compatibility/experiences', { params })
  },

  // 获取单个经验详情
  get(id) {
    return api.get(`/admin/compatibility/experiences/${id}`)
  },

  // 创建经验
  create(data) {
    return api.post('/admin/compatibility/experiences', data)
  },

  // 更新经验
  update(id, data) {
    return api.put(`/admin/compatibility/experiences/${id}`, data)
  },

  // 删除经验
  delete(id) {
    return api.delete(`/admin/compatibility/experiences/${id}`)
  },

  // 批量创建经验
  batchCreate(data) {
    return api.post('/admin/compatibility/experiences/batch', data)
  }
}

// 兼容性检查API（公开）
export const compatibilityCheck = {
  // 兼容性检查
  check(data) {
    return api.post('/public/compatibility/check', data)
  },

  // 兼容性搜索
  search(data) {
    return api.post('/public/compatibility/search', data)
  },

  // 快速兼容性检查
  quickCheck(partAId, partBId) {
    return api.get('/public/compatibility/quick-check', { 
      params: { part_a_id: partAId, part_b_id: partBId } 
    })
  },

  // 获取兼容性建议
  suggestions(partId, params = {}) {
    return api.get(`/public/compatibility/suggestions/${partId}`, { params })
  }
}

// 兼容性系统管理API
export const compatibilitySystem = {
  // 获取系统统计信息
  stats() {
    return api.get('/admin/compatibility/stats')
  },

  // 获取审计日志
  auditLog(params = {}) {
    return api.get('/admin/compatibility/audit-log', { params })
  },

  // 获取安全报告
  securityReport(params = {}) {
    return api.get('/admin/compatibility/security-report', { params })
  },

  // 清理缓存
  clearCache(params = {}) {
    return api.post('/admin/compatibility/clear-cache', {}, { params })
  },

  // 获取零件类别列表
  categories() {
    return api.get('/admin/compatibility/categories')
  },

  // 获取表达式函数列表
  functions() {
    return api.get('/admin/compatibility/expression-functions')
  },

  // 获取系统状态（公开API）
  systemStatus() {
    return api.get('/public/compatibility/system-status')
  },

  // 获取外部反馈渠道（公开API）
  feedbackChannels() {
    return api.get('/public/compatibility/feedback-channels')
  },

  // 获取兼容性知识库（公开API）
  knowledgeBase(params = {}) {
    return api.get('/public/compatibility/knowledge-base', { params })
  },

  // 获取API版本信息（公开API）
  version() {
    return api.get('/public/compatibility/version')
  },

  // 获取API示例（公开API）
  examples() {
    return api.get('/public/compatibility/examples')
  }
}

// 爬虫插件API（保持现有功能）
export const crawlerPluginsAPI = {
  // 获取插件列表
  list(params = {}) {
    return api.get('/admin/crawler-plugins/', { params })
  },

  // 获取插件详情
  get(id) {
    return api.get(`/admin/crawler-plugins/${id}`)
  },

  // 上传插件
  upload(file) {
    const formData = new FormData()
    formData.append('plugin_file', file)
    return api.post('/admin/crawler-plugins/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 启用插件
  enable(id) {
    return api.post(`/admin/crawler-plugins/${id}/enable`)
  },

  // 禁用插件
  disable(id) {
    return api.post(`/admin/crawler-plugins/${id}/disable`)
  },

  // 删除插件
  delete(id) {
    return api.delete(`/admin/crawler-plugins/${id}`)
  },

  // 测试插件
  test(id, config = {}) {
    return api.post(`/admin/crawler-plugins/${id}/test`, { config })
  },

  // 更新插件配置
  updateConfig(id, config) {
    return api.put(`/admin/crawler-plugins/${id}/config`, { config })
  },

  // 获取插件任务列表
  getTasks(id, params = {}) {
    return api.get(`/admin/crawler-plugins/${id}/tasks`, { params })
  },

  // 创建任务
  createTask(id, taskData) {
    return api.post(`/admin/crawler-plugins/${id}/tasks`, taskData)
  },

  // 执行任务
  executeTask(pluginId, taskId, config = {}) {
    return api.post(`/admin/crawler-plugins/${pluginId}/tasks/${taskId}/execute`, { config })
  },

  // 停止任务
  stopTask(pluginId, taskId) {
    return api.post(`/admin/crawler-plugins/${pluginId}/tasks/${taskId}/stop`)
  },

  // 获取任务日志
  getTaskLogs(taskId) {
    return api.get(`/admin/crawler-plugins/tasks/${taskId}/logs`)
  }
}

// 数据导入导出API（保持现有功能）
export const importExportAPI = {
  // 导出数据
  export(params) {
    return api.post('/admin/import-export/export', params, {
      responseType: 'blob'
    })
  },

  // 导入数据
  import(file, options = {}) {
    const formData = new FormData()
    formData.append('file', file)
    
    // 添加导入选项
    Object.keys(options).forEach(key => {
      formData.append(key, options[key])
    })
    
    return api.post('/admin/import-export/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 下载模板
  downloadTemplate(format = 'json') {
    return api.get('/admin/import-export/import/template', {
      params: { format },
      responseType: 'blob'
    })
  }
}

export default api