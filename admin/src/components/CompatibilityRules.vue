<template>
  <div class="compatibility-rules">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="saveRules" :loading="saving">
          <el-icon><DocumentAdd /></el-icon>
          保存规则
        </el-button>
        <el-button @click="validateAll" :loading="validating">
          <el-icon><CircleCheck /></el-icon>
          验证语法
        </el-button>
        <el-button @click="showTestDialog = true" :disabled="!hasValidRules">
          <el-icon><CaretRight /></el-icon>
          测试执行
        </el-button>
        <el-divider direction="vertical" />
        <el-button @click="importRules">
          <el-icon><Upload /></el-icon>
          导入
        </el-button>
        <el-button @click="exportRules">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
      
      <div class="toolbar-right">
        <el-button @click="showHelpDialog = true" type="info" text>
          <el-icon><QuestionFilled /></el-icon>
          语法帮助
        </el-button>
        <el-button @click="loadRules" :loading="loading">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Monaco 编辑器区域 -->
    <div class="editor-container">
      <!-- 使用简单的文本编辑器替代Monaco -->
      <div class="simple-editor" v-if="!editorLoading">
        <!-- 编辑器工具栏 -->
        <div class="editor-toolbar">
          <el-button-group size="small">
            <el-button @click="insertTemplate('rule')">
              <el-icon><DocumentAdd /></el-icon>
              插入规则模板
            </el-button>
            <el-button @click="insertTemplate('expression')">
              <el-icon><Plus /></el-icon>
              常用表达式
            </el-button>
          </el-button-group>
          
          <div class="editor-info">
            <span>行数: {{ lineCount }} | 字符: {{ currentContent.length }}</span>
          </div>
        </div>
        
        <!-- 文本编辑器 -->
        <el-input
          v-model="currentContent"
          type="textarea"
          :rows="22"
          placeholder="在此编辑兼容性规则..."
          class="rule-editor"
          @input="parseRules"
          @keydown="handleKeyDown"
          resize="none"
        />
      </div>
      
      <!-- 编辑器加载状态 -->
      <div v-if="editorLoading" class="editor-loading">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <p>正在加载编辑器...</p>
      </div>
    </div>

    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="status-left">
        <el-tag v-if="parseResult.success" type="success" size="small">
          <el-icon><CircleCheck /></el-icon>
          已加载 {{ parseResult.ruleCount }} 个规则
        </el-tag>
        <el-tag v-else type="danger" size="small">
          <el-icon><CircleClose /></el-icon>
          语法错误
        </el-tag>
        
        <el-tag v-if="validationResult.issues.length > 0" type="warning" size="small">
          <el-icon><Warning /></el-icon>
          {{ validationResult.issues.length }} 个问题
        </el-tag>
        
        <el-tag v-if="lastSaved" type="info" size="small">
          <el-icon><Clock /></el-icon>
          {{ lastSaved }}
        </el-tag>
      </div>
      
      <div class="status-right">
        <span class="cursor-position">行 {{ cursorPosition.line }}, 列 {{ cursorPosition.column }}</span>
      </div>
    </div>

    <!-- 规则测试对话框 -->
    <el-dialog
      title="规则测试"
      v-model="showTestDialog"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="test-container">
        <el-form :model="testForm" label-width="100px">
          <el-form-item label="选择规则">
            <el-select v-model="testForm.selectedRule" placeholder="请选择要测试的规则" style="width: 100%">
              <el-option
                v-for="rule in availableRules"
                :key="rule.name"
                :label="rule.name"
                :value="rule.name"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="测试数据">
            <el-input
              v-model="testForm.testData"
              type="textarea"
              :rows="8"
              placeholder="请输入JSON格式的测试数据"
            />
          </el-form-item>
        </el-form>
        
        <!-- 测试结果 -->
        <div v-if="testResult" class="test-result">
          <el-divider>测试结果</el-divider>
          <el-alert
            :type="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? '测试通过' : '测试失败'"
            :description="testResult.message"
            show-icon
            :closable="false"
          />
          
          <div v-if="testResult.details" class="test-details">
            <p><strong>执行时间:</strong> {{ testResult.execution_time }}ms</p>
            <p><strong>结果:</strong> {{ testResult.result }}</p>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showTestDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="executeTest" 
          :loading="testing"
          :disabled="!testForm.selectedRule || !testForm.testData"
        >
          执行测试
        </el-button>
      </template>
    </el-dialog>

    <!-- 语法帮助对话框 -->
    <el-dialog
      title="规则语法帮助"
      v-model="showHelpDialog"
      width="900px"
    >
      <div class="help-content">
        <el-tabs>
          <el-tab-pane label="基础语法" name="syntax">
            <div class="help-section">
              <h4>规则定义格式</h4>
              <pre class="code-example">rule "规则名称" {
  description: "规则描述"
  category_a: "零件类别A"
  category_b: "零件类别B"
  expression: "兼容性表达式"
  weight: 100
  blocking: false
}</pre>
              
              <h4>字段说明</h4>
              <ul>
                <li><code>description</code>: 可选，规则的详细描述</li>
                <li><code>category_a/category_b</code>: 必需，零件类别</li>
                <li><code>expression</code>: 必需，兼容性判断表达式</li>
                <li><code>weight</code>: 可选，规则权重 (0-1000)，默认100</li>
                <li><code>blocking</code>: 可选，是否为阻断性规则，默认false</li>
              </ul>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="表达式" name="expressions">
            <div class="help-section">
              <h4>变量访问</h4>
              <pre class="code-example">part_a.voltage        // 访问零件A的电压属性
