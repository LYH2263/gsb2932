<template>
  <div class="challenge-container">
    <el-backtop :right="40" :bottom="60" />
    <el-row :gutter="20">
      <el-col :xs="24" :md="8">
        <el-card shadow="hover" class="challenge-list">
          <template #header>
            <div class="section-header">
              <el-icon><Trophy /></el-icon>
              <span>挑战列表</span>
            </div>
          </template>
          <el-empty v-if="challenges.length === 0" description="暂无挑战" />
          <el-menu
            v-else
            :default-active="activeChallenge ? String(activeChallenge.id) : ''"
            @select="handleSelect"
          >
            <el-menu-item v-for="challenge in challenges" :key="challenge.id" :index="String(challenge.id)">
              <div class="challenge-item">
                <div class="title">{{ challenge.title }}</div>
                <div class="meta">{{ formatDate(challenge.start_at) }} - {{ formatDate(challenge.end_at) }}</div>
                <el-tag size="small" :type="getDifficultyType(challenge.difficulty)">
                  {{ getDifficultyText(challenge.difficulty) }}
                </el-tag>
              </div>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="16">
        <el-card shadow="hover" class="challenge-detail" v-loading="loading">
          <template #header>
            <div class="section-header">
              <el-icon><Star /></el-icon>
              <span>挑战详情</span>
            </div>
          </template>
          <el-empty v-if="!activeChallenge" description="请选择一个挑战" />
          <div v-else class="detail-content">
            <div class="detail-hero">
              <div class="detail-text">
                <h2 class="detail-title">{{ activeChallenge.title }}</h2>
                <p class="detail-description">{{ activeChallenge.description }}</p>
                <div class="detail-tags">
                  <el-tag :type="getDifficultyType(activeChallenge.difficulty)" size="small">
                    {{ getDifficultyText(activeChallenge.difficulty) }}
                  </el-tag>
                  <el-tag type="info" size="small">{{ activeChallenge.reward || '参与即可展示' }}</el-tag>
                </div>
              </div>
              <div class="detail-stats">
                <div class="stat-item">
                  <span class="stat-label">开始时间</span>
                  <span class="stat-value">{{ formatDate(activeChallenge.start_at) }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">结束时间</span>
                  <span class="stat-value">{{ formatDate(activeChallenge.end_at) }}</span>
                </div>
              </div>
            </div>

            <el-card shadow="never" class="section-card submission-section">
              <template #header>
                <span class="section-title">提交作品</span>
              </template>
              <el-form :model="submissionForm" label-width="80px">
                <el-form-item label="标题">
                  <el-input v-model="submissionForm.title" placeholder="作品标题" />
                </el-form-item>
                <el-form-item label="链接">
                  <el-input v-model="submissionForm.link" placeholder="作品链接（可选）" />
                </el-form-item>
                <el-form-item label="描述">
                  <el-input v-model="submissionForm.description" type="textarea" :rows="4" placeholder="作品说明" />
                </el-form-item>
                <div class="form-actions">
                  <el-button type="primary" @click="submitWork" :loading="submitting">提交作品</el-button>
                </div>
              </el-form>
            </el-card>

            <el-tabs v-model="activeTab" class="content-tabs">
              <el-tab-pane name="submissions" label="作品展示">
                <el-empty v-if="submissions.length === 0" description="暂无提交" />
                <el-table v-else :data="sortedSubmissions" stripe>
                  <el-table-column prop="author_name" label="作者" width="120" />
                  <el-table-column prop="title" label="作品标题" />
                  <el-table-column label="评分" width="140">
                    <template #default="{ row }">
                      <div class="score-cell">
                        <span class="score-value">{{ row.score.toFixed(1) }}</span>
                        <span class="score-count">({{ row.vote_count }}人)</span>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column label="提交时间" width="160">
                    <template #default="{ row }">
                      {{ formatDate(row.created_at) }}
                    </template>
                  </el-table-column>
                  <el-table-column label="链接" width="100">
                    <template #default="{ row }">
                      <el-link v-if="row.link" :href="row.link" target="_blank" type="primary">查看</el-link>
                      <span v-else>—</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="140">
                    <template #default="{ row }">
                      <el-button
                        v-if="row.user_vote"
                        size="small"
                        type="success"
                        disabled
                      >
                        已投票 ({{ row.user_vote }}星)
                      </el-button>
                      <el-button
                        v-else-if="currentUserId && row.user_id !== currentUserId"
                        size="small"
                        type="primary"
                        @click="openVoteDialog(row)"
                      >
                        投票
                      </el-button>
                      <span
                        v-else-if="currentUserId && row.user_id === currentUserId"
                        class="own-submission-text"
                      >
                        自己的作品
                      </span>
                      <span v-else class="login-prompt-text">
                        登录后投票
                      </span>
                    </template>
                  </el-table-column>
                </el-table>
              </el-tab-pane>
              <el-tab-pane name="leaderboard" label="排行榜">
                <div v-if="leaderboard.length === 0" class="leaderboard-empty">
                  <el-empty description="暂无排行数据" />
                </div>
                <div v-else class="leaderboard-content">
                  <div class="medal-section">
                    <div
                      v-for="entry in topThree" :key="entry.id" class="medal-card" :class="'rank-' + entry.rank">
                      <div class="medal-icon">
                        <el-icon v-if="entry.rank === 1"><Trophy /></el-icon>
                        <el-icon v-else-if="entry.rank === 2"><Medal /></el-icon>
                        <el-icon v-else><Star /></el-icon>
                      </div>
                      <el-avatar :size="64" :src="entry.author_avatar" />
                      <div class="medal-name">{{ entry.author_name }}</div>
                      <div class="medal-title">{{ entry.title }}</div>
                      <div class="medal-score">
                        <span class="score">{{ entry.score.toFixed(1) }}</span>
                        <span class="count">({{ entry.vote_count }}票)</span>
                      </div>
                    </div>
                  </div>
                  <div v-if="otherEntries.length > 0" class="list-section">
                    <el-table :data="otherEntries" stripe>
                      <el-table-column prop="rank" label="排名" width="80">
                        <template #default="{ row }">
                          <span class="rank-badge">{{ row.rank }}</span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="author_name" label="作者" width="120" />
                      <el-table-column prop="title" label="作品标题" />
                      <el-table-column label="评分" width="120">
                        <template #default="{ row }">
                          <span class="table-score">{{ row.score.toFixed(1) }}</span>
                          <span class="table-count">({{ row.vote_count }}人)</span>
                        </template>
                      </el-table-column>
                      <el-table-column label="链接" width="100">
                        <template #default="{ row }">
                          <el-link v-if="row.link" :href="row.link" target="_blank" type="primary">查看</el-link>
                          <span v-else>—</span>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="voteDialogVisible" title="投票评分" width="400px" :close-on-click-modal="false">
      <div class="vote-dialog-content">
        <div class="vote-submission-info">
          <div class="vote-title">{{ currentVoteSubmission?.title }}</div>
          <div class="vote-author">作者: {{ currentVoteSubmission?.author_name }}</div>
        </div>
        <div class="vote-stars">
          <el-rate
            v-model="voteScore"
            :max="5"
            :colors="['#F7BA2A', '#F7BA2A', '#F7BA2A']"
            class="vote-rate"
          />
          <div class="vote-score-text">{{ voteScore }} 星</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="voteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitVote" :loading="voting" :disabled="voteScore === 0">确认投票</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Trophy, Star, Medal } from '@element-plus/icons-vue'
