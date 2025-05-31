// admin/src/utils/api.js - 更新版本，添加兼容性API

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

// 原有的API方法
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

// 🆕 新增：兼容性管理API
export const compatibilityAPI = {
  // 兼容性规则管理
  rules: {
    // 基础CRUD操作
    list: (params = {}) => api.get('/admin/compatibility/rules', { params }),
    get: (id) => api.get(`/admin/compatibility/rules/${id}`),
    create: (data) => api.post('/admin/compatibility/rules', data),
    update: (id, data) => api.put(`/admin/compatibility/rules/${id}`, data),
    
    // 🔥 状态管理 - 重点区分删除和停用
    disable: (id) => api.patch(`/admin/compatibility/rules/${id}/disable`),
    enable: (id) => api.patch(`/admin/compatibility/rules/${id}/enable`),
    delete: (id, force = false) => {
      const url = `/admin/compatibility/rules/${id}${force ? '?force=true' : ''}`
      return api.delete(url)
    },
    
    // 🚀 批量操作
    batchDisable: (ruleIds) => api.patch('/admin/compatibility/rules/batch/disable', ruleIds),
    batchEnable: (ruleIds) => api.patch('/admin/compatibility/rules/batch/enable', ruleIds),
    
    // ⚡ 验证和测试
    validate: (expression) => api.post('/admin/compatibility/rules/validate', { expression }),
    test: (id, testData) => api.post(`/admin/compatibility/rules/${id}/test`, testData),
    
    // 🔧 辅助功能
    getCategories: () => api.get('/admin/compatibility/categories'),
    getFunctions: () => api.get('/admin/compatibility/expression-functions')
  },

  // 兼容性经验管理
  experiences: {
    list: (params = {}) => api.get('/admin/compatibility/experiences', { params }),
    get: (id) => api.get(`/admin/compatibility/experiences/${id}`),
    create: (data) => api.post('/admin/compatibility/experiences', data),
    update: (id, data) => api.put(`/admin/compatibility/experiences/${id}`, data),
    delete: (id) => api.delete(`/admin/compatibility/experiences/${id}`),
    batchCreate: (data) => api.post('/admin/compatibility/experiences/batch', data)
  },

  // 🎯 公开兼容性检查API
  check: {
    // 兼容性检查
    check: (data) => api.post('/public/compatibility/check', data),
    search: (data) => api.post('/public/compatibility/search', data),
    quickCheck: (partAId, partBId) => api.get('/public/compatibility/quick-check', { 
      params: { part_a_id: partAId, part_b_id: partBId } 
    }),
    suggestions: (partId, params = {}) => api.get(`/public/compatibility/suggestions/${partId}`, { params }),
    
    // 系统信息
    systemStatus: () => api.get('/public/compatibility/system-status'),
    feedbackChannels: () => api.get('/public/compatibility/feedback-channels'),
    knowledgeBase: (params = {}) => api.get('/public/compatibility/knowledge-base', { params }),
    version: () => api.get('/public/compatibility/version'),
    examples: () => api.get('/public/compatibility/examples')
  },

  // 📊 系统管理和监控
  system: {
    // 统计信息
    stats: () => api.get('/admin/compatibility/stats'),
    
    // 审计日志
    auditLog: (params = {}) => api.get('/admin/compatibility/audit-log', { params }),
    
    // 安全报告
    securityReport: () => api.get('/admin/compatibility/security-report'),
    
    // 缓存管理
    clearCache: (params = {}) => api.post('/admin/compatibility/clear-cache', params),
    
    // 系统工具
    getCategories: () => api.get('/admin/compatibility/categories'),
    getFunctions: () => api.get('/admin/compatibility/expression-functions')
  }
}

