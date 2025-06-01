// src/utils/compatibilityManager.js
/**
 * 兼容性检查管理器
 * 仿照 comparisonManager 设计，管理待检查零件列表
 */

class CompatibilityCheckManager {
  constructor() {
    this.storageKey = 'openpart_compatibility_check'
    this.maxItems = 10 // 最多10个零件
  }
  
  /**
   * 获取兼容性检查列表
   * @returns {Array} 零件列表
   */
  getCheckList() {
    const stored = localStorage.getItem(this.storageKey)
    try {
      const parsed = stored ? JSON.parse(stored) : []
      // 确保返回的是数组
      return Array.isArray(parsed) ? parsed : []
    } catch (error) {
      console.error('解析兼容性检查列表失败:', error)
      // 清除损坏的数据
      localStorage.removeItem(this.storageKey)
      return []
    }
  }
  
  /**
   * 添加零件到兼容性检查列表
   * @param {Object} part - 零件对象
   * @returns {Object} 操作结果
   */
  addToCheck(part) {
    let list = this.getCheckList()
    
    // 检查是否已存在（严格检查ID类型）
    const partId = parseInt(part.id)
    const existingIndex = list.findIndex(p => parseInt(p.id) === partId)
    
    if (existingIndex !== -1) {
      return { success: false, message: '该零件已在兼容性检查列表中' }
    }
    
    // 检查数量限制
    if (list.length >= this.maxItems) {
      return { success: false, message: `最多只能检查${this.maxItems}个零件的兼容性` }
    }
    
    // 添加新零件
    const newItem = {
      id: partId,
      name: part.name,
      category: part.category,
      image_url: part.image_url,
      addedAt: Date.now()
    }
    
    list.push(newItem)
    
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(list))
      // 触发存储事件，通知其他组件更新
      this.dispatchStorageEvent(list)
    } catch (error) {
      console.error('保存兼容性检查列表失败:', error)
      return { success: false, message: '保存失败，请重试' }
    }
    
    return { success: true, message: '已添加到兼容性检查列表', count: list.length }
  }
  
  /**
   * 从兼容性检查列表中移除零件
   * @param {number} partId - 零件ID
   * @returns {Object} 操作结果
   */
  removeFromCheck(partId) {
    let list = this.getCheckList()
    const targetId = parseInt(partId)
    
    // 过滤掉要移除的零件
    const newList = list.filter(p => parseInt(p.id) !== targetId)
    
    if (newList.length === list.length) {
      return { success: false, message: '零件不在兼容性检查列表中' }
    }
    
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(newList))
      // 触发存储事件
      this.dispatchStorageEvent(newList)
    } catch (error) {
      console.error('保存兼容性检查列表失败:', error)
      return { success: false, message: '移除失败，请重试' }
    }
    
    return { success: true, message: '已从兼容性检查列表移除', count: newList.length }
  }
  
  /**
   * 清空兼容性检查列表
   * @returns {Object} 操作结果
   */
  clearCheckList() {
    try {
      localStorage.removeItem(this.storageKey)
      // 触发存储事件
      this.dispatchStorageEvent([])
    } catch (error) {
      console.error('清空兼容性检查列表失败:', error)
      return { success: false, message: '清空失败，请重试' }
    }
    
    return { success: true, count: 0 }
  }
  
  /**
   * 批量添加零件到检查列表
   * @param {Array} parts - 零件数组
   * @returns {Object} 操作结果
   */
  addMultipleToCheck(parts) {
    if (!Array.isArray(parts) || parts.length === 0) {
      return { success: false, message: '请提供有效的零件列表' }
    }
    
    let list = this.getCheckList()
    let successCount = 0
    let skippedCount = 0
    let errors = []
    
    for (const part of parts) {
      // 检查是否已存在
      const partId = parseInt(part.id)
      if (list.some(p => parseInt(p.id) === partId)) {
        skippedCount++
        continue
      }
      
      // 检查数量限制
      if (list.length >= this.maxItems) {
        errors.push(`达到最大限制${this.maxItems}个零件，剩余零件未添加`)
        break
      }
      
      // 添加零件
      const newItem = {
        id: partId,
        name: part.name,
        category: part.category,
        image_url: part.image_url,
        addedAt: Date.now()
      }
      
      list.push(newItem)
      successCount++
    }
    
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(list))
      this.dispatchStorageEvent(list)
    } catch (error) {
      console.error('批量保存失败:', error)
      return { success: false, message: '保存失败，请重试' }
    }
    
    return {
      success: successCount > 0,
      message: `成功添加${successCount}个零件${skippedCount > 0 ? `，跳过${skippedCount}个已存在的零件` : ''}`,
      count: list.length,
      details: {
        added: successCount,
        skipped: skippedCount,
        errors: errors
      }
    }
  }
  
  /**
   * 检查零件是否在检查列表中
   * @param {number} partId - 零件ID
   * @returns {boolean}
   */
  isInCheck(partId) {
    const list = this.getCheckList()
    const targetId = parseInt(partId)
    return list.some(p => parseInt(p.id) === targetId)
  }
  
  /**
   * 获取检查列表中的零件数量
   * @returns {number}
   */
  getCheckCount() {
    return this.getCheckList().length
  }
  
  /**
   * 获取兼容性检查URL
   * @returns {string|null} 检查URL或null（如果零件不足）
   */
  getCheckUrl() {
    const list = this.getCheckList()
    if (list.length < 2) return null
    
    const ids = list.map(p => p.id).join(',')
    return `/compatibility?parts=${ids}`
  }
  
  /**
   * 切换零件的检查状态
   * @param {Object} part - 零件对象
   * @returns {Object} 操作结果
   */
  toggleCheck(part) {
    const partId = parseInt(part.id)
    
    if (this.isInCheck(partId)) {
      const result = this.removeFromCheck(partId)
      return {
        ...result,
        message: result.success ? '已从兼容性检查列表移除' : result.message,
        action: 'remove'
      }
    } else {
      const result = this.addToCheck(part)
      return {
        ...result,
        message: result.success ? '已添加到兼容性检查列表' : result.message,
        action: 'add'
      }
    }
  }
  
  /**
   * 获取检查列表摘要信息
   * @returns {Object} 摘要信息
   */
  getCheckSummary() {
    const list = this.getCheckList()
    const categories = [...new Set(list.map(p => p.category).filter(Boolean))]
    
    return {
      count: list.length,
      canCheck: list.length >= 2,
      maxReached: list.length >= this.maxItems,
      categories: categories,
      partIds: list.map(p => p.id)
    }
  }
  
  /**
   * 触发存储事件通知其他组件
   * @private
   */
  dispatchStorageEvent(newList) {
    window.dispatchEvent(new StorageEvent('storage', {
      key: this.storageKey,
      newValue: JSON.stringify(newList),
      storageArea: localStorage
    }))
  }
  
  /**
   * 导出检查列表
   * @returns {Object} 操作结果
   */
  exportCheckList() {
    const list = this.getCheckList()
    
    if (list.length === 0) {
      return { success: false, message: '检查列表为空，无法导出' }
    }
    
    try {
      const dataStr = JSON.stringify(list, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      
      const link = document.createElement('a')
      link.href = URL.createObjectURL(dataBlob)
      link.download = `兼容性检查列表_${new Date().toISOString().split('T')[0]}.json`
      link.click()
      
      URL.revokeObjectURL(link.href)
      
      return { success: true, message: '检查列表已导出' }
    } catch (error) {
      console.error('导出失败:', error)
      return { success: false, message: '导出失败，请重试' }
    }
  }
  
  /**
   * 导入检查列表
   * @param {File} file - 导入的文件
   * @returns {Promise<Object>} 操作结果
   */
  async importCheckList(file) {
    try {
      const text = await file.text()
      const importedList = JSON.parse(text)
      
      if (!Array.isArray(importedList)) {
        throw new Error('无效的检查列表格式')
      }
      
      // 验证数据格式
      for (const item of importedList) {
        if (!item.id || !item.name) {
          throw new Error('检查列表数据格式不正确')
        }
      }
      
      // 合并现有列表（去重）
      const currentList = this.getCheckList()
      const currentIds = new Set(currentList.map(p => p.id))
      
      const newItems = importedList.filter(item => !currentIds.has(item.id))
      const mergedList = [...currentList, ...newItems]
      
      // 检查数量限制
      if (mergedList.length > this.maxItems) {
        throw new Error(`导入后将超过检查列表上限(${this.maxItems}个)`)
      }
      
      localStorage.setItem(this.storageKey, JSON.stringify(mergedList))
      this.dispatchStorageEvent(mergedList)
      
      return { 
        success: true, 
        message: `成功导入${newItems.length}个新零件`, 
        count: mergedList.length 
      }
      
    } catch (error) {
      return { success: false, message: error.message }
    }
  }
}

// 导出单例实例
export const compatibilityCheckManager = new CompatibilityCheckManager()

// 导出类（用于测试或特殊用途）
export { CompatibilityCheckManager }