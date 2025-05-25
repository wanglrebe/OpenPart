<!-- portal/src/components/ToastMessage.vue (新组件) -->
<template>
  <teleport to="body">
    <div v-if="visible" class="toast-container">
      <div 
        class="toast-message"
        :class="[type, { 'has-action': !!action }]"
        @click="handleClick"
      >
        <div class="toast-content">
          <svg v-if="type === 'success'" class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <svg v-else-if="type === 'error'" class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          <svg v-else-if="type === 'warning'" class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <svg v-else class="toast-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          
          <span class="toast-text">{{ message }}</span>
        </div>
        
        <button v-if="action" class="toast-action" @click.stop="handleAction">
          {{ action.text }}
        </button>
        
        <button class="toast-close" @click.stop="close">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </teleport>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'ToastMessage',
  props: {
    message: {
      type: String,
      required: true
    },
    type: {
      type: String,
      default: 'info',
      validator: value => ['success', 'error', 'warning', 'info'].includes(value)
    },
    duration: {
      type: Number,
      default: 3000
    },
    action: {
      type: Object,
      default: null
    },
    persistent: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'action'],
  setup(props, { emit }) {
    const visible = ref(false)
    let timer = null
    
    const show = () => {
      visible.value = true
      
      // 如果不是持久化消息且没有操作按钮，自动隐藏
      if (!props.persistent && !props.action && props.duration > 0) {
        timer = setTimeout(() => {
          close()
        }, props.duration)
      }
    }
    
    const close = () => {
      visible.value = false
      if (timer) {
        clearTimeout(timer)
        timer = null
      }
      emit('close')
    }
    
    const handleClick = () => {
      if (!props.action) {
        close()
      }
    }
    
    const handleAction = () => {
      if (props.action && props.action.callback) {
        props.action.callback()
      }
      emit('action')
      close()
    }
    
    onMounted(() => {
      show()
    })
    
    onUnmounted(() => {
      if (timer) {
        clearTimeout(timer)
      }
    })
    
    return {
      visible,
      close,
      handleClick,
      handleAction
    }
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  animation: toastSlideIn 0.3s ease;
}

@keyframes toastSlideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.toast-message {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 300px;
  max-width: 500px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.toast-message:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.toast-message.success {
  border-left: 4px solid #10b981;
  background: color-mix(in srgb, #10b981 3%, var(--bg-card));
}

.toast-message.error {
  border-left: 4px solid #f43f5e;
  background: color-mix(in srgb, #f43f5e 3%, var(--bg-card));
}

.toast-message.warning {
  border-left: 4px solid #f59e0b;
  background: color-mix(in srgb, #f59e0b 3%, var(--bg-card));
}

.toast-message.info {
  border-left: 4px solid var(--primary);
  background: color-mix(in srgb, var(--primary) 3%, var(--bg-card));
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.toast-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.toast-message.success .toast-icon {
  color: #10b981;
}

.toast-message.error .toast-icon {
  color: #f43f5e;
}

.toast-message.warning .toast-icon {
  color: #f59e0b;
}

.toast-message.info .toast-icon {
  color: var(--primary);
}

.toast-text {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.4;
  word-break: break-word;
}

.toast-action {
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 600;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.toast-action:hover {
  background: var(--secondary);
  transform: scale(1.05);
}

.toast-close {
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 50%;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.toast-close:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.toast-close svg {
  width: 14px;
  height: 14px;
}

.toast-message.has-action {
  cursor: default;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .toast-container {
    top: 10px;
    left: 10px;
    right: 10px;
  }
  
  .toast-message {
    min-width: auto;
    max-width: none;
    padding: 14px;
  }
  
  .toast-content {
    gap: 10px;
  }
  
  .toast-text {
    font-size: 13px;
  }
  
  .toast-action {
    font-size: 12px;
    padding: 5px 10px;
  }
}

/* 暗色主题适配 */
[data-theme="dark"] .toast-message {
  backdrop-filter: blur(10px);
}

/* 动画离开效果 */
.toast-message.leaving {
  animation: toastSlideOut 0.3s ease forwards;
}

@keyframes toastSlideOut {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100%);
  }
}
</style>