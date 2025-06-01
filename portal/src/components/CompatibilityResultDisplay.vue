<!-- src/components/CompatibilityResultDisplay.vue -->
<template>
  <div class="compatibility-result-display" v-if="result">
    <!-- 整体兼容性概览 -->
    <div class="result-overview">
      <div class="overview-card">
        <div class="score-display">
          <div class="score-circle">
            <svg class="score-ring" width="120" height="120" viewBox="0 0 120 120">
              <circle
                cx="60"
                cy="60"
                r="50"
                fill="none"
                stroke="var(--bg-secondary)"
                stroke-width="8"
              />
              <circle
                cx="60"
                cy="60"
                r="50"
                fill="none"
                :stroke="getGradeColor(result.overall_compatibility_grade)"
                stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="strokeDashoffset"
                transform="rotate(-90 60 60)"
                class="score-progress"
              />
            </svg>
            <div class="score-content">
              <div class="score-number">{{ result.overall_score }}</div>
              <div class="score-label">分</div>
            </div>
          </div>
          
          <div class="score-info">
            <div class="compatibility-grade">
              <span class="grade-icon">{{ getGradeIcon(result.overall_compatibility_grade) }}</span>
              <span class="grade-text">{{ getGradeText(result.overall_compatibility_grade) }}</span>
            </div>
            <div class="compatibility-status" :class="{ compatible: result.is_overall_compatible }">
              {{ result.is_overall_compatible ? '整体兼容' : '存在兼容性问题' }}
            </div>
            <div v-if="result.execution_time" class="execution-time">
              检查用时: {{ formatExecutionTime(result.execution_time) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 零件对兼容性矩阵 -->
    <div class="compatibility-matrix">
      <div class="matrix-header">
        <h3 class="matrix-title">零件兼容性矩阵</h3>
        <div class="matrix-legend">
          <div class="legend-item" v-for="grade in gradeOptions" :key="grade.value">
            <div class="legend-color" :style="{ backgroundColor: grade.color }"></div>
            <span class="legend-text">{{ grade.text }}</span>
          </div>
        </div>
      </div>
      
      <div class="matrix-table-wrapper">
        <table class="matrix-table">
          <thead>
            <tr>
              <th class="matrix-cell header-cell"></th>
              <th 
                v-for="(part, index) in partsList" 
                :key="`header-${part.id}`"
                class="matrix-cell header-cell"
                :title="part.name"
              >
                {{ getPartShortName(part.name, index + 1) }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(rowPart, rowIndex) in partsList" :key="`row-${rowPart.id}`">
              <th 
                class="matrix-cell header-cell"
                :title="rowPart.name"
              >
                {{ getPartShortName(rowPart.name, rowIndex + 1) }}
              </th>
              <td 
                v-for="(colPart, colIndex) in partsList" 
                :key="`cell-${rowPart.id}-${colPart.id}`"
                class="matrix-cell"
                :class="getMatrixCellClass(rowPart.id, colPart.id, rowIndex, colIndex)"
                :title="getMatrixCellTitle(rowPart.id, colPart.id, rowIndex, colIndex)"
                @click="showCellDetails(rowPart.id, colPart.id, rowIndex, colIndex)"
              >
                <div class="cell-content">
                  <span class="cell-score">{{ getMatrixCellScore(rowPart.id, colPart.id, rowIndex, colIndex) }}</span>
                  <span class="cell-icon">{{ getMatrixCellIcon(rowPart.id, colPart.id, rowIndex, colIndex) }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 警告和建议 -->
    <div v-if="result.warnings?.length > 0 || result.recommendations?.length > 0" class="alerts-section">
      <!-- 警告信息 -->
      <div v-if="result.warnings?.length > 0" class="warnings-card">
        <div class="alert-header">
          <div class="alert-icon warning">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h4 class="alert-title">兼容性警告</h4>
        </div>
        <ul class="alert-list">
          <li v-for="warning in result.warnings" :key="warning" class="alert-item">
            {{ warning }}
          </li>
        </ul>
      </div>

      <!-- 建议信息 -->
      <div v-if="result.recommendations?.length > 0" class="recommendations-card">
        <div class="alert-header">
          <div class="alert-icon recommendation">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h4 class="alert-title">优化建议</h4>
        </div>
        <ul class="alert-list">
          <li v-for="recommendation in result.recommendations" :key="recommendation" class="alert-item">
            {{ recommendation }}
          </li>
        </ul>
      </div>
    </div>

    <!-- 详细规则结果（可折叠） -->
    <div v-if="detailed && result.part_combinations?.length > 0" class="detailed-results">
      <div class="detailed-header">
        <button 
          @click="toggleDetailedView"
          class="toggle-detailed-btn"
          :class="{ expanded: showDetailed }"
        >
          <svg class="toggle-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
          <span>详细规则结果</span>
          <span class="toggle-count">({{ result.part_combinations.length }} 个组合)</span>
        </button>
      </div>
      
      <div v-if="showDetailed" class="detailed-content">
        <div 
          v-for="combination in result.part_combinations" 
          :key="`${combination.part_a_id}-${combination.part_b_id}`"
          class="combination-card"
        >
          <div class="combination-header">
            <div class="combination-parts">
              <span class="part-name">{{ combination.part_a_name }}</span>
              <span class="vs-separator">↔</span>
              <span class="part-name">{{ combination.part_b_name }}</span>
            </div>
            <div class="combination-score">
              <span class="score-value" :style="{ color: getGradeColor(combination.compatibility_grade) }">
                {{ combination.compatibility_score }}分
              </span>
              <span class="score-grade">{{ getGradeText(combination.compatibility_grade) }}</span>
            </div>
          </div>
          
          <!-- 规则结果 -->
          <div v-if="combination.rule_results?.length > 0" class="rule-results">
            <h5 class="rules-title">规则检查结果:</h5>
            <div class="rules-grid">
              <div 
                v-for="ruleResult in combination.rule_results" 
                :key="ruleResult.rule_id"
                class="rule-item"
                :class="{ passed: ruleResult.passed, failed: !ruleResult.passed, blocking: ruleResult.is_blocking }"
              >
                <div class="rule-header">
                  <div class="rule-status">
                    <svg v-if="ruleResult.passed" class="status-icon passed" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <svg v-else class="status-icon failed" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                  <span class="rule-name">{{ ruleResult.rule_name }}</span>
                  <span v-if="ruleResult.is_blocking" class="blocking-badge">必需</span>
                </div>
                <div class="rule-details">
                  <span class="rule-score">{{ ruleResult.score.toFixed(1) }}分 (权重: {{ ruleResult.weight }})</span>
                  <span v-if="ruleResult.execution_time" class="rule-time">{{ (ruleResult.execution_time * 1000).toFixed(1) }}ms</span>
                </div>
                <div v-if="ruleResult.error_message" class="rule-error">
                  错误: {{ ruleResult.error_message }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- 经验数据 -->
          <div v-if="combination.experience_data" class="experience-data">
            <h5 class="experience-title">用户经验数据:</h5>
            <div class="experience-info">
              <span class="experience-status">状态: {{ formatExperienceStatus(combination.experience_data.compatibility_status) }}</span>
              <span v-if="combination.experience_data.source" class="experience-source">来源: {{ formatExperienceSource(combination.experience_data.source) }}</span>
              <span v-if="combination.experience_data.verification_status" class="experience-verification">验证: {{ formatVerificationStatus(combination.experience_data.verification_status) }}</span>
            </div>
            <div v-if="combination.experience_data.notes" class="experience-notes">
              备注: {{ combination.experience_data.notes }}
            </div>
          </div>
          
          <!-- 组合警告 -->
          <div v-if="combination.warnings?.length > 0" class="combination-warnings">
            <h5 class="warnings-title">注意事项:</h5>
            <ul class="warnings-list">
              <li v-for="warning in combination.warnings" :key="warning" class="warning-item">
                {{ warning }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 导出功能 -->
    <div class="export-section">
      <button @click="exportReport" class="export-btn">
        <svg class="export-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        导出兼容性报告
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { compatibilityHelpers } from '../utils/api'

export default {
  name: 'CompatibilityResultDisplay',
  props: {
    result: {
      type: Object,
      required: true
    },
    detailed: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const showDetailed = ref(false)
    
    // 圆环进度计算
    const circumference = 2 * Math.PI * 50 // r=50
    const strokeDashoffset = computed(() => {
      const progress = props.result.overall_score / 100
      return circumference * (1 - progress)
    })
    
    // 零件列表（从结果中提取）
    const partsList = computed(() => {
      if (!props.result.part_combinations?.length) return []
      
      const partsMap = new Map()
      props.result.part_combinations.forEach(combo => {
        if (!partsMap.has(combo.part_a_id)) {
          partsMap.set(combo.part_a_id, {
            id: combo.part_a_id,
            name: combo.part_a_name
          })
        }
        if (!partsMap.has(combo.part_b_id)) {
          partsMap.set(combo.part_b_id, {
            id: combo.part_b_id,
            name: combo.part_b_name
          })
        }
      })
      
      return Array.from(partsMap.values())
    })
    
    // 等级选项
    const gradeOptions = [
      { value: 'official_support', text: '官方支持', color: '#67C23A' },
      { value: 'unofficial_support', text: '社区验证', color: '#409EFF' },
      { value: 'theoretical', text: '理论兼容', color: '#E6A23C' },
      { value: 'incompatible', text: '不兼容', color: '#F56C6C' }
    ]
    
    // 工具方法
    const getGradeColor = (grade) => compatibilityHelpers.getGradeColor(grade)
    const getGradeIcon = (grade) => compatibilityHelpers.getGradeIcon(grade)
    
    const getGradeText = (grade) => {
      const gradeInfo = compatibilityHelpers.formatGrade(grade)
      return gradeInfo.text
    }
    
    const formatExecutionTime = (timeInSeconds) => {
      return compatibilityHelpers.formatExecutionTime(timeInSeconds)
    }
    
    const getPartShortName = (name, index) => {
      if (name.length <= 10) return name
      return `零件${index}`
    }
    
    // 矩阵相关方法
    const findCombination = (partAId, partBId) => {
      return props.result.part_combinations?.find(combo => 
        (combo.part_a_id === partAId && combo.part_b_id === partBId) ||
        (combo.part_a_id === partBId && combo.part_b_id === partAId)
      )
    }
    
    const getMatrixCellScore = (partAId, partBId, rowIndex, colIndex) => {
      if (rowIndex === colIndex) return '-'
      const combination = findCombination(partAId, partBId)
      return combination ? combination.compatibility_score : 'N/A'
    }
    
    const getMatrixCellIcon = (partAId, partBId, rowIndex, colIndex) => {
      if (rowIndex === colIndex) return ''
      const combination = findCombination(partAId, partBId)
      return combination ? compatibilityHelpers.getGradeIcon(combination.compatibility_grade) : '?'
    }
    
    const getMatrixCellClass = (partAId, partBId, rowIndex, colIndex) => {
      if (rowIndex === colIndex) return 'self-cell'
      
      const combination = findCombination(partAId, partBId)
      if (!combination) return 'unknown-cell'
      
      return `grade-${combination.compatibility_grade}`
    }
    
    const getMatrixCellTitle = (partAId, partBId, rowIndex, colIndex) => {
      if (rowIndex === colIndex) return '同一零件'
      
      const combination = findCombination(partAId, partBId)
      if (!combination) return '未检查'
      
      const gradeInfo = compatibilityHelpers.formatGrade(combination.compatibility_grade)
      return `兼容性: ${combination.compatibility_score}分 - ${gradeInfo.text}`
    }
    
    const showCellDetails = (partAId, partBId, rowIndex, colIndex) => {
      if (rowIndex === colIndex) return
      
      const combination = findCombination(partAId, partBId)
      if (combination) {
        // 可以实现点击显示详细信息的功能
        console.log('显示详细信息:', combination)
      }
    }
    
    // 格式化方法
    const formatExperienceStatus = (status) => {
      const statusMap = {
        'compatible': '兼容',
        'incompatible': '不兼容',
        'conditional': '有条件兼容'
      }
      return statusMap[status] || status
    }
    
    const formatExperienceSource = (source) => {
      const sourceMap = {
        'official': '官方',
        'admin': '管理员',
        'user_contribution': '用户贡献'
      }
      return sourceMap[source] || source
    }
    
    const formatVerificationStatus = (status) => {
      const statusMap = {
        'verified': '已验证',
        'pending': '待验证',
        'disputed': '存在争议'
      }
      return statusMap[status] || status
    }
    
    // 切换详细视图
    const toggleDetailedView = () => {
      showDetailed.value = !showDetailed.value
    }
    
    // 导出报告
    const exportReport = () => {
      const report = compatibilityHelpers.createReport(props.result, partsList.value)
      
      const reportText = `# ${report.meta.title}

## 基本信息
- 生成时间: ${report.meta.generateTime}
- 零件数量: ${report.meta.partCount}
- 检查用时: ${report.meta.executionTime}

## 检查零件
${report.parts.map((part, index) => `${index + 1}. ${part.name} (${part.category})`).join('\n')}

## 兼容性总结
- 整体评分: ${report.summary.overallScore}分
- 兼容等级: ${report.summary.overallGrade.text}
- 兼容状态: ${report.summary.isCompatible ? '兼容' : '不兼容'}

## 详细结果
${report.details.map(detail => `
### ${detail.partA} ↔ ${detail.partB}
- 评分: ${detail.score}分
- 等级: ${detail.grade.text}
- 状态: ${detail.compatible ? '兼容' : '不兼容'}
${detail.warnings.length > 0 ? `- 警告: ${detail.warnings.join(', ')}` : ''}
`).join('\n')}

## 问题和建议
${report.issues.length > 0 ? `### 发现的问题\n${report.issues.map(issue => `- ${issue}`).join('\n')}` : ''}

${report.recommendations.length > 0 ? `### 优化建议\n${report.recommendations.map(rec => `- ${rec}`).join('\n')}` : ''}

---
由 OpenPart 兼容性检查系统生成
`
      
      const blob = new Blob([reportText], { type: 'text/plain;charset=utf-8' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `兼容性报告_${new Date().toISOString().split('T')[0]}.txt`
      link.click()
      URL.revokeObjectURL(link.href)
    }
    
    return {
      showDetailed,
      circumference,
      strokeDashoffset,
      partsList,
      gradeOptions,
      getGradeColor,
      getGradeIcon,
      getGradeText,
      formatExecutionTime,
      getPartShortName,
      getMatrixCellScore,
      getMatrixCellIcon,
      getMatrixCellClass,
      getMatrixCellTitle,
      showCellDetails,
      formatExperienceStatus,
      formatExperienceSource,
      formatVerificationStatus,
      toggleDetailedView,
      exportReport
    }
  }
}
</script>

<style scoped>
.compatibility-result-display {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 整体概览 */
.result-overview {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
}

.overview-card {
  display: flex;
  justify-content: center;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 32px;
}

.score-circle {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-ring {
  transform: rotate(-90deg);
}

.score-progress {
  transition: stroke-dashoffset 1s ease-in-out;
}

.score-content {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-number {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.score-label {
  font-size: 14px;
  color: var(--text-muted);
  margin-top: 2px;
}

.score-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.compatibility-grade {
  display: flex;
  align-items: center;
  gap: 8px;
}

.grade-icon {
  font-size: 20px;
}

.grade-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.compatibility-status {
  font-size: 16px;
  font-weight: 500;
  color: #f43f5e;
}

.compatibility-status.compatible {
  color: #10b981;
}

.execution-time {
  font-size: 14px;
  color: var(--text-muted);
}

/* 兼容性矩阵 */
.compatibility-matrix {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
}

.matrix-header {
  margin-bottom: 20px;
}

.matrix-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.matrix-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-text {
  font-size: 13px;
  color: var(--text-secondary);
}

.matrix-table-wrapper {
  overflow-x: auto;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.matrix-cell {
  padding: 8px;
  text-align: center;
  border: 1px solid var(--border-color);
  min-width: 60px;
}

.header-cell {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
  position: sticky;
  top: 0;
  z-index: 1;
}

.matrix-cell:first-child {
  position: sticky;
  left: 0;
  background: var(--bg-secondary);
  z-index: 2;
}

.cell-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.cell-score {
  font-size: 11px;
  font-weight: 500;
}

.cell-icon {
  font-size: 12px;
}

.self-cell {
  background: var(--bg-primary);
  color: var(--text-muted);
}

.unknown-cell {
  background: var(--bg-secondary);
  color: var(--text-muted);
}

.grade-official_support {
  background: color-mix(in srgb, #67C23A 15%, transparent);
  color: #67C23A;
  cursor: pointer;
}

.grade-unofficial_support {
  background: color-mix(in srgb, #409EFF 15%, transparent);
  color: #409EFF;
  cursor: pointer;
}

.grade-theoretical {
  background: color-mix(in srgb, #E6A23C 15%, transparent);
  color: #E6A23C;
  cursor: pointer;
}

.grade-incompatible {
  background: color-mix(in srgb, #F56C6C 15%, transparent);
  color: #F56C6C;
  cursor: pointer;
}

.matrix-cell:hover.grade-official_support,
.matrix-cell:hover.grade-unofficial_support,
.matrix-cell:hover.grade-theoretical,
.matrix-cell:hover.grade-incompatible {
  transform: scale(1.05);
  transition: transform 0.2s ease;
}

/* 警告和建议 */
.alerts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.warnings-card,
.recommendations-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.warnings-card {
  border-left: 4px solid #f59e0b;
}

.recommendations-card {
  border-left: 4px solid #10b981;
}

.alert-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.alert-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.alert-icon.warning {
  color: #f59e0b;
}

.alert-icon.recommendation {
  color: #10b981;
}

.alert-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.alert-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.alert-item {
  padding: 8px 0;
  color: var(--text-secondary);
  line-height: 1.5;
  border-bottom: 1px solid var(--border-color);
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-item::before {
  content: '•';
  color: var(--primary);
  font-weight: bold;
  display: inline-block;
  width: 1em;
}

/* 详细结果 */
.detailed-results {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.detailed-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.toggle-detailed-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 0;
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s ease;
}

.toggle-detailed-btn:hover {
  color: var(--primary);
}

.toggle-icon {
  width: 20px;
  height: 20px;
  transition: transform 0.2s ease;
}

.toggle-detailed-btn.expanded .toggle-icon {
  transform: rotate(180deg);
}

.toggle-count {
  font-size: 14px;
  font-weight: 400;
  color: var(--text-muted);
}

.detailed-content {
  padding: 20px;
}

.combination-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.combination-card:last-child {
  margin-bottom: 0;
}

.combination-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.combination-parts {
  display: flex;
  align-items: center;
  gap: 12px;
}

.part-name {
  font-weight: 500;
  color: var(--text-primary);
}

.vs-separator {
  color: var(--text-muted);
  font-size: 16px;
}

.combination-score {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.score-value {
  font-size: 18px;
  font-weight: 600;
}

.score-grade {
  font-size: 12px;
  color: var(--text-muted);
}

/* 规则结果 */
.rule-results {
  margin-bottom: 16px;
}

.rules-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.rules-grid {
  display: grid;
  gap: 8px;
}

.rule-item {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 12px;
}

.rule-item.passed {
  border-left: 3px solid #10b981;
}

.rule-item.failed {
  border-left: 3px solid #f43f5e;
}

.rule-item.blocking {
  background: color-mix(in srgb, var(--accent) 5%, var(--bg-card));
}

.rule-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.status-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.status-icon.passed {
  color: #10b981;
}

.status-icon.failed {
  color: #f43f5e;
}

.rule-name {
  font-weight: 500;
  color: var(--text-primary);
  flex: 1;
}

.blocking-badge {
  background: var(--accent);
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}

.rule-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--text-muted);
}

.rule-error {
  margin-top: 6px;
  padding: 6px 8px;
  background: color-mix(in srgb, #f43f5e 10%, transparent);
  border-radius: 4px;
  font-size: 12px;
  color: #f43f5e;
}

/* 经验数据 */
.experience-data {
  margin-bottom: 16px;
}

.experience-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.experience-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 8px;
}

.experience-status,
.experience-source,
.experience-verification {
  font-size: 12px;
  color: var(--text-secondary);
}

.experience-notes {
  font-size: 13px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 8px;
  border-radius: 4px;
  font-style: italic;
}

/* 组合警告 */
.combination-warnings {
  margin-bottom: 16px;
}

.warnings-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.warnings-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.warning-item {
  padding: 4px 0;
  font-size: 13px;
  color: #f59e0b;
  line-height: 1.4;
}

.warning-item::before {
  content: '⚠️';
  margin-right: 6px;
}

/* 导出功能 */
.export-section {
  display: flex;
  justify-content: center;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 12px;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.export-btn:hover {
  background: var(--secondary);
  transform: translateY(-1px);
}

.export-icon {
  width: 18px;
  height: 18px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .score-display {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .matrix-table {
    font-size: 12px;
  }
  
  .matrix-cell {
    min-width: 50px;
    padding: 6px;
  }
  
  .alerts-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .compatibility-result-display {
    gap: 16px;
  }
  
  .result-overview,
  .compatibility-matrix,
  .detailed-results {
    padding: 16px;
  }
  
  .score-display {
    gap: 16px;
  }
  
  .score-circle svg {
    width: 100px;
    height: 100px;
  }
  
  .score-number {
    font-size: 24px;
  }
  
  .combination-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .combination-score {
    align-items: flex-start;
  }
  
  .matrix-table {
    font-size: 11px;
  }
  
  .matrix-cell {
    min-width: 40px;
    padding: 4px;
  }
  
  .detailed-content {
    padding: 16px;
  }
  
  .warnings-card,
  .recommendations-card {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .combination-parts {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
  
  .vs-separator {
    transform: rotate(90deg);
  }
  
  .matrix-legend {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .legend-item {
    justify-content: center;
  }
}
</style>