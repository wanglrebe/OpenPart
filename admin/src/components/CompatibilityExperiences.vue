<template>
  <div class="compatibility-experiences">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          添加经验
        </el-button>
        <el-button @click="showBatchImportDialog = true">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button @click="exportExperiences" :disabled="selectedExperiences.length === 0">
          <el-icon><Download /></el-icon>
          导出选中 ({{ selectedExperiences.length }})
        </el-button>
      </div>
      
      <div class="toolbar-right">
        <el-input
          v-model="searchText"
          placeholder="搜索零件名称..."
          style="width: 200px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 120px; margin-left: 10px">
          <el-option label="全部" value="" />
          <el-option label="兼容" value="compatible" />
          <el-option label="不兼容" value="incompatible" />
          <el-option label="有条件兼容" value="conditional" />
        </el-select>
        <el-select v-model="sourceFilter" placeholder="来源筛选" style="width: 120px; margin-left: 10px">
          <el-option label="全部来源" value="" />
          <el-option label="管理员" value="admin" />
          <el-option label="官方" value="official" />
          <el-option label="用户贡献" value="user_contribution" />
        </el-select>
        <el-button @click="refresh" :loading="loading">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 经验列表 -->
    <div class="table-container">
      <el-table 
        :data="filteredExperiences" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        style="width: 100%; height: 100%"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column label="零件组合" min-width="300">
          <template #default="scope">
            <div class="part-combination">
              <div class="part-item">
                <el-tag type="info" size="small">A</el-tag>
                <span class="part-name">{{ scope.row.part_a_name || `ID: ${scope.row.part_a_id}` }}</span>
              </div>
              <div class="combination-arrow">
                <el-icon><Promotion /></el-icon>
              </div>
              <div class="part-item">
                <el-tag type="info" size="small">B</el-tag>
                <span class="part-name">{{ scope.row.part_b_name || `ID: ${scope.row.part_b_id}` }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="兼容性状态" width="120" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.compatibility_status)">
              {{ getStatusText(scope.row.compatibility_status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="评分" width="100" align="center">
          <template #default="scope">
            <div class="score-display">
              <el-progress 
                :percentage="scope.row.compatibility_score || 0" 
                :color="getScoreColor(scope.row.compatibility_score)"
                :show-text="false"
                :stroke-width="8"
              />
              <span class="score-text">{{ scope.row.compatibility_score || 0 }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="数据来源" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getSourceType(scope.row.source)" size="small">
              {{ getSourceText(scope.row.source) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="验证状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getVerificationStatusType(scope.row.verification_status)" size="small">
              {{ getVerificationStatusText(scope.row.verification_status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="备注" show-overflow-tooltip>
          <template #default="scope">
            <span>{{ scope.row.notes || '无备注' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="添加时间" width="150">
          <template #default="scope">
            <span>{{ formatTime(scope.row.created_at) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="editExperience(scope.row)">
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="primary"
              @click="viewDetails(scope.row)"
            >
              详情
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deleteExperience(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100]"
        :total="totalExperiences"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadExperiences"
        @current-change="loadExperiences"
      />
    </div>

    <!-- 创建/编辑经验对话框 -->
    <el-dialog
      :title="editingExperience ? '编辑兼容性经验' : '添加兼容性经验'"
      v-model="showCreateDialog"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="experienceForm" :rules="experienceFormRules" ref="experienceFormRef" label-width="120px">
        <el-form-item label="零件A" prop="part_a_id">
          <el-select
            v-model="experienceForm.part_a_id"
            placeholder="搜索并选择零件A"
            filterable
            remote
            :remote-method="searchPartsA"
            :loading="partsALoading"
            style="width: 100%"
          >
            <el-option
              v-for="part in partsAOptions"
              :key="part.id"
              :label="`${part.name} (${part.category || '未分类'})`"
              :value="part.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="零件B" prop="part_b_id">
          <el-select
            v-model="experienceForm.part_b_id"
            placeholder="搜索并选择零件B"
            filterable
            remote
            :remote-method="searchPartsB"
            :loading="partsBLoading"
            style="width: 100%"
          >
            <el-option
              v-for="part in partsBOptions"
              :key="part.id"
              :label="`${part.name} (${part.category || '未分类'})`"
              :value="part.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="兼容性状态" prop="compatibility_status">
          <el-radio-group v-model="experienceForm.compatibility_status">
            <el-radio label="compatible">兼容</el-radio>
            <el-radio label="incompatible">不兼容</el-radio>
            <el-radio label="conditional">有条件兼容</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="兼容性评分" prop="compatibility_score">
          <div class="score-input">
            <el-slider
              v-model="experienceForm.compatibility_score"
              :min="0"
              :max="100"
              :step="5"
              show-input
              :input-size="'small'"
              style="width: 100%"
            />
          </div>
          <div class="score-hint">
            <span>90-100: 官方支持 | 70-89: 社区验证 | 50-69: 理论兼容 | 0-49: 不兼容</span>
          </div>
        </el-form-item>

        <el-form-item label="数据来源" prop="source">
          <el-radio-group v-model="experienceForm.source">
            <el-radio label="admin">管理员</el-radio>
            <el-radio label="official">官方</el-radio>
            <el-radio label="user_contribution">用户贡献</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="验证状态" prop="verification_status">
          <el-radio-group v-model="experienceForm.verification_status">
            <el-radio label="verified">已验证</el-radio>
            <el-radio label="pending">待验证</el-radio>
            <el-radio label="disputed">有争议</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="外部链接">
          <el-input
            v-model="experienceForm.reference_url"
            placeholder="外部反馈来源链接（可选）"
          />
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="experienceForm.notes"
            type="textarea"
            :rows="3"
            placeholder="详细说明和备注（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="cancelEdit">取消</el-button>
        <el-button type="primary" @click="saveExperience" :loading="saving">
          {{ saving ? '保存中...' : '保存' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      title="批量导入兼容性经验"
      v-model="showBatchImportDialog"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="batch-import-container">
        <el-alert
          type="info"
          title="批量导入说明"
          :description="batchImportHelp"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        />

        <el-upload
          class="upload-area"
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleBatchFileSelect"
          :file-list="batchFileList"
          accept=".json,.csv"
          :limit="1"
        >
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <div class="upload-text">将文件拖到此处，或<em>点击上传</em></div>
          <div class="upload-hint">支持 JSON 和 CSV 格式</div>
        </el-upload>

        <div v-if="batchPreview.length > 0" class="batch-preview">
          <el-divider>预览数据（前5条）</el-divider>
          <el-table :data="batchPreview.slice(0, 5)" size="small">
            <el-table-column prop="part_a_id" label="零件A ID" width="80" />
            <el-table-column prop="part_b_id" label="零件B ID" width="80" />
            <el-table-column prop="compatibility_status" label="状态" width="100" />
            <el-table-column prop="compatibility_score" label="评分" width="80" />
            <el-table-column prop="notes" label="备注" show-overflow-tooltip />
          </el-table>
          <p class="preview-info">总计 {{ batchPreview.length }} 条记录</p>
        </div>
      </div>

      <template #footer>
        <el-button @click="cancelBatchImport">取消</el-button>
        <el-button 
          type="primary" 
          @click="executeBatchImport" 
          :loading="batchImporting"
          :disabled="batchPreview.length === 0"
        >
          {{ batchImporting ? '导入中...' : `导入 ${batchPreview.length} 条记录` }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 经验详情对话框 -->
    <el-dialog
      title="兼容性经验详情"
      v-model="showDetailsDialog"
      width="700px"
    >
      <div v-if="currentExperience" class="experience-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="零件A">
            {{ currentExperience.part_a_name || `ID: ${currentExperience.part_a_id}` }}
          </el-descriptions-item>
          <el-descriptions-item label="零件B">
            {{ currentExperience.part_b_name || `ID: ${currentExperience.part_b_id}` }}
          </el-descriptions-item>
          <el-descriptions-item label="兼容性状态">
            <el-tag :type="getStatusType(currentExperience.compatibility_status)">
              {{ getStatusText(currentExperience.compatibility_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="兼容性评分">
            <div class="score-detail">
              <el-progress 
                :percentage="currentExperience.compatibility_score || 0" 
                :color="getScoreColor(currentExperience.compatibility_score)"
                :stroke-width="12"
              />
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="数据来源">
            <el-tag :type="getSourceType(currentExperience.source)">
              {{ getSourceText(currentExperience.source) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="验证状态">
            <el-tag :type="getVerificationStatusType(currentExperience.verification_status)">
              {{ getVerificationStatusText(currentExperience.verification_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="添加者">
            {{ currentExperience.added_by_username || `ID: ${currentExperience.added_by}` }}
          </el-descriptions-item>
          <el-descriptions-item label="添加时间">
            {{ formatTime(currentExperience.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后更新" v-if="currentExperience.updated_at">
            {{ formatTime(currentExperience.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="外部链接" v-if="currentExperience.reference_url">
            <el-link :href="currentExperience.reference_url" target="_blank">
              {{ currentExperience.reference_url }}
            </el-link>
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="currentExperience.notes" class="experience-notes">
          <el-divider>备注说明</el-divider>
          <div class="notes-content">
            {{ currentExperience.notes }}
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  Plus, Upload, Download, Search, Refresh, Promotion,
  UploadFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { compatibilityExperiences, partsAPI } from '../utils/api'

export default {
  name: 'CompatibilityExperiences',
  components: {
    Plus, Upload, Download, Search, Refresh, Promotion,
    UploadFilled
  },
  emits: ['stats-updated'],
  setup(props, { emit }) {
    const loading = ref(false)
    const saving = ref(false)
    const batchImporting = ref(false)
    
    // 列表数据
    const experiences = ref([])
    const selectedExperiences = ref([])
    const totalExperiences = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(20)
    
    // 筛选
    const searchText = ref('')
    const statusFilter = ref('')
    const sourceFilter = ref('')
    
    // 对话框状态
    const showCreateDialog = ref(false)
    const showBatchImportDialog = ref(false)
    const showDetailsDialog = ref(false)
    
    // 当前编辑的经验
    const editingExperience = ref(null)
    const currentExperience = ref(null)
    
    // 表单数据
    const experienceForm = reactive({
      part_a_id: null,
      part_b_id: null,
      compatibility_status: 'compatible',
      compatibility_score: 80,
      source: 'admin',
      verification_status: 'verified',
      reference_url: '',
      notes: ''
    })
    
    // 表单验证规则
    const experienceFormRules = {
      part_a_id: [
        { required: true, message: '请选择零件A', trigger: 'change' }
      ],
      part_b_id: [
        { required: true, message: '请选择零件B', trigger: 'change' }
      ],
      compatibility_status: [
        { required: true, message: '请选择兼容性状态', trigger: 'change' }
      ]
    }
    
    // 零件选择相关
    const partsAOptions = ref([])
    const partsBOptions = ref([])
    const partsALoading = ref(false)
    const partsBLoading = ref(false)
    
    // 批量导入相关
    const batchFileList = ref([])
    const batchPreview = ref([])
    const batchImportHelp = `
      支持的文件格式：
      • JSON格式：[{"part_a_id": 1, "part_b_id": 2, "compatibility_status": "compatible", "compatibility_score": 85, "notes": "测试通过"}]
      • CSV格式：包含列 part_a_id, part_b_id, compatibility_status, compatibility_score, notes
      
      注意事项：
      • compatibility_status 必须为：compatible, incompatible, conditional
      • compatibility_score 范围：0-100
      • 重复的零件组合将被跳过
    `
    
    // 表单引用
    const experienceFormRef = ref()

    // 计算属性
    const filteredExperiences = computed(() => {
      let filtered = experiences.value
      
      if (searchText.value) {
        const search = searchText.value.toLowerCase()
        filtered = filtered.filter(exp => 
          (exp.part_a_name && exp.part_a_name.toLowerCase().includes(search)) ||
          (exp.part_b_name && exp.part_b_name.toLowerCase().includes(search))
        )
      }
      
      if (statusFilter.value) {
        filtered = filtered.filter(exp => exp.compatibility_status === statusFilter.value)
      }
      
      if (sourceFilter.value) {
        filtered = filtered.filter(exp => exp.source === sourceFilter.value)
      }
      
      return filtered
    })

    // 加载经验列表
    const loadExperiences = async () => {
      loading.value = true
      
      try {
        const response = await compatibilityExperiences.list({
          page: currentPage.value,
          size: pageSize.value
        })
        
        experiences.value = response.data.items || response.data
        totalExperiences.value = response.data.total || experiences.value.length
        
        // 更新统计信息
        const verified = experiences.value.filter(exp => exp.verification_status === 'verified').length
        const pending = experiences.value.filter(exp => exp.verification_status === 'pending').length
        
        emit('stats-updated', {
          total_experiences: totalExperiences.value,
          verified_experiences: verified,
          pending_experiences: pending
        })
        
      } catch (error) {
        console.error('加载经验列表失败:', error)
        ElMessage.error('加载经验列表失败')
      }
      
      loading.value = false
    }

    // 搜索零件A
    const searchPartsA = async (query) => {
      if (!query) {
        partsAOptions.value = []
        return
      }
      
      partsALoading.value = true
      
      try {
        const response = await partsAPI.getParts({
          search: query,
          limit: 20
        })
        partsAOptions.value = response.data
      } catch (error) {
        console.error('搜索零件失败:', error)
      }
      
      partsALoading.value = false
    }

    // 搜索零件B
    const searchPartsB = async (query) => {
      if (!query) {
        partsBOptions.value = []
        return
      }
      
      partsBLoading.value = true
      
      try {
        const response = await partsAPI.getParts({
          search: query,
          limit: 20
        })
        partsBOptions.value = response.data
      } catch (error) {
        console.error('搜索零件失败:', error)
      }
      
      partsBLoading.value = false
    }

    // 创建经验
    const saveExperience = async () => {
      try {
        await experienceFormRef.value.validate()
        
        // 检查是否为同一个零件
        if (experienceForm.part_a_id === experienceForm.part_b_id) {
          ElMessage.error('零件A和零件B不能是同一个')
          return
        }
        
        saving.value = true
        
        const experienceData = {
          part_a_id: experienceForm.part_a_id,
          part_b_id: experienceForm.part_b_id,
          compatibility_status: experienceForm.compatibility_status,
          compatibility_score: experienceForm.compatibility_score,
          source: experienceForm.source,
          verification_status: experienceForm.verification_status,
          reference_url: experienceForm.reference_url || null,
          notes: experienceForm.notes || null
        }
        
        if (editingExperience.value) {
          await compatibilityExperiences.update(editingExperience.value.id, experienceData)
          ElMessage.success('经验更新成功')
        } else {
          await compatibilityExperiences.create(experienceData)
          ElMessage.success('经验添加成功')
        }
        
        showCreateDialog.value = false
        resetForm()
        loadExperiences()
        
      } catch (error) {
        if (error.response?.status === 409) {
          ElMessage.error('该零件组合的兼容性经验已存在')
        } else {
          ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
        }
      }
      
      saving.value = false
    }

    // 编辑经验
    const editExperience = async (experience) => {
      editingExperience.value = experience
      
      // 加载零件信息
      try {
        const [partAResponse, partBResponse] = await Promise.all([
          partsAPI.getPart(experience.part_a_id),
          partsAPI.getPart(experience.part_b_id)
        ])
        
        partsAOptions.value = [partAResponse.data]
        partsBOptions.value = [partBResponse.data]
      } catch (error) {
        console.error('加载零件信息失败:', error)
      }
      
      // 填充表单
      Object.assign(experienceForm, {
        part_a_id: experience.part_a_id,
        part_b_id: experience.part_b_id,
        compatibility_status: experience.compatibility_status,
        compatibility_score: experience.compatibility_score || 0,
        source: experience.source,
        verification_status: experience.verification_status,
        reference_url: experience.reference_url || '',
        notes: experience.notes || ''
      })
      
      showCreateDialog.value = true
    }

    // 删除经验
    const deleteExperience = async (experience) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除零件 "${experience.part_a_name || experience.part_a_id}" 和 "${experience.part_b_name || experience.part_b_id}" 的兼容性经验吗？`,
          '确认删除',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await compatibilityExperiences.delete(experience.id)
        ElMessage.success('经验删除成功')
        loadExperiences()
        
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
        }
      }
    }

    // 查看详情
    const viewDetails = (experience) => {
      currentExperience.value = experience
      showDetailsDialog.value = true
    }

    // 选择变化处理
    const handleSelectionChange = (selection) => {
      selectedExperiences.value = selection
    }

    // 导出选中经验
    const exportExperiences = () => {
      if (selectedExperiences.value.length === 0) {
        ElMessage.warning('请先选择要导出的经验')
        return
      }
      
      const exportData = selectedExperiences.value.map(exp => ({
        part_a_id: exp.part_a_id,
        part_a_name: exp.part_a_name,
        part_b_id: exp.part_b_id,
        part_b_name: exp.part_b_name,
        compatibility_status: exp.compatibility_status,
        compatibility_score: exp.compatibility_score,
        source: exp.source,
        verification_status: exp.verification_status,
        reference_url: exp.reference_url,
        notes: exp.notes,
        created_at: exp.created_at
      }))
      
      const jsonData = JSON.stringify(exportData, null, 2)
      const blob = new Blob([jsonData], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = `compatibility_experiences_${new Date().toISOString().slice(0, 10)}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      URL.revokeObjectURL(url)
      ElMessage.success('经验数据导出成功')
    }

    // 批量导入文件选择
    const handleBatchFileSelect = (file) => {
      batchFileList.value = [file]
      
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const content = e.target.result
          let data = []
          
          if (file.name.endsWith('.json')) {
            data = JSON.parse(content)
          } else if (file.name.endsWith('.csv')) {
            data = parseCSV(content)
          }
          
          // 验证数据格式
          const validData = data.filter(item => {
            return item.part_a_id && item.part_b_id && 
                   item.compatibility_status && 
                   ['compatible', 'incompatible', 'conditional'].includes(item.compatibility_status)
          })
          
          batchPreview.value = validData
          
          if (validData.length !== data.length) {
            ElMessage.warning(`${data.length - validData.length} 条记录格式不正确，已过滤`)
          }
          
        } catch (error) {
          ElMessage.error('文件解析失败: ' + error.message)
          batchPreview.value = []
        }
      }
      
      reader.readAsText(file.raw)
    }

    // 解析CSV
    const parseCSV = (content) => {
      const lines = content.split('\n').filter(line => line.trim())
      if (lines.length < 2) return []
      
      const headers = lines[0].split(',').map(h => h.trim())
      const data = []
      
      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim())
        const item = {}
        
        headers.forEach((header, index) => {
          if (values[index] !== undefined) {
            let value = values[index].replace(/^"|"$/g, '') // 移除引号
            
            // 类型转换
            if (header === 'part_a_id' || header === 'part_b_id') {
              value = parseInt(value)
            } else if (header === 'compatibility_score') {
              value = parseInt(value) || 0
            }
            
            item[header] = value
          }
        })
        
        if (item.part_a_id && item.part_b_id) {
          data.push(item)
        }
      }
      
      return data
    }

    // 执行批量导入
    const executeBatchImport = async () => {
      if (batchPreview.value.length === 0) {
        ElMessage.error('没有有效的数据可导入')
        return
      }
      
      batchImporting.value = true
      
      try {
        const response = await compatibilityExperiences.batchCreate({
          experiences: batchPreview.value
        })
        
        ElMessage.success(
          `批量导入完成! 成功: ${response.data.successful_creates}, ` +
          `跳过: ${response.data.skipped_duplicates}, ` +
          `错误: ${response.data.errors.length}`
        )
        
        if (response.data.errors.length > 0) {
          console.error('导入错误:', response.data.errors)
        }
        
        showBatchImportDialog.value = false
        cancelBatchImport()
        loadExperiences()
        
      } catch (error) {
        ElMessage.error('批量导入失败: ' + (error.response?.data?.detail || error.message))
      }
      
      batchImporting.value = false
    }

    // 重置表单
    const resetForm = () => {
      editingExperience.value = null
      Object.assign(experienceForm, {
        part_a_id: null,
        part_b_id: null,
        compatibility_status: 'compatible',
        compatibility_score: 80,
        source: 'admin',
        verification_status: 'verified',
        reference_url: '',
        notes: ''
      })
      partsAOptions.value = []
      partsBOptions.value = []
    }

    // 取消编辑
    const cancelEdit = () => {
      showCreateDialog.value = false
      resetForm()
    }

    // 取消批量导入
    const cancelBatchImport = () => {
      showBatchImportDialog.value = false
      batchFileList.value = []
      batchPreview.value = []
    }

    // 刷新
    const refresh = () => {
      currentPage.value = 1
      loadExperiences()
    }

    // 工具函数
    const getStatusType = (status) => {
      const statusMap = {
        'compatible': 'success',
        'incompatible': 'danger',
        'conditional': 'warning'
      }
      return statusMap[status] || 'info'
    }

    const getStatusText = (status) => {
      const statusMap = {
        'compatible': '兼容',
        'incompatible': '不兼容',
        'conditional': '有条件兼容'
      }
      return statusMap[status] || status
    }

    const getSourceType = (source) => {
      const sourceMap = {
        'admin': 'primary',
        'official': 'success',
        'user_contribution': 'info'
      }
      return sourceMap[source] || 'info'
    }

    const getSourceText = (source) => {
      const sourceMap = {
        'admin': '管理员',
        'official': '官方',
        'user_contribution': '用户'
      }
      return sourceMap[source] || source
    }

    const getVerificationStatusType = (status) => {
      const statusMap = {
        'verified': 'success',
        'pending': 'warning',
        'disputed': 'danger'
      }
      return statusMap[status] || 'info'
    }

    const getVerificationStatusText = (status) => {
      const statusMap = {
        'verified': '已验证',
        'pending': '待验证',
        'disputed': '有争议'
      }
      return statusMap[status] || status
    }

    const getScoreColor = (score) => {
      if (score >= 90) return '#67c23a'
      if (score >= 70) return '#e6a23c'
      if (score >= 50) return '#409eff'
      return '#f56c6c'
    }

    const formatTime = (timeString) => {
      if (!timeString) return ''
      return new Date(timeString).toLocaleString('zh-CN')
    }

    // 组件挂载
    onMounted(() => {
      loadExperiences()
    })

    return {
      // 响应式数据
      loading,
      saving,
      batchImporting,
      experiences,
      filteredExperiences,
      selectedExperiences,
      totalExperiences,
      currentPage,
      pageSize,
      
      // 筛选
      searchText,
      statusFilter,
      sourceFilter,
      
      // 对话框状态
      showCreateDialog,
      showBatchImportDialog,
      showDetailsDialog,
      
      // 表单
      editingExperience,
      currentExperience,
      experienceForm,
      experienceFormRules,
      experienceFormRef,
      
      // 零件选择
      partsAOptions,
      partsBOptions,
      partsALoading,
      partsBLoading,
      
      // 批量导入
      batchFileList,
      batchPreview,
      batchImportHelp,
      
      // 方法
      loadExperiences,
      searchPartsA,
      searchPartsB,
      saveExperience,
      editExperience,
      deleteExperience,
      viewDetails,
      handleSelectionChange,
      exportExperiences,
      handleBatchFileSelect,
      executeBatchImport,
      resetForm,
      cancelEdit,
      cancelBatchImport,
      refresh,
      
      // 工具函数
      getStatusType,
      getStatusText,
      getSourceType,
      getSourceText,
      getVerificationStatusType,
      getVerificationStatusText,
      getScoreColor,
      formatTime
    }
  }
}
</script>

<style scoped>
.compatibility-experiences {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
  border-radius: 6px 6px 0 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-container {
  flex: 1;
  overflow: hidden;
}

.part-combination {
  display: flex;
  align-items: center;
  gap: 8px;
}

.part-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.part-name {
  font-weight: 500;
  color: #303133;
}

.combination-arrow {
  color: #909399;
  font-size: 16px;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-text {
  font-weight: 600;
  color: #303133;
  min-width: 24px;
}

.pagination-container {
  padding: 16px;
  background: #fafafa;
  border-top: 1px solid #e4e7ed;
  border-radius: 0 0 6px 6px;
}

.score-input {
  margin-bottom: 8px;
}

.score-hint {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.batch-import-container {
  max-height: 500px;
  overflow-y: auto;
}

.upload-area {
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

.batch-preview {
  margin-top: 20px;
}

.preview-info {
  text-align: center;
  color: #909399;
  font-size: 14px;
  margin-top: 10px;
}

.experience-details {
  max-height: 500px;
  overflow-y: auto;
}

.score-detail {
  width: 200px;
}

.experience-notes {
  margin-top: 20px;
}

.notes-content {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.el-slider__input) {
  width: 80px;
}

:deep(.el-table .cell) {
  padding: 8px 12px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #303133;
}

:deep(.el-descriptions__content) {
  color: #606266;
}
</style>