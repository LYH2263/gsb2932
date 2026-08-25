<template>
  <div class="community-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="section-title">社区讨论</h2>
        <p class="section-subtitle">分享学习心得，提出问题，互相帮助</p>
      </div>
      <div class="header-right">
        <el-input v-model="searchQuery" placeholder="搜索帖子标题或内容" clearable class="search-input" @clear="loadPosts" />
        <el-select v-model="categoryFilter" placeholder="全部分类" clearable class="category-select" @change="loadPosts">
          <el-option label="讨论" value="discussion" />
          <el-option label="问答" value="question" />
          <el-option label="分享" value="share" />
        </el-select>
        <el-radio-group v-model="sortBy" size="default" @change="loadPosts">
          <el-radio-button value="latest">最新</el-radio-button>
          <el-radio-button value="hottest">最热</el-radio-button>
        </el-radio-group>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          发布帖子
        </el-button>
      </div>
    </div>

    <el-empty v-if="posts.length === 0" description="暂无帖子" />
    <el-row v-else :gutter="20">
      <el-col :xs="24" :sm="12" :md="8" v-for="post in posts" :key="post.id" class="mb-4">
        <el-card shadow="hover" class="post-card">
          <div @click="openPost(post)">
            <div class="post-title">{{ post.title }}</div>
            <div class="post-meta">
              <el-tag size="small" type="info">{{ mapCategory(post.category) }}</el-tag>
              <span class="post-date">{{ formatDate(post.created_at) }}</span>
            </div>
            <p class="post-preview">{{ truncateHtml(post.content, 120) }}</p>
          </div>
          <div class="post-stats">
            <span><el-icon><View /></el-icon>{{ post.views || 0 }}</span>
            <span><el-icon><ChatLineSquare /></el-icon>{{ commentCounts[post.id] || 0 }}</span>
            <span 
              class="like-btn"
              :class="{ 'liked': likedPostIds.includes(post.id) }"
              @click.stop="handlePostLike(post)"
            >
              <el-icon>
                <component :is="likedPostIds.includes(post.id) ? 'StarFilled' : 'Star'" />
              </el-icon>
              {{ post.likes_count || 0 }}
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-drawer v-model="showPostDrawer" :title="currentPost?.title || '帖子详情'" size="50%">
      <div v-if="currentPost" class="post-detail">
        <div class="detail-meta">
          <el-tag size="small" type="info">{{ mapCategory(currentPost.category) }}</el-tag>
          <span class="detail-date">{{ formatDate(currentPost.created_at) }}</span>
        </div>
        <div class="detail-content" v-html="sanitizeHtml(currentPost.content)"></div>

        <div class="comment-section">
          <div class="comment-header">
            <h3>评论</h3>
            <el-button text type="primary" @click="loadComments(currentPost.id)">刷新</el-button>
          </div>
          <el-empty v-if="comments.length === 0" description="暂无评论" />
          <div v-else class="comments-list">
            <CommentItem
              v-for="comment in comments"
              :key="comment.id"
              :comment="comment"
              :depth="0"
              :liked-comment-ids="likedCommentIds"
              :liking-comment-ids="likingCommentIds"
              @like="handleCommentLike"
              @reply="handleCommentReply"
            />
          </div>

          <el-form :model="commentForm" class="comment-form">
            <el-form-item>
              <el-input v-model="commentForm.content" type="textarea" :rows="3" placeholder="写下你的评论..." />
            </el-form-item>
            <el-button type="primary" :loading="commentSubmitting" @click="submitComment">发布评论</el-button>
          </el-form>
        </div>
      </div>
    </el-drawer>

    <el-dialog v-model="showCreateDialog" title="发布帖子" width="700px" class="create-post-dialog">
      <el-form :model="postForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="postForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="postForm.category" placeholder="选择分类">
            <el-option label="讨论" value="discussion" />
            <el-option label="问答" value="question" />
            <el-option label="分享" value="share" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <RichTextEditor v-model="postForm.content" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="postSubmitting" @click="submitPost">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatLineSquare, View, Plus } from '@element-plus/icons-vue'
import { getPosts, createPost, getCommentsTree, createComment, likePost, likeComment, getLikeStatus } from '../api/community'
import CommentItem from '../components/CommentItem.vue'
import RichTextEditor from '../components/RichTextEditor.vue'
import DOMPurify from 'dompurify'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const isLoggedIn = computed(() => authStore.isAuthenticated)

const posts = ref([])
const comments = ref([])
const commentCounts = ref({})
const currentPost = ref(null)
const showPostDrawer = ref(false)
const showCreateDialog = ref(false)
const postSubmitting = ref(false)
const commentSubmitting = ref(false)
const searchQuery = ref('')
const categoryFilter = ref('')
const sortBy = ref('latest')
const likedPostIds = ref([])
const likedCommentIds = ref([])
const likingPostIds = ref(new Set())
const likingCommentIds = ref(new Set())

const postForm = ref({
  title: '',
  content: '',
  category: 'discussion'
})