// 🆕 新增：文件和上传相关API（如果需要配置文件导入导出）
export const fileAPI = {
  // 配置文件导出
  exportConfig: (format = 'json') => api.get(`/admin/compatibility/export?format=${format}`, {
    responseType: 'blob'
  }),
  
  // 配置文件导入
  importConfig: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/admin/compatibility/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 验证配置文件
  validateConfigFile: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/admin/compatibility/validate-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

// 🔧 兼容性API的便捷封装方法
export const compatibilityHelpers = {
  // 获取完整配置（用于编辑器加载）
  async getFullConfig() {
    try {
      const [rulesRes, experiencesRes, statsRes] = await Promise.all([
        compatibilityAPI.rules.list({ limit: 1000 }),
        compatibilityAPI.experiences.list({ limit: 1000 }),
        compatibilityAPI.system.stats()
      ])

      return {
        metadata: {
          description: "OpenPart 兼容性配置文件",
          version: "1.0.0",
          last_updated: new Date().toISOString(),
          total_rules: rulesRes.data.total,
          active_rules: rulesRes.data.items.filter(r => r.is_active).length,
          total_experiences: experiencesRes.data.total,
          system_stats: statsRes.data
        },
        compatibility_rules: rulesRes.data.items,
        compatibility_experiences: experiencesRes.data.items
      }
    } catch (error) {
      console.error('获取完整配置失败:', error)
      throw error
    }
  },

  // 保存完整配置（从编辑器保存）
  async saveFullConfig(config) {
    try {
      const results = {
        rules: { created: 0, updated: 0, errors: [] },
        experiences: { created: 0, updated: 0, errors: [] }
      }

      // 处理规则
      if (config.compatibility_rules) {
        for (const rule of config.compatibility_rules) {
          try {
            if (rule.id) {
              // 更新现有规则
              await compatibilityAPI.rules.update(rule.id, {
                name: rule.name,
                description: rule.description,
                rule_expression: rule.expression,
                category_a: rule.category_a,
                category_b: rule.category_b,
                weight: rule.weight,
                is_blocking: rule.is_blocking
              })
              
              // 处理启用/停用状态
              const currentRule = await compatibilityAPI.rules.get(rule.id)
              if (currentRule.data.is_active !== rule.is_active) {
                if (rule.is_active) {
                  await compatibilityAPI.rules.enable(rule.id)
                } else {
                  await compatibilityAPI.rules.disable(rule.id)
                }
              }
              
              results.rules.updated++
            } else {
              // 创建新规则
              const newRule = await compatibilityAPI.rules.create({
                name: rule.name,
                description: rule.description,
                rule_expression: rule.expression,
                category_a: rule.category_a,
                category_b: rule.category_b,
                weight: rule.weight,
                is_blocking: rule.is_blocking
              })
              
              // 如果需要停用新创建的规则
              if (!rule.is_active) {
                await compatibilityAPI.rules.disable(newRule.data.id)
              }
              
              results.rules.created++
            }
          } catch (error) {
            results.rules.errors.push({
              rule: rule.name,
              error: error.message
            })
          }
        }
      }

      // 处理经验数据
      if (config.compatibility_experiences) {
        for (const experience of config.compatibility_experiences) {
          try {
            if (experience.id) {
              await compatibilityAPI.experiences.update(experience.id, experience)
              results.experiences.updated++
            } else {
              await compatibilityAPI.experiences.create(experience)
              results.experiences.created++
            }
          } catch (error) {
            results.experiences.errors.push({
              experience: `${experience.part_a_id}-${experience.part_b_id}`,
              error: error.message
            })
          }
        }
      }

      return results
    } catch (error) {
      console.error('保存完整配置失败:', error)
      throw error
    }
  },

  // 批量验证规则表达式
  async validateAllExpressions(rules) {
    const results = []
    
    for (const rule of rules) {
      if (rule.expression) {
        try {
          const validationResult = await compatibilityAPI.rules.validate(rule.expression)
          results.push({
            rule: rule.name,
            expression: rule.expression,
            valid: validationResult.is_safe,
            issues: validationResult.security_issues,
            recommendations: validationResult.recommendations
          })
        } catch (error) {
          results.push({
            rule: rule.name,
            expression: rule.expression,
            valid: false,
            error: error.message
          })
        }
      }
    }
    
    return results
  },

  // 获取所有可用的零件类别
  async getAvailableCategories() {
    try {
      const [partsCategoriesRes, compatCategoriesRes] = await Promise.all([
        partsAPI.getParts({ limit: 1 }), // 只获取一个零件来获取类别信息
        compatibilityAPI.system.getCategories()
      ])
      
      // 合并并去重类别
      const allCategories = new Set()
      
      if (compatCategoriesRes.data) {
        compatCategoriesRes.data.forEach(cat => allCategories.add(cat))
      }
      
      return Array.from(allCategories).sort()
    } catch (error) {
      console.warn('获取类别列表失败:', error)
      return ['CPU', '主板', '内存', '显卡', '电源', '散热器', '存储', '机箱']
    }
  },

  // 获取安全函数列表
  async getSafeFunctions() {
    try {
      const response = await compatibilityAPI.system.getFunctions()
      return response.data
    } catch (error) {
      console.warn('获取安全函数列表失败:', error)
      return [
        { name: 'safe_get(obj, "key", default)', description: '安全获取对象属性值' },
        { name: 'abs(number)', description: '返回数字的绝对值' },
        { name: 'min(...values)', description: '返回最小值' },
        { name: 'max(...values)', description: '返回最大值' },
        { name: 'sum(array)', description: '计算数组元素之和' },
        { name: 'len(array)', description: '返回数组长度' },
        { name: 'round(number, digits)', description: '四舍五入到指定位数' },
        { name: 'all(array)', description: '所有元素都为真时返回true' },
        { name: 'any(array)', description: '任一元素为真时返回true' }
      ]
    }
  }
}

// 导出默认api实例
export default api