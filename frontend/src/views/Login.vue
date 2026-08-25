<template>
  <div class="login-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="50" color="#409EFF" class="logo-icon"><Code /></el-icon>
          <h2>{{ isLogin ? '开启你的编程之旅' : '加入 ProgLearn' }}</h2>
          <p>{{ isLogin ? '继续你的编程学习之路' : '今天就开始你的编程之旅' }}</p>
        </div>
      </template>

      <el-tabs v-model="activeTab" stretch>
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            label-position="left"
            label-width="84px"
            size="large"
          >
            <el-form-item prop="username" label="用户名">
              <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="User" />
            </el-form-item>
            
            <el-form-item prop="password" label="密码">
              <el-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="请输入密码" 
                show-password 
                prefix-icon="Lock" 
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <el-form-item prop="captcha" label="验证码">
              <div class="captcha-container">
                <el-input v-model="loginForm.captcha" placeholder="请输入验证码" style="flex: 1;" />
                <div class="captcha-code" @click="generateCaptcha">{{ captchaText }}</div>
              </div>
            </el-form-item>

            <div class="flex justify-between items-center mb-4">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <el-link type="primary" @click="showForgotPassword">忘记密码?</el-link>
            </div>

            <el-form-item label-width="0">
              <div class="form-actions">
                <el-button type="primary" class="action-button" :loading="loading" @click="handleLogin(loginFormRef)">
                  登录
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            label-position="left"
            label-width="84px"
            size="large"
          >
            <el-form-item prop="email" label="邮箱">
              <el-input v-model="registerForm.email" placeholder="请输入邮箱" prefix-icon="Message" />
            </el-form-item>
            
            <el-form-item prop="username" label="用户名">
              <el-input v-model="registerForm.username" placeholder="请输入用户名" prefix-icon="User" />
            </el-form-item>
            
            <el-form-item prop="password" label="密码">
              <el-input 
                v-model="registerForm.password" 
                type="password" 
                placeholder="请输入密码" 
                show-password 
                prefix-icon="Lock" 
              />
            </el-form-item>

            <el-form-item prop="confirmPassword" label="确认密码">
              <el-input 
                v-model="registerForm.confirmPassword" 
                type="password" 
                placeholder="请再次输入密码" 
                show-password 
                prefix-icon="Lock" 
              />
            </el-form-item>

            <el-form-item prop="captcha" label="验证码">
              <div class="captcha-container">
                <el-input v-model="registerForm.captcha" placeholder="请输入验证码" style="flex: 1;" />
                <div class="captcha-code" @click="generateCaptcha">{{ captchaText }}</div>
              </div>
            </el-form-item>
        
            <div class="mb-4">
              <el-checkbox v-model="agreeTerms">
                我同意 <el-link type="primary" @click.stop="openTerms">服务条款</el-link>
              </el-checkbox>
            </div>

            <el-form-item label-width="0">
              <div class="form-actions">
                <el-button type="primary" class="action-button" :loading="loading" @click="handleRegister(registerFormRef)">
                  注册
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="forgotPasswordDialog" title="忘记密码" width="400px">
      <div class="forgot-tip">请联系管理员重置为默认密码</div>
      <template #footer>
        <el-button type="primary" @click="handleForgotPassword">我知道了</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showTermsDialog" title="服务条款" width="600px">
      <div class="terms-content">
        <h3>1. 服务条款的确认和接纳</h3>
        <p>ProgLearn（以下简称"本站"）提供的服务将完全按照其发布的章程、服务条款和操作规则严格执行。用户在申请注册流程中点击同意本协议之前，应当认真阅读本协议。请您务必审慎阅读、充分理解各条款内容。</p>
        
        <h3>2. 用户账号</h3>
        <p>用户注册成功后，将拥有一个账号及密码，用户有责任维护其账号和密码的安全。用户对利用该账号和密码所进行的一切活动负全部责任。</p>
        
        <h3>3. 用户行为</h3>
        <p>用户在使用本站服务时，必须遵守中华人民共和国相关法律法规，不得利用本站服务从事违法违规活动，不得侵犯本站及其他第三方的合法权益。</p>
        
        <h3>4. 知识产权</h3>
        <p>本站提供的网络服务中包含的任何文本、图片、图形、音频和/或视频资料均受版权、商标和/或其它财产所有权法律的保护。</p>
        
        <h3>5. 免责声明</h3>
        <p>本站不保证服务一定能满足用户的要求，也不保证服务不会中断，对服务的及时性、安全性、准确性也都不作保证。</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="acceptTerms">我已阅读并同意</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'


const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref()
const registerFormRef = ref()

const activeTab = ref('login')
const loading = ref(false)
const rememberMe = ref(false)
const agreeTerms = ref(false)
const captchaText = ref('')
const forgotPasswordDialog = ref(false)
const showTermsDialog = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  captcha: ''
})

