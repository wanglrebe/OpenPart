<!-- admin/src/components/PluginTaskManager.vue -->
<template>
  <div class="plugin-task-manager">
    <!-- 任务统计 -->
    <div class="task-stats">
      <el-row :gutter="15">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-number">{{ taskStats.total }}</div>
            <div class="stat-label">总任务</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item running">
            <div class="stat-number">{{ taskStats.running }}</div>
            <div class="stat-label">运行中</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item completed">
            <div class="stat-number">{{ taskStats.completed }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item failed">
            <div class="stat-number">{{ taskStats.failed }}</div>
            <div class="stat-label">失败</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 操作工具栏 -->
    <div class="task-toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="showCreateTaskDialog = true">
          <el-icon><Plus /></el-icon>
          创建任务
        </el-button>
        <el-button @click="refreshTasks">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-input
          v-model="searchText"
          placeholder="搜索任务..."
          style="width: 200px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 120px; margin-left: 10px">
          <el-option label="全部" value="" />
          <el-option label="等待中" value="pending" />
          <el-option label="运行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
          <el-option label="已停止" value="stopped" />
        </el-select>
      </div>
    </div>

    <!-- 任务列表 -->
    <el-table :data="filteredTasks" v-loading="loading" class="task-table">
      <el-table-column label="任务信息" min-width="250">
        <template #default="scope">
          <div class="task-info">
            <div class="task-name">{{ scope.row.name }}</div>
            <div class="task-description">{{ scope.row.description || '无描述' }}</div>
            <div class="task-meta">
              <span class="schedule-type">
                {{ getScheduleTypeText(scope.row.schedule_type) }}
              </span>
              <span class="created-time">
                创建于 {{ formatTime(scope.row.created_at) }}
              </span>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getTaskStatusType(scope.row.status)">
            {{ getTaskStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="执行统计" width="120">
        <template #default="scope">
          <div class="execution-stats">
            <div class="stat-line">
              运行: <span class="stat-value">{{ scope.row.run_count || 0 }}</span>
            </div>
            <div class="stat-line">
              成功: <span class="stat-value success">{{ scope.row.success_count || 0 }}</span>
            </div>
            <div class="stat-line">
              错误: <span class="stat-value error">{{ scope.row.error_count || 0 }}</span>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="最后执行" width="150">
        <template #default="scope">
          <div v-if="scope.row.started_at" class="last-execution">
            <div class="execution-time">{{ formatTime(scope.row.started_at) }}</div>
            <div v-if="scope.row.execution_time" class="duration">
              耗时: {{ scope.row.execution_time }}s
            </div>
          </div>
          <span v-else class="never-executed">从未执行</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="250">
        <template #default="scope">
          <div class="task-actions">
            <el-button
              size="small"
              type="success"
              @click="executeTask(scope.row)"
              :disabled="scope.row.status === 'running'"
              :loading="scope.row.id === executingTaskId"
            >
              {{ scope.row.status === 'running' ? '运行中' : '执行' }}
            </el-button>
            
            <el-button
              size="small"
              type="warning"
              @click="stopTask(scope.row)"
              :disabled="scope.row.status !== 'running'"
            >
              停止
            </el-button>
            
            <el-dropdown @command="(command) => handleTaskAction(command, scope.row)">
              <el-button size="small">
                更多<el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit" icon="Edit">编辑任务</el-dropdown-item>
                  <el-dropdown-item command="logs" icon="Document">查看日志</el-dropdown-item>
                  <el-dropdown-item command="config" icon="Setting">执行配置</el-dropdown-item>
                  <el-dropdown-item command="delete" icon="Delete" divided>删除任务</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="totalTasks"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadTasks"
        @current-change="loadTasks"
      />
    </div>

    <!-- 创建任务对话框 -->
    <el-dialog
      title="创建新任务"
      v-model="showCreateTaskDialog"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="taskForm" :rules="taskFormRules" ref="taskFormRef" label-width="100px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="任务描述" prop="description">
          <el-input
            v-model="taskForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述"
          />
        </el-form-item>
        
        <el-form-item label="调度类型" prop="schedule_type">
          <el-radio-group v-model="taskForm.schedule_type">
            <el-radio label="manual">手动执行</el-radio>
            <el-radio label="cron">定时执行</el-radio>
            <el-radio label="interval">间隔执行</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- 定时执行配置 -->
        <el-form-item 
          v-if="taskForm.schedule_type === 'cron'" 
          label="Cron表达式" 
          prop="cron_expression"
        >
          <el-input
            v-model="taskForm.cron_expression"
            placeholder="例如: 0 0 * * * (每天零点执行)"
          />
          <div class="help-text">
            格式: 秒 分 时 日 月 周，<a href="#" @click.prevent="showCronHelp">查看帮助</a>
          </div>
        </el-form-item>
        
        <!-- 间隔执行配置 -->
        <el-form-item 
          v-if="taskForm.schedule_type === 'interval'" 
          label="执行间隔"
        >
          <el-row :gutter="10">
            <el-col :span="12">
              <el-input-number 
                v-model="taskForm.interval_value" 
                :min="1" 
                placeholder="间隔数值"
                style="width: 100%"
              />
            </el-col>
            <el-col :span="12">
              <el-select v-model="taskForm.interval_unit" style="width: 100%">
                <el-option label="分钟" value="minutes" />
                <el-option label="小时" value="hours" />
                <el-option label="天" value="days" />
              </el-select>
            </el-col>
          </el-row>
        </el-form-item>
        
        <el-form-item label="使用插件默认配置">
          <el-switch v-model="taskForm.use_default_config" />
          <div class="help-text">关闭后可为此任务单独配置参数</div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="cancelCreateTask">取消</el-button>
        <el-button type="primary" @click="createTask" :loading="creating">
          {{ creating ? '创建中...' : '创建任务' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 任务日志对话框 -->
    <el-dialog
      :title="`任务日志 - ${currentTask?.name}`"
      v-model="showLogsDialog"
      width="900px"
      :close-on-click-modal="false"
    >
      <div class="logs-container">
        <!-- 日志头部信息 -->
        <div class="logs-header">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="log-stat">
                <span class="label">执行状态:</span>
                <el-tag :type="getTaskStatusType(currentTask?.status)">
                  {{ getTaskStatusText(currentTask?.status) }}
                </el-tag>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="log-stat">
                <span class="label">执行时间:</span>
                <span>{{ currentTask?.execution_time || 0 }}秒</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="log-stat">
                <span class="label">数据数量:</span>
                <span>{{ currentTask?.data_count || 0 }}条</span>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 错误信息 -->
        <div v-if="currentTask?.error_message" class="error-section">
          <el-alert
            type="error"
            title="执行错误"
            :description="currentTask.error_message"
            show-icon
            :closable="false"
          />
        </div>

        <!-- 日志内容 -->
        <div class="logs-content">
          <div class="logs-toolbar">
            <el-button size="small" @click="refreshLogs">
              <el-icon><Refresh /></el-icon>
              刷新日志
            </el-button>
            <el-button size="small" @click="downloadLogs">
              <el-icon><Download /></el-icon>
              下载日志
            </el-button>
          </div>
          
          <div class="logs-viewer" ref="logsViewer">
            <div v-if="taskLogs.length === 0 && !logsLoading" class="no-logs">
              暂无日志信息
            </div>
            <div v-else-if="logsLoading" class="logs-loading">
              <el-icon class="loading-icon"><Loading /></el-icon>
              加载日志中...
            </div>
            <div v-else class="logs-list">
              <div 
                v-for="(log, index) in taskLogs" 
                :key="index"
                class="log-entry"
                :class="getLogLevel(log)"
              >
                <span class="log-time">{{ formatLogTime(log.timestamp) }}</span>
                <span class="log-content">{{ log.message || log }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 执行配置对话框 -->
    <el-dialog
      :title="`执行配置 - ${currentTask?.name}`"
      v-model="showConfigDialog"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="execution-config">
        <el-alert
          type="info"
          title="执行配置"
          description="可以临时修改配置参数，仅对本次执行有效"
          :closable="false"
          show-icon
        />
        
        <PluginConfigForm
          v-if="plugin && currentTask"
          :plugin="plugin"
          :config="executionConfig"
          @save="executeWithConfig"
          @cancel="showConfigDialog = false"
          ref="executionConfigRef"
        />
      </div>
    </el-dialog>

    <!-- Cron帮助对话框 -->
    <el-dialog
      title="Cron表达式帮助"
      v-model="showCronHelpDialog"
      width="700px"
    >
      <div class="cron-help">
        <h4>Cron表达式格式</h4>
        <p>格式: 秒 分 时 日 月 周</p>
        
        <el-table :data="cronExamples" class="cron-examples">
          <el-table-column prop="expression" label="表达式" width="200" />
          <el-table-column prop="description" label="说明" />
        </el-table>
        
        <h4>特殊字符说明</h4>
        <ul class="cron-special-chars">
          <li><code>*</code> - 匹配任意值</li>
          <li><code>?</code> - 不关心，仅用于日和周</li>
          <li><code>,</code> - 列举多个值</li>
          <li><code>-</code> - 范围</li>
          <li><code>/</code> - 步长</li>
        </ul>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { 
  Plus, Refresh, Search, ArrowDown, Download, Loading
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PluginConfigForm from './PluginConfigForm.vue'
import { auth } from '../utils/auth'
import axios from 'axios'

export default {
  name: 'PluginTaskManager',
  components: {
    Plus, Refresh, Search, ArrowDown, Download, Loading,
    PluginConfigForm
  },
  props: {
    plugin: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const loading = ref(false)
    const tasks = ref([])
    const searchText = ref('')
    const statusFilter = ref('')
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalTasks = ref(0)
    const executingTaskId = ref(null)

    // 任务统计
    const taskStats = reactive({
      total: 0,
      running: 0,
      completed: 0,
      failed: 0
    })

    // 创建任务相关
    const showCreateTaskDialog = ref(false)
    const creating = ref(false)
    const taskFormRef = ref()
    const taskForm = reactive({
      name: '',
      description: '',
      schedule_type: 'manual',
      cron_expression: '',
      interval_value: 1,
      interval_unit: 'hours',
      use_default_config: true
    })

    // 日志相关
    const showLogsDialog = ref(false)
    const currentTask = ref(null)
    const taskLogs = ref([])
    const logsLoading = ref(false)
    const logsViewer = ref()

    // 配置相关
    const showConfigDialog = ref(false)
    const executionConfig = ref({})
    const executionConfigRef = ref()

    // Cron帮助
    const showCronHelpDialog = ref(false)
    const cronExamples = [
      { expression: '0 0 0 * * ?', description: '每天零点执行' },
      { expression: '0 0 12 * * ?', description: '每天中午12点执行' },
      { expression: '0 0 9-17 * * MON-FRI', description: '工作日9-17点每小时执行' },
      { expression: '0 */30 * * * ?', description: '每30分钟执行一次' },
      { expression: '0 0 0 1 * ?', description: '每月1号零点执行' },
      { expression: '0 0 0 ? * SUN', description: '每周日零点执行' }
    ]

    // 表单验证规则
    const taskFormRules = {
      name: [
        { required: true, message: '请输入任务名称', trigger: 'blur' },
        { min: 2, max: 50, message: '任务名称长度在2-50个字符', trigger: 'blur' }
      ],
      cron_expression: [
        { 
          required: true, 
          message: '请输入Cron表达式', 
          trigger: 'blur',
          validator: (rule, value, callback) => {
            if (taskForm.schedule_type === 'cron' && !value) {
              callback(new Error('请输入Cron表达式'))
            } else {
              callback()
            }
          }
        }
      ]
    }

    // 计算属性
    const filteredTasks = computed(() => {
      let filtered = tasks.value

      // 搜索过滤
      if (searchText.value) {
        const search = searchText.value.toLowerCase()
        filtered = filtered.filter(task => 
          task.name.toLowerCase().includes(search) ||
          (task.description && task.description.toLowerCase().includes(search))
        )
      }

      // 状态过滤
      if (statusFilter.value) {
        filtered = filtered.filter(task => task.status === statusFilter.value)
      }

      return filtered
    })

    // 加载任务列表
    const loadTasks = async () => {
      loading.value = true
      try {
        const response = await axios.get(`/api/admin/crawler-plugins/${props.plugin.id}/tasks`, {
          headers: { Authorization: `Bearer ${auth.getToken()}` },
          params: {
            skip: (currentPage.value - 1) * pageSize.value,
            limit: pageSize.value
          }
        })

        tasks.value = response.data
        totalTasks.value = response.data.length

        // 更新统计
        updateTaskStats()

      } catch (error) {
        ElMessage.error('加载任务列表失败')
        console.error(error)
      }
      loading.value = false
    }

    // 更新任务统计
    const updateTaskStats = () => {
      taskStats.total = tasks.value.length
      taskStats.running = tasks.value.filter(t => t.status === 'running').length
      taskStats.completed = tasks.value.filter(t => t.status === 'completed').length
      taskStats.failed = tasks.value.filter(t => t.status === 'failed').length
    }

    // 刷新任务
    const refreshTasks = () => {
      loadTasks()
    }

    // 创建任务
    const createTask = async () => {
      try {
        await taskFormRef.value.validate()

        creating.value = true

        // 构建调度配置
        let scheduleConfig = {}
        if (taskForm.schedule_type === 'cron') {
          scheduleConfig.cron_expression = taskForm.cron_expression
        } else if (taskForm.schedule_type === 'interval') {
          scheduleConfig.interval_value = taskForm.interval_value
          scheduleConfig.interval_unit = taskForm.interval_unit
        }

        const taskData = {
          name: taskForm.name,
          description: taskForm.description,
          schedule_type: taskForm.schedule_type,
          schedule_config: scheduleConfig,
          config: taskForm.use_default_config ? null : {}
        }

        await axios.post(`/api/admin/crawler-plugins/${props.plugin.id}/tasks`, taskData, {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })

        ElMessage.success('任务创建成功')
        cancelCreateTask()
        refreshTasks()

      } catch (error) {
        ElMessage.error('创建任务失败: ' + (error.response?.data?.detail || error.message))
      }
      creating.value = false
    }

    // 取消创建任务
    const cancelCreateTask = () => {
      showCreateTaskDialog.value = false
      Object.assign(taskForm, {
        name: '',
        description: '',
        schedule_type: 'manual',
        cron_expression: '',
        interval_value: 1,
        interval_unit: 'hours',
        use_default_config: true
      })
    }

    // 执行任务
    const executeTask = async (task) => {
      try {
        await ElMessageBox.confirm(
          `确定要执行任务 "${task.name}" 吗？`,
          '确认执行',
          {
            confirmButtonText: '确定执行',
            cancelButtonText: '取消',
            type: 'info'
          }
        )

        executingTaskId.value = task.id

        await axios.post(`/api/admin/crawler-plugins/${props.plugin.id}/tasks/${task.id}/execute`, {}, {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })

        ElMessage.success('任务开始执行')
        
        // 延迟刷新，让任务状态更新
        setTimeout(() => {
          refreshTasks()
          executingTaskId.value = null
        }, 1000)

      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('执行任务失败: ' + (error.response?.data?.detail || error.message))
        }
        executingTaskId.value = null
      }
    }

    // 停止任务
    const stopTask = async (task) => {
      try {
        await ElMessageBox.confirm(
          `确定要停止任务 "${task.name}" 吗？`,
          '确认停止',
          {
            confirmButtonText: '确定停止',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        await axios.post(`/api/admin/crawler-plugins/${props.plugin.id}/tasks/${task.id}/stop`, {}, {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })

        ElMessage.success('任务已停止')
        refreshTasks()

      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('停止任务失败: ' + (error.response?.data?.detail || error.message))
        }
      }
    }

    // 处理任务操作
    const handleTaskAction = async (command, task) => {
      currentTask.value = task

      switch (command) {
        case 'edit':
          // TODO: 实现编辑任务
          ElMessage.info('编辑任务功能开发中...')
          break
        case 'logs':
          await showTaskLogs(task)
          break
        case 'config':
          showExecutionConfig(task)
          break
        case 'delete':
          await deleteTask(task)
          break
      }
    }

    // 显示任务日志
    const showTaskLogs = async (task) => {
      showLogsDialog.value = true
      await loadTaskLogs(task.id)
    }

    // 加载任务日志
    const loadTaskLogs = async (taskId) => {
      logsLoading.value = true
      try {
        const response = await axios.get(`/api/admin/crawler-plugins/tasks/${taskId}/logs`, {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })

        taskLogs.value = response.data.logs || []

      } catch (error) {
        ElMessage.error('加载日志失败')
        console.error(error)
      }
      logsLoading.value = false
    }

    // 刷新日志
    const refreshLogs = () => {
      if (currentTask.value) {
        loadTaskLogs(currentTask.value.id)
      }
    }

    // 下载日志
    const downloadLogs = () => {
      if (taskLogs.value.length === 0) {
        ElMessage.warning('暂无日志可下载')
        return
      }

      const logContent = taskLogs.value.map(log => 
        typeof log === 'string' ? log : `${log.timestamp || ''} ${log.message || log}`
      ).join('\n')

      const blob = new Blob([logContent], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `task_${currentTask.value.id}_logs.txt`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }

    // 显示执行配置
    const showExecutionConfig = (task) => {
      executionConfig.value = { ...props.plugin.config }
      showConfigDialog.value = true
    }

    // 使用配置执行
    const executeWithConfig = async (config) => {
      try {
        await axios.post(`/api/admin/crawler-plugins/${props.plugin.id}/tasks/${currentTask.value.id}/execute`, {
          config
        }, {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })

        ElMessage.success('任务开始执行')
        showConfigDialog.value = false
        refreshTasks()

      } catch (error) {
        ElMessage.error('执行任务失败: ' + (error.response?.data?.detail || error.message))
      }
    }

    // 删除任务
    const deleteTask = async (task) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除任务 "${task.name}" 吗？此操作不可撤销。`,
          '确认删除',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        await axios.delete(`/api/admin/crawler-plugins/${props.plugin.id}/tasks/${task.id}`, {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })

        ElMessage.success('任务删除成功')
        refreshTasks()

      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除任务失败: ' + (error.response?.data?.detail || error.message))
        }
      }
    }

    // 显示Cron帮助
    const showCronHelp = () => {
      showCronHelpDialog.value = true
    }

    // 工具函数
    const getScheduleTypeText = (type) => {
      const typeMap = {
        'manual': '手动',
        'cron': '定时',
        'interval': '间隔'
      }
      return typeMap[type] || type
    }

    const getTaskStatusType = (status) => {
      const statusMap = {
        'pending': 'info',
        'running': 'warning',
        'completed': 'success',
        'failed': 'danger',
        'stopped': 'info'
      }
      return statusMap[status] || 'info'
    }

    const getTaskStatusText = (status) => {
      const statusMap = {
        'pending': '等待中',
        'running': '运行中',
        'completed': '已完成',
        'failed': '失败',
        'stopped': '已停止'
      }
      return statusMap[status] || status
    }

    const formatTime = (timeString) => {
      if (!timeString) return ''
      const date = new Date(timeString)
      return date.toLocaleString('zh-CN')
    }

    const formatLogTime = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleTimeString('zh-CN')
    }

    const getLogLevel = (log) => {
      if (typeof log === 'string') {
        if (log.includes('错误') || log.includes('失败') || log.includes('ERROR')) {
          return 'error'
        }
        if (log.includes('警告') || log.includes('WARN')) {
          return 'warning'
        }
        if (log.includes('成功') || log.includes('完成')) {
          return 'success'
        }
      }
      return 'info'
    }

    // 监听插件变化
    watch(() => props.plugin, () => {
      if (props.plugin) {
        refreshTasks()
      }
    }, { immediate: true })

    onMounted(() => {
      if (props.plugin) {
        loadTasks()
      }
    })

    return {
      loading,
      tasks,
      filteredTasks,
      searchText,
      statusFilter,
      currentPage,
      pageSize,
      totalTasks,
      taskStats,
      executingTaskId,

      // 创建任务
      showCreateTaskDialog,
      creating,
      taskFormRef,
      taskForm,
      taskFormRules,
      createTask,
      cancelCreateTask,

      // 日志
      showLogsDialog,
      currentTask,
      taskLogs,
      logsLoading,
      logsViewer,
      refreshLogs,
      downloadLogs,

      // 配置
      showConfigDialog,
      executionConfig,
      executionConfigRef,
      executeWithConfig,

      // Cron帮助
      showCronHelpDialog,
      cronExamples,
      showCronHelp,

      // 方法
      loadTasks,
      refreshTasks,
      executeTask,
      stopTask,
      handleTaskAction,
      showTaskLogs,

      // 工具函数
      getScheduleTypeText,
      getTaskStatusType,
      getTaskStatusText,
      formatTime,
      formatLogTime,
      getLogLevel,
      plugin: props.plugin
    }
  }
}
</script>

<style scoped>
.plugin-task-manager {
  padding: 20px 0;
}

.task-stats {
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: white;
  border-radius: 4px;
  border-left: 4px solid #e4e7ed;
}

.stat-item.running {
  border-left-color: #e6a23c;
}

.stat-item.completed {
  border-left-color: #67c23a;
}

.stat-item.failed {
  border-left-color: #f56c6c;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.task-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.toolbar-left {
  display: flex;
  gap: 10px;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.task-table {
  background: white;
  border-radius: 6px;
}

.task-info {
  padding: 5px 0;
}

.task-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.task-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.task-meta {
  font-size: 12px;
  color: #909399;
}

.schedule-type {
  margin-right: 10px;
}

.execution-stats {
  font-size: 12px;
}

.stat-line {
  margin-bottom: 3px;
}

.stat-value.success {
  color: #67c23a;
}

.stat-value.error {
  color: #f56c6c;
}

.last-execution {
  font-size: 12px;
}

.execution-time {
  color: #606266;
  margin-bottom: 3px;
}

.duration {
  color: #909399;
}

.never-executed {
  font-size: 12px;
  color: #c0c4cc;
}

.task-actions {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.help-text {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.logs-container {
  max-height: 600px;
}

.logs-header {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 15px;
}

.log-stat {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.log-stat .label {
  color: #606266;
  font-weight: 500;
}

.error-section {
  margin-bottom: 15px;
}

.logs-content {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.logs-toolbar {
  padding: 10px 15px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  gap: 10px;
}

.logs-viewer {
  height: 400px;
  overflow-y: auto;
  background: #fafafa;
}

.no-logs {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  font-size: 14px;
}

.logs-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #606266;
  font-size: 14px;
}

.loading-icon {
  margin-right: 10px;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.logs-list {
  padding: 10px;
}

.log-entry {
  display: flex;
  margin-bottom: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  border-left: 3px solid #e4e7ed;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.4;
}

.log-entry.info {
  border-left-color: #409eff;
}

.log-entry.success {
  border-left-color: #67c23a;
  background: #f0f9ff;
}

.log-entry.warning {
  border-left-color: #e6a23c;
  background: #fdf6ec;
}

.log-entry.error {
  border-left-color: #f56c6c;
  background: #fef0f0;
}

.log-time {
  color: #909399;
  margin-right: 15px;
  white-space: nowrap;
  min-width: 80px;
}

.log-content {
  color: #303133;
  word-break: break-all;
  flex: 1;
}

.execution-config {
  padding: 20px 0;
}

.cron-help h4 {
  color: #303133;
  margin-bottom: 15px;
}

.cron-help p {
  color: #606266;
  margin-bottom: 20px;
}

.cron-examples {
  margin-bottom: 20px;
}

.cron-special-chars {
  list-style: none;
  padding: 0;
}

.cron-special-chars li {
  margin-bottom: 8px;
  color: #606266;
}

.cron-special-chars code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  color: #e6a23c;
  margin-right: 10px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

:deep(.el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-alert__description) {
  font-size: 14px;
  line-height: 1.6;
}
</style>