import { getChallenges, getChallengeDetail, createChallengeSubmission, voteSubmission, getChallengeLeaderboard } from '../api/community'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

const challenges = ref([])
const activeChallenge = ref(null)
const submissions = ref([])
const leaderboard = ref([])
const loading = ref(false)
const submitting = ref(false)
const voting = ref(false)
const activeTab = ref('submissions')

const submissionForm = ref({
  title: '',
  link: '',
  description: ''
})

const voteDialogVisible = ref(false)
const currentVoteSubmission = ref(null)
const voteScore = ref(0)

const sortedSubmissions = computed(() => {
  return [...submissions.value].sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score
    return new Date(b.created_at) - new Date(a.created_at)
  })
})

const topThree = computed(() => {
  return leaderboard.value.slice(0, 3)
})

const otherEntries = computed(() => {
  return leaderboard.value.slice(3)
})

const loadChallenges = async () => {
  loading.value = true
  try {
    const list = await getChallenges()
    challenges.value = list
    if (list.length > 0) {
      await loadChallengeDetail(list[0].id)
    }
  } catch (error) {
    ElMessage.error('加载挑战列表失败')
  } finally {
    loading.value = false
  }
}

const loadChallengeDetail = async (id) => {
  loading.value = true
  try {
    const detail = await getChallengeDetail(id)
    activeChallenge.value = detail
    submissions.value = detail.submissions || []
    await loadLeaderboard(id)
  } catch (error) {
    ElMessage.error('加载挑战详情失败')
  } finally {
    loading.value = false
  }
}