const commentForm = ref({
  content: ''
})

let searchTimer = null

const mapCategory = (category) => {
  if (category === 'question') return '问答'
  if (category === 'share') return '分享'
  return '讨论'
}

const formatDate = (date) => {
  const d = new Date(date)
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

const stripHtml = (html) => {
  const tmp = document.createElement('div')
  tmp.innerHTML = html
  return tmp.textContent || tmp.innerText || ''
}

const truncateHtml = (html, length) => {
  const text = stripHtml(html)
  return text.length > length ? text.substring(0, length) + '...' : text
}

const sanitizeHtml = (html) => {
  return DOMPurify.sanitize(html, {
    ADD_TAGS: ['p', 'br', 'strong', 'em', 'u', 's', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'img', 'pre', 'code', 'blockquote'],
    ADD_ATTR: ['href', 'src', 'alt', 'title', 'target'],
    FORBID_TAGS: ['script', 'style', 'iframe', 'form', 'input', 'button'],
    FORBID_ATTR: ['onclick', 'onload', 'onerror', 'style']
  })
}

const loadLikeStatus = async () => {
  if (!isLoggedIn.value) {
    likedPostIds.value = []
    likedCommentIds.value = []
    return
  }
  try {
    const status = await getLikeStatus()
    likedPostIds.value = status.post_ids || []
    likedCommentIds.value = status.comment_ids || []
  } catch (error) {
    console.warn('获取点赞状态失败')
  }
}

const loadPosts = async () => {
  try {
    const params = { limit: 50, sort_by: sortBy.value }
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    if (categoryFilter.value) {
      params.category = categoryFilter.value
    }
    posts.value = await getPosts(params)
  } catch (error) {
    ElMessage.error('加载帖子失败')
  }
}

watch(searchQuery, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    loadPosts()
  }, 300)
})

const openPost = async (post) => {
  currentPost.value = post
  showPostDrawer.value = true
  await loadComments(post.id)
}

const loadComments = async (postId) => {
  try {
    comments.value = await getCommentsTree(postId, 3)
    commentCounts.value = { ...commentCounts.value, [postId]: getTotalCommentsCount(comments.value) }
  } catch (error) {
    ElMessage.error('加载评论失败')
  }
}

const getTotalCommentsCount = (commentList) => {
  let count = 0
  for (const comment of commentList) {
    count += 1
    if (comment.replies && comment.replies.length > 0) {
      count += getTotalCommentsCount(comment.replies)
    }
  }
  return count
}

const findCommentById = (commentList, commentId) => {
  for (const comment of commentList) {
    if (comment.id === commentId) {
      return comment
    }
    if (comment.replies && comment.replies.length > 0) {
      const found = findCommentById(comment.replies, commentId)
      if (found) return found
    }
  }
  return null
}

const addReplyToComment = (commentList, parentId, reply) => {
  for (const comment of commentList) {
    if (comment.id === parentId) {
      if (!comment.replies) {
        comment.replies = []
      }
      comment.replies.push(reply)
      comment.replies_count = (comment.replies_count || 0) + 1
      return true
    }
    if (comment.replies && comment.replies.length > 0) {
      if (addReplyToComment(comment.replies, parentId, reply)) {
        return true
      }
    }
  }
  return false
}

const handleCommentReply = async (replyData) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    return
  }
  if (!currentPost.value) return
  commentSubmitting.value = true
  try {
    const created = await createComment(currentPost.value.id, {
      content: replyData.content,
      parent_id: replyData.parentId
    })
    created.replies = []
    created.replies_count = 0
    created.depth = 0
    created.is_collapsed = false
    addReplyToComment(comments.value, replyData.parentId, created)
    commentCounts.value = { ...commentCounts.value, [currentPost.value.id]: getTotalCommentsCount(comments.value) }
    ElMessage.success('评论发布成功')
  } catch (error) {
    ElMessage.error('评论发布失败')
  } finally {
    commentSubmitting.value = false
  }
}

const handlePostLike = async (post) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    return
  }
  if (likingPostIds.value.has(post.id)) return
  likingPostIds.value.add(post.id)
  
  try {
    const result = await likePost(post.id)
    const postIndex = posts.value.findIndex(p => p.id === post.id)
    if (postIndex !== -1) {
      posts.value[postIndex].likes_count = result.likes_count
    }
    if (currentPost.value && currentPost.value.id === post.id) {
      currentPost.value.likes_count = result.likes_count
    }
    
    if (result.is_liked) {
      if (!likedPostIds.value.includes(post.id)) {
        likedPostIds.value.push(post.id)
      }
    } else {
      likedPostIds.value = likedPostIds.value.filter(id => id !== post.id)
    }
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    likingPostIds.value.delete(post.id)
  }
}

const updateCommentLikes = (commentList, commentId, likesCount) => {
  for (const comment of commentList) {
    if (comment.id === commentId) {
      comment.likes_count = likesCount
      return true
    }
    if (comment.replies && comment.replies.length > 0) {
      if (updateCommentLikes(comment.replies, commentId, likesCount)) {
        return true
      }
    }
  }
  return false
}

