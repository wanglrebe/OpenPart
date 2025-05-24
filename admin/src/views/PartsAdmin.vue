<template>
  <div class="parts-admin">
    <NavBar />
    
    <el-main class="main-content">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>零件管理</span>
            <el-button type="primary" @click="showAddDialog = true">
              <el-icon><Plus /></el-icon>
              添加零件
            </el-button>
          </div>
        </template>
        
        <!-- 搜索栏 -->
        <el-row :gutter="20" class="search-bar">
          <el-col :span="8">
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
          <el-col :span="8">
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
          <el-col :span="8">
            <el-button @click="resetSearch">重置</el-button>
            <el-button type="primary" @click="searchParts">搜索</el-button>
          </el-col>
        </el-row>
        
        <!-- 零件表格 -->
        <el-table :data="parts" style="width: 100%" v-loading="loading">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="category" label="类别" />
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button size="small" @click="editPart(scope.row)">
                编辑
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
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import { partsAPI } from '../utils/api'

export default {
  name: 'PartsAdmin',
  components: {
    NavBar,
    Plus,
    Search
  },
  setup() {
    const parts = ref([])
    const categories = ref([])
    const loading = ref(false)
    const saving = ref(false)
    const showAddDialog = ref(false)
    const editingPart = ref(null)
    const partFormRef = ref()
    
    // 搜索相关
    const searchName = ref('')
    const searchCategory = ref('')
    
    // 分页相关
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(0)
    
    // 表单数据
    const partForm = reactive({
      name: '',
      category: '',
      description: '',
      properties: []
    })
    
    // 加载零件列表
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
        
        // 前端过滤名称（因为后端可能不支持名称搜索）
        if (searchName.value) {
          partsData = partsData.filter(p => 
            p.name.toLowerCase().includes(searchName.value.toLowerCase())
          )
        }
        
        parts.value = partsData
        total.value = partsData.length
        
        // 提取所有类别
        const allCategories = new Set(partsData.map(p => p.category).filter(Boolean))
        categories.value = Array.from(allCategories)
        
      } catch (error) {
        ElMessage.error('加载零件列表失败')
        console.error(error)
      }
      loading.value = false
    }
    
    // 搜索零件
    const searchParts = () => {
      currentPage.value = 1
      loadParts()
    }
    
    // 重置搜索
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
    
    // 分页处理
    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
      loadParts()
    }
    
    const handleCurrentChange = (val) => {
      currentPage.value = val
      loadParts()
    }
    
    // 监听对话框关闭
    const handleDialogClose = () => {
      resetForm()
    }
    
    onMounted(() => {
      loadParts()
    })
    
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
      loadParts,
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
      handleDialogClose
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
</style>