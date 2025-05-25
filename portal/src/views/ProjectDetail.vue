<!-- portal/src/views/ProjectDetail.vue (优化版本 - 显示零件名称和缩略图) -->
<template>
  <div class="project-detail-page">
    <!-- 头部导航 -->
    <header class="project-header">
      <div class="container">
        <div class="project-nav">
          <button class="back-btn" @click="goBack">
            <svg class="back-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            返回项目列表
          </button>
          
          <div class="nav-actions">
            <button class="action-btn" @click="showSettings = true" title="项目设置">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载项目详情...</p>
    </div>

    <!-- 项目不存在 -->
    <div v-else-if="!project" class="error-container">
      <div class="error-icon">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h3>项目不存在</h3>
      <p>请检查项目ID是否正确</p>
      <button class="btn btn-primary" @click="goBack">
        返回项目列表
      </button>
    </div>

    <!-- 项目详情内容 -->
    <main v-else class="project-main">
      <div class="container">
        <!-- 项目概览 -->
        <div class="project-overview">
          <div class="project-info">
            <div class="project-header-info">
              <h1 class="project-name">{{ project.name }}</h1>
              <span class="project-template">基于: {{ getTemplateName() }}</span>
            </div>
            <p v-if="project.description" class="project-description">
              {{ project.description }}
            </p>
          </div>

          <div class="project-stats">
            <div class="stat-card">
              <div class="stat-value">{{ Math.round(project.progress * 100) }}%</div>
              <div class="stat-label">完成进度</div>
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: `${project.progress * 100}%` }"
                ></div>
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-value">¥{{ project.actual_cost || 0 }}</div>
              <div class="stat-label">实际花费</div>
              <div class="budget-info">
                预算: ¥{{ project.budget_limit || project.estimated_cost }}
              </div>
            </div>
            
            <div class="stat-card">
              <div class="stat-value">{{ getOwnedCount() }}/{{ project.items.length }}</div>
              <div class="stat-label">零件进度</div>
              <div class="parts-breakdown">
                <span class="owned">{{ getOwnedCount() }} 已有</span>
                <span class="needed">{{ getNeededCount() }} 缺少</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 零件清单 -->
        <div class="parts-list-section">
          <!-- 操作栏 -->
          <div class="list-controls">
            <div class="controls-left">
              <h2>零件清单</h2>
              <div class="filter-buttons">
                <button 
                  class="filter-btn"
                  :class="{ active: statusFilter === 'all' }"
                  @click="statusFilter = 'all'"
                >
                  全部 ({{ project.items.length }})
                </button>
                <button 
                  class="filter-btn needed"
                  :class="{ active: statusFilter === 'needed' }"
                  @click="statusFilter = 'needed'"
                >
                  缺少 ({{ getNeededCount() }})
                </button>
                <button 
                  class="filter-btn owned"
                  :class="{ active: statusFilter === 'owned' }"
                  @click="statusFilter = 'owned'"
                >
                  已有 ({{ getOwnedCount() }})
                </button>
                <button 
                  class="filter-btn purchased"
                  :class="{ active: statusFilter === 'purchased' }"
                  @click="statusFilter = 'purchased'"
                >
                  已购 ({{ getPurchasedCount() }})
                </button>
              </div>
            </div>
            
            <div class="controls-right">
              <button class="btn btn-outline" @click="exportProject">
                <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
                导出清单
              </button>
            </div>
          </div>

          <!-- 零件列表 -->
          <div class="parts-list">
            <div 
              v-for="item in filteredItems" 
              :key="item.template_item_id"
              class="part-item"
              :class="{ 
                'required': getTemplateItem(item.template_item_id)?.is_required,
                'optional': !getTemplateItem(item.template_item_id)?.is_required,
                [item.status]: true 
              }"
            >
              <!-- 零件基本信息 -->
              <div class="part-info">
                <div class="part-header">
                  <h3 class="part-category">{{ getTemplateItem(item.template_item_id)?.category }}</h3>
                  <div class="part-badges">
                    <span 
                      class="required-badge" 
                      v-if="getTemplateItem(item.template_item_id)?.is_required"
                    >
                      必需
                    </span>
                    <span 
                      class="optional-badge" 
                      v-else
                    >
                      可选
                    </span>
                    <span class="status-badge" :class="item.status">
                      {{ getStatusText(item.status) }}
                    </span>
                  </div>
                </div>
                
                <p class="part-description">
                  {{ getTemplateItem(item.template_item_id)?.description }}
                </p>
                
                <div class="part-suggestions" v-if="getTemplateItem(item.template_item_id)?.notes">
                  <small class="suggestions-text">
                    💡 {{ getTemplateItem(item.template_item_id)?.notes }}
                  </small>
                </div>
              </div>

              <!-- 零件选择和管理 -->
              <div class="part-management">
                <!-- 已选择的零件 -->
                <div v-if="item.part_id" class="selected-part">
                  <div class="selected-part-info">
                    <h4>已选择零件</h4>
                    <div class="part-details">
                      <!-- 零件缩略图 -->
                      <div class="part-thumbnail">
                        <img 
                          v-if="getPartInfo(item.part_id)?.image_url && !imageErrors[item.part_id]" 
                          :src="getPartInfo(item.part_id).image_url" 
                          :alt="getPartInfo(item.part_id)?.name || `零件 #${item.part_id}`"
                          class="part-img"
                          @error="onImageError(item.part_id)"
                        />
                        <div v-else class="part-placeholder">
                          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                          </svg>
                        </div>
                      </div>
                      
                      <!-- 零件信息 -->
                      <div class="part-detail-info">
                        <span class="part-name">{{ getPartInfo(item.part_id)?.name || `零件 #${item.part_id}` }}</span>
                        <span v-if="getPartInfo(item.part_id)?.category" class="part-category-tag">
                          {{ getPartInfo(item.part_id).category }}
                        </span>
                        <button 
                          class="view-part-btn"
                          @click="viewPartDetail(item.part_id)"
                        >
                          查看详情
                        </button>
                      </div>
                    </div>
                  </div>
                  <button 
                    class="change-part-btn"
                    @click="showPartSelection(item)"
                  >
                    更换零件
                  </button>
                </div>

                <!-- 未选择零件 -->
                <div v-else class="no-part-selected">
                  <p class="no-part-text">尚未选择具体零件</p>
                  <button 
                    class="select-part-btn"
                    @click="showPartSelection(item)"
                  >
                    选择零件
                  </button>
                </div>

                <!-- 状态和价格管理 -->
                <div class="part-controls">
                  <div class="status-control">
                    <label>状态:</label>
                    <select 
                      v-model="item.status" 
                      @change="updateProjectItem(item)"
                      class="status-select"
                    >
                      <option value="needed">❌ 需要获取</option>
                      <option value="owned">✅ 已有</option>
                      <option value="purchased">📦 已购买</option>
                      <option value="optional">⚪ 可选</option>
                    </select>
                  </div>

                  <div class="price-control" v-if="item.status !== 'optional'">
                    <label>价格:</label>
                    <input 
                      type="number" 
                      v-model.number="item.price"
                      @input="updateProjectItem(item)"
                      placeholder="填写实际价格"
                      step="0.01"
                      min="0"
                      class="price-input"
                    />
                  </div>
                </div>

                <!-- 备注 -->
                <div class="notes-control">
                  <label>备注:</label>
                  <input 
                    type="text"
                    v-model="item.notes"
                    @input="updateProjectItem(item)"
                    placeholder="记录购买渠道、使用心得等..."
                    class="notes-input"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="filteredItems.length === 0" class="empty-filter">
            <div class="empty-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.414A1 1 0 013 6.707V4z" />
              </svg>
            </div>
            <h3>该状态下没有零件</h3>
            <p>尝试切换其他筛选条件</p>
          </div>
        </div>
      </div>
    </main>

    <!-- 零件选择器 -->
    <PartSelector
      v-if="showPartSelector"
      :target-category="getTemplateItem(currentSelectingItem?.template_item_id)?.category"
      :is-required="getTemplateItem(currentSelectingItem?.template_item_id)?.is_required"
      :current-part-id="currentSelectingItem?.part_id"
      :template-item="getTemplateItem(currentSelectingItem?.template_item_id)"
      @close="onPartSelectorClose"
      @select="onPartSelected"
      @view-detail="onViewPartDetail"
    />

    <!-- 消息提示 -->
    <div v-if="toast.show" class="toast-overlay" @click="hideToast">
      <div class="toast-message" :class="toast.type">
        <div class="toast-content">
          <svg v-if="toast.type === 'success'" class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <svg v-else-if="toast.type === 'error'" class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          <svg v-else class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="toast-text">{{ toast.message }}</span>
        </div>
        <button v-if="toast.action" class="toast-action" @click.stop="toast.action.callback">
          {{ toast.action.text }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ThemeToggle from '../components/ThemeToggle.vue'
import PartSelector from '../components/PartSelector.vue'
import { getTemplateById } from '../data/projectTemplates'
import { partsAPI } from '../utils/api'

export default {
  name: 'ProjectDetail',
  components: {
    ThemeToggle,
    PartSelector
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const project = ref(null)
    const template = ref(null)
    const loading = ref(false)
    const statusFilter = ref('all')
    const showSettings = ref(false)
    const showPartSelector = ref(false)
    const currentSelectingItem = ref(null)
    
    // 零件信息缓存和图片错误状态
    const partsCache = ref({})
    const imageErrors = ref({})
    
    // 消息提示
    const toast = ref({
      show: false,
      type: 'info',
      message: '',
      action: null
    })
    
    // 项目管理器（与Projects.vue保持一致）
    class ProjectManager {
      constructor() {
        this.storageKey = 'openpart_projects'
      }
      
      getProjects() {
        const stored = localStorage.getItem(this.storageKey)
        try {
          return stored ? JSON.parse(stored) : []
        } catch (error) {
          console.error('解析项目列表失败:', error)
          return []
        }
      }
      
      getProject(projectId) {
        const projects = this.getProjects()
        return projects.find(p => p.id === projectId)
      }
      
      updateProject(projectId, updates) {
        const projects = this.getProjects()
        const index = projects.findIndex(p => p.id === projectId)
        
        if (index === -1) {
          return { success: false, message: '项目不存在' }
        }
        
        projects[index] = {
          ...projects[index],
          ...updates,
          updated_at: new Date().toISOString()
        }
        
        try {
          localStorage.setItem(this.storageKey, JSON.stringify(projects))
          return { success: true, project: projects[index] }
        } catch (error) {
          console.error('保存项目失败:', error)
          return { success: false, message: '保存失败' }
        }
      }
    }
    
    const projectManager = new ProjectManager()
    
    // 计算属性
    const filteredItems = computed(() => {
      if (!project.value) return []
      
      if (statusFilter.value === 'all') {
        return project.value.items
      }
      
      return project.value.items.filter(item => item.status === statusFilter.value)
    })
    
    // 加载零件信息
    const loadPartInfo = async (partId) => {
      if (partsCache.value[partId]) {
        return partsCache.value[partId]
      }
      
      try {
        const response = await partsAPI.getPart(partId)
        partsCache.value[partId] = response.data
        return response.data
      } catch (error) {
        console.error('加载零件信息失败:', error)
        // 返回默认信息
        const defaultInfo = {
          id: partId,
          name: `零件 #${partId}`,
          category: '',
          image_url: null
        }
        partsCache.value[partId] = defaultInfo
        return defaultInfo
      }
    }
    
    // 获取零件信息
    const getPartInfo = (partId) => {
      return partsCache.value[partId] || { 
        id: partId,
        name: `零件 #${partId}`,
        category: '',
        image_url: null
      }
    }
    
    // 图片加载错误处理
    const onImageError = (partId) => {
      imageErrors.value[partId] = true
    }
    
    // 加载项目
    const loadProject = async () => {
      loading.value = true
      
      const projectId = route.params.id
      const foundProject = projectManager.getProject(projectId)
      
      if (foundProject) {
        project.value = foundProject
        template.value = getTemplateById(foundProject.template_id)
        
        // 预加载所有零件信息
        const partIds = foundProject.items
          .filter(item => item.part_id)
          .map(item => item.part_id)
        
        // 并行加载所有零件信息
        await Promise.all(partIds.map(partId => loadPartInfo(partId)))
      }
      
      loading.value = false
    }
    
    // 获取模板名称
    const getTemplateName = () => {
      return template.value ? template.value.name : '未知模板'
    }
    
    // 获取模板条目
    const getTemplateItem = (templateItemId) => {
      if (!template.value) return null
      return template.value.items.find(item => item.id === templateItemId)
    }
    
    // 状态统计
    const getOwnedCount = () => {
      if (!project.value) return 0
      return project.value.items.filter(item => item.status === 'owned').length
    }
    
    const getNeededCount = () => {
      if (!project.value) return 0
      return project.value.items.filter(item => item.status === 'needed').length
    }
    
    const getPurchasedCount = () => {
      if (!project.value) return 0
      return project.value.items.filter(item => item.status === 'purchased').length
    }
    
    // 状态文本
    const getStatusText = (status) => {
      const statusMap = {
        'needed': '需要获取',
        'owned': '已有',
        'purchased': '已购买',
        'optional': '可选'
      }
      return statusMap[status] || status
    }
    
    // 更新项目条目
    const updateProjectItem = (item) => {
      // 重新计算项目进度和成本
      const totalItems = project.value.items.length
      const completedItems = project.value.items.filter(item => 
        item.status === 'owned' || item.status === 'optional'
      ).length
      
      const progress = totalItems > 0 ? completedItems / totalItems : 0
      const actualCost = project.value.items
        .filter(item => item.price && item.status !== 'optional')
        .reduce((sum, item) => sum + (item.price || 0), 0)
      
      const updates = {
        progress: progress,
        actual_cost: actualCost,
        items: project.value.items
      }
      
      const result = projectManager.updateProject(project.value.id, updates)
      
      if (result.success) {
        project.value = result.project
      } else {
        showToast({
          type: 'error',
          message: '保存失败，请重试'
        })
      }
    }
    
    // 零件选择相关方法
    const showPartSelection = (item) => {
      currentSelectingItem.value = item
      showPartSelector.value = true
    }
    
    const onPartSelected = async (selectedPart) => {
      if (!currentSelectingItem.value || !selectedPart) return
      
      // 更新项目条目的零件ID
      currentSelectingItem.value.part_id = selectedPart.id
      
      // 自动设置状态为"需要获取"（如果当前是可选状态）
      if (currentSelectingItem.value.status === 'optional') {
        currentSelectingItem.value.status = 'needed'
      }
      
      // 加载选中零件的信息到缓存
      await loadPartInfo(selectedPart.id)
      
      // 保存项目更新
      updateProjectItem(currentSelectingItem.value)
      
      // 关闭选择器
      showPartSelector.value = false
      currentSelectingItem.value = null
      
      showToast({
        type: 'success',
        message: `已选择零件: ${selectedPart.name}`
      })
    }
    
    const onPartSelectorClose = () => {
      showPartSelector.value = false
      currentSelectingItem.value = null
    }
    
    const onViewPartDetail = (part) => {
      // 关闭选择器并跳转到零件详情
      showPartSelector.value = false
      currentSelectingItem.value = null
      router.push(`/part/${part.id}`)
    }
    
    // 操作方法
    const goBack = () => {
      router.push('/projects')
    }
    
    const viewPartDetail = (partId) => {
      router.push(`/part/${partId}`)
    }
    
    const exportProject = () => {
      // TODO: 实现项目导出功能
      showToast({
        type: 'info',
        message: '导出功能开发中...'
      })
    }
    
    // 消息提示
    const showToast = (options) => {
      toast.value = {
        show: true,
        type: options.type || 'info',
        message: options.message,
        action: options.action || null
      }
      
      if (!options.action) {
        setTimeout(() => {
          hideToast()
        }, 3000)
      }
    }
    
    const hideToast = () => {
      toast.value.show = false
    }
    
    // 监听存储变化
    const handleStorageChange = (e) => {
      if (e.key === 'openpart_projects') {
        loadProject()
      }
    }
    
    onMounted(() => {
      loadProject()
      window.addEventListener('storage', handleStorageChange)
    })
    
    onUnmounted(() => {
      window.removeEventListener('storage', handleStorageChange)
    })
    
    return {
      project,
      template,
      loading,
      statusFilter,
      showSettings,
      showPartSelector,
      currentSelectingItem,
      toast,
      partsCache,
      imageErrors,
      filteredItems,
      getTemplateName,
      getTemplateItem,
      getOwnedCount,
      getNeededCount,
      getPurchasedCount,
      getStatusText,
      getPartInfo,
      onImageError,
      updateProjectItem,
      showPartSelection,
      onPartSelected,
      onPartSelectorClose,
      onViewPartDetail,
      goBack,
      viewPartDetail,
      exportProject,
      showToast,
      hideToast
    }
  }
}
</script>

/* ProjectDetail.vue 样式完整版 */
<style scoped>
.project-detail-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* 头部导航 */
.project-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 0;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
}

