<template>
  <div class="app-container">
    <!-- 顶部标题区 -->
    <header class="header">
      <div class="header-content">
        <div class="header-portrait">
          <img src="/images/mao-portrait.png" alt="毛泽东" class="portrait-image">
        </div>
        <div class="header-text">
          <h1 class="main-title fade-in">{{ personInfo.name }}</h1>
          <p class="subtitle fade-in">{{ personInfo.period }}</p>
          <p class="today-note">今天是 {{ todayFormatted }}</p>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 侧边事件时间轴 -->
      <aside class="events-sidebar fade-in" v-if="todayEvents.length > 0">
        <div class="sidebar-header">
          <span class="sidebar-icon">📅</span>
          <span class="sidebar-title">今日事件</span>
        </div>
        <div class="events-timeline">
          <div v-for="event in todayEvents" :key="event.date + event.time"
               class="timeline-event"
               :class="getEventStatus(event)">
            <div class="event-time-marker">{{ formatEventTime(event.time) }}</div>
            <div class="event-info">
              <div class="event-title-small">{{ event.event }}</div>
              <div class="event-impact-badge" v-if="event.impact === '高'">重大</div>
            </div>
            <div class="event-status-icon">
              <span v-if="getEventStatus(event) === 'completed'">✓</span>
              <span v-else-if="getEventStatus(event) === 'active'" class="pulse-dot">●</span>
              <span v-else>○</span>
            </div>
          </div>
        </div>
      </aside>

      <div class="content-wrapper vintage-paper">
        <!-- 背景诗词图片 -->
        <div class="background-poetry"></div>

        <!-- 历史时间显示 -->
        <div class="time-display fade-in">
          <div class="historical-date">{{ historicalDateFormatted }}</div>
          <div class="current-time">{{ formattedTime }}</div>
        </div>

        <!-- 当前活动内容 -->
        <!-- 如果有正在发生的历史事件，显示所有事件 -->
        <div v-if="currentHistoricalEvents.length > 0">
          <div v-for="(event, index) in currentHistoricalEvents" :key="event.date + event.time + index"
               class="activity-card fade-in"
               :style="{ animationDelay: (index * 0.1) + 's' }">
            <div class="activity-type type-historical">
              重大历史事件 {{ currentHistoricalEvents.length > 1 ? `(${index + 1}/${currentHistoricalEvents.length})` : '' }}
            </div>
            <h2 class="activity-title">{{ event.event }}</h2>
            <div class="activity-description">
              {{ event.description }}
            </div>

            <!-- 事件元数据 -->
            <div class="event-metadata">
              <!-- 历史背景 -->
              <div v-if="event.historical_context" class="metadata-item context">
                <div class="metadata-label">📖 历史背景</div>
                <div class="metadata-content">{{ event.historical_context }}</div>
              </div>

              <!-- 心情和影响 -->
              <div class="metadata-row">
                <div v-if="event.mood" class="metadata-item mood">
                  <div class="metadata-label">💭 当时心情</div>
                  <div class="metadata-content">{{ event.mood }}</div>
                </div>
                <div v-if="event.impact" class="metadata-item impact" :class="'impact-' + event.impact">
                  <div class="metadata-label">⚡ 历史影响</div>
                  <div class="metadata-content">{{ getImpactText(event.impact) }}</div>
                </div>
              </div>

              <div class="historical-badge">
                <span class="badge-icon">📜</span>
                <span>重大历史事件</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 如果没有历史事件，显示日常活动 -->
        <div v-else-if="currentActivity" class="activity-card fade-in">
          <div class="activity-type type-routine">
            日常活动
          </div>
          <h2 class="activity-title">{{ currentActivity.title }}</h2>
          <div class="activity-description">
            {{ currentActivity.description }}
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-else class="loading pulse">
          <p>正在查询历史资料...</p>
        </div>
      </div>
    </main>

    <!-- 底部信息 -->
    <footer class="footer">
      <p>本站内容基于历史文献整理，仅供历史研究参考</p>
      <p class="footer-note">数据更新中 · 更多内容即将添加</p>
      <div class="social-links-icons">
        <a href="https://github.com/Comui520/What-was-Mao-doing-at-this-time-in-the-past" target="_blank" rel="noopener noreferrer" title="GitHub">
          <img src="/images/github.png" alt="GitHub" class="social-icon">
        </a>
        <a href="https://space.bilibili.com/171609789" target="_blank" rel="noopener noreferrer" title="Bilibili">
          <img src="/images/bilibili.png" alt="Bilibili" class="social-icon">
        </a>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 人物基础信息
