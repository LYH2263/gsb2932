<template>
  <div class="markdown-editor">
    <div class="editor-toolbar">
      <el-button-group>
        <el-button size="small" @click="insertBold" title="Ctrl+B 加粗">
          <el-icon><Bold /></el-icon>
        </el-button>
        <el-button size="small" @click="insertItalic" title="Ctrl+I 斜体">
          <el-icon><Italic /></el-icon>
        </el-button>
        <el-button size="small" @click="insertLink" title="Ctrl+K 插入链接">
          <el-icon><Link /></el-icon>
        </el-button>
      </el-button-group>
      <span class="toolbar-hint">提示：Ctrl+B 加粗 | Ctrl+I 斜体 | Ctrl+K 链接 | Tab 缩进</span>
    </div>
    <div class="editor-container">
      <div class="editor-pane">
        <div class="pane-header">编辑区</div>
        <textarea
          ref="textareaRef"
          v-model="localContent"
          class="editor-textarea"
          placeholder="在此输入 Markdown 内容..."
          @keydown="handleKeydown"
          @input="handleInput"
        ></textarea>
      </div>
      <div class="preview-pane">
        <div class="pane-header">预览区</div>
        <div class="preview-content" v-html="renderedContent"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Bold, Italic, Link } from '@element-plus/icons-vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({
  breaks: true,
  gfm: true
})

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const textareaRef = ref(null)
const localContent = ref(props.modelValue)

watch(() => props.modelValue, (newVal) => {
  localContent.value = newVal
})

const handleInput = () => {
  emit('update:modelValue', localContent.value)
}

const renderedContent = computed(() => {
  if (!localContent.value) return ''
  const rawHtml = marked.parse(localContent.value)
  return DOMPurify.sanitize(rawHtml)
})

const insertAtCursor = (before, after = '') => {
  const textarea = textareaRef.value
  if (!textarea) return
  
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = localContent.value.substring(start, end)
  
  const newText = localContent.value.substring(0, start) + before + selectedText + after + localContent.value.substring(end)
  localContent.value = newText
  emit('update:modelValue', newText)
  
  setTimeout(() => {
    textarea.focus()
    const newCursorPos = start + before.length + selectedText.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
  }, 0)
}

const insertBold = () => {
  insertAtCursor('**', '**')
}

const insertItalic = () => {
  insertAtCursor('*', '*')
}

const insertLink = () => {
  insertAtCursor('[链接文本](', ')')
}

const handleKeydown = (e) => {
  if (e.ctrlKey || e.metaKey) {
    if (e.key === 'b' || e.key === 'B') {
      e.preventDefault()
      insertBold()
    } else if (e.key === 'i' || e.key === 'I') {
      e.preventDefault()
      insertItalic()
    } else if (e.key === 'k' || e.key === 'K') {
      e.preventDefault()
      insertLink()
    }
  } else if (e.key === 'Tab') {
    e.preventDefault()
    insertAtCursor('  ')
  }
}

onMounted(() => {
})

onUnmounted(() => {
})
</script>

<style scoped>
.markdown-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
}

.toolbar-hint {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

.editor-container {
  display: flex;
  flex: 1;
  border: 1px solid #e4e7ed;
  border-radius: 0 0 4px 4px;
  overflow: hidden;
}

.editor-pane,
.preview-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.editor-pane {
  border-right: 1px solid #e4e7ed;
}

.pane-header {
  padding: 8px 12px;
  background: #f5f7fa;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  border-bottom: 1px solid #e4e7ed;
}

.editor-textarea {
  flex: 1;
  width: 100%;
  padding: 12px;
  border: none;
  resize: none;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  outline: none;
  box-sizing: border-box;
}

.preview-content {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
}

.preview-content :deep(h1) {
  font-size: 24px;
  margin: 16px 0 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #409EFF;
}

.preview-content :deep(h2) {
  font-size: 20px;
  margin: 14px 0 10px;
  color: #303133;
}

.preview-content :deep(h3) {
  font-size: 16px;
  margin: 12px 0 8px;
  color: #606266;
}

.preview-content :deep(p) {
  margin: 8px 0;
}

.preview-content :deep(strong) {
  font-weight: 600;
  color: #303133;
}

.preview-content :deep(em) {
  font-style: italic;
}

.preview-content :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: #e6a23c;
}

.preview-content :deep(pre) {
  background: #1e1e1e;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
  margin: 12px 0;
}

.preview-content :deep(pre code) {
  background: none;
  padding: 0;
  color: #d4d4d4;
  font-size: 13px;
  line-height: 1.6;
}

.preview-content :deep(blockquote) {
  margin: 12px 0;
  padding: 8px 16px;
  border-left: 4px solid #409EFF;
  background: #f0f7ff;
  color: #606266;
}

.preview-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.preview-content :deep(th),
.preview-content :deep(td) {
  border: 1px solid #e4e7ed;
  padding: 8px 12px;
  text-align: left;
}

.preview-content :deep(th) {
  background: #f5f7fa;
  font-weight: 600;
  color: #303133;
}

.preview-content :deep(tr:nth-child(even)) {
  background: #fafafa;
}

.preview-content :deep(a) {
  color: #409EFF;
  text-decoration: none;
}

.preview-content :deep(a:hover) {
  text-decoration: underline;
}

.preview-content :deep(ul),
.preview-content :deep(ol) {
  padding-left: 24px;
  margin: 8px 0;
}

.preview-content :deep(li) {
  margin: 4px 0;
}

.preview-content :deep(hr) {
  border: none;
  border-top: 1px solid #e4e7ed;
  margin: 16px 0;
}

.preview-content :deep(img) {
  max-width: 100%;
  border-radius: 4px;
}

@media (max-width: 768px) {
  .editor-container {
    flex-direction: column;
  }
  
  .editor-pane {
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
  }
}
</style>