part_b.power           // 访问零件B的功率属性
safe_get(part_a, "frequency", 0)  // 安全获取属性，带默认值</pre>
              
              <h4>比较操作</h4>
              <pre class="code-example">part_a.voltage == part_b.voltage     // 相等
part_a.power >= part_b.min_power      // 大于等于
part_a.socket != part_b.socket        // 不等于</pre>
              
              <h4>逻辑操作</h4>
              <pre class="code-example">expr1 && expr2        // 逻辑与
expr1 || expr2        // 逻辑或
!(expr)               // 逻辑非</pre>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="安全函数" name="functions">
            <div class="help-section">
              <h4>可用函数</h4>
              <div v-if="availableFunctions.length > 0">
                <div v-for="func in availableFunctions" :key="func.name" class="function-item">
                  <code>{{ func.name }}</code>
                  <span class="function-desc">{{ func.description }}</span>
                </div>
              </div>
              <el-skeleton v-else :rows="5" animated />
              
              <h4>使用示例</h4>
              <pre class="code-example">// 安全获取属性
safe_get(part_a, "voltage", 12)

// 数学计算
sum([part_a.power, part_b.power]) <= 1000
max(part_a.frequency, part_b.frequency) <= 3200

// 长度检查
len(part_a.name) > 0</pre>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="示例" name="examples">
            <div class="help-section">
              <h4>完整示例</h4>
              <pre class="code-example">// CPU和主板插槽匹配
rule "CPU主板插槽兼容" {
  description: "确保CPU和主板的插槽类型匹配"
  category_a: "CPU"
  category_b: "主板"
  expression: "part_a.socket == part_b.socket"
  weight: 100
  blocking: true
}

// 电源功率检查
rule "电源功率充足" {
  description: "检查电源功率是否满足显卡需求"
  category_a: "电源"
  category_b: "显卡"
  expression: "part_a.wattage >= part_b.power_consumption * 1.2"
  weight: 95
  blocking: true
}

