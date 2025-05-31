<template>
  <div class="compatibility-page">
    <!-- 🆕 保留导航栏 -->
    <NavBar />
    
    <div class="compatibility-editor">
      <!-- 工具栏 -->
      <div class="editor-toolbar">
        <div class="toolbar-left">
          <h2>🎯 兼容性配置编辑器</h2>
          <el-tag :type="validationStatus.type" class="status-tag">
            {{ validationStatus.text }}
          </el-tag>
          <el-tag v-if="hasUnsavedChanges" type="warning">
            📝 未保存的更改
          </el-tag>
        </div>
        
        <div class="toolbar-right">
          <el-button @click="formatDocument" size="small">
            ✨ 格式化
          </el-button>
          <el-button @click="validateAll" :loading="validating" size="small">
            ⚡ 验证全部
          </el-button>
          <el-button @click="reloadConfig" type="info" size="small">
            🔄 重新加载
          </el-button>
          <el-button 
            @click="saveConfig" 
            type="primary" 
            :loading="saving"
            :disabled="!validationStatus.valid || !hasUnsavedChanges"
            size="small"
          >
            💾 保存配置
          </el-button>
          <el-button @click="showHelp = true" size="small" type="info">
            📚 帮助
          </el-button>
        </div>
      </div>

      <!-- 代码编辑器容器 -->
      <div class="editor-container">
        <el-input
          v-model="configContent"
          type="textarea"
          :rows="30"
          class="code-editor"
          placeholder="正在加载配置..."
          @input="onContentChange"
          @keydown="onKeyDown"
          spellcheck="false"
        />
      </div>

      <!-- 状态栏 -->
      <div class="editor-statusbar">
        <div class="status-left">
          <span>总长度: {{ configContent.length }} 字符</span>
          <span class="separator">|</span>
          <span>{{ configStats.totalRules }} 规则, {{ configStats.activeRules }} 启用</span>
          <span class="separator">|</span>
          <span>{{ configStats.totalExperiences }} 经验记录</span>
        </div>
        
        <div class="status-right">
          <span v-if="validationMessage" class="validation-msg">
            {{ validationMessage }}
          </span>
          <span class="separator">|</span>
          <span>最后保存: {{ lastSaved || '从未保存' }}</span>
        </div>
      </div>

      <!-- 帮助面板 -->
      <el-drawer v-model="showHelp" title="📚 配置帮助" size="450px">
        <div class="help-content">
          <el-alert
            title="快捷键"
            type="info"
            :closable="false"
            show-icon
          >
            <ul>
              <li><kbd>Ctrl+S</kbd> - 保存配置</li>
              <li><kbd>Ctrl+F</kbd> - 格式化JSON</li>
              <li><kbd>Ctrl+Enter</kbd> - 验证全部</li>
            </ul>
          </el-alert>

          <el-divider>安全函数列表</el-divider>
          <div class="function-list">
            <div v-for="func in availableFunctions" :key="func.name" class="function-item">
              <el-tag size="small" type="primary">{{ func.name.split('(')[0] }}</el-tag>
              <p>{{ func.description }}</p>
              <code>{{ func.name }}</code>
            </div>
          </div>

          <el-divider>配置模板</el-divider>
          <div class="template-buttons">
            <el-button @click="insertRuleTemplate" size="small" type="primary">
              插入规则模板
            </el-button>
            <el-button @click="insertExperienceTemplate" size="small" type="success">
              插入经验模板
            </el-button>
            <el-button @click="insertFullTemplate" size="small" type="warning">
              插入完整模板
            </el-button>
          </div>

          <el-divider>配置示例</el-divider>
          <el-collapse>
            <el-collapse-item title="规则配置示例" name="rule-example">
              <pre class="example-code">{{ruleExample}}</pre>
            </el-collapse-item>
            <el-collapse-item title="经验配置示例" name="experience-example">
              <pre class="example-code">{{experienceExample}}</pre>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-drawer>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onBeforeUnmount, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { compatibilityAPI } from '../utils/api'
import NavBar from '../components/NavBar.vue'  // 🆕 导入NavBar组件

