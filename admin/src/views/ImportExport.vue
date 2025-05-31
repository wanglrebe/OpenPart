<!-- admin/src/views/ImportExport.vue -->
<template>
  <div class="import-export">
    <NavBar />
    
    <el-main class="main-content">
      <el-row :gutter="20">
        <!-- 导出功能 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>数据导出</span>
                <el-icon><Download /></el-icon>
              </div>
            </template>
            
            <el-form :model="exportForm" label-width="120px">
              <el-form-item label="导出格式">
                <el-radio-group v-model="exportForm.format">
                  <el-radio value="json">JSON 格式</el-radio>
                  <el-radio value="csv">CSV 格式</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="包含图片">
                <el-switch v-model="exportForm.include_images" />
              </el-form-item>
              
              <el-form-item label="时间范围">
                <el-date-picker
                  v-model="exportDateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  @change="updateExportDateRange"
                />
              </el-form-item>
              
              <el-form-item label="类别筛选">
                <el-select
                  v-model="exportForm.categories"
                  multiple
                  placeholder="选择要导出的类别（空表示全部）"
                  style="width: 100%"
                >
                  <el-option
                    v-for="category in availableCategories"
                    :key="category"
                    :label="category"
                    :value="category"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button
                  type="primary"
                  @click="exportData"
                  :loading="exportLoading"
                  style="width: 100%"
                >
                  <el-icon><Download /></el-icon>
                  {{ exportLoading ? '导出中...' : '开始导出' }}
                </el-button>
              </el-form-item>
            </el-form>
            
            <div class="export-info">
              <p><strong>说明：</strong></p>
              <ul>
                <li>JSON格式：保留完整数据结构，推荐用于备份</li>
                <li>CSV格式：Excel兼容，便于数据分析</li>
                <li>包含图片选项：是否导出图片URL信息</li>
              </ul>
            </div>
          </el-card>
        </el-col>
        
        <!-- 导入功能 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>数据导入</span>
                <el-icon><Upload /></el-icon>
              </div>
            </template>
            
            <el-form :model="importForm" label-width="120px">
              <el-form-item label="冲突处理">
                <el-radio-group v-model="importForm.conflict_strategy">
                  <el-radio value="skip">跳过重复</el-radio>
                  <el-radio value="update">更新现有</el-radio>
                  <el-radio value="rename">重命名导入</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="重复检查">
                <el-checkbox-group v-model="importForm.duplicate_check_fields">
                  <el-checkbox value="name">名称</el-checkbox>
                  <el-checkbox value="category">类别</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              
              <el-form-item label="数据验证">
                <el-switch v-model="importForm.validate_data" />
                <span class="help-text">开启后会验证必需字段</span>
              </el-form-item>
              
              <el-form-item label="选择文件">
                <el-upload
                  class="upload-area"
                  drag
                  action="#"
                  :auto-upload="false"
                  :on-change="handleFileSelect"
                  :file-list="fileList"
                  accept=".json,.csv"
                >
                  <el-icon class="upload-icon"><UploadFilled /></el-icon>
                  <div class="upload-text">将文件拖到此处，或<em>点击上传</em></div>
                  <div class="upload-hint">支持 JSON 和 CSV 格式</div>
                </el-upload>
              </el-form-item>
              
              <el-form-item>
                <el-button
                  type="primary"
                  @click="importData"
                  :loading="importLoading"
                  :disabled="!selectedFile"
                  style="width: 100%"
                >
                  <el-icon><Upload /></el-icon>
                  {{ importLoading ? '导入中...' : '开始导入' }}
                </el-button>
              </el-form-item>
            </el-form>
            
            <div class="template-section">
              <el-divider>模板下载</el-divider>
              <el-button-group>
                <el-button @click="downloadTemplate('csv')">
                  <el-icon><Document /></el-icon>
                  CSV 模板
                </el-button>
                <el-button @click="downloadTemplate('json')">
                  <el-icon><Document /></el-icon>
                  JSON 模板
                </el-button>
              </el-button-group>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 导入结果显示 -->
      <el-row v-if="importResult" style="margin-top: 20px">
        <el-col :span="24">
          <el-card>
            <template #header>
              <span>导入结果</span>
            </template>
            
            <el-row :gutter="20">
              <el-col :span="6">
                <el-statistic title="总处理数" :value="importResult.total_processed" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="成功导入" :value="importResult.successful_imports" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="跳过重复" :value="importResult.skipped_duplicates" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="更新现有" :value="importResult.updated_existing" />
              </el-col>
            </el-row>
            
            <div v-if="importResult.errors.length > 0" class="error-section">
              <el-divider>错误信息</el-divider>
              <el-table :data="importResult.errors" style="width: 100%" max-height="300">
                <el-table-column prop="row" label="行号" width="80" />
                <el-table-column prop="error" label="错误信息" />
              </el-table>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { Download, Upload, UploadFilled, Document } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import { auth } from '../utils/auth'
import axios from 'axios'