// 内存频率兼容
rule "内存频率支持" {
  category_a: "内存"
  category_b: "主板"
  expression: "part_a.frequency <= safe_get(part_b, 'max_memory_freq', 3200)"
  weight: 80
  blocking: false
}</pre>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInput"
      type="file"
      accept=".txt,.rules"
      style="display: none"
      @change="handleFileImport"
    />
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import {
  DocumentAdd, CircleCheck, CaretRight, Upload, Download,
  QuestionFilled, Refresh, Loading, CircleClose, Warning, Clock
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { compatibilityRules, compatibilitySystem } from '../utils/api'

export default {
  name: 'CompatibilityRules',
  components: {
    DocumentAdd, CircleCheck, CaretRight, Upload, Download,
    QuestionFilled, Refresh, Loading, CircleClose, Warning, Clock
  },
  emits: ['stats-updated'],
  setup(props, { emit }) {
    const loading = ref(false)
    const saving = ref(false)
    const validating = ref(false)
    const testing = ref(false)
    const editorLoading = ref(true)
    
    // 编辑器相关
    const editorContainer = ref()
    const currentContent = ref('')
    
    // 解析和验证结果
    const parseResult = reactive({
      success: false,
      ruleCount: 0,
      errors: []
    })
    
    const validationResult = reactive({
      issues: [],
      lastValidated: null
    })
    
    // 光标位置
    const cursorPosition = reactive({
      line: 1,
      column: 1
    })
    
    // 保存状态
    const lastSaved = ref('')
    
    // 测试相关
    const showTestDialog = ref(false)
    const testForm = reactive({
      selectedRule: '',
      testData: ''
    })
    const testResult = ref(null)
    
    // 帮助对话框
    const showHelpDialog = ref(false)
    const availableFunctions = ref([])
    
    // 可用规则列表
    const availableRules = ref([])
    
    // 计算属性
    const hasValidRules = ref(false)
    const lineCount = computed(() => {
      return currentContent.value ? currentContent.value.split('\n').length : 0
    })

    // 默认规则模板
    const defaultRulesTemplate = `// OpenPart 兼容性规则配置
// 创建时间: ${new Date().toLocaleString('zh-CN')}
// 管理员: 系统管理员

// 示例规则：CPU和主板插槽匹配
rule "CPU主板插槽兼容" {
  description: "确保CPU和主板的插槽类型匹配"
  category_a: "CPU"
  category_b: "主板"
  expression: "part_a.socket == part_b.socket"
  weight: 100
  blocking: true
}

// 示例规则：电源功率检查
rule "电源功率充足" {
  description: "检查电源功率是否满足组件需求"
  category_a: "电源"
  category_b: "显卡"
  expression: "part_a.wattage >= part_b.power_consumption * 1.2"
  weight: 95
  blocking: true
}

// 请在下方添加更多规则...
`

    // 初始化Monaco编辑器
    const initMonacoEditor = async () => {
      try {
        // 暂时使用简单的文本编辑器，避免Monaco加载问题
        // 后续可以配置Monaco编辑器
        editorLoading.value = false
        
        // 设置初始内容
        if (!currentContent.value) {
          currentContent.value = defaultRulesTemplate
        }
        
        // 初始解析
        parseRules()
        
      } catch (error) {
        console.error('编辑器初始化失败:', error)
        ElMessage.error('编辑器加载失败，使用简化模式')
        editorLoading.value = false
        
        // 设置默认内容
        if (!currentContent.value) {
          currentContent.value = defaultRulesTemplate
        }
        parseRules()
      }
    }

    // 解析规则文本
    const parseRules = () => {
      try {
        const content = currentContent.value
        const rules = parseRulesFromText(content)
        
        parseResult.success = true
        parseResult.ruleCount = rules.length
        parseResult.errors = []
        
        availableRules.value = rules
        hasValidRules.value = rules.length > 0
        
      } catch (error) {
        parseResult.success = false
        parseResult.ruleCount = 0
        parseResult.errors = [error.message]
        hasValidRules.value = false
      }
    }

    // 从文本解析规则
    const parseRulesFromText = (text) => {
      const rules = []
      const ruleRegex = /rule\s+"([^"]+)"\s*\{([^}]+)\}/g
      let match
      
      while ((match = ruleRegex.exec(text)) !== null) {
        const [, name, body] = match
        const rule = { name }
        
        // 解析规则体
        const lines = body.split('\n')
        for (const line of lines) {
          const trimmed = line.trim()
          if (trimmed && !trimmed.startsWith('//')) {
            const [key, ...valueParts] = trimmed.split(':')
            if (key && valueParts.length > 0) {
              const value = valueParts.join(':').trim().replace(/,$/, '').replace(/^"/, '').replace(/"$/, '')
              rule[key.trim()] = value
            }
          }
        }
        
        rules.push(rule)
      }
      
      return rules
    }

    // 加载规则
    const loadRules = async () => {
      loading.value = true
      
      try {
        const response = await compatibilityRules.list({ limit: 1000 })
        const rules = response.data.items || response.data
        
        // 转换为文本格式
        const rulesText = convertRulesToText(rules)
        currentContent.value = rulesText
        
        // 更新统计信息
        emit('stats-updated', {
          total_rules: rules.length,
          active_rules: rules.filter(r => r.is_active).length
        })
        
        ElMessage.success(`已加载 ${rules.length} 个规则`)
        
      } catch (error) {
        console.error('加载规则失败:', error)
        ElMessage.error('加载规则失败')
      }
      
      loading.value = false
    }

    // 转换规则为文本格式
    const convertRulesToText = (rules) => {
      if (!rules || rules.length === 0) {
        return defaultRulesTemplate
      }
      
      let text = `// OpenPart 兼容性规则配置\n// 最后更新: ${new Date().toLocaleString('zh-CN')}\n\n`
      
      for (const rule of rules) {
        text += `rule "${rule.name}" {\n`
        
        if (rule.description) {
          text += `  description: "${rule.description}"\n`
        }
        
        text += `  category_a: "${rule.category_a}"\n`
        text += `  category_b: "${rule.category_b}"\n`
        text += `  expression: "${rule.rule_expression}"\n`
        
        if (rule.weight !== undefined && rule.weight !== 100) {
          text += `  weight: ${rule.weight}\n`
        }
        
        if (rule.is_blocking) {
          text += `  blocking: true\n`
        }
        
        text += `}\n\n`
      }
      
      return text
    }

    // 保存规则
    const saveRules = async () => {
      if (!parseResult.success) {
        ElMessage.error('请先修复语法错误')
        return
      }
      
      saving.value = true
      
      try {
        // 获取当前所有规则
        const currentRulesResponse = await compatibilityRules.list({ limit: 1000 })
        const currentRules = currentRulesResponse.data.items || currentRulesResponse.data
        const currentRuleNames = new Set(currentRules.map(r => r.name))
        
        const parsedRules = availableRules.value
        const newRuleNames = new Set(parsedRules.map(r => r.name))
        
        // 创建新规则
        let created = 0
        let updated = 0
        let errors = []
        
        for (const rule of parsedRules) {
          try {
            const ruleData = {
              name: rule.name,
              description: rule.description || '',
              rule_expression: rule.expression,
              category_a: rule.category_a,
              category_b: rule.category_b,
              weight: parseInt(rule.weight) || 100,
              is_blocking: rule.blocking === 'true' || rule.blocking === true
            }
            
            const existingRule = currentRules.find(r => r.name === rule.name)
            
            if (existingRule) {
              await compatibilityRules.update(existingRule.id, ruleData)
              updated++
            } else {
              await compatibilityRules.create(ruleData)
              created++
            }
          } catch (error) {
            errors.push(`规则 "${rule.name}": ${error.response?.data?.detail || error.message}`)
          }
        }
        
        // 删除不再存在的规则
        let deleted = 0
        for (const currentRule of currentRules) {
          if (!newRuleNames.has(currentRule.name)) {
            try {
              await compatibilityRules.delete(currentRule.id)
              deleted++
            } catch (error) {
              errors.push(`删除规则 "${currentRule.name}": ${error.response?.data?.detail || error.message}`)
            }
          }
        }
        
        // 显示结果
        if (errors.length === 0) {
          ElMessage.success(`保存成功! 创建: ${created}, 更新: ${updated}, 删除: ${deleted}`)
          lastSaved.value = `已保存 ${new Date().toLocaleTimeString('zh-CN')}`
        } else {
          ElMessage.warning(`部分保存成功! 创建: ${created}, 更新: ${updated}, 删除: ${deleted}, 错误: ${errors.length}`)
          console.error('保存错误:', errors)
        }
        
        // 更新统计
        const totalRules = Math.max(0, (currentRules.length + created - deleted))
        emit('stats-updated', {
          total_rules: totalRules,
          active_rules: totalRules // 假设新创建的规则都是活跃的
        })
        
      } catch (error) {
        console.error('保存规则失败:', error)
        ElMessage.error('保存规则失败')
      }
      
      saving.value = false
    }

    // 验证所有规则
    const validateAll = async () => {
      if (!hasValidRules.value) {
        ElMessage.warning('没有可验证的规则')
        return
      }
      
      validating.value = true
      validationResult.issues = []
      
      try {
        for (const rule of availableRules.value) {
          if (rule.expression) {
            try {
              const response = await compatibilityRules.validate(rule.expression)
              
              if (!response.data.is_safe) {
                validationResult.issues.push({
                  rule: rule.name,
                  type: 'security',
                  message: `安全问题: ${response.data.security_issues.map(i => i.message).join(', ')}`
                })
              }
            } catch (error) {
              validationResult.issues.push({
                rule: rule.name,
                type: 'error',
                message: error.response?.data?.detail || error.message
              })
            }
          }
        }
        
        validationResult.lastValidated = new Date().toLocaleTimeString('zh-CN')
        
        if (validationResult.issues.length === 0) {
          ElMessage.success('所有规则验证通过')
        } else {
          ElMessage.warning(`发现 ${validationResult.issues.length} 个问题`)
        }
        
      } catch (error) {
        console.error('验证失败:', error)
        ElMessage.error('验证失败')
      }
      
      validating.value = false
    }

    // 执行测试
    const executeTest = async () => {
      if (!testForm.selectedRule || !testForm.testData) {
        ElMessage.error('请选择规则和输入测试数据')
        return
      }
      
      testing.value = true
      testResult.value = null
      
      try {
        // 解析测试数据
        const testData = JSON.parse(testForm.testData)
        
        // 找到规则
        const rule = availableRules.value.find(r => r.name === testForm.selectedRule)
        if (!rule) {
          throw new Error('未找到选择的规则')
        }
        
        // 创建临时规则进行测试
        const tempRule = await compatibilityRules.create({
          name: `temp_test_${Date.now()}`,
          description: 'Temporary rule for testing',
          rule_expression: rule.expression,
          category_a: rule.category_a || 'test',
          category_b: rule.category_b || 'test',
          weight: 100,
          is_blocking: false
        })
        
        try {
          const response = await compatibilityRules.test(tempRule.data.id, { test_data: testData })
          
          testResult.value = {
            success: response.data.success,
            message: response.data.success ? '测试执行成功' : response.data.error_message,
            result: response.data.result,
            execution_time: response.data.execution_time,
            details: response.data
          }
        } finally {
          // 删除临时规则
          await compatibilityRules.delete(tempRule.data.id)
        }
        
      } catch (error) {
        testResult.value = {
          success: false,
          message: error.message || '测试执行失败',
          result: null,
          execution_time: 0
        }
      }
      
      testing.value = false
    }

    // 导入规则
    const importRules = () => {
      fileInput.value.click()
    }

    // 处理文件导入
    const handleFileImport = (event) => {
      const file = event.target.files[0]
      if (!file) return
      
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target.result
        currentContent.value = content
        ElMessage.success('规则文件导入成功')
      }
      reader.readAsText(file)
      
      // 清空文件选择
      event.target.value = ''
    }

    // 导出规则
    const exportRules = () => {
      const content = currentContent.value
      const blob = new Blob([content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      
      const link = document.createElement('a')
      link.href = url
      link.download = `compatibility_rules_${new Date().toISOString().slice(0, 10)}.txt`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      URL.revokeObjectURL(url)
      ElMessage.success('规则文件导出成功')
    }

    // 插入模板
    const insertTemplate = (type) => {
      let template = ''
      
      switch (type) {
        case 'rule':
          template = `
rule "新规则名称" {
  description: "规则描述"
  category_a: "零件类别A"
  category_b: "零件类别B"
  expression: "part_a.property == part_b.property"
  weight: 100
  blocking: false
}

`
          break
        case 'expression':
          template = 'part_a.voltage == part_b.voltage'
          break
      }
      
      // 在当前光标位置插入模板
      const textarea = document.querySelector('.rule-editor textarea')
      if (textarea) {
        const start = textarea.selectionStart
        const end = textarea.selectionEnd
        const text = currentContent.value
        
        currentContent.value = text.substring(0, start) + template + text.substring(end)
        
        // 重新设置光标位置
        nextTick(() => {
          textarea.selectionStart = textarea.selectionEnd = start + template.length
          textarea.focus()
        })
      } else {
        currentContent.value += template
      }
      
      parseRules()
    }

    // 键盘快捷键处理
    const handleKeyDown = (event) => {
      // Ctrl/Cmd + S 保存
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault()
        saveRules()
      }
      
      // Tab 键缩进
      if (event.key === 'Tab') {
        event.preventDefault()
        const textarea = event.target
        const start = textarea.selectionStart
        const end = textarea.selectionEnd
        
        // 插入2个空格
        const text = currentContent.value
        currentContent.value = text.substring(0, start) + '  ' + text.substring(end)
        
        // 重新设置光标位置
        nextTick(() => {
          textarea.selectionStart = textarea.selectionEnd = start + 2
        })
      }
    }
    const loadAvailableFunctions = async () => {
      try {
        const response = await compatibilitySystem.functions()
        const functions = response.data.functions || []
        const help = response.data.help || {}
        
        availableFunctions.value = functions.map(name => ({
          name,
          description: help[name] || '无描述'
        }))
      } catch (error) {
        console.error('加载函数列表失败:', error)
      }
    }

    // 对外暴露的刷新方法
    const refresh = async () => {
      await loadRules()
    }

    // 隐藏的文件输入引用
    const fileInput = ref()

    // 组件挂载
    onMounted(async () => {
      await nextTick()
      await initMonacoEditor()
      await loadRules()
      await loadAvailableFunctions()
    })

    // 组件卸载时清理
    onUnmounted(() => {
      // 清理工作（如果需要）
    })

    return {
      // 响应式数据
      loading,
      saving,
      validating,
      testing,
      editorLoading,
      
      // 编辑器相关
      editorContainer,
      currentContent,
      
      // 解析和验证
      parseResult,
      validationResult,
      cursorPosition,
      lastSaved,
      
      // 测试相关
      showTestDialog,
      testForm,
      testResult,
      availableRules,
      hasValidRules,
      
      // 帮助相关
      showHelpDialog,
      availableFunctions,
      
      // 文件输入
      fileInput,
      
      // 方法
      loadRules,
      saveRules,
      validateAll,
      executeTest,
      importRules,
      exportRules,
      handleFileImport,
      refresh
    }
  }
}
</script>