const loadLeaderboard = async (id) => {
  try {
    const response = await getChallengeLeaderboard(id)
    leaderboard.value = response.entries || []
  } catch (error) {
    console.error('加载排行榜失败', error)
  }
}

const handleSelect = (id) => {
  loadChallengeDetail(id)
}

const submitWork = async () => {
  if (!activeChallenge.value) return
  if (!submissionForm.value.title.trim() || !submissionForm.value.description.trim()) {
    ElMessage.warning('请填写作品标题和描述')
    return
  }
  submitting.value = true
  try {
    const response = await createChallengeSubmission(activeChallenge.value.id, submissionForm.value)
    submissions.value = [response, ...submissions.value]
    submissionForm.value = { title: '', link: '', description: '' }
    ElMessage.success('提交成功')
    await loadLeaderboard(activeChallenge.value.id)
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

const openVoteDialog = (row) => {
  currentVoteSubmission.value = row
  voteScore.value = 0
  voteDialogVisible.value = true
}

const submitVote = async () => {
  if (voteScore.value < 1 || voteScore.value > 5) {
    ElMessage.warning('请选择 1-5 星评分')
    return
  }
  voting.value = true
  try {
    const response = await voteSubmission(currentVoteSubmission.value.id, voteScore.value)
    const idx = submissions.value.findIndex(s => s.id === currentVoteSubmission.value.id)
    if (idx !== -1) {
      submissions.value[idx].score = response.score
      submissions.value[idx].vote_count = response.vote_count
      submissions.value[idx].user_vote = response.user_vote
    }
    voteDialogVisible.value = false
    ElMessage.success('投票成功')
    await loadLeaderboard(activeChallenge.value.id)
  } catch (error) {
    ElMessage.error('投票失败')
  } finally {
    voting.value = false
  }
}

const formatDate = (date) => {
  const d = new Date(date)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const getDifficultyText = (difficulty) => {
  if (difficulty === 'Advanced') return '高级'
  if (difficulty === 'Intermediate') return '中级'
  return '初级'
}

const getDifficultyType = (difficulty) => {
  if (difficulty === 'Advanced') return 'danger'
  if (difficulty === 'Intermediate') return 'warning'
  return 'success'
}

onMounted(loadChallenges)
</script>

<style scoped>
.challenge-container {
  padding: 24px 20px 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1f2a44;
}

.challenge-list {
  min-height: 540px;
  border-radius: 18px;
  border: none;
  background: #f8fafc;
}

.challenge-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.challenge-item .title {
  font-weight: 600;
  color: #1f2a44;
}

.challenge-item .meta {
  font-size: 12px;
  color: #8a94a6;
}

.challenge-list :deep(.el-menu) {
  border-right: none;
  background: transparent;
}

.challenge-list :deep(.el-menu-item) {
  height: auto;
  padding: 12px 16px;
  margin: 6px 0;
  border-radius: 12px;
}

.challenge-list :deep(.el-menu-item.is-active) {
  background: #ffffff;
  color: inherit;
  box-shadow: 0 10px 24px rgba(31, 42, 68, 0.08);
}

.detail-title {
  margin: 0 0 10px 0;
  font-size: 22px;
  font-weight: 700;
  color: #1f2a44;
}

.detail-description {
  color: #5c667b;
  line-height: 1.7;
  margin-bottom: 16px;
}

.challenge-detail {
  border-radius: 18px;
  border: none;
  background: #ffffff;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-hero {
  padding: 20px 24px;
  border-radius: 16px;
  background: linear-gradient(135deg, #eef2ff 0%, #f7f5ff 100%);
  display: flex;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}

.detail-text {
  flex: 1;
  min-width: 240px;
}

.detail-tags {
  display: flex;
  gap: 10px;
}

.detail-stats {
  min-width: 220px;
  display: grid;
  gap: 12px;
  align-content: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-label {
  color: #7d879a;
  font-size: 12px;
}

.stat-value {
  color: #1f2a44;
  font-weight: 600;
}

.section-card {
  border-radius: 16px;
  border: 1px solid #eef2f6;
}

.section-title {
  font-weight: 600;
  color: #1f2a44;
}

.submission-section,
.leaderboard-section {
  margin-top: 0;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.content-tabs {
  margin-top: 0;
}

.own-submission-text,
.login-prompt-text {
  color: #909399;
  font-size: 12px;
}

.score-cell {
  display: flex;
  align-items: center;
  gap: 4px;
}

.score-value {
  font-weight: 600;
  color: #f7ba2a;
  font-size: 16px;
}

.score-count {
  color: #909399;
  font-size: 12px;
}

.leaderboard-empty {
  padding: 40px 0;
}

.leaderboard-content {
  padding: 20px 0;
}

.medal-section {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}

.medal-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  border-radius: 16px;
  min-width: 180px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  position: relative;
  transition: transform 0.3s;
}

.medal-card:hover {
  transform: translateY(-4px);
}

.medal-card.rank-1 {
  order: 2;
  background: linear-gradient(135deg, #fff9e6 0%, #ffd700 30%, #ffed4e 100%);
  box-shadow: 0 10px 30px rgba(255, 215, 0, 0.3);
}

.medal-card.rank-2 {
  order: 1;
  background: linear-gradient(135deg, #f0f0f0 0%, #c0c0c0 30%, #e8e8e8 100%);
  box-shadow: 0 8px 24px rgba(192, 192, 192, 0.3);
}

.medal-card.rank-3 {
  order: 3;
  background: linear-gradient(135deg, #f5e6d3 0%, #cd7f32 30%, #daa520 100%);
  box-shadow: 0 6px 20px rgba(205, 127, 50, 0.3);
}

.medal-icon {
  position: absolute;
  top: -20px;
  font-size: 40px;
}

.medal-icon :deep(.el-icon) {
  font-size: 40px;
}

.medal-name {
  margin-top: 8px 0 4px;
  font-weight: 600;
  color: #1f2a44;
  font-size: 14px;
}

.medal-title {
  color: #5c667b;
  font-size: 12px;
  text-align: center;
  margin-bottom: 8px;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.medal-score {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.medal-score .score {
  font-size: 24px;
  font-weight: 700;
  color: #e6a23c;
}

.medal-score .count {
  font-size: 12px;
  color: #909399;
}

.list-section {
  margin-top: 24px 0 0;
}

.rank-badge {
  display: inline-block;
  width: 28px;
  height: 28px;
  line-height: 28px;
  text-align: center;
  background: #f0f2f5;
  border-radius: 50%;
  font-weight: 600;
  color: #606266;
}

.table-score {
  font-weight: 600;
  color: #f7ba2a;
  margin-right: 4px;
}

.table-count {
  color: #909399;
  font-size: 12px;
}

.vote-dialog-content {
  padding: 20px 0;
}

.vote-submission-info {
  margin-bottom: 24px;
  text-align: center;
}

.vote-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2a44;
  margin-bottom: 8px;
}

.vote-author {
  color: #909399;
  font-size: 14px;
}

.vote-stars {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.vote-rate {
  font-size: 32px;
}

.vote-score-text {
  font-size: 16px;
  color: #f7ba2a;
  font-weight: 600;
}

:deep(.el-tabs__header) {
  margin-bottom: 0;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

@media (max-width: 768px) {
  .medal-section {
    flex-direction: column;
    align-items: center;
  }
  
  .medal-card.rank-1 {
    order: 1;
  }
  
  .medal-card.rank-2 {
    order: 2;
  }
  
  .medal-card.rank-3 {
    order: 3;
  }
}
</style>
