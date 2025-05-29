<template>
  <div class="parts-admin">
    <NavBar />
    
    <el-main class="main-content">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>零件管理</span>
            <div class="header-actions">
              <el-button type="primary" @click="showAddDialog = true">
                <el-icon><Plus /></el-icon>
                添加零件
              </el-button>
              
              <!-- 批量操作按钮 -->
              <el-dropdown 
                v-if="selectedParts.length > 0" 
                @command="handleBatchCommand"
                class="batch-actions"
              >
                <el-button type="warning">
                  批量操作 ({{ selectedParts.length }})
                  <el-icon><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="export">
                      <el-icon><Download /></el-icon>
                      导出选中项
                    </el-dropdown-item>
                    <el-dropdown-item command="batch-edit">
                      <el-icon><Edit /></el-icon>
                      批量编辑
                    </el-dropdown-item>
                    <el-dropdown-item command="batch-category">
                      <el-icon><Collection /></el-icon>
                      批量设置类别
                    </el-dropdown-item>
                    <el-dropdown-item command="batch-delete" divided>
                      <el-icon><Delete /></el-icon>
                      批量删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </template>
        
        <!-- 搜索栏 -->
        <el-row :gutter="20" class="search-bar">
          <el-col :span="6">
            <el-input
              v-model="searchName"
              placeholder="搜索零件名称"
              clearable
              @input="searchParts"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="6">
            <el-select
              v-model="searchCategory"
              placeholder="选择类别"
              clearable
              @change="searchParts"
            >
              <el-option
                v-for="category in categories"
                :key="category"
                :label="category"
                :value="category"
              />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-button @click="resetSearch">重置</el-button>
            <el-button type="primary" @click="searchParts">搜索</el-button>
          </el-col>
          <el-col :span="6" class="selection-info">
            <span v-if="selectedParts.length > 0" class="selection-text">
              已选择 {{ selectedParts.length }} 项
              <el-button type="text" @click="clearSelection">清空选择</el-button>
            </span>
          </el-col>
        </el-row>
        
        <!-- 零件表格 - 添加选择列 -->
        <el-table 
          :data="parts" 
          style="width: 100%" 
          v-loading="loading"
          @selection-change="handleSelectionChange"
          ref="partsTableRef"
        >
          <!-- 选择列 -->
          <el-table-column type="selection" width="55" />
          
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="category" label="类别" />
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <!-- 在零件表格中添加图片列，在操作列之前添加： -->
          <el-table-column label="图片" width="100">
            <template #default="scope">
              <div class="part-image-cell">
                <img 
                  v-if="scope.row.image_url" 
                  :src="scope.row.image_url" 
                  class="part-thumbnail"
                  @click="previewImage(scope.row.image_url)"
                />
                <div v-else class="no-image-placeholder">
                  <el-icon><Picture /></el-icon>
                </div>
              </div>
            </template>
          </el-table-column>
          <!-- 在操作列中添加图片管理按钮： -->
          <el-table-column label="操作" width="250">
            <template #default="scope">
              <el-button size="small" @click="editPart(scope.row)">
                编辑
              </el-button>
              <el-button 
                size="small" 
                type="primary"
                @click="showImageUpload(scope.row)"
              >
                {{ scope.row.image_url ? '更换图片' : '上传图片' }}
              </el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="deletePart(scope.row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          class="pagination"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </el-card>
    </el-main>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      :title="editingPart ? '编辑零件' : '添加零件'"
      v-model="showAddDialog"
      width="600px"
    >
      <el-form :model="partForm" label-width="100px" ref="partFormRef">
        <el-form-item label="名称" required>
          <el-input v-model="partForm.name" />
        </el-form-item>
        <el-form-item label="类别">
          <el-input v-model="partForm.category" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="partForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="自定义属性">
          <div v-for="(prop, key) in partForm.properties" :key="key" class="property-item">
            <el-input v-model="prop.key" placeholder="属性名" style="width: 180px" />
            <el-input v-model="prop.value" placeholder="属性值" style="width: 180px; margin-left: 10px" />
            <el-button @click="removeProperty(key)" type="danger" size="small" style="margin-left: 10px">
              删除
            </el-button>
          </div>
          <el-button @click="addProperty" type="primary" size="small">
            添加属性
          </el-button>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="savePart">
          {{ saving ? '保存中...' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
    <!-- 在对话框后添加图片上传对话框： -->
    <el-dialog
      title="零件图片管理"
      v-model="showImageDialog"
      width="500px"
    >
      <div class="image-upload-container">
        <div v-if="currentPart?.image_url" class="current-image">
          <h4>当前图片</h4>
          <img :src="currentPart.image_url" class="current-image-preview" />
          <el-button 
            type="danger" 
            size="small" 
            @click="deleteImage"
            :loading="deleting"
          >
            删除图片
          </el-button>
        </div>
        
        <div class="upload-section">
          <h4>{{ currentPart?.image_url ? '更换图片' : '上传图片' }}</h4>
          <el-upload
            class="image-uploader"
            :action="`/api/admin/upload/upload/${currentPart?.id}`"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeImageUpload"
            accept="image/*"
          >
            <div class="upload-area">
              <el-icon class="upload-icon"><Plus /></el-icon>
              <div class="upload-text">点击上传图片</div>
              <div class="upload-hint">支持 JPG、PNG、GIF、WebP 格式，最大 5MB</div>
            </div>
          </el-upload>
        </div>
      </div>
    </el-dialog>
    <!-- 图片预览对话框 -->
    <el-dialog
      title="图片预览"
      v-model="showPreviewDialog"
      width="600px"
    >
      <div class="image-preview-container">
        <img :src="previewImageUrl" class="preview-image" />
      </div>
    </el-dialog>


    <!-- 批量编辑对话框 -->
    <el-dialog
      title="批量编辑零件"
      v-model="showBatchEditDialog"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-alert
        type="info"
        :title="`将对 ${selectedParts.length} 个零件进行批量编辑`"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />
      
      <el-form :model="batchEditForm" label-width="100px">
        <el-form-item label="类别">
          <el-input 
            v-model="batchEditForm.category" 
            placeholder="留空表示不修改"
          />
        </el-form-item>
        <el-form-item label="描述前缀">
          <el-input 
            v-model="batchEditForm.descriptionPrefix" 
            placeholder="为所有选中零件的描述添加前缀"
          />
        </el-form-item>
        <el-form-item label="描述后缀">
          <el-input 
            v-model="batchEditForm.descriptionSuffix" 
            placeholder="为所有选中零件的描述添加后缀"
          />
        </el-form-item>
        <el-form-item label="批量属性">
          <div v-for="(prop, index) in batchEditForm.properties" :key="index" class="property-item">
            <el-input v-model="prop.key" placeholder="属性名" style="width: 180px" />
            <el-input v-model="prop.value" placeholder="属性值" style="width: 180px; margin-left: 10px" />
            <el-button 
              @click="removeBatchProperty(index)" 
              type="danger" 
              size="small" 
              style="margin-left: 10px"
            >
              删除
            </el-button>
          </div>
          <el-button @click="addBatchProperty" type="primary" size="small">
            添加属性
          </el-button>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showBatchEditDialog = false">取消</el-button>
        <el-button type="primary" @click="executeBatchEdit" :loading="batchOperating">
          {{ batchOperating ? '处理中...' : '确认修改' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量设置类别对话框 -->
    <el-dialog
      title="批量设置类别"
      v-model="showBatchCategoryDialog"
      width="400px"
    >
      <el-alert
        type="info"
        :title="`将为 ${selectedParts.length} 个零件设置类别`"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />
      
      <el-form>
        <el-form-item label="新类别">
          <el-select
            v-model="batchCategoryValue"
            placeholder="选择或输入新类别"
            filterable
            allow-create
            style="width: 100%"
          >
            <el-option
              v-for="category in categories"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showBatchCategoryDialog = false">取消</el-button>
        <el-button type="primary" @click="executeBatchCategory" :loading="batchOperating">
          {{ batchOperating ? '设置中...' : '确认设置' }}
        </el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search, Picture, Download, Edit, Collection, Delete, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import { partsAPI } from '../utils/api'
import { auth } from '../utils/auth'
import axios from 'axios'

export default {
  name: 'PartsAdmin',
  components: {
    NavBar,
    Plus,
    Search,
    Picture,
    Download,
    Edit,
    Collection,
    Delete,
    ArrowDown
  },
  setup() {
    // 现有的响应式变量...
    const parts = ref([])
    const categories = ref([])
    const loading = ref(false)
    const saving = ref(false)
    const showAddDialog = ref(false)
    const editingPart = ref(null)
    const partFormRef = ref()
    
    const searchName = ref('')
    const searchCategory = ref('')
    
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(0)
    
    const partForm = reactive({
      name: '',
      category: '',
      description: '',
      properties: []
    })

    // 批量操作相关的新变量
    const selectedParts = ref([])
    const partsTableRef = ref()
    const batchOperating = ref(false)
    
    // 批量编辑相关
    const showBatchEditDialog = ref(false)
    const batchEditForm = reactive({
      category: '',
      descriptionPrefix: '',
      descriptionSuffix: '',
      properties: []
    })
    
    // 批量设置类别相关
    const showBatchCategoryDialog = ref(false)
    const batchCategoryValue = ref('')

    // 现有方法保持不变...
    const loadParts = async () => {
      loading.value = true
      try {
        const params = {
          skip: (currentPage.value - 1) * pageSize.value,
          limit: pageSize.value
        }
        
        if (searchCategory.value) {
          params.category = searchCategory.value
        }
        
        const response = await partsAPI.getParts(params)
        let partsData = response.data
        
        if (searchName.value) {
          partsData = partsData.filter(p => 
            p.name.toLowerCase().includes(searchName.value.toLowerCase())
          )
        }
        
        parts.value = partsData
        
        // 获取总数
        await loadTotalCount()
        
        const allCategories = new Set(partsData.map(p => p.category).filter(Boolean))
        categories.value = Array.from(allCategories)
        
      } catch (error) {
        ElMessage.error('加载零件列表失败')
        console.error(error)
      }
      loading.value = false
    }

    const loadTotalCount = async () => {
      try {
        const params = {}
        if (searchCategory.value) {
          params.category = searchCategory.value
        }
        
        const countResponse = await partsAPI.getParts({ 
          ...params, 
          limit: 10000
        })
        
        let totalData = countResponse.data
        
        if (searchName.value) {
          totalData = totalData.filter(p => 
            p.name.toLowerCase().includes(searchName.value.toLowerCase())
          )
        }
        
        total.value = totalData.length
        
      } catch (error) {
        console.error('获取总数失败:', error)
        total.value = 0
      }
    }

    // 新增：批量操作相关方法
    const handleSelectionChange = (selection) => {
      selectedParts.value = selection
      console.log(`选中了 ${selection.length} 个零件`)
    }

    const clearSelection = () => {
      partsTableRef.value.clearSelection()
      selectedParts.value = []
    }

    const handleBatchCommand = (command) => {
      if (selectedParts.value.length === 0) {
        ElMessage.warning('请先选择要操作的零件')
        return
      }

      switch (command) {
        case 'export':
          exportSelectedParts()
          break
        case 'batch-edit':
          showBatchEditDialog.value = true
          break
        case 'batch-category':
          showBatchCategoryDialog.value = true
          break
        case 'batch-delete':
          batchDeleteParts()
          break
      }
    }

    // 导出选中零件
    const exportSelectedParts = async () => {
      try {
        const partIds = selectedParts.value.map(p => p.id)
        
        ElMessage.info('正在导出选中的零件...')
        
        // 调用导出API
        const response = await axios.post('/api/admin/import-export/export', {
          format: 'json',
          include_images: true,
          part_ids: partIds  // 传递选中的零件ID
        }, {
          headers: { Authorization: `Bearer ${auth.getToken()}` },
          responseType: 'blob'
        })
        
        // 下载文件
        const blob = new Blob([response.data])
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
        link.download = `selected_parts_${timestamp}.json`
        
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        ElMessage.success(`成功导出 ${selectedParts.value.length} 个零件`)
        
      } catch (error) {
        ElMessage.error('导出失败: ' + (error.response?.data?.detail || error.message))
      }
    }

    // 批量删除零件
    const batchDeleteParts = async () => {
      try {
        await ElMessageBox.confirm(
          `确定要删除选中的 ${selectedParts.value.length} 个零件吗？此操作不可撤销。`,
          '批量删除确认',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        batchOperating.value = true
        const deletePromises = selectedParts.value.map(part => 
          partsAPI.deletePart(part.id)
        )
        
        await Promise.all(deletePromises)
        
        ElMessage.success(`成功删除 ${selectedParts.value.length} 个零件`)
        clearSelection()
        loadParts()
        
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('批量删除失败')
          console.error(error)
        }
      }
      batchOperating.value = false
    }

    // 执行批量编辑
    const executeBatchEdit = async () => {
      try {
        batchOperating.value = true
        
        const updatePromises = selectedParts.value.map(async (part) => {
          const updateData = {}
          
          // 设置类别
          if (batchEditForm.category) {
            updateData.category = batchEditForm.category
          }
          
          // 处理描述
          if (batchEditForm.descriptionPrefix || batchEditForm.descriptionSuffix) {
            let newDescription = part.description || ''
            if (batchEditForm.descriptionPrefix) {
              newDescription = batchEditForm.descriptionPrefix + newDescription
            }
            if (batchEditForm.descriptionSuffix) {
              newDescription = newDescription + batchEditForm.descriptionSuffix
            }
            updateData.description = newDescription
          }
          
          // 处理属性
          if (batchEditForm.properties.length > 0) {
            const newProperties = { ...(part.properties || {}) }
            batchEditForm.properties.forEach(prop => {
              if (prop.key && prop.value) {
                newProperties[prop.key] = prop.value
              }
            })
            updateData.properties = newProperties
          }
          
          if (Object.keys(updateData).length > 0) {
            return partsAPI.updatePart(part.id, updateData)
          }
        })
        
        await Promise.all(updatePromises)
        
        ElMessage.success(`成功批量编辑 ${selectedParts.value.length} 个零件`)
        showBatchEditDialog.value = false
        resetBatchEditForm()
        clearSelection()
        loadParts()
        
      } catch (error) {
        ElMessage.error('批量编辑失败')
        console.error(error)
      }
      batchOperating.value = false
    }

    // 执行批量设置类别
    const executeBatchCategory = async () => {
      if (!batchCategoryValue.value) {
        ElMessage.error('请输入新类别')
        return
      }
      
      try {
        batchOperating.value = true
        
        const updatePromises = selectedParts.value.map(part => 
          partsAPI.updatePart(part.id, { category: batchCategoryValue.value })
        )
        
        await Promise.all(updatePromises)
        
        ElMessage.success(`成功为 ${selectedParts.value.length} 个零件设置类别`)
        showBatchCategoryDialog.value = false
        batchCategoryValue.value = ''
        clearSelection()
        loadParts()
        
      } catch (error) {
        ElMessage.error('批量设置类别失败')
        console.error(error)
      }
      batchOperating.value = false
    }

    // 批量编辑表单相关方法
    const addBatchProperty = () => {
      batchEditForm.properties.push({ key: '', value: '' })
    }

    const removeBatchProperty = (index) => {
      batchEditForm.properties.splice(index, 1)
    }

    const resetBatchEditForm = () => {
      batchEditForm.category = ''
      batchEditForm.descriptionPrefix = ''
      batchEditForm.descriptionSuffix = ''
      batchEditForm.properties = []
    }

    // 现有方法保持不变...
    const searchParts = () => {
      currentPage.value = 1
      loadParts()
    }
    
    const resetSearch = () => {
      searchName.value = ''
      searchCategory.value = ''
      currentPage.value = 1
      loadParts()
    }
    
    // 编辑零件
    const editPart = (part) => {
      editingPart.value = part
      partForm.name = part.name
      partForm.category = part.category || ''
      partForm.description = part.description || ''
      partForm.properties = part.properties ? 
        Object.entries(part.properties).map(([key, value]) => ({ key, value })) : 
        []
      showAddDialog.value = true
    }
    
    // 保存零件
    const savePart = async () => {
      if (!partForm.name.trim()) {
        ElMessage.error('请输入零件名称')
        return
      }
      
      saving.value = true
      try {
        // 转换属性格式
        const properties = {}
        partForm.properties.forEach(prop => {
          if (prop.key && prop.value) {
            properties[prop.key] = prop.value
          }
        })
        
        const partData = {
          name: partForm.name,
          category: partForm.category,
          description: partForm.description,
          properties: Object.keys(properties).length > 0 ? properties : null
        }
        
        if (editingPart.value) {
          await partsAPI.updatePart(editingPart.value.id, partData)
          ElMessage.success('零件更新成功')
        } else {
          await partsAPI.createPart(partData)
          ElMessage.success('零件添加成功')
        }
        
        showAddDialog.value = false
        resetForm()
        loadParts()
        
      } catch (error) {
        ElMessage.error('保存失败')
        console.error(error)
      }
      saving.value = false
    }
    
    // 删除零件
    const deletePart = async (part) => {
      try {
        await ElMessageBox.confirm('确定要删除这个零件吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await partsAPI.deletePart(part.id)
        ElMessage.success('删除成功')
        loadParts()
        
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
          console.error(error)
        }
      }
    }
    
    // 添加属性
    const addProperty = () => {
      partForm.properties.push({ key: '', value: '' })
    }
    
    // 移除属性
    const removeProperty = (index) => {
      partForm.properties.splice(index, 1)
    }
    
    // 重置表单
    const resetForm = () => {
      editingPart.value = null
      partForm.name = ''
      partForm.category = ''
      partForm.description = ''
      partForm.properties = []
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString('zh-CN')
    }
    
    // 修复分页处理方法
    const handleSizeChange = (val) => {
      console.log(`页大小变更: ${pageSize.value} -> ${val}`)
      pageSize.value = val
      currentPage.value = 1  // 重置到第一页
      loadParts()
    }
    
    const handleCurrentChange = (val) => {
      console.log(`页码变更: ${currentPage.value} -> ${val}`)
      currentPage.value = val
      loadParts()  // 重新加载数据
    }
    
    // 监听对话框关闭
    const handleDialogClose = () => {
      resetForm()
    }
    
    onMounted(() => {
      loadParts()
    })

    // 在 setup() 中添加数据：
    const showImageDialog = ref(false)
    const showPreviewDialog = ref(false)
    const currentPart = ref(null)
    const previewImageUrl = ref('')
    const deleting = ref(false)
    
    // 添加上传headers
    const uploadHeaders = {
      'Authorization': `Bearer ${auth.getToken()}`
    }
    
    // 添加方法：
    const showImageUpload = (part) => {
      currentPart.value = part
      showImageDialog.value = true
    }
    
    const previewImage = (imageUrl) => {
      previewImageUrl.value = imageUrl
      showPreviewDialog.value = true
    }
    
    const beforeImageUpload = (file) => {
      const isValidType = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)
      const isLt5M = file.size / 1024 / 1024 < 5
    
      if (!isValidType) {
        ElMessage.error('只能上传 JPG、PNG、GIF、WebP 格式的图片!')
        return false
      }
      if (!isLt5M) {
        ElMessage.error('图片大小不能超过 5MB!')
        return false
      }
      return true
    }
    
    const handleUploadSuccess = (response) => {
      ElMessage.success('图片上传成功')
      currentPart.value.image_url = response.image_url
      showImageDialog.value = false
      loadParts() // 刷新列表
    }
    
    const handleUploadError = (error) => {
      console.error('上传失败:', error)
      ElMessage.error('图片上传失败')
    }
    
    const deleteImage = async () => {
      try {
        deleting.value = true
        await axios.delete(`/api/admin/upload/delete/${currentPart.value.id}`, {
          headers: { Authorization: `Bearer ${auth.getToken()}` }
        })
        
        ElMessage.success('图片删除成功')
        currentPart.value.image_url = null
        showImageDialog.value = false
        loadParts()
      } catch (error) {
        ElMessage.error('删除失败')
        console.error(error)
      }
      deleting.value = false
    }

    
    return {
      parts,
      categories,
      loading,
      saving,
      showAddDialog,
      editingPart,
      partFormRef,
      searchName,
      searchCategory,
      currentPage,
      pageSize,
      total,
      partForm,
      
      // 方法
      loadParts,
      loadTotalCount,  // 新增
      searchParts,
      resetSearch,
      editPart,
      savePart,
      deletePart,
      addProperty,
      removeProperty,
      resetForm,
      formatDate,
      handleSizeChange,
      handleCurrentChange,
      
      // 其他已有方法...
      handleDialogClose,
      showImageDialog,
      showPreviewDialog,
      currentPart,
      previewImageUrl,
      deleting,
      uploadHeaders,
      showImageUpload,
      previewImage,
      beforeImageUpload,
      handleUploadSuccess,
      handleUploadError,
      deleteImage,

      // 批量操作变量
      selectedParts,
      partsTableRef,
      batchOperating,
      showBatchEditDialog,
      batchEditForm,
      showBatchCategoryDialog,
      batchCategoryValue,

      // 批量操作方法
      handleSelectionChange,
      clearSelection,
      handleBatchCommand,
      exportSelectedParts,
      batchDeleteParts,
      executeBatchEdit,
      executeBatchCategory,
      addBatchProperty,
      removeBatchProperty,
      resetBatchEditForm,
    }
  }
}
</script>

<style scoped>
.parts-admin {
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
}

.search-bar {
  margin-bottom: 20px;
}

.property-item {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.part-image-cell {
  display: flex;
  justify-content: center;
  align-items: center;
}

.part-thumbnail {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid #ddd;
}

.no-image-placeholder {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 4px;
  color: #ccc;
}

.image-upload-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.current-image {
  text-align: center;
}

.current-image h4 {
  margin-bottom: 10px;
  color: #303133;
}

.current-image-preview {
  max-width: 200px;
  max-height: 200px;
  object-fit: contain;
  border-radius: 8px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
}

.upload-section h4 {
  margin-bottom: 10px;
  color: #303133;
}

.image-uploader .upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  width: 200px;
  height: 200px;
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.image-uploader .upload-area:hover {
  border-color: #409EFF;
}

.upload-icon {
  font-size: 28px;
  color: #8c939d;
  margin-bottom: 8px;
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

.image-preview-container {
  text-align: center;
}

.preview-image {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
  border-radius: 8px;
}
.batch-actions {
  margin-left: 10px;
}

.selection-info {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.selection-text {
  color: #409eff;
  font-size: 14px;
}

.property-item {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}
</style>