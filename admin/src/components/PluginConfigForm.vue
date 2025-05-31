<!-- admin/src/components/PluginConfigForm.vue - 完整版（支持文件上传） -->
<template>
  <div class="plugin-config-form">
    <!-- 插件信息展示 -->
    <div class="plugin-info-section">
      <el-card shadow="never" class="info-card">
        <div class="plugin-header">
          <div class="plugin-basic">
            <h3>{{ plugin.display_name }}</h3>
            <div class="plugin-meta">
              <el-tag size="small">v{{ plugin.version }}</el-tag>
              <span class="author">{{ plugin.author }}</span>
              <span class="data-source">{{ plugin.data_source }}</span>
            </div>
          </div>
          <div class="plugin-status">
            <el-tag :type="plugin.is_active ? 'success' : 'info'">
              {{ plugin.is_active ? '已启用' : '未启用' }}
            </el-tag>
          </div>
        </div>
        
        <p class="plugin-description">{{ plugin.description }}</p>
        
        <!-- 插件权限和域名信息 -->
        <div class="plugin-details">
          <div class="detail-item" v-if="plugin.allowed_domains?.length">
            <strong>允许域名：</strong>
            <el-tag 
              v-for="domain in plugin.allowed_domains" 
              :key="domain" 
              size="small" 
              type="info"
              class="domain-tag"
            >
              {{ domain }}
            </el-tag>
          </div>
          
          <div class="detail-item" v-if="plugin.required_permissions?.length">
            <strong>需要权限：</strong>
            <el-tag 
              v-for="permission in plugin.required_permissions" 
              :key="permission" 
              size="small" 
              type="warning"
              class="permission-tag"
            >
              {{ getPermissionText(permission) }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 动态配置表单 -->
    <div class="config-form-section">
      <el-card shadow="never">
        <template #header>
          <div class="section-header">
            <span>插件配置</span>
            <div class="header-actions">
              <el-button 
                size="small" 
                @click="testConnection" 
                :loading="testing"
                :disabled="!hasValidConfig"
              >
                <el-icon><Link /></el-icon>
                测试连接
              </el-button>
              <el-button 
                size="small" 
                @click="resetConfig"
                :disabled="!hasChanges"
              >
                <el-icon><RefreshLeft /></el-icon>
                重置
              </el-button>
            </div>
          </div>
        </template>

        <!-- 测试结果显示 -->
        <div v-if="testResult" class="test-result-section">
          <el-alert
            :type="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? '连接测试成功' : '连接测试失败'"
            :description="testResult.message"
            :closable="true"
            @close="testResult = null"
          >
            <template v-if="testResult.success && testResult.response_time">
              <div class="test-details">
                <p><strong>响应时间：</strong>{{ testResult.response_time }} 秒</p>
                <div v-if="testResult.sample_data" class="sample-data">
                  <strong>示例数据：</strong>
                  <pre>{{ JSON.stringify(testResult.sample_data, null, 2) }}</pre>
                </div>
              </div>
            </template>
          </el-alert>
        </div>

        <!-- 动态生成的配置表单 -->
        <el-form
          ref="configFormRef"
          :model="formData"
          :rules="formRules"
          label-width="120px"
          class="config-form"
        >
          <div 
            v-for="field in configSchema" 
            :key="field.name"
            class="form-field-group"
          >
            <!-- 文本输入 -->
            <el-form-item 
              v-if="field.type === 'text'"
              :label="field.label"
              :prop="field.name"
              :required="field.required"
            >
              <el-input
                v-model="formData[field.name]"
                :placeholder="field.placeholder"
                clearable
              />
              <div v-if="field.help_text" class="help-text">
                {{ field.help_text }}
              </div>
            </el-form-item>

            <!-- 密码输入 -->
            <el-form-item 
              v-else-if="field.type === 'password'"
              :label="field.label"
              :prop="field.name"
              :required="field.required"
            >
              <el-input
                v-model="formData[field.name]"
                type="password"
                :placeholder="field.placeholder"
                show-password
                clearable
              />
              <div v-if="field.help_text" class="help-text">
                {{ field.help_text }}
              </div>
            </el-form-item>

            <!-- 数字输入 -->
            <el-form-item 
              v-else-if="field.type === 'number'"
              :label="field.label"
              :prop="field.name"
              :required="field.required"
            >
              <el-input-number
                v-model="formData[field.name]"
                :min="field.validation?.min"
                :max="field.validation?.max"
                :step="field.validation?.step || 1"
                :placeholder="field.placeholder"
                style="width: 100%"
              />
              <div v-if="field.help_text" class="help-text">
                {{ field.help_text }}
              </div>
            </el-form-item>

            <!-- 下拉选择 -->
            <el-form-item 
              v-else-if="field.type === 'select'"
              :label="field.label"
              :prop="field.name"
              :required="field.required"
            >
              <el-select
                v-model="formData[field.name]"
                :placeholder="field.placeholder || '请选择'"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="option in field.options"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
                />
              </el-select>
              <div v-if="field.help_text" class="help-text">
                {{ field.help_text }}
              </div>
            </el-form-item>

            <!-- 多行文本 -->
            <el-form-item 
              v-else-if="field.type === 'textarea'"
              :label="field.label"
              :prop="field.name"
              :required="field.required"
            >
              <el-input
                v-model="formData[field.name]"
                type="textarea"
                :rows="4"
                :placeholder="field.placeholder"
                resize="vertical"
              />
              <div v-if="field.help_text" class="help-text">
                {{ field.help_text }}
              </div>
            </el-form-item>

            <!-- 复选框 -->
            <el-form-item 
              v-else-if="field.type === 'checkbox'"
              :label="field.label"
              :prop="field.name"
            >
              <el-checkbox v-model="formData[field.name]">
                {{ field.help_text || field.label }}
              </el-checkbox>
            </el-form-item>

            <!-- 多选框组 -->
            <el-form-item 
              v-else-if="field.type === 'checkbox-group'"
              :label="field.label"
              :prop="field.name"
              :required="field.required"
            >
              <el-checkbox-group v-model="formData[field.name]">
                <el-checkbox
                  v-for="option in field.options"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </el-checkbox>
              </el-checkbox-group>
              <div v-if="field.help_text" class="help-text">
                {{ field.help_text }}
              </div>
            </el-form-item>

            <!-- 单选按钮组 -->
            <el-form-item 
              v-else-if="field.type === 'radio'"
              :label="field.label"
              :prop="field.name"
              :required="field.required"
            >
              <el-radio-group v-model="formData[field.name]">
                <el-radio
                  v-for="option in field.options"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </el-radio>
              </el-radio-group>
              <div v-if="field.help_text" class="help-text">
                {{ field.help_text }}
              </div>
            </el-form-item>

            <!-- URL输入 -->
            <el-form-item 
              v-else-if="field.type === 'url'"
              :label="field.label"
              :prop="field.name"
              :required="field.required"
            >
              <el-input
                v-model="formData[field.name]"
                :placeholder="field.placeholder"
                clearable
              >
                <template #prepend>
                  <el-icon><Link /></el-icon>
                </template>
              </el-input>
              <div v-if="field.help_text" class="help-text">
                {{ field.help_text }}
              </div>
            </el-form-item>

            <!-- JSON编辑器 -->
            <el-form-item 
              v-else-if="field.type === 'json'"
              :label="field.label"
              :prop="field.name"
              :required="field.required"
            >
              <el-input
                v-model="formData[field.name]"
                type="textarea"
                :rows="6"
                :placeholder="field.placeholder || '请输入有效的JSON格式'"
                class="json-editor"
              />
              <div class="json-actions">
                <el-button size="small" @click="formatJson(field.name)">
                  格式化
                </el-button>
                <el-button size="small" @click="validateJson(field.name)">
                  验证JSON
                </el-button>
              </div>
              <div v-if="field.help_text" class="help-text">
                {{ field.help_text }}
              </div>
            </el-form-item>

            <!-- 文件上传 - 新增 -->
            <el-form-item 
              v-else-if="field.type === 'file'"
              :label="field.label"
              :prop="field.name"
              :required="field.required"
            >
              <div class="file-upload-field">
                <!-- 显示当前文件信息 -->
                <div v-if="formData[field.name + '_info']" class="current-file-info">
                  <el-tag type="success" closable @close="clearUploadedFile(field.name)">
                    <el-icon><Document /></el-icon>
                    {{ formData[field.name + '_info'].filename }}
                    ({{ formatFileSize(formData[field.name + '_info'].file_size) }})
                  </el-tag>
                  <div class="file-upload-time">
                    上传时间: {{ formatUploadTime(formData[field.name + '_info'].uploaded_at) }}
                  </div>
                </div>
                
                <!-- 文件上传组件 -->
                <el-upload
                  class="plugin-file-uploader"
                  :action="uploadUrl"
                  :headers="uploadHeaders"
                  :data="{ field_name: field.name }"
                  :accept="field.validation?.accept || '*'"
                  :limit="1"
                  :on-success="(response) => handleFileUploadSuccess(response, field.name)"
                  :on-error="(error) => handleFileUploadError(error, field.name)"
                  :before-upload="(file) => beforeFileUpload(file, field)"
                  :show-file-list="false"
                  :disabled="uploading[field.name]"
                >
                  <el-button :loading="uploading[field.name]" :disabled="uploading[field.name]">
                    <el-icon><Upload /></el-icon>
                    {{ uploading[field.name] ? '上传中...' : '选择文件' }}
                  </el-button>
                </el-upload>
                
                <div v-if="field.help_text" class="help-text">
                  {{ field.help_text }}
                </div>
                
                <!-- 文件类型和大小限制说明 -->
                <div class="file-constraints">
                  <div v-if="field.validation?.accept" class="file-accept-info">
                    支持格式: {{ field.validation.accept }}
                  </div>
                  <div v-if="field.validation?.max_size" class="file-size-info">
                    最大大小: {{ formatFileSize(field.validation.max_size) }}
                  </div>
                </div>
              </div>
            </el-form-item>

            <!-- 不支持的字段类型 -->
            <el-form-item 
              v-else
              :label="field.label"
              :prop="field.name"
            >
              <el-alert
                type="warning"
                :title="`不支持的字段类型: ${field.type}`"
                :closable="false"
                show-icon
              />
            </el-form-item>
          </div>
        </el-form>

        <!-- 配置预览 -->
        <div class="config-preview-section">
          <el-collapse>
            <el-collapse-item title="配置预览" name="preview">
              <pre class="config-preview">{{ JSON.stringify(formData, null, 2) }}</pre>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-card>
    </div>

    <!-- 操作按钮 -->
    <div class="form-actions">
      <el-button @click="handleCancel">取消</el-button>
      <el-button 
        type="primary" 
        @click="saveConfig"
        :loading="saving"
        :disabled="!hasValidConfig"
      >
        {{ saving ? '保存中...' : '保存配置' }}
      </el-button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { Link, RefreshLeft, Document, Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { auth } from '../utils/auth'

export default {
  name: 'PluginConfigForm',
  components: {
    Link,
    RefreshLeft,
    Document,
    Upload
  },
  props: {
    plugin: {
      type: Object,
      required: true
    },
    config: {
      type: Object,
      default: () => ({})
    },
    onTest: {
      type: Function,
      required: true
    }
  },
  emits: ['save', 'cancel'],
  setup(props, { emit }) {
    const configFormRef = ref()
    const formData = reactive({})
    const originalConfig = ref({})
    const testResult = ref(null)
    const testing = ref(false)
    const saving = ref(false)
    
    // 文件上传相关
    const uploading = reactive({})
    const uploadUrl = '/api/admin/files/upload'
    const uploadHeaders = {
      'Authorization': `Bearer ${auth.getToken()}`
    }

    // 计算属性
    const configSchema = computed(() => {
      return props.plugin.config_schema || []
    })

    const hasValidConfig = computed(() => {
      // 检查必填字段是否已填写
      for (const field of configSchema.value) {
        if (field.required && !formData[field.name]) {
          return false
        }
      }
      return true
    })

    const hasChanges = computed(() => {
      return JSON.stringify(formData) !== JSON.stringify(originalConfig.value)
    })

    // 动态生成表单验证规则
    const formRules = computed(() => {
      const rules = {}
      
      configSchema.value.forEach(field => {
        const fieldRules = []
        
        // 必填验证
        if (field.required) {
          fieldRules.push({
            required: true,
            message: `${field.label}不能为空`,
            trigger: ['blur', 'change']
          })
        }
        
        // 字符串长度验证
        if (field.validation?.min_length || field.validation?.max_length) {
          fieldRules.push({
            min: field.validation.min_length || 0,
            max: field.validation.max_length || Infinity,
            message: `${field.label}长度应在${field.validation.min_length || 0}-${field.validation.max_length || '无限'}之间`,
            trigger: 'blur'
          })
        }
        
        // 正则验证
        if (field.validation?.pattern) {
          fieldRules.push({
            pattern: new RegExp(field.validation.pattern),
            message: field.validation.message || `${field.label}格式不正确`,
            trigger: 'blur'
          })
        }
        
        // URL验证
        if (field.type === 'url') {
          fieldRules.push({
            type: 'url',
            message: '请输入有效的URL地址',
            trigger: 'blur'
          })
        }
        
        // 数字范围验证
        if (field.type === 'number' && (field.validation?.min !== undefined || field.validation?.max !== undefined)) {
          fieldRules.push({
            type: 'number',
            min: field.validation.min,
            max: field.validation.max,
            message: `${field.label}应在${field.validation.min || 0}-${field.validation.max || '无限'}之间`,
            trigger: 'blur'
          })
        }
        
        // JSON格式验证
        if (field.type === 'json') {
          fieldRules.push({
            validator: (rule, value, callback) => {
              if (value && value.trim()) {
                try {
                  JSON.parse(value)
                  callback()
                } catch (e) {
                  callback(new Error('请输入有效的JSON格式'))
                }
              } else {
                callback()
              }
            },
            trigger: 'blur'
          })
        }
        
        if (fieldRules.length > 0) {
          rules[field.name] = fieldRules
        }
      })
      
      return rules
    })

    // 初始化表单数据
    const initFormData = () => {
      // 清空现有数据
      Object.keys(formData).forEach(key => {
        delete formData[key]
      })
      
      // 设置默认值
      configSchema.value.forEach(field => {
        let defaultValue = field.default
        
        // 根据字段类型设置默认值
        if (defaultValue === undefined) {
          switch (field.type) {
            case 'checkbox':
              defaultValue = false
              break
            case 'checkbox-group':
              defaultValue = []
              break
            case 'number':
              defaultValue = 0
              break
            case 'file':
              defaultValue = null
              break
            default:
              defaultValue = ''
          }
        }
        
        formData[field.name] = props.config[field.name] !== undefined 
          ? props.config[field.name] 
          : defaultValue
          
        // 文件字段的附加信息
        if (field.type === 'file') {
          formData[field.name + '_info'] = props.config[field.name + '_info'] || null
          uploading[field.name] = false
        }
      })
      
      // 保存原始配置用于对比
      originalConfig.value = { ...formData }
    }

    // 重置配置
    const resetConfig = () => {
      Object.assign(formData, originalConfig.value)
      testResult.value = null
    }

    // 测试连接
    const testConnection = async () => {
      // 先验证表单
      try {
        await configFormRef.value.validate()
      } catch (error) {
        ElMessage.error('请先完成必填字段的配置')
        return
      }

      testing.value = true
      testResult.value = null
      
      try {
        console.log('发送测试请求，配置:', { ...formData })
        const result = await props.onTest({ ...formData })
        console.log('收到测试结果:', result)
        
        if (result && typeof result === 'object' && 'success' in result) {
          testResult.value = result
          
          if (result.success) {
            ElMessage.success('连接测试成功')
          } else {
            ElMessage.error('连接测试失败: ' + (result.message || '未知错误'))
          }
        } else {
          console.error('意外的返回值格式:', result)
          testResult.value = {
            success: false,
            message: '测试连接返回数据格式异常'
          }
          ElMessage.error('测试连接失败：返回数据格式异常')
        }
      } catch (error) {
        console.error('测试连接错误:', error)
        testResult.value = {
          success: false,
          message: error.message || '测试连接时发生错误'
        }
        ElMessage.error('测试连接失败: ' + (error.message || '未知错误'))
      }
      
      testing.value = false
    }

    // 保存配置
    const saveConfig = async () => {
      try {
        await configFormRef.value.validate()
        
        saving.value = true
        emit('save', { ...formData })
        
      } catch (error) {
        ElMessage.error('请检查配置项是否正确填写')
      } finally {
        saving.value = false
      }
    }

    // 处理取消按钮
    const handleCancel = () => {
      emit('cancel')
    }

    // 文件上传相关方法
    const beforeFileUpload = (file, field) => {
      console.log('准备上传文件:', file.name, '字段:', field.name)
      
      // 检查文件大小
      if (field.validation?.max_size && file.size > field.validation.max_size) {
        ElMessage.error(`文件大小超过限制 (${formatFileSize(field.validation.max_size)})`)
        return false
      }
      
      // 检查文件类型
      if (field.validation?.accept) {
        const acceptTypes = field.validation.accept.split(',').map(type => type.trim())
        const fileExt = '.' + file.name.split('.').pop().toLowerCase()
        const isAccepted = acceptTypes.some(type => {
          if (type.startsWith('.')) {
            return type.toLowerCase() === fileExt
          }
          return file.type.includes(type)
        })
        
        if (!isAccepted) {
          ElMessage.error(`不支持的文件类型，支持: ${field.validation.accept}`)
          return false
        }
      }
      
      uploading[field.name] = true
      return true
    }

    const handleFileUploadSuccess = (response, fieldName) => {
      console.log('文件上传成功:', response)
      uploading[fieldName] = false
      
      if (response.success) {
        // 保存文件ID和信息
        formData[fieldName] = response.file_id
        formData[fieldName + '_info'] = {
          file_id: response.file_id,
          filename: response.filename,
          file_size: response.file_size,
          content_type: response.content_type,
          download_url: response.download_url,
          uploaded_at: new Date().toISOString()
        }
        
        ElMessage.success(`文件上传成功: ${response.filename}`)
      } else {
        ElMessage.error('文件上传失败: ' + response.message)
      }
    }

    const handleFileUploadError = (error, fieldName) => {
      console.error('文件上传失败:', error)
      uploading[fieldName] = false
      ElMessage.error('文件上传失败，请重试')
    }

    const clearUploadedFile = (fieldName) => {
      // 清空文件相关数据
      formData[fieldName] = null
      formData[fieldName + '_info'] = null
      ElMessage.info('已清除上传的文件')
    }

    // 工具函数
    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const formatUploadTime = (timeString) => {
      if (!timeString) return ''
      return new Date(timeString).toLocaleString('zh-CN')
    }

    // JSON相关方法
    const formatJson = (fieldName) => {
      try {
        const jsonObj = JSON.parse(formData[fieldName])
        formData[fieldName] = JSON.stringify(jsonObj, null, 2)
        ElMessage.success('JSON格式化成功')
      } catch (error) {
        ElMessage.error('JSON格式无效，无法格式化')
      }
    }

    const validateJson = (fieldName) => {
      try {
        JSON.parse(formData[fieldName])
        ElMessage.success('JSON格式验证通过')
      } catch (error) {
        ElMessage.error(`JSON格式错误: ${error.message}`)
      }
    }

    // 权限文本转换
    const getPermissionText = (permission) => {
      const permissionMap = {
        'network': '网络访问',
        'file_read': '文件读取',
        'file_write': '文件写入'
      }
      return permissionMap[permission] || permission
    }

    // 监听配置变化
    watch(() => props.config, (newConfig) => {
      initFormData()
    }, { deep: true })

    onMounted(() => {
      initFormData()
    })

    return {
      configFormRef,
      formData,
      formRules,
      configSchema,
      testResult,
      testing,
      saving,
      hasValidConfig,
      hasChanges,
      
      // 文件上传相关
      uploading,
      uploadUrl,
      uploadHeaders,
      
      // 方法
      resetConfig,
      testConnection,
      saveConfig,
      handleCancel,
      formatJson,
      validateJson,
      getPermissionText,
      
      // 文件上传方法
      beforeFileUpload,
      handleFileUploadSuccess,
      handleFileUploadError,
      clearUploadedFile,
      formatFileSize,
      formatUploadTime
    }
  }
}
</script>

<style scoped>
.plugin-config-form {
  max-width: 800px;
  margin: 0 auto;
}

.plugin-info-section {
  margin-bottom: 20px;
}

.info-card {
  border: 1px solid #e4e7ed;
}

.plugin-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.plugin-basic h3 {
  margin: 0 0 8px 0;
  color: #303133;
}

.plugin-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #909399;
}

.plugin-description {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 15px;
}

.plugin-details {
  border-top: 1px solid #f5f7fa;
  padding-top: 15px;
}

.detail-item {
  margin-bottom: 8px;
  font-size: 14px;
}

.domain-tag, .permission-tag {
  margin-right: 5px;
  margin-bottom: 5px;
}

.config-form-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.test-result-section {
  margin-bottom: 20px;
}

.test-details {
  margin-top: 10px;
  font-size: 14px;
}

.sample-data pre {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.config-form {
  margin-bottom: 20px;
}

.form-field-group {
  margin-bottom: 20px;
}

.help-text {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.4;
}

.json-editor {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.json-actions {
  margin-top: 8px;
  display: flex;
  gap: 10px;
}

/* 文件上传相关样式 */
.file-upload-field {
  width: 100%;
}

.current-file-info {
  margin-bottom: 10px;
  padding: 10px;
  background: #f0f9ff;
  border: 1px solid #e1f5fe;
  border-radius: 4px;
}

.file-upload-time {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}

.plugin-file-uploader .el-upload {
  width: 100%;
}

.plugin-file-uploader .el-button {
  width: 100%;
}

.file-constraints {
  margin-top: 8px;
}

.file-accept-info,
.file-size-info {
  font-size: 12px;
  color: #909399;
  margin-top: 3px;
}

.config-preview-section {
  margin-top: 20px;
}

.config-preview {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 300px;
  overflow-y: auto;
  color: #606266;
}

.form-actions {
  text-align: right;
  padding: 20px 0;
  border-top: 1px solid #e4e7ed;
}

.form-actions .el-button {
  margin-left: 10px;
}

:deep(.el-collapse-item__header) {
  font-size: 14px;
  font-weight: 500;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-alert__description) {
  font-size: 14px;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.el-divider__text) {
  font-weight: bold;
  color: #303133;
}
</style>