const handleCommentLike = async (comment) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    return
  }
  if (likingCommentIds.value.has(comment.id)) return
  likingCommentIds.value.add(comment.id)
  
  try {
    const result = await likeComment(comment.id)
    updateCommentLikes(comments.value, comment.id, result.likes_count)
    
    if (result.is_liked) {
      if (!likedCommentIds.value.includes(comment.id)) {
        likedCommentIds.value.push(comment.id)
      }
    } else {
      likedCommentIds.value = likedCommentIds.value.filter(id => id !== comment.id)
    }
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    likingCommentIds.value.delete(comment.id)
  }
}

const submitPost = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    return
  }
  if (!postForm.value.title.trim() || !postForm.value.content.trim()) {
    ElMessage.warning('请填写标题和内容')
    return
  }
  postSubmitting.value = true
  try {
    const created = await createPost({
      title: postForm.value.title,
      content: postForm.value.content,
      category: postForm.value.category
    })
    posts.value.unshift(created)
    showCreateDialog.value = false
    postForm.value = { title: '', content: '', category: 'discussion' }
    ElMessage.success('帖子发布成功')
  } catch (error) {
    ElMessage.error('帖子发布失败')
  } finally {
    postSubmitting.value = false
  }
}

const submitComment = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    return
  }
  if (!currentPost.value) return
  if (!commentForm.value.content.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  commentSubmitting.value = true
  try {
    const created = await createComment(currentPost.value.id, { content: commentForm.value.content })
    created.replies = []
    created.replies_count = 0
    created.depth = 0
    created.is_collapsed = false
    comments.value.unshift(created)
    commentCounts.value = { ...commentCounts.value, [currentPost.value.id]: getTotalCommentsCount(comments.value) }
    commentForm.value.content = ''
    ElMessage.success('评论发布成功')
  } catch (error) {
    ElMessage.error('评论发布失败')
  } finally {
    commentSubmitting.value = false
  }
}

onMounted(async () => {
  await loadLikeStatus()
  await loadPosts()
})
</script>

<style scoped>
.community-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

.section-title {
  margin: 0 0 6px;
  font-size: 24px;
  color: #303133;
}

.section-subtitle {
  margin: 0;
  color: #909399;
}

.header-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  width: 240px;
}

.category-select {
  width: 120px;
}

.post-card {
  cursor: pointer;
  height: 100%;
}

.post-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #909399;
  font-size: 12px;
  margin-bottom: 10px;
}

.post-preview {
  color: #606266;
  line-height: 1.6;
  min-height: 48px;
}

.post-stats {
  margin-top: 12px;
  display: flex;
  gap: 16px;
  color: #909399;
  font-size: 12px;
}

.post-stats span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.like-btn {
  cursor: pointer;
  transition: color 0.2s;
}

.like-btn:hover {
  color: #f56c6c;
}

.like-btn.liked {
  color: #f56c6c;
}

.post-detail {
  padding: 10px 0;
}

.detail-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  color: #909399;
}

.detail-content {
  line-height: 1.8;
  color: #303133;
  margin-bottom: 20px;
}

.detail-content :deep(h1) {
  font-size: 24px;
  font-weight: 600;
  margin: 20px 0 12px;
}

.detail-content :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin: 18px 0 10px;
}

.detail-content :deep(h3) {
  font-size: 18px;
  font-weight: 600;
  margin: 16px 0 8px;
}

.detail-content :deep(p) {
  margin: 10px 0;
}

.detail-content :deep(strong) {
  font-weight: 600;
}

.detail-content :deep(em) {
  font-style: italic;
}

.detail-content :deep(u) {
  text-decoration: underline;
}

.detail-content :deep(s) {
  text-decoration: line-through;
}

.detail-content :deep(ul),
.detail-content :deep(ol) {
  padding-left: 24px;
  margin: 10px 0;
}

.detail-content :deep(li) {
  margin: 4px 0;
}

.detail-content :deep(a) {
  color: #409eff;
  text-decoration: none;
}

.detail-content :deep(a:hover) {
  text-decoration: underline;
}

.detail-content :deep(img) {
  max-width: 100%;
  border-radius: 4px;
  margin: 10px 0;
}

.detail-content :deep(pre) {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 10px 0;
}

.detail-content :deep(code) {
  font-family: 'Consolas', 'Monaco', monospace;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 14px;
}

.detail-content :deep(pre code) {
  background: none;
  padding: 0;
}

.detail-content :deep(blockquote) {
  border-left: 4px solid #dcdfe6;
  padding-left: 16px;
  margin: 10px 0;
  color: #606266;
  font-style: italic;
}

.comment-section {
  margin-top: 20px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comments-list {
  margin-bottom: 16px;
}

.comments-list > :deep(.comment-item:first-child) {
  padding-top: 0;
}

.comment-form {
  margin-top: 16px;
}

.mb-4 {
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-right {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .search-input,
  .category-select {
    width: 100%;
  }
}
</style>
