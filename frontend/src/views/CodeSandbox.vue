<template>
  <div class="code-sandbox-container">
    <div class="sandbox-layout">
      <transition name="slide">
        <div v-if="historyVisible" class="history-panel">
          <div class="history-header">
            <div class="history-title">
              <el-icon><Clock /></el-icon>
              <span>历史记录</span>
            </div>
            <el-button :icon="ArrowLeft" circle size="small" @click="historyVisible = false" />
          </div>
          <div class="history-list">
            <div v-if="snippets.length === 0" class="history-empty">
              <el-empty description="暂无保存记录" :image-size="60" />
            </div>
            <div
              v-for="snippet in snippets"
              :key="snippet.id"
              class="history-item"
              :class="{ active: currentSnippetId === snippet.id }"
              @click="loadSnippet(snippet)"
            >
              <div class="snippet-info">
                <div class="snippet-title">{{ snippet.title }}</div>
                <div class="snippet-meta">
                  <el-tag size="small" :type="snippet.language === 'python' ? 'success' : 'warning'">{{ snippet.language }}</el-tag>
                  <span class="snippet-time">{{ formatTime(snippet.updated_at) }}</span>
                </div>
              </div>
              <div class="snippet-actions" @click.stop>
                <el-tooltip content="分享" placement="top">
                  <el-button :icon="Share" circle size="small" @click="handleShare(snippet)" />
                </el-tooltip>
                <el-tooltip content="删除" placement="top">
                  <el-button :icon="Delete" circle size="small" type="danger" @click="handleDeleteSnippet(snippet.id)" />
                </el-tooltip>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <div class="sandbox-main">
        <el-card class="sandbox-card" shadow="hover">
          <template #header>
            <div class="sandbox-header">
              <div class="header-left">
                <el-button v-if="!historyVisible" :icon="Clock" circle @click="toggleHistory" title="历史记录" />
                <el-icon :size="24" color="#409EFF"><Monitor /></el-icon>
                <span class="title">代码沙盒</span>
                <el-tag type="info" size="small">在线编程环境</el-tag>
              </div>
              <div class="header-right">
                <el-select v-model="language" placeholder="选择语言" style="width: 140px" size="large">
                  <el-option label="Python" value="python" />
                  <el-option label="JavaScript" value="javascript" />
                </el-select>
                <el-button type="success" @click="showSaveDialog" size="large" :icon="FolderOpened">
                  保存
                </el-button>
                <el-button
                  type="primary"
                  @click="handleRun"
                  :loading="running"
                  size="large"
                  :icon="VideoPlay"
                >
                  运行代码
                </el-button>
                <el-button
                  @click="clearCode"
                  size="large"
                  :icon="Delete"
                >
                  清空
                </el-button>
              </div>
            </div>
          </template>

          <div class="editor-layout">
            <div class="code-section">
              <div class="section-header">
                <el-icon><Edit /></el-icon>
                <span>代码编辑器</span>
                <el-tag size="small" :type="language === 'python' ? 'success' : 'warning'">{{ language.toUpperCase() }}</el-tag>
              </div>
              <el-input
                v-model="code"
                type="textarea"
                :rows="18"
                :placeholder="codePlaceholder"
                class="code-editor"
                resize="none"
              />
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

        <el-row :gutter="20" class="tips-section">
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="tip-header">
                  <el-icon><InfoFilled /></el-icon>
                  <span>使用提示</span>
                </div>
              </template>
              <ul class="tip-list">
                <li v-for="tip in tips" :key="tip">{{ tip }}</li>
              </ul>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <template #header>
                <div class="tip-header">
                  <el-icon><Star /></el-icon>
                  <span>示例代码</span>
                </div>
              </template>
              <el-space wrap>
                <el-button v-for="example in examples" :key="example.name" @click="loadExample(example.code)" size="small">
                  {{ example.name }}
                </el-button>
              </el-space>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>

    <el-dialog v-model="saveDialogVisible" title="保存代码片段" width="420px" :close-on-click-modal="false">
      <el-form :model="saveForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="saveForm.title" placeholder="请输入代码片段标题" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="公开分享">
          <el-switch v-model="saveForm.is_public" active-text="公开" inactive-text="私有" />
        </el-form-item>
        <el-form-item v-if="currentSnippetId" label="保存方式">
          <el-radio-group v-model="saveForm.saveMode">
            <el-radio value="update">更新当前片段</el-radio>
            <el-radio value="new">另存为新片段</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="shareDialogVisible" title="分享代码" width="460px">
      <div class="share-dialog-content">
        <p class="share-desc">复制以下链接分享你的代码：</p>
        <el-input :model-value="shareLink" readonly>
          <template #append>
            <el-button @click="copyShareLink">复制</el-button>
          </template>
        </el-input>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { executeCode, saveSnippet, getMySnippets, deleteSnippet, updateSnippet } from '../api/sandbox'
