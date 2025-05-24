import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/public/parts',
  timeout: 10000
})

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API错误:', error)
    return Promise.reject(error)
  }
)

// 防抖函数
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// API方法
export const partsAPI = {
  // 搜索零件
  search(params = {}) {
    return api.get('/search', { params })
  },
  
  // 获取零件列表
  getParts(params = {}) {
    return api.get('/', { params })
  },
  
  // 获取零件详情
  getPart(id) {
    return api.get(`/${id}`)
  },
  
  // 获取搜索建议
  getSuggestions(query) {
    return api.get('/suggestions', { params: { q: query } })
  },
  
  // 获取分类列表
  getCategories() {
    return api.get('/categories/')
  }
}

// 缓存管理
class Cache {
  constructor(ttl = 5 * 60 * 1000) { // 默认5分钟过期
    this.cache = new Map()
    this.ttl = ttl
  }
  
  set(key, value) {
    const expiry = Date.now() + this.ttl
    this.cache.set(key, { value, expiry })
  }
  
  get(key) {
    const item = this.cache.get(key)
    if (!item) return null
    
    if (Date.now() > item.expiry) {
      this.cache.delete(key)
      return null
    }
    
    return item.value
  }
  
  clear() {
    this.cache.clear()
  }
}

export const searchCache = new Cache()

export default api