const personInfo = ref({
  name: '毛泽东',
  period: '1945 - 1949 解放战争时期',
  description: '中国共产党领导人'
})

// 当前真实时间
// 🧪 测试模式：取消下面的注释来测试特定日期
// const currentDate = ref(new Date(2030, 9, 1, 15, 0)) // 2027年1月22日 12:00
const currentDate = ref(new Date())
// 对应的历史日期
const historicalDate = ref(new Date())
const currentActivity = ref(null)
// 今天的所有事件
const todayEvents = ref([])
// 当前时间正在发生的历史事件（可能有多个）
const currentHistoricalEvents = ref([])

// 今天的日期（真实日期）
const todayFormatted = computed(() => {
  const date = currentDate.value
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}年${month}月${day}日`
})

// 历史日期格式化
const historicalDateFormatted = computed(() => {
  const date = historicalDate.value
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  const weekday = weekdays[date.getDay()]
  return `${year}年${month}月${day}日 ${weekday}`
})

// 格式化时间
const formattedTime = computed(() => {
  const date = currentDate.value
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  return `${hour}:${minute}`
})

// 活动类型
const activityType = computed(() => {
  return currentActivity.value?.isHistorical ? '重大历史事件' : '日常活动'
})

const activityTypeClass = computed(() => {
  return currentActivity.value?.isHistorical ? 'type-historical' : 'type-routine'
})

// 影响程度文本
function getImpactText(impact) {
  const impactMap = {
    '高': '深远影响',
    '中': '重要影响',
    '低': '一般影响'
  }
  return impactMap[impact] || impact
}

// 格式化事件时间
function formatEventTime(time) {
  const hour = parseInt(time)
  return `${String(hour).padStart(2, '0')}:00`
}

// 判断事件是否正在发生
function isEventActive(event) {
  const currentHour = currentDate.value.getHours()
  return parseInt(event.time) === currentHour
}

// 获取事件状态
function getEventStatus(event) {
  const currentHour = currentDate.value.getHours()
  const eventHour = parseInt(event.time)

  if (eventHour < currentHour) {
    return 'completed' // 已完成
  } else if (eventHour === currentHour) {
    return 'active' // 正在进行
  } else {
    return 'pending' // 待发生
  }
}

// 计算对应的历史年份（循环1945-1949）
function getHistoricalYear(currentYear) {
  const startYear = 1945
  const endYear = 1949
  const baseYear = 2026 // 基准年，2026年对应1945年
  const totalYears = endYear - startYear + 1 // 5年

  // 计算当前年份相对于基准年的偏移
  const yearOffset = (currentYear - baseYear) % totalYears

  // 处理负数情况（如果当前年份小于2026）
  const normalizedOffset = yearOffset >= 0 ? yearOffset : yearOffset + totalYears

  return startYear + normalizedOffset
}

// 检查日期是否有效
function isValidDate(year, month, day) {
  const date = new Date(year, month - 1, day)
  return date.getFullYear() === year &&
         date.getMonth() === month - 1 &&
         date.getDate() === day
}

// 加载数据
async function loadData() {
  try {
    // 加载所有数据文件
    const base = import.meta.env.BASE_URL
    const [routineRes, eventsRes] = await Promise.all([
      fetch(`${base}data/daily_routine.json`),
      fetch(`${base}data/historical_events.json`)
    ])

    const dailyRoutine = await routineRes.json()
    const historicalEvents = await eventsRes.json()

    // 计算历史日期
    const now = currentDate.value
    const currentYear = now.getFullYear()
    const currentMonth = now.getMonth() + 1
    const currentDay = now.getDate()
    const currentHour = now.getHours()

    // 获取对应的历史年份
    const histYear = getHistoricalYear(currentYear)

    // 检查这个日期在历史年份中是否有效（处理闰年2月29日的情况）
    if (isValidDate(histYear, currentMonth, currentDay)) {
      historicalDate.value = new Date(histYear, currentMonth - 1, currentDay, currentHour)
    } else {
      // 如果无效（比如2月29日但那年不是闰年），使用2月28日
      historicalDate.value = new Date(histYear, currentMonth - 1, currentDay - 1, currentHour)
    }

    // 获取今天的所有事件
    const year = historicalDate.value.getFullYear()
    const month = String(historicalDate.value.getMonth() + 1).padStart(2, '0')
    const day = String(historicalDate.value.getDate()).padStart(2, '0')
    const fullDate = `${year}-${month}-${day}`

    todayEvents.value = historicalEvents.filter(event => event.date === fullDate)
      .sort((a, b) => parseInt(a.time) - parseInt(b.time))

    // 获取当前时间的所有历史事件
    currentHistoricalEvents.value = historicalEvents.filter(event => {
      const eventHour = parseInt(event.time)
      return event.date === fullDate && eventHour === currentHour
    })

    // 获取当前活动（日常作息）
    currentActivity.value = getCurrentActivity(dailyRoutine, currentHour)
  } catch (error) {
    console.error('加载数据失败:', error)
    // 显示默认内容
    currentActivity.value = {
      title: '数据加载中...',
      description: '正在准备历史资料，请稍候。',
      isHistorical: false
    }
  }
}

// 获取当前活动（日常作息）
function getCurrentActivity(dailyRoutine, currentHour) {
  const routineKey = Object.keys(dailyRoutine).find(key => {
    const [start, end] = key.split('-').map(Number)
    return currentHour >= start && currentHour < end
  })

  if (routineKey && dailyRoutine[routineKey]) {
    return {
      title: dailyRoutine[routineKey].activity,
      description: dailyRoutine[routineKey].description,
      isHistorical: false
    }
  }

  // 默认返回
  return {
    title: '休息时间',
    description: '此时毛泽东通常在休息。',
    isHistorical: false
  }
}

// 更新时间
function updateTime() {
  currentDate.value = new Date()
  loadData()
}

onMounted(() => {
  loadData()
  // 每分钟更新一次
  setInterval(updateTime, 60000)
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 头部样式 */
.header {
  background: linear-gradient(135deg, #8b0000 0%, #dc143c 100%);
  padding: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: stretch;
  position: relative;
  z-index: 1;
}

.header-portrait {
  flex-shrink: 0;
  width: auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

.portrait-image {
  height: 100%;
  width: auto;
  max-width: 300px;
  object-fit: cover;
  filter: drop-shadow(0 8px 20px rgba(0, 0, 0, 0.3));
  transition: transform 0.3s ease;
}

.portrait-image:hover {
  transform: scale(1.02);
}

.header-text {
  flex: 1;
  padding: 3rem 3rem 3rem 2rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: left;
}

.main-title {
  font-size: 3.5rem;
  font-weight: 900;
  color: #ffd700;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.5);
  margin-bottom: 0.5rem;
  letter-spacing: 0.5rem;
}

.subtitle {
  font-size: 1.2rem;
  color: #ffe4b5;
  font-weight: 400;
  letter-spacing: 0.3rem;
  margin-bottom: 1rem;
}

.today-note {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 300;
  letter-spacing: 0.1rem;
  margin-top: 0.5rem;
}

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 3rem 2rem;
  display: flex;
  gap: 2rem;
  justify-content: center;
  align-items: flex-start;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* 侧边事件时间轴 */
.events-sidebar {
  width: 280px;
  background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
  position: sticky;
  top: 2rem;
  max-height: calc(100vh - 4rem);
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
}

.sidebar-icon {
  font-size: 1.5rem;
}

.sidebar-title {
  font-size: 1.1rem;
  font-weight: 900;
  color: #ffd700;
  letter-spacing: 0.1rem;
}

.events-timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.timeline-event {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1rem;
  border-left: 4px solid #4a5568;
  transition: all 0.3s ease;
  position: relative;
}

.timeline-event:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.timeline-event.pending {
  border-left-color: #718096;
  opacity: 0.7;
}

.timeline-event.active {
  border-left-color: #ffd700;
  background: linear-gradient(135deg, rgba(220, 20, 60, 0.2) 0%, rgba(139, 0, 0, 0.2) 100%);
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
  animation: activeGlow 2s ease-in-out infinite;
}

@keyframes activeGlow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
  }
  50% {
    box-shadow: 0 0 30px rgba(255, 215, 0, 0.6);
  }
}

.timeline-event.completed {
  border-left-color: #48bb78;
  opacity: 0.6;
}

.event-time-marker {
  font-size: 0.9rem;
  font-weight: 700;
  color: #ffd700;
  margin-bottom: 0.5rem;
}

.event-info {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.event-title-small {
  flex: 1;
  font-size: 0.9rem;
  color: #e2e8f0;
  line-height: 1.4;
  font-weight: 500;
}

.event-impact-badge {
  background: #dc143c;
  color: #ffd700;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 900;
  white-space: nowrap;
}

.event-status-icon {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 1.2rem;
}

.timeline-event.pending .event-status-icon {
  color: #718096;
}

.timeline-event.active .event-status-icon {
  color: #ffd700;
}

.timeline-event.completed .event-status-icon {
  color: #48bb78;
}

.pulse-dot {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

.content-wrapper {
  max-width: 900px;
  width: 100%;
  padding: 3rem;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  position: relative;
  overflow: hidden;
}

/* 背景诗词图片 */
.background-poetry {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url('/images/mao-poetry-bg.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 0.15;
  pointer-events: none;
  z-index: 0;
  /* 如果图片加载失败，显示淡灰色背景 */
  background-color: transparent;
}

.content-wrapper > * {
  position: relative;
  z-index: 1;
}

/* 时间显示 */
.time-display {
  text-align: center;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid rgba(139, 0, 0, 0.3);
}

.historical-date {
  font-size: 1.8rem;
  color: #8b0000;
  font-weight: 900;
  margin-bottom: 0.8rem;
  letter-spacing: 0.1rem;
}

.current-time {
  font-size: 3rem;
  color: #dc143c;
  font-weight: 900;
  letter-spacing: 0.2rem;
}

/* 活动卡片 */
.activity-card {
  position: relative;
  margin-bottom: 2rem;
}

.activity-card:last-child {
  margin-bottom: 0;
}

.activity-type {
  display: inline-block;
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  letter-spacing: 0.1rem;
}

.type-routine {
  background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
  color: #fff;
}

.type-historical {
  background: linear-gradient(135deg, #dc143c 0%, #8b0000 100%);
  color: #ffd700;
  box-shadow: 0 4px 15px rgba(220, 20, 60, 0.4);
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(220, 20, 60, 0.4);
  }
  50% {
    box-shadow: 0 4px 25px rgba(220, 20, 60, 0.6);
  }
}

.activity-title {
  font-size: 2.5rem;
  color: #2d3748;
  margin-bottom: 1.5rem;
  line-height: 1.4;
  font-weight: 900;
}

.activity-description {
  font-size: 1.2rem;
  color: #4a5568;
  line-height: 2;
  text-align: justify;
  text-indent: 2em;
}

/* 事件元数据 */
.event-metadata {
  margin-top: 2rem;
}

.metadata-item {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.02);
}

.metadata-label {
  font-size: 0.9rem;
  font-weight: 700;
  color: #8b0000;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.metadata-content {
  font-size: 1rem;
  color: #4a5568;
  line-height: 1.8;
}

.metadata-item.context {
  background: rgba(139, 0, 0, 0.05);
  border-left: 3px solid #8b0000;
}

.metadata-item.context .metadata-content {
  text-indent: 2em;
  text-align: justify;
}

.metadata-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metadata-item.mood {
  background: rgba(100, 149, 237, 0.1);
  border-left: 3px solid #6495ed;
}

.metadata-item.mood .metadata-label {
  color: #4169e1;
}

.metadata-item.impact {
  border-left: 3px solid #ffa500;
}

.metadata-item.impact .metadata-label {
  color: #ff8c00;
}

.metadata-item.impact-高 {
  background: rgba(220, 20, 60, 0.1);
  border-left: 3px solid #dc143c;
}

.metadata-item.impact-高 .metadata-label {
  color: #dc143c;
}

.metadata-item.impact-中 {
  background: rgba(255, 165, 0, 0.1);
  border-left: 3px solid #ffa500;
}

.metadata-item.impact-低 {
  background: rgba(128, 128, 128, 0.1);
  border-left: 3px solid #808080;
}

.metadata-item.impact-低 .metadata-label {
  color: #696969;
}

.historical-badge {
  margin-top: 2rem;
  padding: 1rem;
  background: rgba(220, 20, 60, 0.1);
  border-left: 4px solid #dc143c;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #8b0000;
  font-weight: 700;
}

.badge-icon {
  font-size: 1.5rem;
}

/* 加载状态 */
.loading {
  text-align: center;
  padding: 4rem 2rem;
  color: #8b0000;
  font-size: 1.3rem;
}

/* 底部 */
.footer {
  background: #1a1a1a;
  padding: 2rem;
  text-align: center;
  color: #999;
}

.social-links-icons {
  margin: 1rem 0;
  display: flex;
  justify-content: center;
  gap: 2rem;
}

.social-icon {
  width: 32px;
  height: 32px;
  transition: transform 0.3s ease;
  filter: brightness(0.8);
}

.social-icon:hover {
  transform: scale(1.3);
  filter: brightness(1.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
  }

  .header-portrait {
    width: 100%;
    max-height: 200px;
  }

  .portrait-image {
    width: 100%;
    height: auto;
    max-width: 100%;
    max-height: 200px;
  }

  .header-text {
    padding: 2rem;
    text-align: center;
  }

  .main-title {
    font-size: 2.5rem;
    letter-spacing: 0.3rem;
  }

  .subtitle {
    font-size: 1rem;
    letter-spacing: 0.2rem;
  }

  .today-note {
    font-size: 0.8rem;
  }

  .content-wrapper {
    padding: 2rem 1.5rem;
  }

  .historical-date {
    font-size: 1.4rem;
  }

  .current-time {
    font-size: 2.5rem;
  }

  .activity-title {
    font-size: 1.8rem;
  }

  .activity-description {
    font-size: 1rem;
  }

  .metadata-row {
    grid-template-columns: 1fr;
  }

  .metadata-item {
    padding: 0.8rem;
  }

  .metadata-label {
    font-size: 0.85rem;
  }

  .metadata-content {
    font-size: 0.9rem;
  }

  .main-content {
    flex-direction: column;
    padding: 2rem 1rem;
  }

  .events-sidebar {
    width: 100%;
    position: static;
    max-height: none;
    margin-bottom: 1.5rem;
  }

  .events-timeline {
    gap: 0.8rem;
  }

  .timeline-event {
    padding: 0.8rem;
  }

  .event-title-small {
    font-size: 0.85rem;
  }

  .event-time-marker {
    font-size: 0.85rem;
  }

  .event-status-icon {
    font-size: 1rem;
  }

  .content-wrapper {
    width: 100%;
  }
}
</style>