import { useAuthStore } from '../stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor, VideoPlay, Delete, Edit, Loading, InfoFilled, Star,
  FolderOpened, Clock, Share, ArrowLeft
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const pythonDefault = 'print("Hello, World!")\nfor i in range(5):\n    print(i)'
const javascriptDefault = 'console.log("Hello, World!");\nfor (let i = 0; i < 5; i++) {\n  console.log(`第 ${i + 1} 次循环`);\n}'
const code = ref(pythonDefault)
const language = ref('python')
const output = ref('')
const running = ref(false)
const hasError = ref(false)

const historyVisible = ref(false)
const snippets = ref([])
const currentSnippetId = ref(null)

const saveDialogVisible = ref(false)
const saving = ref(false)
const saveForm = ref({
  title: '',
  is_public: false,
  saveMode: 'update'
})

const shareDialogVisible = ref(false)
const shareLink = ref('')

const pythonExamples = [
  { name: 'Hello World', code: 'print("Hello, World!")' },
  { name: '循环示例', code: 'for i in range(5):\n    print(f"第 {i+1} 次循环")' },
  { name: '列表操作', code: 'numbers = [1, 2, 3, 4, 5]\nprint(f"列表: {numbers}")\nprint(f"总和: {sum(numbers)}")\nprint(f"最大值: {max(numbers)}")' },
  { name: '函数定义', code: 'def greet(name):\n    return f"你好, {name}!"\n\nprint(greet("编程学习者"))' }
]
const javascriptExamples = [
  { name: 'Hello World', code: 'console.log("Hello, World!");' },
  { name: '数组操作', code: 'const numbers = [1, 2, 3, 4, 5];\nconsole.log(numbers);\nconsole.log(numbers.reduce((a, b) => a + b, 0));' },
  { name: '函数定义', code: 'function greet(name) {\n  return `你好, ${name}!`;\n}\nconsole.log(greet("编程学习者"));' },
  { name: '对象遍历', code: 'const user = { name: "Alice", score: 95 };\nObject.entries(user).forEach(([k, v]) => console.log(k, v));' }
]

const examples = computed(() => (language.value === 'python' ? pythonExamples : javascriptExamples))
const tips = computed(() => {
  if (language.value === 'python') {
    return ['支持标准 Python 3 语法', '可以使用 print() 输出结果', '支持基础数学运算和数据结构', '代码执行有时间限制（5秒）', '点击「保存」可保存代码片段']
  }
  return ['支持标准 JavaScript 语法', '可以使用 console.log() 输出结果', '支持基础数组与对象操作', '代码执行有时间限制（5秒）', '点击「保存」可保存代码片段']
})
const codePlaceholder = computed(() => (language.value === 'python' ? '# 在此编写 Python 代码...' : '// 在此编写 JavaScript 代码...'))

watch(language, (newLang) => {
  code.value = newLang === 'python' ? pythonDefault : javascriptDefault
})

onMounted(() => {
  fetchSnippets()
})

const fetchSnippets = async () => {
  try {
    snippets.value = await getMySnippets()
  } catch (e) {
    // ignore
  }
}

const toggleHistory = () => {
  historyVisible.value = !historyVisible.value
}