<style scoped>
.compatibility-rules {
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

.editor-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.simple-editor {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.editor-info {
  font-size: 12px;
  color: #909399;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.rule-editor {
  flex: 1;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
}

.rule-editor :deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  border: none;
  border-radius: 0;
  resize: none;
  padding: 16px;
  background: #fafafa;
  color: #303133;
}

.rule-editor :deep(.el-textarea__inner):focus {
  border: none;
  box-shadow: none;
  background: #ffffff;
}

.editor-wrapper {
  width: 100%;
  height: 100%;
}

.editor-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: white;
  z-index: 1000;
}

.loading-icon {
  font-size: 32px;
  color: #409eff;
  margin-bottom: 12px;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #f8f9fa;
  border-top: 1px solid #e4e7ed;
  border-radius: 0 0 6px 6px;
  font-size: 12px;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-right {
  color: #909399;
}

.cursor-position {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.test-container {
  max-height: 500px;
  overflow-y: auto;
}

.test-result {
  margin-top: 20px;
}

.test-details {
  margin-top: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 14px;
}

.help-content {
  max-height: 600px;
  overflow-y: auto;
}

.help-section {
  padding: 20px 0;
}

.help-section h4 {
  color: #303133;
  margin: 20px 0 10px 0;
  font-size: 16px;
  font-weight: 600;
}

.help-section ul {
  margin: 10px 0;
  padding-left: 20px;
}

.help-section li {
  margin: 8px 0;
  color: #606266;
  line-height: 1.6;
}

.code-example {
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  color: #303133;
  margin: 10px 0;
  overflow-x: auto;
  white-space: pre;
}

.function-item {
  display: flex;
  align-items: center;
  margin: 8px 0;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.function-item code {
  background: #e4e7ed;
  color: #e6a23c;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  margin-right: 12px;
  min-width: 100px;
}

.function-desc {
  color: #606266;
  font-size: 14px;
}

/* Element Plus 组件样式覆盖 */
:deep(.el-button--small) {
  padding: 6px 12px;
  font-size: 12px;
}

:deep(.el-tag--small) {
  height: 22px;
  line-height: 20px;
  padding: 0 8px;
  font-size: 11px;
}

:deep(.el-divider--vertical) {
  height: 20px;
  margin: 0 12px;
}

:deep(.el-dialog__body) {
  padding: 15px 20px;
  max-height: 70vh;
  overflow-y: auto;
}

:deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

:deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 500;
}

:deep(.el-tabs__content) {
  padding: 20px 0;
}

/* 确保编辑器适应容器 */
:deep(.monaco-editor) {
  border-radius: 0;
}

:deep(.monaco-editor .margin) {
  background-color: #fafafa;
}

:deep(.monaco-editor .monaco-editor-background) {
  background-color: #ffffff;
}
</style>