.project-nav {
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

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--primary);
}

.action-btn svg {
  width: 20px;
  height: 20px;
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

/* 主要内容 */
.project-main {
  padding: 24px 0;
}

/* 项目概览 */
.project-overview {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 32px;
  align-items: start;
}

.project-info {
  min-width: 0;
}

.project-header-info {
  margin-bottom: 12px;
}

.project-name {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.project-template {
  font-size: 14px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 4px 12px;
  border-radius: 6px;
}

.project-description {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.project-stats {
  display: flex;
  gap: 20px;
}

.stat-card {
  text-align: center;
  min-width: 120px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: var(--bg-secondary);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  border-radius: 3px;
  transition: width 0.3s ease;
}

.budget-info {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

.parts-breakdown {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}

.parts-breakdown .owned {
  color: #10b981;
  margin-right: 8px;
}

.parts-breakdown .needed {
  color: #f59e0b;
}

/* 零件清单区域 */
.parts-list-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.list-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.controls-left h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.filter-buttons {
  display: flex;
  gap: 8px;
}

.filter-btn {
  padding: 6px 12px;
  font-size: 13px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  background: var(--bg-primary);
  border-color: var(--primary);
}

.filter-btn.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.filter-btn.needed.active {
  background: #f59e0b;
  border-color: #f59e0b;
}

.filter-btn.owned.active {
  background: #10b981;
  border-color: #10b981;
}

.filter-btn.purchased.active {
  background: #3b82f6;
  border-color: #3b82f6;
}

/* 零件列表 */
.parts-list {
  max-height: 70vh;
  overflow-y: auto;
}

.part-item {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.2s ease;
}

.part-item:hover {
  background: var(--bg-secondary);
}

.part-item:last-child {
  border-bottom: none;
}

.part-item.required {
  border-left: 4px solid #f59e0b;
}

.part-item.optional {
  border-left: 4px solid var(--text-muted);
}

.part-item.needed {
  background: color-mix(in srgb, #f59e0b 3%, var(--bg-card));
}

.part-item.owned {
  background: color-mix(in srgb, #10b981 3%, var(--bg-card));
}

.part-item.purchased {
  background: color-mix(in srgb, #3b82f6 3%, var(--bg-card));
}

/* 零件信息 */
.part-info {
  min-width: 0;
}

.part-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.part-category {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.part-badges {
  display: flex;
  gap: 8px;
}

.required-badge,
.optional-badge,
.status-badge {
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 500;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.required-badge {
  background: color-mix(in srgb, #f59e0b 15%, transparent);
  color: #f59e0b;
}

.optional-badge {
  background: color-mix(in srgb, var(--text-muted) 15%, transparent);
  color: var(--text-muted);
}

.status-badge.needed {
  background: color-mix(in srgb, #f59e0b 15%, transparent);
  color: #f59e0b;
}

.status-badge.owned {
  background: color-mix(in srgb, #10b981 15%, transparent);
  color: #10b981;
}

.status-badge.purchased {
  background: color-mix(in srgb, #3b82f6 15%, transparent);
  color: #3b82f6;
}

.status-badge.optional {
  background: color-mix(in srgb, var(--text-muted) 15%, transparent);
  color: var(--text-muted);
}

.part-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 12px 0;
}

.part-suggestions {
  margin-top: 8px;
}

.suggestions-text {
  font-size: 12px;
  color: var(--text-muted);
  font-style: italic;
}

/* 零件管理区域 */
.part-management {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
}

/* 已选择零件 */
.selected-part {
  margin-bottom: 16px;
}

.selected-part-info h4 {
  font-size: 14px;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

/* 零件缩略图样式 */
.part-thumbnail {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.part-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: white;
}

.part-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.part-placeholder svg {
  width: 24px;
  height: 24px;
}

/* 零件详情信息 */
.part-details {
  display: grid;
  grid-template-columns: 60px 1fr;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.part-detail-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.part-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.part-category-tag {
  font-size: 12px;
  color: var(--primary);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  padding: 2px 6px;
  border-radius: 3px;
  align-self: flex-start;
  font-weight: 500;
}

.view-part-btn {
  padding: 4px 8px;
  font-size: 12px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  align-self: flex-start;
}

.view-part-btn:hover {
  background: var(--secondary);
}

.change-part-btn {
  width: 100%;
  padding: 8px 12px;
  font-size: 13px;
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.change-part-btn:hover {
  background: var(--bg-primary);
  border-color: var(--primary);
}

/* 未选择零件 */
.no-part-selected {
  text-align: center;
  margin-bottom: 16px;
}

.no-part-text {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0 0 12px 0;
}

.select-part-btn {
  width: 100%;
  padding: 12px;
  font-size: 14px;
  font-weight: 500;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.select-part-btn:hover {
  background: var(--secondary);
}

/* 控制区域 */
.part-controls {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

.status-control,
.price-control {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-control label,
.price-control label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.status-select,
.price-input {
  padding: 6px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 13px;
}

.status-select:focus,
.price-input:focus {
  outline: none;
  border-color: var(--primary);
}

.notes-control {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.notes-control label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.notes-input {
  padding: 6px 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 13px;
}

.notes-input:focus {
  outline: none;
  border-color: var(--primary);
}

/* 空状态 */
.empty-filter {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.empty-filter h3 {
  font-size: 18px;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-filter p {
  color: var(--text-secondary);
  margin: 0;
}

/* 消息提示样式 */
.toast-overlay {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1001;
  animation: toastSlideIn 0.3s ease;
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.toast-message {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 300px;
  max-width: 500px;
  cursor: pointer;
}

.toast-message.success {
  border-color: #10b981;
  background: color-mix(in srgb, #10b981 5%, var(--bg-card));
}

.toast-message.error {
  border-color: #f43f5e;
  background: color-mix(in srgb, #f43f5e 5%, var(--bg-card));
}

.toast-message.info {
  border-color: var(--primary);
  background: color-mix(in srgb, var(--primary) 5%, var(--bg-card));
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.toast-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.toast-message.success .toast-icon {
  color: #10b981;
}

.toast-message.error .toast-icon {
  color: #f43f5e;
}

.toast-message.info .toast-icon {
  color: var(--primary);
}

.toast-text {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.4;
}

.toast-action {
  padding: 6px 12px;
  font-size: 13px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.toast-action:hover {
  background: var(--secondary);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .project-overview {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .project-stats {
    justify-content: center;
  }
  
  .part-item {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .list-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .filter-buttons {
    justify-content: center;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .project-main {
    padding: 16px 0;
  }
  
  .project-overview {
    padding: 16px;
    margin-bottom: 16px;
  }
  
  .project-name {
    font-size: 24px;
  }
  
  .project-stats {
    flex-direction: column;
    gap: 16px;
  }
  
  .part-item {
    padding: 16px;
  }
  
  .part-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .part-controls {
    grid-template-columns: 1fr;
  }
  
  .list-controls {
    padding: 16px;
  }
  
  .toast-overlay {
    left: 16px;
    right: 16px;
    transform: none;
  }
  
  .toast-message {
    min-width: auto;
    max-width: none;
  }
  
  /* 移动端零件详情布局调整 */
  .part-details {
    grid-template-columns: 50px 1fr;
    gap: 10px;
  }
  
  .part-thumbnail {
    width: 50px;
    height: 50px;
  }
  
  .part-name {
    font-size: 14px;
  }
  
  .view-part-btn {
    font-size: 11px;
    padding: 3px 6px;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 动画增强 */
.part-item {
  animation: partItemEnter 0.3s ease;
}

@keyframes partItemEnter {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>