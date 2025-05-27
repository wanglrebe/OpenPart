<!-- portal/src/views/Projects.vue 完整版 - 使用全局导航 -->
<template>
  <div class="projects-page">
    <!-- 全局导航 -->
    <GlobalNavigation />
    
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">项目清单</h1>
      </div>
    </div>
    
    <!-- 主要内容 -->
    <main class="projects-main">
      <div class="container">
        <!-- 项目概览 -->
        <div class="projects-summary">
          <div class="summary-stats">
            <div class="stat-item">
              <span class="stat-number">{{ projects.length }}</span>
              <span class="stat-label">我的项目</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ activeProjects.length }}</span>
              <span class="stat-label">进行中</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ completedProjects.length }}</span>
              <span class="stat-label">已完成</span>
            </div>
          </div>
          
          <div class="summary-actions">
            <button class="btn btn-primary" @click="showCreateDialog = true">
              <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              创建新项目
            </button>
          </div>
        </div>
        
        <!-- 项目列表 -->
        <div class="projects-content">
          <!-- 空状态 -->
          <div v-if="projects.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3>还没有创建任何项目</h3>
            <p>基于模板创建项目清单，跟踪零件状态和项目进度</p>
            <button class="btn btn-primary" @click="showCreateDialog = true">
              创建第一个项目
            </button>
          </div>
          
          <!-- 项目网格 -->
          <div v-else class="projects-grid">
            <div 
              v-for="project in projects" 
              :key="project.id"
              class="project-card"
              @click="goToProject(project.id)"
            >
              <div class="project-header">
                <div class="project-info">
                  <h3 class="project-name">{{ project.name }}</h3>
                  <span class="project-template">{{ getTemplateName(project.template_id) }}</span>
                </div>
                <div class="project-actions">
                  <button 
                    class="action-btn"
                    @click.stop="editProject(project)"
                    title="编辑项目"
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button 
                    class="action-btn delete-btn"
                    @click.stop="deleteProject(project.id)"
                    title="删除项目"
                  >
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <div class="project-progress">
                <div class="progress-info">
                  <span class="progress-text">进度 {{ Math.round(project.progress * 100) }}%</span>
                  <span class="progress-cost">￥{{ project.actual_cost || 0 }} / ￥{{ project.estimated_cost }}</span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill"
                    :style="{ width: `${project.progress * 100}%` }"
                  ></div>
                </div>
              </div>
              
              <div class="project-stats">
                <div class="stat-item">
                  <span class="stat-value">{{ getProjectStats(project).owned }}</span>
                  <span class="stat-label">已有</span>
                </div>
                <div class="stat-item">
                  <span class="stat-value">{{ getProjectStats(project).needed }}</span>
                  <span class="stat-label">缺少</span>
                </div>
                <div class="stat-item">
                  <span class="stat-value">{{ getProjectStats(project).total }}</span>
                  <span class="stat-label">总计</span>
                </div>
              </div>
              
              <div class="project-meta">
                <span class="project-date">{{ formatDate(project.created_at) }}</span>
                <span class="project-status" :class="project.progress >= 1 ? 'completed' : 'active'">
                  {{ project.progress >= 1 ? '已完成' : '进行中' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 创建项目对话框 -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click="closeCreateDialog">
      <div class="create-dialog" @click.stop>
        <div class="dialog-header">
          <h3>创建新项目</h3>
          <button class="close-btn" @click="closeCreateDialog">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div class="dialog-content">
          <!-- 步骤1：选择模板 -->
          <div v-if="createStep === 1" class="create-step">
            <h4>选择项目模板</h4>
            <div class="templates-grid">
              <div 
                v-for="template in availableTemplates" 
                :key="template.id"
                class="template-card"
                :class="{ selected: selectedTemplate?.id === template.id }"
                @click="selectTemplate(template)"
              >
                <div class="template-header">
                  <h5>{{ template.name }}</h5>
                  <span class="template-difficulty" :class="template.difficulty">
                    {{ template.difficulty }}
                  </span>
                </div>
                <p class="template-description">{{ template.description }}</p>
                <div class="template-stats">
                  <span class="template-cost">预算: ￥{{ template.estimated_cost }}</span>
                  <span class="template-time">时间: {{ template.estimated_time }}</span>
                </div>
                <div class="template-category">{{ template.category }}</div>
              </div>
            </div>
          </div>
          
          <!-- 步骤2：项目配置 -->
          <div v-if="createStep === 2" class="create-step">
            <h4>配置项目信息</h4>
            <form class="project-form">
              <div class="form-group">
                <label>项目名称</label>
                <input 
                  v-model="newProject.name"
                  type="text" 
                  class="form-input"
                  placeholder="给你的项目起个名字..."
                  maxlength="50"
                />
              </div>
              
              <div class="form-group">
                <label>项目描述（可选）</label>
                <textarea 
                  v-model="newProject.description"
                  class="form-textarea"
                  placeholder="描述一下这个项目的用途和目标..."
                  maxlength="200"
                ></textarea>
              </div>
              
              <div class="form-group">
                <label>预算上限（可选）</label>
                <input 
                  v-model.number="newProject.budget_limit"
                  type="number"
                  class="form-input"
                  placeholder="设置项目预算上限..."
                  min="0"
                  step="0.01"
                />
              </div>
            </form>
            
            <!-- 模板预览 -->
            <div class="template-preview">
              <h5>基于模板: {{ selectedTemplate?.name }}</h5>
              <div class="template-items-preview">
                <div class="preview-stats">
                  <span>{{ selectedTemplate?.items.filter(i => i.is_required).length }} 个必需零件</span>
                  <span>{{ selectedTemplate?.items.filter(i => !i.is_required).length }} 个可选零件</span>
                  <span>预估成本: ￥{{ selectedTemplate?.estimated_cost }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="dialog-footer">
          <button 
            v-if="createStep > 1"
            class="btn btn-outline"
            @click="createStep--"
          >
            上一步
          </button>
          
          <div class="dialog-actions">
            <button class="btn btn-outline" @click="closeCreateDialog">
              取消
            </button>
            
            <button 
              v-if="createStep === 1"
              class="btn btn-primary"
              :disabled="!selectedTemplate"
              @click="createStep++"
            >
              下一步
            </button>
            
            <button 
              v-if="createStep === 2"
              class="btn btn-primary"
              :disabled="!newProject.name.trim()"
              @click="createProject"
            >
              创建项目
            </button>
          </div>
        </div>
      </div>
    </div>
    
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
import { useRouter } from 'vue-router'
import GlobalNavigation from '../components/GlobalNavigation.vue'
import { projectTemplates, getTemplateById } from '../data/projectTemplates'

export default {
  name: 'Projects',
  components: {
    GlobalNavigation
  },
  setup() {
    const router = useRouter()
    
    // 基础状态
    const projects = ref([])
    const showCreateDialog = ref(false)
    const createStep = ref(1)
    const selectedTemplate = ref(null)
    const availableTemplates = ref(projectTemplates)
    
    // 新项目表单
    const newProject = ref({
      name: '',
      description: '',
      budget_limit: null
    })
    
    // 消息提示
    const toast = ref({
      show: false,
      type: 'info',
      message: '',
      action: null
    })
    
    // 计算属性
    const activeProjects = computed(() => {
      return projects.value.filter(p => p.progress < 1)
    })
    
    const completedProjects = computed(() => {
      return projects.value.filter(p => p.progress >= 1)
    })
    
    // 项目管理器类
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
      
      saveProjects(projectsList) {
        try {
          localStorage.setItem(this.storageKey, JSON.stringify(projectsList))
          return { success: true }
        } catch (error) {
          console.error('保存项目列表失败:', error)
          return { success: false, message: '保存失败' }
        }
      }
      
      createProject(projectData) {
        const projects = this.getProjects()
        const newId = Date.now().toString()
        
        const project = {
          id: newId,
          name: projectData.name,
          description: projectData.description || '',
          template_id: projectData.template_id,
          budget_limit: projectData.budget_limit || null,
          estimated_cost: projectData.estimated_cost,
          actual_cost: 0,
          progress: 0,
          items: projectData.items || [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
        
        projects.unshift(project)
        const result = this.saveProjects(projects)
        
        return result.success ? 
          { success: true, project, message: '项目创建成功' } :
          { success: false, message: result.message }
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
        
        const result = this.saveProjects(projects)
        return result.success ?
          { success: true, project: projects[index], message: '项目更新成功' } :
          { success: false, message: result.message }
      }
      
      deleteProject(projectId) {
        const projects = this.getProjects()
        const filteredProjects = projects.filter(p => p.id !== projectId)
        
        if (filteredProjects.length === projects.length) {
          return { success: false, message: '项目不存在' }
        }
        
        const result = this.saveProjects(filteredProjects)
        return result.success ?
          { success: true, message: '项目删除成功' } :
          { success: false, message: result.message }
      }
    }
    
    const projectManager = new ProjectManager()
    
    // 项目操作
    const loadProjects = () => {
      projects.value = projectManager.getProjects()
    }
    
    const goToProject = (projectId) => {
      router.push(`/projects/${projectId}`)
    }
    
    const editProject = (project) => {
      // TODO: 实现编辑功能
      showToast({
        type: 'info',
        message: '编辑功能开发中...'
      })
    }
    
    const deleteProject = async (projectId) => {
      const confirmDelete = confirm('确定要删除这个项目吗？此操作无法撤销。')
      if (!confirmDelete) return
      
      const result = projectManager.deleteProject(projectId)
      
      if (result.success) {
        showToast({
          type: 'success',
          message: result.message
        })
        loadProjects()
      } else {
        showToast({
          type: 'error',
          message: result.message
        })
      }
    }
    
    // 创建项目相关
    const selectTemplate = (template) => {
      selectedTemplate.value = template
    }
    
    const createProject = () => {
      if (!selectedTemplate.value || !newProject.value.name.trim()) {
        showToast({
          type: 'error',
          message: '请填写完整的项目信息'
        })
        return
      }
      
      // 基于模板创建项目
      const projectData = {
        name: newProject.value.name.trim(),
        description: newProject.value.description.trim(),
        template_id: selectedTemplate.value.id,
        budget_limit: newProject.value.budget_limit,
        estimated_cost: selectedTemplate.value.estimated_cost,
        items: selectedTemplate.value.items.map(item => ({
          template_item_id: item.id,
          part_id: null,
          status: item.is_required ? 'needed' : 'optional',
          price: null,
          notes: ''
        }))
      }
      
      const result = projectManager.createProject(projectData)
      
      if (result.success) {
        showToast({
          type: 'success',
          message: result.message,
          action: {
            text: '查看项目',
            callback: () => {
              goToProject(result.project.id)
            }
          }
        })
        
        closeCreateDialog()
        loadProjects()
      } else {
        showToast({
          type: 'error',
          message: result.message
        })
      }
    }
    
    const closeCreateDialog = () => {
      showCreateDialog.value = false
      createStep.value = 1
      selectedTemplate.value = null
      newProject.value = {
        name: '',
        description: '',
        budget_limit: null
      }
    }
    
    // 工具函数
    const getTemplateName = (templateId) => {
      const template = getTemplateById(templateId)
      return template ? template.name : '未知模板'
    }
    
    const getProjectStats = (project) => {
      const owned = project.items.filter(item => item.status === 'owned').length
      const needed = project.items.filter(item => item.status === 'needed').length
      const total = project.items.length
      
      return { owned, needed, total }
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return ''
      
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now - date
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) return '今天创建'
      if (diffDays === 1) return '昨天创建'
      if (diffDays < 7) return `${diffDays}天前创建`
      if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前创建`
      
      return date.toLocaleDateString('zh-CN')
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
        loadProjects()
      }
    }
    
    onMounted(() => {
      loadProjects()
      window.addEventListener('storage', handleStorageChange)
    })
    
    onUnmounted(() => {
      window.removeEventListener('storage', handleStorageChange)
    })
    
    return {
      projects,
      activeProjects,
      completedProjects,
      showCreateDialog,
      createStep,
      selectedTemplate,
      availableTemplates,
      newProject,
      toast,
      goToProject,
      editProject,
      deleteProject,
      selectTemplate,
      createProject,
      closeCreateDialog,
      getTemplateName,
      getProjectStats,
      formatDate,
      showToast,
      hideToast
    }
  }
}
</script>

/* Projects.vue 样式完整版 - 使用全局导航 */
<style scoped>
.projects-page {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* 页面标题区域 */
.page-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  padding: 20px 0;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* 主要内容 */
.projects-main {
  padding: 24px 0;
}

/* 项目概览 */
.projects-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.summary-stats {
  display: flex;
  gap: 32px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 项目内容区域 */
.projects-content {
  min-height: 400px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  color: var(--text-muted);
  margin-bottom: 24px;
}

.empty-state h3 {
  font-size: 24px;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.empty-state p {
  color: var(--text-secondary);
  margin: 0 0 32px 0;
  max-width: 400px;
  line-height: 1.6;
}

/* 项目网格 */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.project-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.project-info {
  flex: 1;
  min-width: 0;
}

.project-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-template {
  font-size: 13px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 2px 8px;
  border-radius: 4px;
}

.project-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.project-card:hover .project-actions {
  opacity: 1;
}

.action-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: var(--primary);
  color: white;
}

.delete-btn:hover {
  background: #f43f5e;
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

/* 项目进度 */
.project-progress {
  margin-bottom: 16px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.progress-cost {
  font-size: 13px;
  color: var(--text-secondary);
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

/* 项目统计 */
.project-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
  padding: 12px 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.project-stats .stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.project-stats .stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 项目元信息 */
.project-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.project-date {
  color: var(--text-muted);
}

.project-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

/* Projects.vue 样式完整版 - 续 */

.project-status.active {
  background: color-mix(in srgb, #f59e0b 10%, transparent);
  color: #f59e0b;
}

.project-status.completed {
  background: color-mix(in srgb, #10b981 10%, transparent);
  color: #10b981;
}

/* 创建项目对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  backdrop-filter: blur(4px);
}

.create-dialog {
  background: var(--bg-card);
  border-radius: 12px;
  width: 700px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  animation: dialogSlideIn 0.3s ease;
}

@keyframes dialogSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.dialog-header h3 {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary);
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--primary);
  color: white;
}

.close-btn svg {
  width: 16px;
  height: 16px;
}

.dialog-content {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.create-step h4 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: var(--text-primary);
}

/* 模板网格 */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.template-card {
  border: 2px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.template-card:hover {
  border-color: var(--primary);
  background: color-mix(in srgb, var(--primary) 3%, var(--bg-card));
}

.template-card.selected {
  border-color: var(--primary);
  background: color-mix(in srgb, var(--primary) 8%, var(--bg-card));
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.template-card h5 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.template-difficulty {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.template-difficulty.初级 {
  background: color-mix(in srgb, #10b981 15%, transparent);
  color: #10b981;
}

.template-difficulty.中级 {
  background: color-mix(in srgb, #f59e0b 15%, transparent);
  color: #f59e0b;
}

.template-difficulty.高级 {
  background: color-mix(in srgb, #f43f5e 15%, transparent);
  color: #f43f5e;
}

.template-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.4;
  margin: 0 0 12px 0;
}

.template-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.template-category {
  font-size: 12px;
  color: var(--primary);
  background: color-mix(in srgb, var(--primary) 10%, transparent);
  padding: 2px 6px;
  border-radius: 3px;
  align-self: flex-start;
}

/* 项目表单 */
.project-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  background: var(--bg-card);
  color: var(--text-primary);
  transition: border-color 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary);
}

.form-textarea {
  min-height: 80px;
  resize: vertical;
}

/* 模板预览 */
.template-preview {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.template-preview h5 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: var(--text-primary);
}

.preview-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
}

.preview-stats span {
  background: var(--bg-card);
  padding: 4px 8px;
  border-radius: 4px;
}

/* 对话框底部 */
.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.dialog-actions {
  display: flex;
  gap: 12px;
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
  .projects-summary {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .summary-stats {
    justify-content: center;
  }
  
  .projects-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }
  
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .create-dialog {
    width: 600px;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 16px 0;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .projects-main {
    padding: 16px 0;
  }
  
  .projects-summary {
    padding: 16px;
    margin-bottom: 16px;
  }
  
  .summary-stats {
    gap: 20px;
  }
  
  .stat-number {
    font-size: 24px;
  }
  
  .projects-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .project-actions {
    opacity: 1;
  }
  
  .create-dialog {
    width: 100%;
    margin: 10px;
  }
  
  .dialog-content {
    max-height: 50vh;
  }
  
  .dialog-footer {
    flex-direction: column;
    gap: 12px;
  }
  
  .dialog-actions {
    width: 100%;
    justify-content: center;
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
}

/* 动画增强 */
.project-card {
  animation: projectCardEnter 0.3s ease;
}

@keyframes projectCardEnter {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.template-card {
  animation: templateCardEnter 0.2s ease;
}

@keyframes templateCardEnter {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>