const registerForm = reactive({
  email: '',
  username: '',
  password: '',
  confirmPassword: '',
  captcha: ''
})

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const validateCaptcha = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入验证码'))
  } else if (value.toLowerCase() !== captchaText.value.toLowerCase()) {
    callback(new Error('验证码错误'))
    generateCaptcha()
  } else {
    callback()
  }
}

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度应为 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 个字符', trigger: 'blur' }
  ],
  captcha: [
    { validator: validateCaptcha, trigger: 'blur' }
  ]
}

const registerRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度应为 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validatePass2, trigger: 'blur' }
  ],
  captcha: [
    { validator: validateCaptcha, trigger: 'blur' }
  ]
}

const generateCaptcha = () => {
  const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  captchaText.value = ''
  for (let i = 0; i < 4; i++) {
    captchaText.value += chars.charAt(Math.floor(Math.random() * chars.length))
  }
}

onMounted(() => {
  generateCaptcha()
})

const showForgotPassword = () => {
  forgotPasswordDialog.value = true
}

const handleForgotPassword = () => {
  forgotPasswordDialog.value = false
}

const openTerms = () => {
  showTermsDialog.value = true
}

const acceptTerms = () => {
  agreeTerms.value = true
  showTermsDialog.value = false
}

const handleLogin = async (formEl) => {
  if (!formEl) return
  
  await formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.login({ username: loginForm.username, password: loginForm.password })
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error) {
        console.error(error)
        ElMessage.error(error.response?.data?.detail === 'Incorrect username or password' ? '用户名或密码错误' : (error.response?.data?.detail || '登录失败'))
        generateCaptcha()
      } finally {
        loading.value = false
      }
    }
  })
}

const handleRegister = async (formEl) => {
  if (!formEl) return
  
  if (!agreeTerms.value) {
    ElMessage.warning('请先同意服务条款')
    return
  }

  await formEl.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.register(registerForm)
        ElMessage.success('注册成功，请登录')
        activeTab.value = 'login'
        formEl.resetFields()
        generateCaptcha()
      } catch (error) {
        ElMessage.error(error?.response?.data?.detail || '注册失败，请稍后重试')
        generateCaptcha()
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: 24px 16px 32px;
  position: relative;
  overflow: hidden;
}

.box-card {
  width: 480px;
  max-width: 100%;
  border-radius: 20px;
  box-shadow: 0 24px 70px rgba(24, 44, 94, 0.18);
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.box-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 28px 80px rgba(24, 44, 94, 0.22);
}

.card-header {
  text-align: center;
  padding: 10px 0 6px;
}

.logo-icon {
  margin-bottom: 6px;
}

.card-header h2 {
  margin: 8px 0 6px;
  color: #1f2a44;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 0.2px;
}

.card-header p {
  margin: 0;
  color: #6b778c;
  font-size: 14px;
}

.captcha-container {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.captcha-code {
  padding: 0 18px;
  background: linear-gradient(135deg, #5b8cff 0%, #7b6cf6 100%);
  color: #fff;
  font-weight: bold;
  font-size: 18px;
  letter-spacing: 3px;
  border-radius: 10px;
  cursor: pointer;
  user-select: none;
  min-width: 116px;
  text-align: center;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12px 24px rgba(91, 140, 255, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.captcha-code:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 28px rgba(91, 140, 255, 0.35);
}

.forgot-tip {
  text-align: center;
  color: #6b7280;
  padding: 12px 0 4px;
}

.w-full {
  width: 100%;
}

.form-actions {
  width: 100%;
  display: flex;
  justify-content: center;
}

.action-button {
  width: 220px;
}

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.items-center {
  align-items: center;
}

.mb-4 {
  margin-bottom: 1rem;
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: #eef2f6;
}

:deep(.el-card__header) {
  border-bottom: none;
  padding: 22px 26px 8px;
}

:deep(.el-card__body) {
  padding: 12px 26px 28px;
}

:deep(.el-tabs__nav) {
  gap: 12px;
}

:deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 600;
  color: #6b7280;
}

:deep(.el-tabs__item.is-active) {
  color: #2b5bff;
}

:deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 999px;
  background: linear-gradient(90deg, #2b5bff 0%, #7b6cf6 100%);
}

:deep(.el-input__wrapper) {
  background: #f8fafc;
  border-radius: 10px;
  box-shadow: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  min-height: 40px;
}

:deep(.el-input__wrapper.is-focus) {
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(43, 91, 255, 0.12);
}

:deep(.el-button) {
  border-radius: 12px;
  font-weight: 600;
}

:deep(.el-form-item__label) {
  color: #6b7280;
  font-weight: 500;
  line-height: 40px;
}

:deep(.el-form-item__content) {
  align-items: center;
}

:deep(.el-button--primary) {
  background: linear-gradient(90deg, #2b5bff 0%, #5b8cff 50%, #7b6cf6 100%);
  border: none;
  box-shadow: 0 12px 24px rgba(43, 91, 255, 0.25);
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(90deg, #234ee6 0%, #4d7fff 50%, #6c5ff2 100%);
  box-shadow: 0 16px 28px rgba(43, 91, 255, 0.3);
}

:deep(.el-button--primary:active) {
  transform: translateY(1px);
}
</style>
