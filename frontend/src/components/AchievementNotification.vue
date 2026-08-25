<template>
  <Teleport to="body">
    <Transition name="achievement-slide">
      <div v-if="visible" class="achievement-notification" @click="handleClick">
        <div class="notification-content">
          <div class="badge-wrapper">
            <div class="badge-glow"></div>
            <el-icon class="achievement-badge" :size="48">
              <component :is="badgeIcon" />
            </el-icon>
          </div>
          <div class="text-content">
            <div class="congrats-text">🎉 恭喜解锁成就！</div>
            <div class="achievement-name">{{ achievement?.name }}</div>
            <div class="achievement-desc">{{ achievement?.description }}</div>
          </div>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ animation: `shrink ${duration}ms linear forwards` }"></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { User, Reading, Calendar, ChatDotRound, Star, Clock, Medal, Trophy } from '@element-plus/icons-vue'

const props = defineProps({
  achievement: Object,
  visible: Boolean,
  duration: {
    type: Number,
    default: 3000
  }
})

const emit = defineEmits(['close'])

const iconMap = {
  User,
  Reading,
  Calendar,
  ChatDotRound,
  Star,
  Clock,
  Medal,
  Trophy
}

const badgeIcon = computed(() => {
  if (!props.achievement?.icon) return Trophy
  return iconMap[props.achievement.icon] || Trophy
})

let timer = null

const handleClick = () => {
  if (timer) clearTimeout(timer)
  emit('close')
}

watch(() => props.visible, (newVal) => {
  if (newVal) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      emit('close')
    }, props.duration)
  }
})
</script>

<style scoped>
.achievement-notification {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 9999;
  background: linear-gradient(135deg, #fff9e6 0%, #fff5d6 100%);
  border: 2px solid #ffd700;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(255, 193, 7, 0.3), 0 0 60px rgba(255, 215, 0, 0.2);
  min-width: 320px;
  overflow: hidden;
  cursor: pointer;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.badge-wrapper {
  position: relative;
  flex-shrink: 0;
}

.badge-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(255, 215, 0, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.achievement-badge {
  position: relative;
  color: #ffd700;
  filter: drop-shadow(0 2px 8px rgba(255, 193, 7, 0.5));
}

.text-content {
  flex: 1;
  min-width: 0;
}

.congrats-text {
  font-size: 14px;
  font-weight: 600;
  color: #e6a23c;
  margin-bottom: 4px;
}

.achievement-name {
  font-size: 18px;
  font-weight: 700;
  color: #1f2a44;
  margin-bottom: 4px;
}

.achievement-desc {
  font-size: 12px;
  color: #8a94a6;
}

.progress-bar {
  height: 4px;
  background: rgba(255, 215, 0, 0.2);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ffd700, #ff9500);
}

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.8;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0.4;
  }
}

@keyframes shrink {
  from {
    width: 100%;
  }
  to {
    width: 0%;
  }
}

.achievement-slide-enter-active {
  animation: slideIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.achievement-slide-leave-active {
  animation: slideOut 0.4s ease-in forwards;
}

@keyframes slideIn {
  from {
    transform: translateX(120%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(120%);
    opacity: 0;
  }
}
</style>