export default {
  name: 'CompatibilityEditor',
  components: {
    NavBar  // 🆕 注册NavBar组件
  },
  setup() {
    // 响应式数据
    const configContent = ref('')
    const originalContent = ref('')
    const saving = ref(false)
    const validating = ref(false)
    const showHelp = ref(false)
    const lastSaved = ref('')
    
    const validationStatus = reactive({
      valid: true,
      type: 'success',
      text: '✅ 配置有效'
    })
    
    const validationMessage = ref('')
    const configStats = reactive({
      totalRules: 0,
      activeRules: 0,
      totalExperiences: 0
    })
    
    const availableFunctions = ref([
      { name: 'safe_get(obj, "key", default)', description: '安全获取对象属性值' },
      { name: 'abs(number)', description: '返回数字的绝对值' },
      { name: 'min(a, b, ...)', description: '返回最小值' },
      { name: 'max(a, b, ...)', description: '返回最大值' },
      { name: 'sum([numbers])', description: '计算数组元素之和' },
      { name: 'len(array)', description: '返回数组长度' },
      { name: 'round(number, digits)', description: '四舍五入到指定位数' },
      { name: 'all([booleans])', description: '所有元素都为真时返回true' },
      { name: 'any([booleans])', description: '任一元素为真时返回true' }
    ])

    // 示例代码
    const ruleExample = ref(`{
  "name": "CPU电压匹配",
  "description": "确保CPU和主板电压兼容",
  "expression": "part_a.voltage == part_b.voltage",
  "category_a": "CPU",
  "category_b": "主板",
  "weight": 100,
  "is_blocking": false,
  "is_active": true
}`)

    const experienceExample = ref(`{
  "part_a_id": 1,
  "part_b_id": 2,
  "compatibility_status": "compatible",
  "compatibility_score": 95,
  "notes": "完美兼容，官方测试通过",
  "source": "admin",
  "verification_status": "verified"
}`)

    // 计算属性
    const hasUnsavedChanges = computed(() => {
      return configContent.value !== originalContent.value
    })

    // 内容变化处理
    const onContentChange = () => {
      validateSyntax()
    }

    // 快捷键处理
    const onKeyDown = (event) => {
      // Ctrl+S 保存
      if (event.ctrlKey && event.key === 's') {
        event.preventDefault()
        saveConfig()
        return
      }
      
      // Ctrl+F 格式化
      if (event.ctrlKey && event.key === 'f') {
        event.preventDefault()
        formatDocument()
        return
      }
      
      // Ctrl+Enter 验证
      if (event.ctrlKey && event.key === 'Enter') {
        event.preventDefault()
        validateAll()
        return
      }
    }

    // 加载配置
    const loadConfig = async () => {
      try {
        validationMessage.value = '正在加载配置...'
        console.log('🔄 开始加载配置...')
        
        console.log('📡 调用API获取规则和经验...')
        const [rulesRes, experiencesRes] = await Promise.all([
          compatibilityAPI.rules.list({ limit: 1000 }),
          compatibilityAPI.experiences.list({ limit: 1000 })
        ])

        console.log('📋 规则API响应:', rulesRes)
        console.log('📚 经验API响应:', experiencesRes)
        console.log('📊 规则数据:', rulesRes.data.items)
        console.log('📈 经验数据:', experiencesRes.data.items)

        const config = {
          metadata: {
            description: "OpenPart 兼容性配置文件",
            version: "1.0.0",
            last_updated: new Date().toISOString(),
            total_rules: rulesRes.data.total,
            active_rules: rulesRes.data.items.filter(r => r.is_active).length,
            total_experiences: experiencesRes.data.total
          },
          compatibility_rules: rulesRes.data.items.map(rule => {
            console.log(`🔧 处理规则: ${rule.name} (ID: ${rule.id})`, rule)
            return {
              id: rule.id,
              name: rule.name,
              description: rule.description,
              expression: rule.rule_expression, // 注意：这里是关键映射
              category_a: rule.category_a,
              category_b: rule.category_b,
              weight: rule.weight,
              is_blocking: rule.is_blocking,
              is_active: rule.is_active,
              created_at: rule.created_at
            }
          }),
          compatibility_experiences: experiencesRes.data.items.map(exp => ({
            id: exp.id,
            part_a_id: exp.part_a_id,
            part_b_id: exp.part_b_id,
            compatibility_status: exp.compatibility_status,
            compatibility_score: exp.compatibility_score,
            notes: exp.notes,
            source: exp.source,
            verification_status: exp.verification_status,
            created_at: exp.created_at
          }))
        }

        console.log('🏗️ 构建的配置对象:', config)
        console.log('📝 规则详情:', config.compatibility_rules)

        const formattedContent = JSON.stringify(config, null, 2)
        console.log('📄 格式化的JSON长度:', formattedContent.length)
        
        configContent.value = formattedContent
        originalContent.value = formattedContent
        
        updateStats(config)
        validationMessage.value = '配置加载完成'
        ElMessage.success('配置加载成功')
        
        console.log('✅ 配置加载完成，当前编辑器内容长度:', configContent.value.length)
        
      } catch (error) {
        console.error('❌ 加载配置失败:', error)
        ElMessage.error('加载配置失败: ' + error.message)
        validationMessage.value = '加载失败: ' + error.message
      }
    }

    // 更新统计信息
    const updateStats = (config) => {
      if (config.metadata) {
        configStats.totalRules = config.metadata.total_rules || 0
        configStats.activeRules = config.metadata.active_rules || 0
        configStats.totalExperiences = config.metadata.total_experiences || 0
      } else if (config.compatibility_rules) {
        configStats.totalRules = config.compatibility_rules.length
        configStats.activeRules = config.compatibility_rules.filter(r => r.is_active).length
        configStats.totalExperiences = config.compatibility_experiences?.length || 0
      }
    }

    // 语法验证
    const validateSyntax = () => {
      try {
        const config = JSON.parse(configContent.value)
        updateStats(config)
        
        if (!config.compatibility_rules || !Array.isArray(config.compatibility_rules)) {
          throw new Error('缺少 compatibility_rules 数组')
        }

        validationStatus.valid = true
        validationStatus.type = 'success'
        validationStatus.text = '✅ 配置有效'
        validationMessage.value = ''
        
      } catch (error) {
        validationStatus.valid = false
        validationStatus.type = 'danger'
        validationStatus.text = '❌ 语法错误'
        validationMessage.value = error.message
      }
    }

    // 格式化JSON
    const formatDocument = () => {
      try {
        const config = JSON.parse(configContent.value)
        configContent.value = JSON.stringify(config, null, 2)
        ElMessage.success('JSON格式化成功')
      } catch (error) {
        ElMessage.error('格式化失败：JSON语法错误')
      }
    }

    // 验证所有规则表达式
    const validateAll = async () => {
      if (!validationStatus.valid) {
        ElMessage.error('请先修复JSON语法错误')
        return
      }

      validating.value = true
      validationMessage.value = '正在验证规则表达式...'

      try {
        const config = JSON.parse(configContent.value)
        const rules = config.compatibility_rules || []
        
        console.log('开始验证规则，总数:', rules.length)
        
        let errorCount = 0
        let validationResults = []
        
        for (const rule of rules) {
          if (rule.expression) {
            try {
              console.log(`验证规则: ${rule.name}`)
              console.log(`表达式: ${rule.expression}`)
              
              const result = await compatibilityAPI.rules.validate(rule.expression)
              console.log(`验证结果:`, result)
              
              // 检查响应结构
              const validationData = result.data || result
              
              if (!validationData.is_safe) {
                errorCount++
                validationResults.push(`❌ 规则 "${rule.name}": 存在安全风险`)
                console.warn(`规则 "${rule.name}" 安全风险:`, validationData.security_issues)
              } else {
                validationResults.push(`✅ 规则 "${rule.name}": 验证通过`)
              }
            } catch (error) {
              errorCount++
              validationResults.push(`❌ 规则 "${rule.name}": ${error.message}`)
              console.error(`规则 "${rule.name}" 验证失败:`, error)
            }
          } else {
            validationResults.push(`⚠️ 规则 "${rule.name}": 缺少表达式`)
          }
        }

        console.log('验证结果详情:', validationResults)

        if (errorCount > 0) {
          validationMessage.value = `发现 ${errorCount} 个规则存在问题`
          ElMessage.warning(`验证完成，发现 ${errorCount} 个问题，请检查控制台`)
        } else {
          validationMessage.value = '所有规则验证通过'
          ElMessage.success('所有规则验证通过！')
        }
        
      } catch (error) {
        console.error('验证失败:', error)
        validationMessage.value = '验证失败: ' + error.message
        ElMessage.error('验证失败: ' + error.message)
      } finally {
        validating.value = false
      }
    }

    // 保存配置
    const saveConfig = async () => {
      if (!validationStatus.valid) {
        ElMessage.error('配置文件存在错误，无法保存')
        return
      }

      saving.value = true
      validationMessage.value = '正在保存配置...'

      try {
        const config = JSON.parse(configContent.value)
        const rules = config.compatibility_rules || []

        console.log('🚀 开始完整同步配置...')
        console.log('📊 编辑器中的规则数量:', rules.length)

        // 🔍 第一步：获取当前数据库中的所有规则
        console.log('📡 获取数据库中现有的规则...')
        const currentRulesResponse = await compatibilityAPI.rules.list({ limit: 1000 })
        const currentRules = currentRulesResponse.data.items
        console.log('💾 数据库中的规则数量:', currentRules.length)
        console.log('💾 数据库中的规则:', currentRules.map(r => ({ id: r.id, name: r.name })))

        // 🔍 第二步：分析需要执行的操作
        const editorRuleIds = new Set(rules.filter(r => r.id).map(r => r.id))
        const dbRuleIds = new Set(currentRules.map(r => r.id))
        
        // 🔧 修复：区分真实存在的规则和虚假ID的规则
        const rulesToCreate = rules.filter(r => {
          // 没有ID，或者有ID但在数据库中不存在（虚假ID）
          return !r.id || (r.id && !dbRuleIds.has(r.id))
        })
        
        const rulesToUpdate = rules.filter(r => {
          // 有ID且在数据库中真实存在
          return r.id && dbRuleIds.has(r.id)
        })
        
        const rulesToDelete = currentRules.filter(r => !editorRuleIds.has(r.id)) // 数据库中有但编辑器中没有

        console.log('📋 操作计划:')
        console.log('  ➕ 需要创建:', rulesToCreate.length, '个规则')
        console.log('  ➕ 创建列表:', rulesToCreate.map(r => ({ 
          id: r.id || 'NEW', 
          name: r.name,
          reason: !r.id ? '无ID' : '虚假ID'
        })))
        console.log('  🔄 需要更新:', rulesToUpdate.length, '个规则')
        console.log('  🔄 更新列表:', rulesToUpdate.map(r => ({ id: r.id, name: r.name })))
        console.log('  🗑️ 需要删除:', rulesToDelete.length, '个规则')
        console.log('  🗑️ 删除列表:', rulesToDelete.map(r => ({ id: r.id, name: r.name })))

        let savedCount = 0
        let errorCount = 0
        let operationDetails = []

        // 🗑️ 第三步：删除不在编辑器中的规则
        console.log('🗑️ 开始删除规则...')
        for (const ruleToDelete of rulesToDelete) {
          try {
            console.log(`🗑️ 删除规则: ${ruleToDelete.name} (ID: ${ruleToDelete.id})`)
            
            // 先尝试普通删除
            try {
              await compatibilityAPI.rules.delete(ruleToDelete.id, false)
              operationDetails.push(`🗑️ 删除规则: ${ruleToDelete.name}`)
              console.log(`✅ 成功删除规则: ${ruleToDelete.name}`)
            } catch (normalDeleteError) {
              console.log(`⚠️ 普通删除失败，尝试强制删除: ${ruleToDelete.name}`)
              console.log('删除错误:', normalDeleteError.message)
              
              // 如果普通删除失败，使用强制删除
              if (normalDeleteError.message.includes('依赖') || normalDeleteError.response?.status === 409) {
                console.log(`🔥 强制删除规则: ${ruleToDelete.name}`)
                await compatibilityAPI.rules.delete(ruleToDelete.id, true) // force=true
                operationDetails.push(`🔥 强制删除规则: ${ruleToDelete.name} (忽略依赖)`)
                console.log(`✅ 强制删除成功: ${ruleToDelete.name}`)
              } else {
                // 如果不是依赖问题，重新抛出错误
                throw normalDeleteError
              }
            }
            
          } catch (error) {
            errorCount++
            console.error(`❌ 删除规则失败: ${ruleToDelete.name}`, error)
            operationDetails.push(`❌ 删除失败: ${ruleToDelete.name} - ${error.message}`)
          }
        }

        // ➕ 第四步：创建新规则
        console.log('➕ 开始创建新规则...')
        for (const ruleToCreate of rulesToCreate) {
          try {
            console.log(`➕ 创建新规则: ${ruleToCreate.name}`)
            
            const createData = {
              name: ruleToCreate.name,
              description: ruleToCreate.description,
              rule_expression: ruleToCreate.expression,
              category_a: ruleToCreate.category_a,
              category_b: ruleToCreate.category_b,
              weight: ruleToCreate.weight,
              is_blocking: ruleToCreate.is_blocking
            }
            
            const newRuleResponse = await compatibilityAPI.rules.create(createData)
            const newRule = newRuleResponse.data
            console.log(`✅ 创建成功，新规则ID: ${newRule.id}`)
            
            // 处理启用/停用状态
            if (!ruleToCreate.is_active) {
              console.log(`⏸️ 停用新创建的规则: ${newRule.id}`)
              await compatibilityAPI.rules.disable(newRule.id)
              operationDetails.push(`➕ 创建并停用规则: ${ruleToCreate.name}`)
            } else {
              operationDetails.push(`➕ 创建规则: ${ruleToCreate.name}`)
            }
            
            savedCount++
            
          } catch (error) {
            errorCount++
            console.error(`❌ 创建规则失败: ${ruleToCreate.name}`, error)
            operationDetails.push(`❌ 创建失败: ${ruleToCreate.name} - ${error.message}`)
          }
        }

        // 🔄 第五步：更新现有规则
        console.log('🔄 开始更新现有规则...')
        for (const rule of rulesToUpdate) {
          try {
            console.log(`🔄 更新规则: ${rule.name} (ID: ${rule.id})`)
            
            const updateData = {
              name: rule.name,
              description: rule.description,
              rule_expression: rule.expression,
              category_a: rule.category_a,
              category_b: rule.category_b,
              weight: rule.weight,
              is_blocking: rule.is_blocking
            }
            
            await compatibilityAPI.rules.update(rule.id, updateData)
            
            // 处理启用/停用状态
            const currentRule = currentRules.find(r => r.id === rule.id)
            if (currentRule && currentRule.is_active !== rule.is_active) {
              if (rule.is_active) {
                console.log(`▶️ 启用规则: ${rule.id}`)
                await compatibilityAPI.rules.enable(rule.id)
                operationDetails.push(`🔄 更新并启用规则: ${rule.name}`)
              } else {
                console.log(`⏸️ 停用规则: ${rule.id}`)
                await compatibilityAPI.rules.disable(rule.id)
                operationDetails.push(`🔄 更新并停用规则: ${rule.name}`)
              }
            } else {
              operationDetails.push(`🔄 更新规则: ${rule.name}`)
            }
            
            savedCount++
            
          } catch (error) {
            errorCount++
            console.error(`❌ 更新规则失败: ${rule.name}`, error)
            operationDetails.push(`❌ 更新失败: ${rule.name} - ${error.message}`)
          }
        }

        console.log('📊 同步操作完成!')
        console.log('🔍 操作详情:', operationDetails)
        console.log(`📈 统计结果: ${savedCount} 成功, ${errorCount} 失败`)
        console.log(`🗑️ 删除: ${rulesToDelete.length} 个`)
        console.log(`➕ 创建: ${rulesToCreate.length} 个`)
        console.log(`🔄 更新: ${rulesToUpdate.length} 个`)

        // 🆕 第七步：同步经验数据
        console.log('📚 开始同步经验数据...')
        const experiences = config.compatibility_experiences || []
        console.log('📊 编辑器中的经验数量:', experiences.length)

        // 获取当前数据库中的所有经验
        console.log('📡 获取数据库中现有的经验...')
        const currentExperiencesResponse = await compatibilityAPI.experiences.list({ limit: 1000 })
        const currentExperiences = currentExperiencesResponse.data.items
        console.log('💾 数据库中的经验数量:', currentExperiences.length)
        console.log('💾 数据库中的经验:', currentExperiences.map(e => ({ id: e.id, part_a_id: e.part_a_id, part_b_id: e.part_b_id })))

        // 分析经验操作
        const editorExperienceIds = new Set(experiences.filter(e => e.id).map(e => e.id))
        const dbExperienceIds = new Set(currentExperiences.map(e => e.id))
        
        const experiencesToCreate = experiences.filter(e => {
          return !e.id || (e.id && !dbExperienceIds.has(e.id))
        })
        
        const experiencesToUpdate = experiences.filter(e => {
          return e.id && dbExperienceIds.has(e.id)
        })
        
        const experiencesToDelete = currentExperiences.filter(e => !editorExperienceIds.has(e.id))

        console.log('📋 经验操作计划:')
        console.log('  ➕ 需要创建:', experiencesToCreate.length, '个经验')
        console.log('  ➕ 创建列表:', experiencesToCreate.map(e => ({ 
          id: e.id || 'NEW', 
          parts: `${e.part_a_id}-${e.part_b_id}`,
          reason: !e.id ? '无ID' : '虚假ID'
        })))
        console.log('  🔄 需要更新:', experiencesToUpdate.length, '个经验')
        console.log('  🔄 更新列表:', experiencesToUpdate.map(e => ({ id: e.id, parts: `${e.part_a_id}-${e.part_b_id}` })))
        console.log('  🗑️ 需要删除:', experiencesToDelete.length, '个经验')
        console.log('  🗑️ 删除列表:', experiencesToDelete.map(e => ({ id: e.id, parts: `${e.part_a_id}-${e.part_b_id}` })))

        // 删除不在编辑器中的经验
        console.log('🗑️ 开始删除经验...')
        for (const experienceToDelete of experiencesToDelete) {
          try {
            console.log(`🗑️ 删除经验: ${experienceToDelete.part_a_id}-${experienceToDelete.part_b_id} (ID: ${experienceToDelete.id})`)
            await compatibilityAPI.experiences.delete(experienceToDelete.id)
            operationDetails.push(`🗑️ 删除经验: ${experienceToDelete.part_a_id}-${experienceToDelete.part_b_id}`)
            console.log(`✅ 成功删除经验: ${experienceToDelete.id}`)
          } catch (error) {
            errorCount++
            console.error(`❌ 删除经验失败: ${experienceToDelete.id}`, error)
            operationDetails.push(`❌ 删除经验失败: ${experienceToDelete.part_a_id}-${experienceToDelete.part_b_id} - ${error.message}`)
          }
        }

        // 创建新经验
        console.log('➕ 开始创建新经验...')
        for (const experienceToCreate of experiencesToCreate) {
          try {
            console.log(`➕ 创建新经验: ${experienceToCreate.part_a_id}-${experienceToCreate.part_b_id}`)
            
            const createData = {
              part_a_id: experienceToCreate.part_a_id,
              part_b_id: experienceToCreate.part_b_id,
              compatibility_status: experienceToCreate.compatibility_status,
              compatibility_score: experienceToCreate.compatibility_score,
              notes: experienceToCreate.notes,
              source: experienceToCreate.source || 'admin',
              verification_status: experienceToCreate.verification_status || 'verified'
            }
            
            const newExperienceResponse = await compatibilityAPI.experiences.create(createData)
            const newExperience = newExperienceResponse.data
            console.log(`✅ 创建成功，新经验ID: ${newExperience.id}`)
            
            operationDetails.push(`➕ 创建经验: ${experienceToCreate.part_a_id}-${experienceToCreate.part_b_id}`)
            savedCount++
            
          } catch (error) {
            errorCount++
            console.error(`❌ 创建经验失败: ${experienceToCreate.part_a_id}-${experienceToCreate.part_b_id}`, error)
            operationDetails.push(`❌ 创建经验失败: ${experienceToCreate.part_a_id}-${experienceToCreate.part_b_id} - ${error.message}`)
          }
        }

        // 更新现有经验
        console.log('🔄 开始更新现有经验...')
        for (const experience of experiencesToUpdate) {
          try {
            console.log(`🔄 更新经验: ${experience.part_a_id}-${experience.part_b_id} (ID: ${experience.id})`)
            
            const updateData = {
              part_a_id: experience.part_a_id,
              part_b_id: experience.part_b_id,
              compatibility_status: experience.compatibility_status,
              compatibility_score: experience.compatibility_score,
              notes: experience.notes,
              source: experience.source || 'admin',
              verification_status: experience.verification_status || 'verified'
            }
            
            await compatibilityAPI.experiences.update(experience.id, updateData)
            operationDetails.push(`🔄 更新经验: ${experience.part_a_id}-${experience.part_b_id}`)
            savedCount++
            
          } catch (error) {
            errorCount++
            console.error(`❌ 更新经验失败: ${experience.part_a_id}-${experience.part_b_id}`, error)
            operationDetails.push(`❌ 更新经验失败: ${experience.part_a_id}-${experience.part_b_id} - ${error.message}`)
          }
        }

        console.log('📚 经验同步完成!')
        console.log(`📈 经验统计: 删除 ${experiencesToDelete.length} 个，创建 ${experiencesToCreate.length} 个，更新 ${experiencesToUpdate.length} 个`)

        originalContent.value = configContent.value
        lastSaved.value = new Date().toLocaleString()
        validationMessage.value = `完整同步完成: ${savedCount} 成功, ${errorCount} 失败`
        
        if (errorCount > 0) {
          ElMessage.warning(`同步完成，但有 ${errorCount} 个操作失败，请查看控制台`)
          console.warn('失败的操作:', operationDetails.filter(op => op.includes('❌')))
        } else {
          ElMessage.success(`配置完整同步成功！规则：删除 ${rulesToDelete.length}，创建 ${rulesToCreate.length}，更新 ${rulesToUpdate.length}；经验：删除 ${experiencesToDelete.length}，创建 ${experiencesToCreate.length}，更新 ${experiencesToUpdate.length}`)
          console.log('✅ 所有操作成功:', operationDetails)
        }
        
      } catch (error) {
        console.error('❌ 同步失败:', error)
        ElMessage.error('同步失败: ' + error.message)
        validationMessage.value = '同步失败: ' + error.message
      } finally {
        saving.value = false
      }
    }

    // 重新加载配置
    const reloadConfig = async () => {
      if (hasUnsavedChanges.value) {
        try {
          await ElMessageBox.confirm(
            '重新加载将丢失未保存的更改，确定继续吗？',
            '确认重新加载',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning'
            }
          )
        } catch {
          return
        }
      }
      
      await loadConfig()
    }

    // 插入模板
    const insertRuleTemplate = () => {
      const template = {
        "name": "新建规则",
        "description": "规则描述", 
        "expression": "part_a.property == part_b.property",
        "category_a": "类别A",
        "category_b": "类别B",
        "weight": 100,
        "is_blocking": false,
        "is_active": true
      }
      
      const templateText = JSON.stringify(template, null, 2)
      configContent.value += '\n' + templateText
      ElMessage.success('规则模板已插入')
    }

    const insertExperienceTemplate = () => {
      const template = {
        "part_a_id": 1,
        "part_b_id": 2,
        "compatibility_status": "compatible",
        "compatibility_score": 95,
        "notes": "兼容性说明",
        "source": "admin",
        "verification_status": "verified"
      }
      
      const templateText = JSON.stringify(template, null, 2)
      configContent.value += '\n' + templateText
      ElMessage.success('经验模板已插入')
    }

    const insertFullTemplate = () => {
      const template = {
        "metadata": {
          "description": "OpenPart 兼容性配置文件",
          "version": "1.0.0",
          "last_updated": new Date().toISOString()
        },
        "compatibility_rules": [
          {
            "name": "示例规则",
            "description": "这是一个示例规则",
            "expression": "part_a.voltage == part_b.voltage",
            "category_a": "CPU",
            "category_b": "主板",
            "weight": 100,
            "is_blocking": false,
            "is_active": true
          }
        ],
        "compatibility_experiences": [
          {
            "part_a_id": 1,
            "part_b_id": 2,
            "compatibility_status": "compatible",
            "compatibility_score": 95,
            "notes": "示例兼容性经验",
            "source": "admin",
            "verification_status": "verified"
          }
        ]
      }
      
      configContent.value = JSON.stringify(template, null, 2)
      ElMessage.success('完整模板已插入')
    }

    // 页面离开前检查
    const beforeUnload = (e) => {
      if (hasUnsavedChanges.value) {
        e.preventDefault()
        e.returnValue = '您有未保存的更改，确定要离开吗？'
        return e.returnValue
      }
    }

    // 生命周期
    onMounted(async () => {
      console.log('简化版编辑器已加载')
      await loadConfig()
      window.addEventListener('beforeunload', beforeUnload)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('beforeunload', beforeUnload)
    })

    return {
      // 响应式数据
      configContent,
      saving,
      validating,
      showHelp,
      lastSaved,
      validationStatus,
      validationMessage,
      configStats,
      availableFunctions,
      hasUnsavedChanges,
      ruleExample,
      experienceExample,
      
      // 方法
      onContentChange,
      onKeyDown,
      loadConfig,
      saveConfig,
      reloadConfig,
      validateAll,
      formatDocument,
      insertRuleTemplate,
      insertExperienceTemplate,
      insertFullTemplate
    }
  }
}
</script>

