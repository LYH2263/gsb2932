<template>
  <div class="rich-text-editor">
    <Toolbar
      :editor="editorRef"
      :defaultConfig="toolbarConfig"
      mode="default"
      style="border-bottom: 1px solid #ccc;"
    />
    <Editor
      :defaultConfig="editorConfig"
      v-model="valueHtml"
      mode="default"
      style="height: 300px; overflow-y: hidden;"
      @onCreated="handleCreated"
      @onChange="handleChange"
    />
  </div>
</template>

<script setup>
import { ref, shallowRef, watch, onBeforeUnmount } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'
import { uploadImage } from '../api/community'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const editorRef = shallowRef()
const valueHtml = ref(props.modelValue)

watch(() => props.modelValue, (newVal) => {
  if (newVal !== valueHtml.value) {
    valueHtml.value = newVal
  }
})

watch(valueHtml, (newVal) => {
  emit('update:modelValue', newVal)
})

const toolbarConfig = {
  toolbarKeys: [
    'bold',
    'italic',
    'through',
    'code',
    'sub',
    'sup',
    'clearStyle',
    '|',
    'headerSelect',
    '|',
    'bulletedList',
    'numberedList',
    '|',
    'justifyLeft',
    'justifyRight',
    'justifyCenter',
    '|',
    'insertLink',
    'insertImage',
    'codeBlock',
    '|',
    'undo',
    'redo'
  ]
}

const editorConfig = {
  placeholder: '请输入内容...',
  MENU_CONF: {
    insertImage: {
      customUpload(file, insertFn) {
        handleCustomUpload(file, insertFn)
      }
    },
    uploadImage: {
      customUpload(file, insertFn) {
        handleCustomUpload(file, insertFn)
      }
    }
  }
}

const handleCustomUpload = async (file, insertFn) => {
  try {
    console.log('Uploading file:', file.name, file.type, file.size)
    const result = await uploadImage(file)
    console.log('Upload result:', result)
    
    if (!result || !result.url) {
      throw new Error('返回格式错误')
    }
    
    const baseUrl = import.meta.env.VITE_API_BASE_URL || ''
    const fullUrl = `${baseUrl}${result.url}`
    console.log('Inserting image with URL:', fullUrl)
    insertFn(fullUrl, file.name, fullUrl)
    ElMessage.success('图片上传成功')
  } catch (error) {
    console.error('Image upload error:', error)
    const errorMsg = error.response?.data?.detail || error.message || '图片上传失败'
    ElMessage.error(errorMsg)
  }
}

const handleCreated = (editor) => {
  editorRef.value = editor
}

const handleChange = (editor) => {
  valueHtml.value = editor.getHtml()
}

onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
})
</script>

<style scoped>
.rich-text-editor {
  border: 1px solid #ccc;
  border-radius: 4px;
  overflow: hidden;
}

:deep(.w-e-text-container) {
  background-color: #fff;
}

:deep(.w-e-text-placeholder) {
  color: #999;
}
</style>
