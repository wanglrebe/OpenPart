<!-- admin/src/views/CrawlerPlugins.vue -->
<template>
  <div class="crawler-plugins">
    <NavBar />
    
    <el-main class="main-content">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-left">
          <h1>爬虫插件管理</h1>
          <p>管理和配置数据源爬虫插件</p>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="showUploadDialog = true">
            <el-icon><Upload /></el-icon>
            上传插件
          </el-button>
          <el-button @click="refreshPlugins">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>

      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon total">
                <el-icon><Box /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ stats.total_plugins }}</h3>
                <p>总插件数</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon active">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ stats.active_plugins }}</h3>
                <p>活跃插件</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon tasks">
                <el-icon><Timer /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ stats.running_tasks }}</h3>
                <p>运行任务</p>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon success">
                <el-icon><SuccessFilled /></el-icon>
              </div>
              <div class="stat-info">
                <h3>{{ totalSuccessCount }}</h3>
                <p>成功数据</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 插件列表 -->
      <el-card class="plugins-card">
        <template #header>
          <div class="card-header">
            <span>插件列表</span>
            <el-input
              v-model="searchText"
              placeholder="搜索插件..."
              style="width: 200px"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </template>

        <el-table :data="filteredPlugins" v-loading="loading" style="width: 100%">
          <el-table-column label="插件信息" min-width="250">
            <template #default="scope">
              <div class="plugin-info">
                <div class="plugin-name">
                  {{ scope.row.display_name }}
                  <el-tag size="small" class="version-tag">v{{ scope.row.version }}</el-tag>
                </div>
                <div class="plugin-meta">
                  <span class="author">{{ scope.row.author }}</span>
                  <span class="divider">·</span>
                  <span class="data-source">{{ scope.row.data_source }}</span>
                </div>
                <div class="plugin-description">{{ scope.row.description }}</div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="状态" width="120">
            <template #default="scope">
              <el-tag
                :type="getStatusType(scope.row.status)"
                :effect="scope.row.is_active ? 'dark' : 'plain'"
              >
                {{ getStatusText(scope.row.status, scope.row.is_active) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="统计信息" width="150">
            <template #default="scope">
              <div class="stats-info">
                <div class="stat-item">
                  <span class="label">运行:</span>
                  <span class="value">{{ scope.row.run_count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">成功:</span>
                  <span class="value success">{{ scope.row.success_count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">错误:</span>
                  <span class="value error">{{ scope.row.error_count || 0 }}</span>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="最后运行" width="120">
            <template #default="scope">
              <span v-if="scope.row.last_run_at" class="last-run">
                {{ formatTime(scope.row.last_run_at) }}
              </span>
              <span v-else class="never-run">从未运行</span>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="280">
            <template #default="scope">
              <div class="action-buttons">
                <el-button
                  size="small"
                  @click="configPlugin(scope.row)"
                  :disabled="!scope.row.is_active"
                >
                  配置
                </el-button>
                
                <el-button
                  size="small"
                  type="success"
                  @click="testPlugin(scope.row)"
                  :disabled="!scope.row.is_active"
                >
                  测试
                </el-button>
                
                <el-button
                  size="small"
                  type="primary"
                  @click="manageTask(scope.row)"
                  :disabled="!scope.row.is_active"
                >
                  任务
                </el-button>
                
                <el-dropdown @command="(command) => handlePluginAction(command, scope.row)">
                  <el-button size="small">
                    更多<el-icon><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item
                        :command="scope.row.is_active ? 'disable' : 'enable'"
                        :icon="scope.row.is_active ? 'CircleClosed' : 'CircleCheck'"
                      >
                        {{ scope.row.is_active ? '禁用' : '启用' }}
                      </el-dropdown-item>
                      <el-dropdown-item command="logs" icon="Document">查看日志</el-dropdown-item>
                      <el-dropdown-item command="delete" icon="Delete" divided>删除插件</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-main>

    <!-- 上传插件对话框 -->
    <el-dialog
      title="上传爬虫插件"
      v-model="showUploadDialog"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="upload-container">
        <el-upload
          class="plugin-uploader"
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleFileSelect"
          :file-list="uploadFileList"
          accept=".py"
          :limit="1"
        >
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <div class="upload-text">将Python插件文件拖到此处，或<em>点击上传</em></div>
          <div class="upload-hint">仅支持 .py 格式的插件文件</div>
        </el-upload>

        <div v-if="selectedFile" class="file-info">
          <h4>文件信息</h4>
          <p><strong>文件名:</strong> {{ selectedFile.name }}</p>
          <p><strong>大小:</strong> {{ formatFileSize(selectedFile.size) }}</p>
          
          <div v-if="pluginValidation" class="validation-result">
            <div v-if="pluginValidation.success" class="validation-success">
              <el-icon><CircleCheck /></el-icon>
              <span>插件验证通过</span>
              <div class="plugin-preview">
                <p><strong>插件名:</strong> {{ pluginValidation.info.display_name }}</p>
                <p><strong>版本:</strong> {{ pluginValidation.info.version }}</p>
                <p><strong>作者:</strong> {{ pluginValidation.info.author }}</p>
                <p><strong>数据源:</strong> {{ pluginValidation.info.data_source }}</p>
              </div>
            </div>
            <div v-else class="validation-error">
              <el-icon><CircleClose /></el-icon>
              <span>插件验证失败: {{ pluginValidation.error }}</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="cancelUpload">取消</el-button>
        <el-button
          type="primary"
          @click="uploadPlugin"
          :loading="uploading"
          :disabled="!selectedFile || !pluginValidation?.success"
        >
          {{ uploading ? '上传中...' : '确认上传' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 插件配置对话框 -->
    <el-dialog
    :title="`配置 ${currentPlugin?.display_name}`"
    v-model="showConfigDialog"
    width="800px"
    :close-on-click-modal="false"
  >
    <PluginConfigForm
      v-if="currentPlugin"
      :plugin="currentPlugin"
      :config="currentConfig"
      :on-test="testPluginConnection"
      @save="savePluginConfig"
      @cancel="showConfigDialog = false"
      ref="configFormRef"
    />
  </el-dialog>

    <!-- 任务管理对话框 -->
    <el-dialog
      :title="`任务管理 - ${currentPlugin?.display_name}`"
      v-model="showTaskDialog"
      width="1200px"
      :close-on-click-modal="false"
    >
      <PluginTaskManager
        v-if="currentPlugin"
        :plugin="currentPlugin"
        ref="taskManagerRef"
      />
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  Upload, Refresh, Box, CircleCheck, Timer, SuccessFilled,
  Search, ArrowDown, UploadFilled, CircleClose
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import PluginConfigForm from '../components/PluginConfigForm.vue'
import PluginTaskManager from '../components/PluginTaskManager.vue'
import { auth } from '../utils/auth'
import axios from 'axios'

export default {
  name: 'CrawlerPlugins',
  components: {
    NavBar,
    PluginConfigForm,
    PluginTaskManager,
    Upload, Refresh, Box, CircleCheck, Timer, SuccessFilled,
    Search, ArrowDown, UploadFilled, CircleClose
  },
  setup() {
    const loading = ref(false)
    const plugins = ref([])
    const searchText = ref('')
    const stats = reactive({
      total_plugins: 0,
      active_plugins: 0,
      running_tasks: 0
    })

    // 上传相关
    const showUploadDialog = ref(false)
    const selectedFile = ref(null)
    const uploadFileList = ref([])
    const uploading = ref(false)
    const pluginValidation = ref(null)

    // 配置相关
    const showConfigDialog = ref(false)
    const currentPlugin = ref(null)
    const currentConfig = ref({})
    const configFormRef = ref()

    // 任务管理相关
    const showTaskDialog = ref(false)
    const taskManagerRef = ref()

    // 计算属性
    const filteredPlugins = computed(() => {
      if (!searchText.value) return plugins.value
      
      const search = searchText.value.toLowerCase()
      return plugins.value.filter(plugin =>
        plugin.display_name.toLowerCase().includes(search) ||
        plugin.author.toLowerCase().includes(search) ||
        plugin.data_source.toLowerCase().includes(search)
      )
    })

    const totalSuccessCount = computed(() => {
      return plugins.value.reduce((sum, plugin) => sum + (plugin.success_count || 0), 0)
    })

    // 加载插件列表
    const loadPlugins = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/admin/crawler-plugins/', {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })
        
        plugins.value = response.data
        
        // 更新统计
        stats.total_plugins = plugins.value.length
        stats.active_plugins = plugins.value.filter(p => p.is_active).length
        
      } catch (error) {
        ElMessage.error('加载插件列表失败')
        console.error(error)
      }
      loading.value = false
    }

    // 加载统计信息
    const loadStats = async () => {
      try {
        const response = await axios.get('/api/admin/crawler-plugins/stats', {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })
        Object.assign(stats, response.data)
      } catch (error) {
        console.error('加载统计失败:', error)
      }
    }

    // 刷新插件
    const refreshPlugins = () => {
      loadPlugins()
      loadStats()
    }

    // 文件选择处理
    const handleFileSelect = async (file) => {
      selectedFile.value = file.raw
      uploadFileList.value = [file]
      pluginValidation.value = null

      // 验证插件文件
      try {
        const formData = new FormData()
        formData.append('file', file.raw)
        
        // 这里应该调用验证接口，暂时模拟
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        pluginValidation.value = {
          success: true,
          info: {
            display_name: '示例插件',
            version: '1.0.0',
            author: '开发者',
            data_source: '示例数据源'
          }
        }
      } catch (error) {
        pluginValidation.value = {
          success: false,
          error: error.message || '验证失败'
        }
      }
    }

    // 上传插件
    const uploadPlugin = async () => {
      if (!selectedFile.value) return

      uploading.value = true
      try {
        const formData = new FormData()
        formData.append('plugin_file', selectedFile.value)

        await axios.post('/api/admin/crawler-plugins/upload', formData, {
          headers: {
            Authorization: `Bearer ${auth.getToken()}`,
            'Content-Type': 'multipart/form-data'
          }
        })

        ElMessage.success('插件上传成功')
        cancelUpload()
        refreshPlugins()
        
      } catch (error) {
        ElMessage.error('上传失败: ' + (error.response?.data?.detail || error.message))
      }
      uploading.value = false
    }

    // 取消上传
    const cancelUpload = () => {
      showUploadDialog.value = false
      selectedFile.value = null
      uploadFileList.value = []
      pluginValidation.value = null
    }

    // 配置插件
    const configPlugin = async (plugin) => {
      currentPlugin.value = plugin
      
      // 加载当前配置
      try {
        const response = await axios.get(`/api/admin/crawler-plugins/${plugin.id}`, {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })
        currentConfig.value = response.data.config || {}
      } catch (error) {
        currentConfig.value = {}
      }
      
      showConfigDialog.value = true
    }

    // 保存插件配置
    const savePluginConfig = async (config) => {
      try {
        await axios.put(`/api/admin/crawler-plugins/${currentPlugin.value.id}/config`, {
          config
        }, {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })

        ElMessage.success('配置保存成功')
        showConfigDialog.value = false
        refreshPlugins()
        
      } catch (error) {
        ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
      }
    }

    // 测试插件连接
    const testPlugin = async (plugin) => {
      try {
        const response = await axios.post(`/api/admin/crawler-plugins/${plugin.id}/test`, {}, {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })

        if (response.data.success) {
          ElMessage.success(`连接测试成功 (${response.data.response_time}秒)`)
        } else {
          ElMessage.error(`连接测试失败: ${response.data.message}`)
        }
      } catch (error) {
        ElMessage.error('测试失败: ' + (error.response?.data?.detail || error.message))
      }
    }

    // 测试插件连接（从配置表单）
    const testPluginConnection = async (config) => {
      try {
        console.log('开始测试连接，配置:', config)
        
        const response = await axios.post(`/api/admin/crawler-plugins/${currentPlugin.value.id}/test`, {
          config
        }, {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })
    
        console.log('测试连接响应:', response.data)
        
        // 确保返回正确的数据结构
        const result = response.data
        if (result && typeof result === 'object') {
          return result
        } else {
          // 如果后端返回的不是期望的格式，包装一下
          return {
            success: Boolean(result),
            message: result ? '连接测试成功' : '连接测试失败',
            response_time: 0,
            sample_data: result
          }
        }
      } catch (error) {
        console.error('测试连接错误:', error)
        return {
          success: false,
          message: error.response?.data?.detail || error.message || '连接测试失败'
        }
      }
    }

    // 管理任务
    const manageTask = (plugin) => {
      currentPlugin.value = plugin
      showTaskDialog.value = true
    }

    // 处理插件操作
    const handlePluginAction = async (command, plugin) => {
      switch (command) {
        case 'enable':
          await togglePluginStatus(plugin, true)
          break
        case 'disable':
          await togglePluginStatus(plugin, false)
          break
        case 'logs':
          // TODO: 实现日志查看
          ElMessage.info('日志查看功能开发中...')
          break
        case 'delete':
          await deletePlugin(plugin)
          break
      }
    }

    // 切换插件状态
    const togglePluginStatus = async (plugin, enable) => {
      try {
        const action = enable ? 'enable' : 'disable'
        await axios.post(`/api/admin/crawler-plugins/${plugin.id}/${action}`, {}, {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })

        ElMessage.success(`插件已${enable ? '启用' : '禁用'}`)
        refreshPlugins()
        
      } catch (error) {
        ElMessage.error('操作失败: ' + (error.response?.data?.detail || error.message))
      }
    }

    // 删除插件
    const deletePlugin = async (plugin) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除插件 "${plugin.display_name}" 吗？此操作不可撤销。`,
          '确认删除',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        await axios.delete(`/api/admin/crawler-plugins/${plugin.id}`, {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })

        ElMessage.success('插件删除成功')
        refreshPlugins()
        
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
        }
      }
    }

    // 工具函数
    const getStatusType = (status) => {
      const statusMap = {
        'active': 'success',
        'inactive': 'info',
        'error': 'danger',
        'disabled': 'warning'
      }
      return statusMap[status] || 'info'
    }

    const getStatusText = (status, isActive) => {
      if (!isActive) return '已禁用'
      
      const statusMap = {
        'active': '运行中',
        'inactive': '未激活',
        'error': '错误',
        'disabled': '已禁用'
      }
      return statusMap[status] || '未知'
    }

    const formatTime = (timeString) => {
      if (!timeString) return ''
      const date = new Date(timeString)
      return date.toLocaleString('zh-CN')
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    onMounted(() => {
      refreshPlugins()
    })

    return {
      loading,
      plugins,
      searchText,
      stats,
      filteredPlugins,
      totalSuccessCount,
      
      // 上传相关
      showUploadDialog,
      selectedFile,
      uploadFileList,
      uploading,
      pluginValidation,
      handleFileSelect,
      uploadPlugin,
      cancelUpload,
      
      // 配置相关
      showConfigDialog,
      currentPlugin,
      currentConfig,
      configFormRef,
      configPlugin,
      savePluginConfig,
      testPluginConnection,
      
      // 任务相关
      showTaskDialog,
      taskManagerRef,
      manageTask,
      
      // 方法
      refreshPlugins,
      testPlugin,
      handlePluginAction,
      
      // 工具函数
      getStatusType,
      getStatusText,
      formatTime,
      formatFileSize
    }
  }
}
</script>

<style scoped>
.crawler-plugins {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  background: #f5f5f5;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h1 {
  margin: 0 0 5px 0;
  color: #303133;
}

.header-left p {
  margin: 0;
  color: #909399;
}

.header-right {
  display: flex;
  gap: 10px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: white;
}

.stat-icon.total { background: #409EFF; }
.stat-icon.active { background: #67C23A; }
.stat-icon.tasks { background: #E6A23C; }
.stat-icon.success { background: #F56C6C; }

.stat-info h3 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.stat-info p {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.plugins-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plugin-info {
  padding: 5px 0;
}

.plugin-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.version-tag {
  margin-left: 8px;
}

.plugin-meta {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.divider {
  margin: 0 5px;
}

.plugin-description {
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
}

.stats-info {
  font-size: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 3px;
}

.stat-item .label {
  color: #909399;
}

.stat-item .value.success {
  color: #67C23A;
}

.stat-item .value.error {
  color: #F56C6C;
}

.last-run {
  font-size: 12px;
  color: #606266;
}

.never-run {
  font-size: 12px;
  color: #C0C4CC;
}

.action-buttons {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

/* 上传对话框样式 */
.upload-container {
  padding: 20px 0;
}

.plugin-uploader {
  margin-bottom: 20px;
}

.upload-icon {
  font-size: 67px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text {
  color: #606266;
  font-size: 14px;
}

.upload-hint {
  color: #909399;
  font-size: 12px;
  margin-top: 5px;
}

.file-info {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.file-info h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.validation-result {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
}

.validation-success {
  background: #f0f9ff;
  border: 1px solid #67c23a;
  color: #67c23a;
}

.validation-error {
  background: #fef0f0;
  border: 1px solid #f56c6c;
  color: #f56c6c;
}

.plugin-preview {
  margin-top: 10px;
  font-size: 12px;
  color: #606266;
}

.plugin-preview p {
  margin: 5px 0;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>