<template>
  <div class="login-container">
    <div class="login-card">
      <h2>OpenPart 管理后台</h2>
      <p class="subtitle">请使用管理员账户登录</p>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            size="large"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-tips">
        <p>默认账户：admin / admin123</p>
        <p class="warning">⚠️ 请在生产环境中更改默认密码</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authAPI } from '../utils/api'
import { auth } from '../utils/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const loginFormRef = ref()
    const loading = ref(false)
    
    const loginForm = reactive({
      username: 'admin',
      password: 'admin123'
    })
    
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少6位', trigger: 'blur' }
      ]
    }
    
    const handleLogin = async () => {
      try {
        // 表单验证
        const valid = await loginFormRef.value.validate()
        if (!valid) return
        
        loading.value = true
        
        // 发送登录请求
        const response = await authAPI.login({
          username: loginForm.username,
          password: loginForm.password
        })
        
        const { access_token } = response.data
        
        // 保存token
        auth.setToken(access_token)
        
        // 获取用户信息
        const userResponse = await authAPI.getCurrentUser()
        auth.setUser(userResponse.data)
        
        ElMessage.success('登录成功')
        
        // 跳转到仪表板
        router.push('/dashboard')
        
      } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error('登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
    
    return {
      loginFormRef,
      loginForm,
      rules,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 400px;
  max-width: 90vw;
}

.login-card h2 {
  text-align: center;
  color: #409EFF;
  margin-bottom: 10px;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.login-form {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
}

.login-tips {
  text-align: center;
  color: #999;
  font-size: 14px;
}

.login-tips p {
  margin: 5px 0;
}

.warning {
  color: #E6A23C !important;
  font-weight: bold;
}
</style>