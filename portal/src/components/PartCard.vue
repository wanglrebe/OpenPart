<template>
  <div class="part-card" @click="goToDetail">
    <!-- 零件图片 -->
    <div class="part-image">
      <img 
        v-if="part.image_url" 
        :src="part.image_url" 
        :alt="part.name"
        class="part-img"
        @error="onImageError"
      />
      <div v-else class="part-placeholder">
        <svg class="placeholder-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
    </div>
    
    <!-- 零件信息 -->
    <div class="part-content">
      <div class="part-header">
        <h3 class="part-name">{{ part.name }}</h3>
        <span v-if="part.category" class="part-category">{{ part.category }}</span>
      </div>
      
      <p v-if="part.description" class="part-description">
        {{ part.description }}
      </p>
      
      <!-- 参数列表 -->
      <div v-if="part.properties && Object.keys(part.properties).length > 0" class="part-properties">
        <div 
          v-for="[key, value] in displayProperties" 
          :key="key"
          class="property-item"
        >
          <span class="property-key">{{ key }}:</span>
          <span class="property-value">{{ value }}</span>
        </div>
        
        <button 
          v-if="hiddenPropertiesCount > 0"
          class="show-more-btn"
          @click.stop="showAllProperties = !showAllProperties"
        >
          {{ showAllProperties ? '收起' : `+${hiddenPropertiesCount} 更多` }}
        </button>
      </div>
      
      <!-- 创建时间 -->
      <div class="part-meta">
        <span class="created-time">{{ formatTime(part.created_at) }}</span>
      </div>
    </div>
    
    <!-- 悬浮操作 -->
    <div class="part-actions">
      <button class="action-btn" @click.stop="toggleFavorite" title="收藏">
        <svg class="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      </button>
      
      <button class="action-btn" @click.stop="addToCompare" title="添加到对比">
        <svg class="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'PartCard',
  props: {
    part: {
      type: Object,
      required: true
    }
  },
  emits: ['favorite', 'compare'],
  setup(props, { emit }) {
    const router = useRouter()
    const showAllProperties = ref(false)
    const imageError = ref(false)
    
    // 显示的属性（限制显示数量）
    const displayProperties = computed(() => {
      if (!props.part.properties) return []
      
      const entries = Object.entries(props.part.properties)
      const maxDisplay = showAllProperties.value ? entries.length : 3
      
      return entries.slice(0, maxDisplay)
    })
    
    // 隐藏的属性数量
    const hiddenPropertiesCount = computed(() => {
      if (!props.part.properties) return 0
      return Math.max(0, Object.keys(props.part.properties).length - 3)
    })
    
    const goToDetail = () => {
      router.push({
        name: 'Detail',
        params: { id: props.part.id }
      })
    }
    
    const onImageError = () => {
      imageError.value = true
    }
    
    const toggleFavorite = () => {
      emit('favorite', props.part)
      // TODO: 实现收藏功能
    }
    
    const addToCompare = () => {
      emit('compare', props.part)
      // TODO: 实现对比功能
    }
    
    const formatTime = (timeString) => {
      if (!timeString) return ''
      
      const date = new Date(timeString)
      const now = new Date()
      const diffMs = now - date
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) return '今天'
      if (diffDays === 1) return '昨天'
      if (diffDays < 7) return `${diffDays}天前`
      if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前`
      if (diffDays < 365) return `${Math.floor(diffDays / 30)}个月前`
      
      return date.toLocaleDateString('zh-CN')
    }
    
    return {
      showAllProperties,
      imageError,
      displayProperties,
      hiddenPropertiesCount,
      goToDetail,
      onImageError,
      toggleFavorite,
      addToCompare,
      formatTime
    }
  }
}
</script>

<style scoped>
.part-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.part-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary);
}

.part-card:hover .part-actions {
  opacity: 1;
  transform: translateY(0);
}

.part-image {
  position: relative;
  width: 100%;
  height: 160px;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.part-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.part-card:hover .part-img {
  transform: scale(1.05);
}

.part-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.placeholder-icon {
  width: 48px;
  height: 48px;
  color: var(--text-muted);
}

.part-content {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.part-header {
  margin-bottom: 8px;
}

.part-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  line-height: 1.4;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.part-category {
  display: inline-block;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 500;
  color: var(--primary);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  border-radius: 4px;
}

.part-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 12px 0;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.part-properties {
  flex: 1;
  margin-bottom: 12px;
}

.property-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  font-size: 13px;
  border-bottom: 1px solid var(--border-color);
}

.property-item:last-child {
  border-bottom: none;
}

.property-key {
  color: var(--text-secondary);
  font-weight: 500;
  flex-shrink: 0;
  margin-right: 8px;
}

.property-value {
  color: var(--text-primary);
  font-weight: 600;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.show-more-btn {
  margin-top: 8px;
  padding: 4px 8px;
  font-size: 12px;
  color: var(--primary);
  background: none;
  border: 1px solid var(--primary);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.show-more-btn:hover {
  background: var(--primary);
  color: white;
}

.part-meta {
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

.created-time {
  font-size: 12px;
  color: var(--text-muted);
}

.part-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transform: translateY(-4px);
  transition: all 0.3s ease;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.9);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  backdrop-filter: blur(8px);
}

[data-theme="dark"] .action-btn {
  background: rgba(15, 23, 42, 0.9);
}

.action-btn:hover {
  background: var(--primary);
  color: white;
  transform: scale(1.1);
}

.action-icon {
  width: 16px;
  height: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .part-image {
    height: 140px;
  }
  
  .part-content {
    padding: 12px;
  }
  
  .part-name {
    font-size: 15px;
  }
  
  .part-description {
    font-size: 13px;
  }
  
  .property-item {
    font-size: 12px;
  }
  
  .part-actions {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 网格布局适配 */
@media (min-width: 1200px) {
  .part-image {
    height: 180px;
  }
}
</style>