<style scoped>
/* 🆕 页面容器 - 保持导航栏 */
.compatibility-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.compatibility-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  /* 移除 height: 100vh，因为现在不是根容器 */
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.status-tag {
  font-size: 12px;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.editor-container {
  flex: 1;
  padding: 20px;
  overflow: hidden;
}

.code-editor {
  height: 100%;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
  font-size: 14px;
  line-height: 1.5;
}

:deep(.code-editor .el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
  font-size: 14px;
  line-height: 1.5;
  background: #1e1e1e;
  color: #d4d4d4;
  border: 1px solid #404040;
  border-radius: 4px;
  padding: 16px;
  resize: none;
  height: 100% !important;
}

:deep(.code-editor .el-textarea__inner:focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.editor-statusbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 20px;
  background: #409eff;
  color: #ffffff;
  font-size: 12px;
  flex-shrink: 0;
}

.status-left,
.status-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.separator {
  color: rgba(255, 255, 255, 0.6);
}

.validation-msg {
  color: #ffec3d;
  font-weight: 500;
}

.help-content {
  padding: 16px;
}

.function-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin: 16px 0;
}

.function-item {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.function-item p {
  margin: 8px 0;
  font-size: 13px;
  color: #606266;
}

.function-item code {
  display: block;
  background: #2d2d30;
  color: #d4d4d4;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  margin-top: 8px;
  font-family: 'Consolas', 'Monaco', monospace;
}

.template-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 16px 0;
}

.example-code {
  background: #2d2d30;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  font-family: 'Consolas', 'Monaco', monospace;
  overflow-x: auto;
  white-space: pre;
}

kbd {
  background: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 3px;
  padding: 2px 6px;
  font-size: 11px;
  font-family: monospace;
  margin: 0 2px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .toolbar-left,
  .toolbar-right {
    justify-content: center;
  }
  
  .editor-container {
    padding: 10px;
  }
}
</style>