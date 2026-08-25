<template>
  <div class="shared-sandbox-container">
    <div v-if="loading" class="loading-wrapper">
      <el-icon :size="40" class="is-loading"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="error-wrapper">
      <el-result icon="warning" title="代码片段不存在" sub-title="该分享链接无效或代码片段已被删除">
        <template #extra>
          <el-button type="primary" @click="router.push('/')">返回首页</el-button>
        </template>
      </el-result>
    </div>

    <template v-else>
      <el-card class="shared-card" shadow="hover">
        <template #header>
          <div class="shared-header">
            <div class="header-left">
              <el-icon :size="24" color="#409EFF"><Monitor /></el-icon>
              <span class="title">{{ snippet.title }}</span>
            </div>
            <div class="header-right">
              <el-tag :type="snippet.language === 'python' ? 'success' : 'warning'" size="large">
                {{ snippet.language.toUpperCase() }}
              </el-tag>
            </div>
          </div>
        </template>

        <div class="author-bar">
          <div class="author-info">
            <el-avatar :size="36" :src="snippet.author_avatar">
              {{ snippet.author_name?.charAt(0) }}
            </el-avatar>
            <div class="author-detail">
              <span class="author-name">{{ snippet.author_name }}</span>
              <span class="created-time">{{ formatTime(snippet.created_at) }}</span>
            </div>
          </div>
          <el-tag type="info" size="small" effect="plain">
            <el-icon><View /></el-icon> 只读模式
          </el-tag>
        </div>

        <div class="editor-layout">
          <div class="code-section">
            <div class="section-header">
              <el-icon><Edit /></el-icon>
              <span>源代码</span>
              <el-tag size="small" :type="snippet.language === 'python' ? 'success' : 'warning'">{{ snippet.language.toUpperCase() }}</el-tag>
            </div>
            <div class="code-display">
              <pre>{{ snippet.code }}</pre>
            </div>
          </div>

          <el-divider direction="vertical" class="divider" />

          <div class="output-section">
            <div class="section-header">
              <el-icon><Monitor /></el-icon>
              <span>运行结果</span>
              <el-tag v-if="running" type="warning" size="small" effect="dark">
                <el-icon class="is-loading"><Loading /></el-icon> 运行中
              </el-tag>
              <el-tag v-else-if="output" type="success" size="small">已完成</el-tag>
            </div>
            <div class="output-content" :class="{ 'has-error': hasError }">
              <pre v-if="output">{{ output }}</pre>
              <el-empty v-else description="点击运行按钮查看结果" :image-size="100" />
            </div>
          </div>
        </div>
      </el-card>

      <div class="action-bar">
        <el-button type="primary" size="large" @click="handleRun" :loading="running" :icon="VideoPlay">
          运行代码
        </el-button>
        <el-button type="success" size="large" @click="handleFork" :icon="CopyDocument">
          Fork 到我的沙盒
        </el-button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSharedSnippet, executeCode, saveSnippet } from '../api/sandbox'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import {
  Monitor, VideoPlay, Edit, Loading, View, CopyDocument
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const snippet = ref({})
const loading = ref(true)
const error = ref(false)
const output = ref('')
const running = ref(false)
const hasError = ref(false)

const formatTime = (dt) => {
  if (!dt) return ''
  const d = new Date(dt)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(async () => {
  try {
    const token = route.params.shareToken
    snippet.value = await getSharedSnippet(token)
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
})

const handleRun = async () => {
  running.value = true
  hasError.value = false
  output.value = '正在运行...'

  try {
    const response = await executeCode(snippet.value.code, snippet.value.language)
    output.value = response.output || '无输出'
    hasError.value = !!response.error
    if (response.error) {
      output.value = response.error
    }
  } catch (e) {
    output.value = `错误: ${e.message || '执行失败'}`
    hasError.value = true
  } finally {
    running.value = false
  }
}

const handleFork = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录后再 Fork')
    router.push('/login')
    return
  }
  try {
    await saveSnippet({
      title: `Fork: ${snippet.value.title}`,
      code: snippet.value.code,
      language: snippet.value.language,
      is_public: false
    })
    ElMessage.success('已 Fork 到你的沙盒，即将跳转...')
    router.push('/sandbox')
  } catch (e) {
    ElMessage.error('Fork 失败')
  }
}
</script>

<style scoped>
.shared-sandbox-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.loading-wrapper,
.error-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-wrapper p {
  margin-top: 16px;
  color: #909399;
}

.shared-card {
  margin-bottom: 20px;
}

.shared-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left .title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.author-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  margin-bottom: 16px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-detail {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.created-time {
  font-size: 12px;
  color: #909399;
}

.editor-layout {
  display: flex;
  gap: 0;
  min-height: 450px;
}

.code-section,
.output-section {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  font-weight: 500;
  color: #606266;
}

.code-display {
  flex: 1;
  padding: 16px;
  background: #1e1e1e;
  color: #d4d4d4;
  border: 1px solid #dcdfe6;
  border-radius: 0 0 4px 4px;
  overflow: auto;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.code-display pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.output-content {
  flex: 1;
  padding: 16px;
  background: #1e1e1e;
  color: #d4d4d4;
  border: 1px solid #dcdfe6;
  border-radius: 0 0 4px 4px;
  overflow: auto;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.output-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.output-content.has-error {
  color: #f56c6c;
}

.divider {
  height: auto;
  margin: 0 20px;
}

.action-bar {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px 0;
}

@media (max-width: 768px) {
  .editor-layout {
    flex-direction: column;
  }

  .divider {
    display: none;
  }

  .shared-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .author-bar {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>