const formatTime = (dt) => {
  if (!dt) return ''
  const d = new Date(dt)
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${mm}-${dd} ${hh}:${mi}`
}

const loadSnippet = (snippet) => {
  code.value = snippet.code
  language.value = snippet.language
  currentSnippetId.value = snippet.id
  output.value = ''
  hasError.value = false
  ElMessage.success('已加载代码片段')
}

const showSaveDialog = () => {
  if (currentSnippetId.value) {
    const current = snippets.value.find(s => s.id === currentSnippetId.value)
    saveForm.value.title = current ? current.title : ''
    saveForm.value.is_public = current ? current.is_public : false
    saveForm.value.saveMode = 'update'
  } else {
    saveForm.value.title = ''
    saveForm.value.is_public = false
    saveForm.value.saveMode = 'new'
  }
  saveDialogVisible.value = true
}

const handleSave = async () => {
  if (!saveForm.value.title.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  saving.value = true
  try {
    if (saveForm.value.saveMode === 'update' && currentSnippetId.value) {
      await updateSnippet(currentSnippetId.value, {
        title: saveForm.value.title,
        code: code.value,
        language: language.value,
        is_public: saveForm.value.is_public
      })
      ElMessage.success('片段已更新')
    } else {
      await saveSnippet({
        title: saveForm.value.title,
        code: code.value,
        language: language.value,
        is_public: saveForm.value.is_public
      })
      ElMessage.success('新片段已保存')
    }
    saveDialogVisible.value = false
    await fetchSnippets()
    if (!historyVisible.value) {
      historyVisible.value = true
    }
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleShare = async (snippet) => {
  if (!snippet.is_public) {
    try {
      await ElMessageBox.confirm('该片段尚未公开，是否公开并分享？', '提示', {
        confirmButtonText: '公开并分享',
        cancelButtonText: '取消',
        type: 'info'
      })
      await updateSnippet(snippet.id, { is_public: true })
      snippet.is_public = true
      shareLink.value = `${window.location.origin}/sandbox/shared/${snippet.share_token}`
      shareDialogVisible.value = true
    } catch (e) {
      // cancelled or error
    }
    return
  }
  shareLink.value = `${window.location.origin}/sandbox/shared/${snippet.share_token}`
  shareDialogVisible.value = true
}

const copyShareLink = () => {
  navigator.clipboard.writeText(shareLink.value).then(() => {
    ElMessage.success('链接已复制')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}

const handleDeleteSnippet = async (snippetId) => {
  try {
    await ElMessageBox.confirm('确定删除该代码片段？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteSnippet(snippetId)
    ElMessage.success('已删除')
    if (currentSnippetId.value === snippetId) {
      currentSnippetId.value = null
    }
    await fetchSnippets()
  } catch (e) {
    // cancelled or error
  }
}

const handleRun = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请输入代码')
    return
  }

  running.value = true
  hasError.value = false
  output.value = '正在运行...'

  try {
    const response = await executeCode(code.value, language.value)
    output.value = response.output || '无输出'
    hasError.value = !!response.error || output.value.startsWith('Error:')
    if (response.error) {
      output.value = response.error
    }
  } catch (error) {
    output.value = `错误: ${error.message || '执行失败'}`
    hasError.value = true
    ElMessage.error('代码执行失败')
  } finally {
    running.value = false
  }
}

const clearCode = () => {
  code.value = ''
  output.value = ''
  hasError.value = false
  currentSnippetId.value = null
  ElMessage.success('已清空')
}

const loadExample = (exampleCode) => {
  code.value = exampleCode
  currentSnippetId.value = null
  ElMessage.success('已加载示例代码')
}
</script>

<style scoped>
.code-sandbox-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.sandbox-layout {
  display: flex;
  gap: 0;
  min-height: 600px;
}

.history-panel {
  width: 280px;
  min-width: 280px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  margin-right: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  background: #f5f7fa;
}

.history-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.history-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 4px;
}

.history-item:hover {
  background: #ecf5ff;
}

.history-item.active {
  background: #d9ecff;
  border: 1px solid #b3d8ff;
}

.snippet-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.snippet-title {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.snippet-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.snippet-time {
  font-size: 11px;
  color: #909399;
}

.snippet-actions {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.history-item:hover .snippet-actions {
  opacity: 1;
}

.sandbox-main {
  flex: 1;
  min-width: 0;
}

.sandbox-card {
  margin-bottom: 20px;
}

.sandbox-header {
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

.code-editor :deep(.el-textarea__inner) {
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
  background: #1e1e1e;
  color: #d4d4d4;
  border: 1px solid #dcdfe6;
  border-radius: 0 0 4px 4px;
  padding: 16px;
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

.tips-section {
  margin-top: 20px;
}

.tip-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.tip-list {
  margin: 0;
  padding-left: 20px;
  color: #606266;
  line-height: 2;
}

.tip-list li {
  margin-bottom: 4px;
}

.share-dialog-content {
  padding: 0 0 8px;
}

.share-desc {
  margin: 0 0 12px;
  color: #606266;
  font-size: 14px;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
  margin-right: 0;
  width: 0;
  min-width: 0;
  padding: 0;
  overflow: hidden;
}

:deep(.el-empty__description) {
  color: #909399;
}

@media (max-width: 768px) {
  .sandbox-layout {
    flex-direction: column;
  }

  .history-panel {
    width: 100%;
    min-width: 100%;
    margin-right: 0;
    margin-bottom: 16px;
    max-height: 250px;
  }

  .editor-layout {
    flex-direction: column;
  }

  .divider {
    display: none;
  }

  .sandbox-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .header-right {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