export default {
  name: 'ImportExport',
  components: {
    NavBar,
    Download,
    Upload,
    UploadFilled,
    Document
  },
  setup() {
    const exportLoading = ref(false)
    const importLoading = ref(false)
    const availableCategories = ref([])
    const exportDateRange = ref([])
    const selectedFile = ref(null)
    const fileList = ref([])
    const importResult = ref(null)
    
    // 导出表单
    const exportForm = reactive({
      format: 'json',
      include_images: true,
      date_from: null,
      date_to: null,
      categories: []
    })
    
    // 导入表单
    const importForm = reactive({
      conflict_strategy: 'skip',
      duplicate_check_fields: ['name', 'category'],
      validate_data: true
    })
    
    // 加载可用类别
    const loadCategories = async () => {
      try {
        const response = await axios.get('/api/public/parts/categories/')
        availableCategories.value = response.data
      } catch (error) {
        console.error('加载类别失败:', error)
      }
    }
    
    // 更新导出日期范围
    const updateExportDateRange = (dates) => {
      if (dates && dates.length === 2) {
        exportForm.date_from = dates[0]
        exportForm.date_to = dates[1]
      } else {
        exportForm.date_from = null
        exportForm.date_to = null
      }
    }
    
    // 导出数据 - 继续
    const exportData = async () => {
      try {
        exportLoading.value = true
        
        const response = await axios.post('/api/admin/import-export/export', exportForm, {
          headers: {
            'Authorization': `Bearer ${auth.getToken()}`
          },
          responseType: 'blob'
        })
        
        // 创建下载链接
        const blob = new Blob([response.data])
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // 生成文件名
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
        const filename = `openpart_export_${timestamp}.${exportForm.format}`
        link.download = filename
        
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('数据导出成功')
        
      } catch (error) {
        ElMessage.error('导出失败: ' + (error.response?.data?.detail || error.message))
        console.error('导出失败:', error)
      } finally {
        exportLoading.value = false
      }
    }
    
    // 文件选择处理
    const handleFileSelect = (file) => {
      selectedFile.value = file.raw
      fileList.value = [file]
      importResult.value = null // 清空之前的结果
    }
    
    // 导入数据 - 修复版本
    const importData = async () => {
      if (!selectedFile.value) {
        ElMessage.error('请先选择要导入的文件')
        return
      }
      
      try {
        await ElMessageBox.confirm(
          '导入操作将会修改数据库，建议先进行数据备份。确定要继续吗？',
          '确认导入',
          {
            confirmButtonText: '确定导入',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        importLoading.value = true
        
        // 创建FormData，简化参数传递
        const formData = new FormData()
        formData.append('file', selectedFile.value)
        formData.append('conflict_strategy', importForm.conflict_strategy)
        formData.append('validate_data', importForm.validate_data.toString())
        
        // 处理重复检查字段
        const checkName = importForm.duplicate_check_fields.includes('name')
        const checkCategory = importForm.duplicate_check_fields.includes('category')
        
        formData.append('duplicate_check_name', checkName.toString())
        formData.append('duplicate_check_category', checkCategory.toString())
        
        console.log('发送导入请求...')
        console.log('冲突策略:', importForm.conflict_strategy)
        console.log('数据验证:', importForm.validate_data)
        console.log('检查名称:', checkName)
        console.log('检查类别:', checkCategory)
        
        const response = await axios.post('/api/admin/import-export/import', formData, {
          headers: {
            'Authorization': `Bearer ${auth.getToken()}`,
            'Content-Type': 'multipart/form-data'
          }
        })
        
        importResult.value = response.data
        
        ElMessage.success(
          `导入完成！成功: ${response.data.successful_imports}, ` +
          `跳过: ${response.data.skipped_duplicates}, ` +
          `更新: ${response.data.updated_existing}` +
          (response.data.errors.length > 0 ? `，错误: ${response.data.errors.length}` : '')
        )
        
        // 清空文件选择
        fileList.value = []
        selectedFile.value = null
        
      } catch (error) {
        if (error !== 'cancel') {
          console.error('导入错误详情:', error)
          const errorMessage = error.response?.data?.detail || error.message || '未知错误'
          ElMessage.error('导入失败: ' + errorMessage)
        }
      } finally {
        importLoading.value = false
      }
    }
    
    // 下载模板
    const downloadTemplate = async (format) => {
      try {
        const response = await axios.get(`/api/admin/import-export/import/template`, {
          headers: {
            'Authorization': `Bearer ${auth.getToken()}`
          },
          params: { format },
          responseType: 'blob'
        })
        
        // 创建下载链接
        const blob = new Blob([response.data])
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `import_template.${format}`
        
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('模板下载成功')
        
      } catch (error) {
        ElMessage.error('模板下载失败')
        console.error('模板下载失败:', error)
      }
    }
    
    onMounted(() => {
      loadCategories()
    })
    
    return {
      exportLoading,
      importLoading,
      availableCategories,
      exportDateRange,
      selectedFile,
      fileList,
      importResult,
      exportForm,
      importForm,
      updateExportDateRange,
      exportData,
      handleFileSelect,
      importData,
      downloadTemplate
    }
  }
}
</script>

<style scoped>
.import-export {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  background: #f5f5f5;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.export-info {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 14px;
}

.export-info ul {
  margin: 10px 0;
  padding-left: 20px;
}

.export-info li {
  margin: 5px 0;
  color: #606266;
}

.upload-area {
  width: 100%;
}

.upload-icon {
  font-size: 67px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text {
  color: #606266;
  font-size: 14px;
  margin-bottom: 4px;
}

.upload-hint {
  color: #909399;
  font-size: 12px;
}

.help-text {
  font-size: 12px;
  color: #909399;
  margin-left: 10px;
}

.template-section {
  margin-top: 20px;
  text-align: center;
}

.error-section {
  margin-top: 20px;
}

.el-statistic {
  text-align: center;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.el-divider__text) {
  font-weight: bold;
  color: #303133;
}
</style>