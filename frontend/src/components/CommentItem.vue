<template>
  <div class="comment-item" :style="{ marginLeft: depth > 0 ? '40px' : '0' }">
    <div class="comment-main">
      <div class="comment-header">
        <el-avatar :size="28" :src="comment.author_avatar" icon="UserFilled" class="comment-avatar" />
        <div class="comment-meta">
          <span class="comment-author">{{ comment.author_name }}</span>
          <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
        </div>
        <div class="comment-actions">
          <span 
            class="like-btn"
            :class="{ 'liked': isLiked }"
            @click.stop="handleLike"
          >
            <el-icon>
              <component :is="isLiked ? 'StarFilled' : 'Star'" />
            </el-icon>
            {{ comment.likes_count || 0 }}
          </span>
          <el-button text type="primary" size="small" @click.stop="toggleReply">
            回复
          </el-button>
        </div>
      </div>
      <div class="comment-content">
        <span v-if="parentAuthor" class="reply-prefix">回复 @{{ parentAuthor }}：</span>
        {{ comment.content }}
      </div>
      
      <div v-if="showReplyBox" class="reply-form">
        <el-input
          v-model="replyContent"
          type="textarea"
          :rows="2"
          :placeholder="`回复 @${comment.author_name}...`"
          class="reply-textarea"
        />
        <div class="reply-actions">
          <el-button size="small" @click.stop="cancelReply">取消</el-button>
          <el-button type="primary" size="small" :loading="submitting" @click.stop="submitReply">
            发布
          </el-button>
        </div>
      </div>
    </div>
    
    <div v-if="comment.replies && comment.replies.length > 0" class="comment-replies">
      <div v-if="shouldShowCollapseBtn" class="collapse-toggle">
        <el-button text type="primary" size="small" @click.stop="toggleCollapse">
          <el-icon>
            <component :is="isCollapsed ? 'ArrowDown' : 'ArrowUp'" />
          </el-icon>
          {{ isCollapsed ? `展开 ${collapsedCount} 条回复` : '收起回复' }}
        </el-button>
      </div>
      
      <transition-group name="comment-list">
        <CommentItem
          v-for="reply in visibleReplies"
          :key="reply.id"
          :comment="reply"
          :depth="depth + 1"
          :parent-author="comment.author_name"
          :liked-comment-ids="likedCommentIds"
          :liking-comment-ids="likingCommentIds"
          @like="handleChildLike"
          @reply="handleChildReply"
        />
      </transition-group>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'
import { ArrowDown, ArrowUp } from '@element-plus/icons-vue'

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  depth: {
    type: Number,
    default: 0
  },
  parentAuthor: {
    type: String,
    default: ''
  },
  likedCommentIds: {
    type: Array,
    default: () => []
  },
  likingCommentIds: {
    type: Set,
    default: () => new Set()
  }
})

const emit = defineEmits(['like', 'reply'])

const showReplyBox = ref(false)
const replyContent = ref('')
const submitting = ref(false)
const isCollapsed = ref(props.comment.is_collapsed || false)

const MAX_DEPTH = 3

const isLiked = computed(() => props.likedCommentIds.includes(props.comment.id))
const isLiking = computed(() => props.likingCommentIds.has(props.comment.id))

const shouldShowCollapseBtn = computed(() => {
  return props.comment.collapsed_replies_count > 0 || props.comment.depth >= MAX_DEPTH - 1
})

const collapsedCount = computed(() => {
  return props.comment.collapsed_replies_count || props.comment.replies?.length || 0
})

const visibleReplies = computed(() => {
  if (!props.comment.replies) return []
  if (isCollapsed.value) {
    return props.comment.replies.filter(r => r.depth < MAX_DEPTH)
  }
  return props.comment.replies
})

const formatDate = (date) => {
  const d = new Date(date)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

const toggleReply = () => {
  showReplyBox.value = !showReplyBox.value
  if (showReplyBox.value) {
    replyContent.value = ''
  }
}

const cancelReply = () => {
  showReplyBox.value = false
  replyContent.value = ''
}

const submitReply = async () => {
  if (!replyContent.value.trim()) return
  submitting.value = true
  emit('reply', {
    parentId: props.comment.id,
    content: replyContent.value.trim()
  })
  showReplyBox.value = false
  replyContent.value = ''
  submitting.value = false
}

const handleLike = () => {
  emit('like', props.comment)
}

const handleChildLike = (comment) => {
  emit('like', comment)
}

const handleChildReply = (replyData) => {
  emit('reply', replyData)
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<style scoped>
.comment-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.comment-avatar {
  flex-shrink: 0;
}

.comment-meta {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.comment-author {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.comment-time {
  font-size: 12px;
  color: #909399;
}

.comment-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.like-btn {
  cursor: pointer;
  transition: color 0.2s;
  color: #909399;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  user-select: none;
}

.like-btn:hover {
  color: #f56c6c;
}

.like-btn.liked {
  color: #f56c6c;
}

.comment-content {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  padding-left: 38px;
}

.reply-prefix {
  color: #409eff;
  font-weight: 500;
}

.reply-form {
  margin-left: 38px;
  margin-top: 8px;
}

.reply-textarea {
  margin-bottom: 8px;
}

.reply-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.comment-replies {
  margin-top: 4px;
}

.collapse-toggle {
  padding-left: 38px;
  margin: 4px 0;
}

.comment-list-enter-active,
.comment-list-leave-active {
  transition: all 0.3s ease;
}

.comment-list-enter-from,
.comment-list-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
