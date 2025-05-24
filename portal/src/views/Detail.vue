<!-- portal/src/views/Detail.vue -->
<template>
  <div class="detail-page">
    <!-- 头部导航 -->
    <header class="detail-header">
      <div class="container">
        <div class="detail-nav">
          <button class="back-btn" @click="goBack">
            <svg class="back-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            返回搜索
          </button>
          
          <div class="nav-actions">
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
    
    <!-- 详情内容 -->
    <main class="detail-main">
      <div class="container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="error" class="error-container">
          <div class="error-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3>加载失败</h3>
          <p>{{ error }}</p>
          <button class="btn btn-primary" @click="loadPart">
            重试
          </button>
        </div>
        
        <!-- 零件详情 -->
        <div v-else-if="part" class="part-detail">
          <div class="detail-grid">
            <!-- 左侧：图片和基本信息 -->
            <div class="detail-left">
              <div class="part-image-container">
                <img 
                  v-if="part.image_url && !imageError" 
                  :src="part.image_url" 
                  :alt="part.name"
                  class="part-image"
                  @error="onImageError"
                />
                <div v-else class="part-placeholder">
                  <svg class="placeholder-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  <p>暂无图片</p>
                </div>
              </div>
              
              <!-- 操作按钮 -->
              <div class="action-buttons">
                <button class="btn btn-primary" @click="toggleFavorite">
                  <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                  收藏零件
                </button>
                <button class="btn btn-outline" @click="addToCompare">
                  <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  添加到对比
                </button>
              </div>
            </div>
            
            <!-- 右侧：详细信息 -->
            <div class="detail-right">
              <div class="part-info">
                <div class="part-header">
                  <h1 class="part-name">{{ part.name }}</h1>
                  <span v-if="part.category" class="part-category">{{ part.category }}</span>
                </div>
                
                <p v-if="part.description" class="part-description">
                  {{ part.description }}
                </p>
                
                <!-- 详细参数 -->
                <div v-if="part.properties && Object.keys(part.properties).length > 0" class="part-specifications">
                  <h3 class="spec-title">详细参数</h3>
                  <div class="spec-grid">
                    <div 
                      v-for="[key, value] in Object.entries(part.properties)" 
                      :key="key"
                      class="spec-item"
                    >
                      <div class="spec-key">{{ key }}</div>
                      <div class="spec-value">{{ value }}</div>
                    </div>
                  </div>
                </div>
                
                <!-- 元数据 -->
                <div class="part-metadata">
                  <h3 class="meta-title">其他信息</h3>
                  <div class="meta-grid">
                    <div class="meta-item">
                      <div class="meta-key">零件ID</div>
                      <div class="meta-value">#{{ part.id }}</div>
                    </div>
                    <div class="meta-item">
                      <div class="meta-key">创建时间</div>
                      <div class="meta-value">{{ formatDate(part.created_at) }}</div>
                    </div>
                    <div v-if="part.updated_at" class="meta-item">
                      <div class="meta-key">更新时间</div>
                      <div class="meta-value">{{ formatDate(part.updated_at) }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import { partsAPI } from '../utils/api'

export default {
  name: 'Detail',
  components: {
    ThemeToggle
  },
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  setup(props) {
    const route = useRoute()
    const router = useRouter()
    
    const part = ref(null)
    const loading = ref(false)
    const error = ref('')
    const imageError = ref(false)
    
    const loadPart = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await partsAPI.getPart(props.id)
        part.value = response.data
      } catch (err) {
        console.error('加载零件详情失败:', err)
        error.value = '零件不存在或加载失败'
      }
      
      loading.value = false
    }
    
    const goBack = () => {
      if (window.history.length > 2) {
        router.go(-1)
      } else {
        router.push('/')
      }
    }
    
    const onImageError = () => {
      imageError.value = true
    }
    
    const toggleFavorite = () => {
      console.log('收藏零件:', part.value.name)
      // TODO: 实现收藏功能
    }
    
    const addToCompare = () => {
      console.log('添加到对比:', part.value.name)
      // TODO: 实现对比功能
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('zh-CN')
    }
    
    onMounted(() => {
      loadPart()
    })
    
    return {
      part,
      loading,
      error,
      imageError,
      loadPart,
      goBack,
      onImageError,
      toggleFavorite,
      addToCompare,
      formatDate
    }
  }
}
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* 头部导航 */
.detail-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 0;
}

.detail-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--primary);
}

.back-icon {
  width: 16px;
  height: 16px;
}

/* 主要内容 */
.detail-main {
  padding: 32px 0;
}

/* 加载和错误状态 */
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.error-icon {
  width: 64px;
  height: 64px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

/* 零件详情 */
.detail-grid {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 48px;
  align-items: start;
}

.detail-left {
  position: sticky;
  top: 100px;
}

.part-image-container {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 24px;
}

.part-image {
  width: 100%;
  height: 300px;
  object-fit: cover;
}

.part-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-muted);
}

.placeholder-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 12px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* 详细信息 */
.part-info {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 32px;
}

.part-header {
  margin-bottom: 24px;
}

.part-name {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px 0;
  line-height: 1.2;
}

.part-category {
  display: inline-block;
  padding: 6px 12px;
  font-size: 14px;
  font-weight: 500;
  color: var(--primary);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  border-radius: 6px;
}

.part-description {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 32px 0;
}

.spec-title,
.meta-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--primary);
}

.spec-grid,
.meta-grid {
  display: grid;
  gap: 12px;
}

.spec-item,
.meta-item {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.spec-item:last-child,
.meta-item:last-child {
  border-bottom: none;
}

.spec-key,
.meta-key {
  font-weight: 500;
  color: var(--text-secondary);
}

.spec-value,
.meta-value {
  font-weight: 600;
  color: var(--text-primary);
}

.part-specifications {
  margin-bottom: 32px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }
  
  .detail-left {
    position: static;
    order: 2;
  }
  
  .detail-right {
    order: 1;
  }
  
  .part-image-container {
    margin-bottom: 16px;
  }
  
  .action-buttons {
    flex-direction: row;
  }
}

@media (max-width: 768px) {
  .detail-main {
    padding: 20px 0;
  }
  
  .part-info {
    padding: 20px;
  }
  
  .part-name {
    font-size: 24px;
  }
  
  .part-description {
    font-size: 15px;
  }
  
  .spec-item,
  .meta-item {
    grid-template-columns: 1fr;
    gap: 4px;
  }
  
  .spec-key,
  .meta-key {
    font-size: 13px;
  }
  
  .spec-value,
  .meta-value {
    font-size: 15px;
    font-weight: 500;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>