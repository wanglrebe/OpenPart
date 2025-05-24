<template>
  <div class="parts-list">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>零件列表</span>
              <el-button type="primary" @click="showAddDialog = true">
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
              />
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
          </el-row>
          
          <!-- 零件表格 -->
          <el-table :data="parts" style="width: 100%" v-loading="loading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="category" label="类别" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
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
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      :title="editingPart ? '编辑零件' : '添加零件'"
      v-model="showAddDialog"
      width="600px"
    >
      <el-form :model="partForm" label-width="100px">
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
            <el-input v-model="prop.key" placeholder="属性名" style="width: 200px" />
            <el-input v-model="prop.value" placeholder="属性值" style="width: 200px; margin-left: 10px" />
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
        <el-button type="primary" @click="savePart">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'PartsList',
  data() {
    return {
      parts: [],
      categories: [],
      loading: false,
      searchName: '',
      searchCategory: '',
      showAddDialog: false,
      editingPart: null,
      partForm: {
        name: '',
        category: '',
        description: '',
        properties: []
      }
    }
  },
  mounted() {
    this.loadParts()
  },
  methods: {
    async loadParts() {
      this.loading = true
      try {
        const response = await axios.get('/api/parts/')
        this.parts = response.data
        
        // 提取所有类别
        this.categories = [...new Set(this.parts.map(p => p.category).filter(Boolean))]
      } catch (error) {
        this.$message.error('加载零件列表失败')
        console.error(error)
      }
      this.loading = false
    },
    
    async searchParts() {
      this.loading = true
      try {
        const params = {}
        if (this.searchCategory) params.category = this.searchCategory
        
        const response = await axios.get('/api/parts/', { params })
        let parts = response.data
        
        // 前端过滤名称
        if (this.searchName) {
          parts = parts.filter(p => 
            p.name.toLowerCase().includes(this.searchName.toLowerCase())
          )
        }
        
        this.parts = parts
      } catch (error) {
        this.$message.error('搜索失败')
        console.error(error)
      }
      this.loading = false
    },
    
    editPart(part) {
      this.editingPart = part
      this.partForm = {
        name: part.name,
        category: part.category || '',
        description: part.description || '',
        properties: part.properties ? 
          Object.entries(part.properties).map(([key, value]) => ({ key, value })) : 
          []
      }
      this.showAddDialog = true
    },
    
    async savePart() {
      try {
        // 转换属性格式
        const properties = {}
        this.partForm.properties.forEach(prop => {
          if (prop.key && prop.value) {
            properties[prop.key] = prop.value
          }
        })
        
        const partData = {
          name: this.partForm.name,
          category: this.partForm.category,
          description: this.partForm.description,
          properties: Object.keys(properties).length > 0 ? properties : null
        }
        
        if (this.editingPart) {
          await axios.put(`/api/parts/${this.editingPart.id}`, partData)
          this.$message.success('零件更新成功')
        } else {
          await axios.post('/api/parts/', partData)
          this.$message.success('零件添加成功')
        }
        
        this.showAddDialog = false
        this.resetForm()
        this.loadParts()
      } catch (error) {
        this.$message.error('保存失败')
        console.error(error)
      }
    },
    
    async deletePart(part) {
      try {
        await this.$confirm('确定要删除这个零件吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await axios.delete(`/api/parts/${part.id}`)
        this.$message.success('删除成功')
        this.loadParts()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败')
          console.error(error)
        }
      }
    },
    
    addProperty() {
      this.partForm.properties.push({ key: '', value: '' })
    },
    
    removeProperty(index) {
      this.partForm.properties.splice(index, 1)
    },
    
    resetForm() {
      this.editingPart = null
      this.partForm = {
        name: '',
        category: '',
        description: '',
        properties: []
      }
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
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
</style>