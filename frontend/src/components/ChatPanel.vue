<template>
  <div class="chat-panel" :class="{ 'chat-panel--open': open }">
    <div class="chat-header">
      <div class="chat-header-left">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2a10 10 0 1 0 10 10H12V2z"/>
          <path d="M12 2a10 10 0 0 1 10 10h-2a8 8 0 0 0-8-8V2z"/>
          <circle cx="12" cy="12" r="3" fill="#8b5cf6"/>
        </svg>
        <span>AI 病害诊断助手</span>
      </div>
      <button class="chat-close" @click="$emit('close')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>

    <div class="chat-body" ref="bodyRef">
      <div class="chat-context" v-if="detections.length" :class="{ 'chat-context--collapsed': ctxCollapsed }">
        <div class="chat-context-head" @click="ctxCollapsed = !ctxCollapsed">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          <span>当前检测摘要 ({{ detections.length }} 个目标)</span>
          <svg class="ctx-chevron" :class="{ 'ctx-chevron--flip': ctxCollapsed }" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
        <div class="chat-context-list">
          <div class="ctx-tag" v-for="(d, i) in detections" :key="i" :style="{'--dc': d.color || colors[i % colors.length]}">
            <span class="ctx-dot" :style="{background: d.color || colors[i % colors.length]}"></span>
            <span class="ctx-name">{{ cnName(d.class_name) }}</span>
            <span class="ctx-conf">{{ (d.confidence * 100).toFixed(0) }}%</span>
          </div>
        </div>
      </div>

      <div class="chat-msgs">
        <div v-if="messages.length === 0 && !streaming" class="chat-empty">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" opacity=".25">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <span>检测完成后，可针对结果提问</span>
        </div>

        <div class="chat-msg" v-for="(m, i) in messages" :key="i" :class="'chat-msg--' + m.role">
          <div class="chat-msg-avatar">
            <template v-if="m.role === 'assistant'">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round"><path d="M12 2a10 10 0 1 0 10 10H12V2z"/><circle cx="12" cy="12" r="3" fill="#8b5cf6"/></svg>
            </template>
            <template v-else>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" stroke-width="1.8" stroke-linecap="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </template>
          </div>
          <div class="chat-msg-bubble" v-html="renderMd(m.content)"></div>
        </div>

        <div class="chat-msg chat-msg--assistant" v-if="streaming">
          <div class="chat-msg-avatar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="2" stroke-linecap="round"><path d="M12 2a10 10 0 1 0 10 10H12V2z"/><circle cx="12" cy="12" r="3" fill="#8b5cf6"/></svg>
          </div>
          <div class="chat-msg-bubble">
            <span v-html="renderMd(streamText)"></span><span class="chat-cursor">▌</span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-foot">
      <div class="chat-err" v-if="error">{{ error }}</div>
      <div class="chat-input-row">
        <input
          class="chat-input"
          v-model="input"
          placeholder="输入问题... (Enter 发送)"
          :disabled="streaming || !wsReady"
          @keydown.enter="send"
        />
        <button class="chat-send" :disabled="!input.trim() || streaming || !wsReady" @click="send">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'

const props = defineProps({
  open: Boolean,
  detections: { type: Array, default: () => [] },
  imageBase64: { type: String, default: '' },
})

defineEmits(['close'])

const colors = ['#10b981','#3b82f6','#f59e0b','#ef4444','#8b5cf6','#ec4899','#06b6d4','#f97316']

const classMap = {
  'Apple Scab Leaf': '苹果疮痂病叶',
  'Apple leaf': '苹果叶',
  'Apple rust leaf': '苹果锈病叶',
  'Bell_pepper leaf': '甜椒叶',
  'Bell_pepper leaf spot': '甜椒叶斑病',
  'Blueberry leaf': '蓝莓叶',
  'Cherry leaf': '樱桃叶',
  'Corn Gray leaf spot': '玉米灰斑病',
  'Corn leaf blight': '玉米叶枯病',
  'Corn rust leaf': '玉米锈病叶',
  'Peach leaf': '桃叶',
  'Potato leaf': '马铃薯叶',
  'Potato leaf early blight': '马铃薯早疫病',
  'Potato leaf late blight': '马铃薯晚疫病',
  'Raspberry leaf': '覆盆子叶',
  'Soyabean leaf': '大豆叶',
  'Soybean leaf': '大豆叶',
  'Squash Powdery mildew leaf': '南瓜白粉病叶',
  'Strawberry leaf': '草莓叶',
  'Tomato Early blight leaf': '番茄早疫病叶',
  'Tomato Septoria leaf spot': '番茄斑枯病叶',
  'Tomato leaf': '番茄叶',
  'Tomato leaf bacterial spot': '番茄细菌性斑点病叶',
  'Tomato leaf late blight': '番茄晚疫病叶',
  'Tomato leaf mosaic virus': '番茄花叶病毒病叶',
  'Tomato leaf yellow virus': '番茄黄化曲叶病毒病叶',
  'Tomato mold leaf': '番茄叶霉病叶',
  'Tomato two spotted spider mites leaf': '番茄二斑叶螨为害叶',
  'grape leaf': '葡萄叶',
  'grape leaf black rot': '葡萄黑腐病叶',
}

function cnName(name) {
  return classMap[name] || name
}

const bodyRef = ref(null)
const input = ref('')
const error = ref('')
const messages = ref([])
const streamText = ref('')
const streaming = ref(false)
const wsReady = ref(false)
const ctxCollapsed = ref(false)

let ws = null
let reconnectTimer = null

function connect() {
  if (ws && ws.readyState === WebSocket.OPEN) return
  ws = new WebSocket('ws://localhost:8080/api/v1/ws/chat')

  ws.onopen = () => {
    wsReady.value = true
    error.value = ''
    if (props.detections.length || props.imageBase64) {
      ws.send(JSON.stringify({
        action: 'attach',
        detections: props.detections,
        image_base64: props.imageBase64,
      }))
    }
  }

  ws.onmessage = (e) => {
    const data = JSON.parse(e.data)
    if (data.type === 'token') {
      streamText.value += data.text
    } else if (data.type === 'done') {
      messages.value.push({ role: 'assistant', content: streamText.value })
      streamText.value = ''
      streaming.value = false
    } else if (data.type === 'error') {
      error.value = data.message
      streaming.value = false
    }
  }

  ws.onclose = () => {
    wsReady.value = false
    if (props.open) {
      reconnectTimer = setTimeout(connect, 3000)
    }
  }

  ws.onerror = () => {
    wsReady.value = false
    error.value = '连接失败，请确认后端服务已启动'
  }
}

function send() {
  const text = input.value.trim()
  if (!text || streaming.value || !wsReady.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  error.value = ''
  streaming.value = true
  streamText.value = ''
  ws.send(JSON.stringify({ action: 'ask', question: text }))
}

function renderMd(text) {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/^#{1,4}\s(.+)$/gm, '<strong class="chat-heading">$1</strong>')
    .replace(/^---+\s*$/gm, '<hr class="chat-hr"/>')
    .replace(/^\*\s+(.+)$/gm, '<li class="chat-li">• $1</li>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>')
    .replace(/<p>/g, '<p>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^-\s(.+)$/gm, '<li class="chat-li">• $1</li>')
    .replace(/^(\d+)\.\s(.+)$/gm, '<li class="chat-li">$1. $2</li>')
}

watch(() => props.open, (v) => {
  if (v) {
    messages.value = []
    streamText.value = ''
    streaming.value = false
    error.value = ''
    nextTick(connect)
  } else {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    if (ws) { ws.onclose = null; ws.close() }
    ws = null
    wsReady.value = false
  }
})

watch(() => [props.detections, props.imageBase64], () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      action: 'attach',
      detections: props.detections,
      image_base64: props.imageBase64,
    }))
  }
})

watch([messages, streamText], () => {
  nextTick(() => {
    if (bodyRef.value) bodyRef.value.scrollTop = bodyRef.value.scrollHeight
  })
}, { deep: true })

onBeforeUnmount(() => {
  if (reconnectTimer) clearTimeout(reconnectTimer)
  if (ws) { ws.onclose = null; ws.close() }
})
</script>

<style scoped>
.chat-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-md);
  overflow: hidden;
  min-width: 0;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid var(--c-border);
  flex-shrink: 0;
  background: linear-gradient(180deg, rgba(139,92,246,.04) 0%, transparent 100%);
}
.chat-header-left {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 14px;
  font-weight: 700;
  color: var(--c-txt);
}
.chat-close {
  border: none;
  background: transparent;
  color: var(--c-txt3);
  cursor: pointer;
  padding: 5px;
  border-radius: var(--r-xs);
  display: flex;
  transition: all .2s;
}
.chat-close:hover { color: var(--c-txt); background: rgba(255,255,255,.04); }

.chat-body {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.chat-body::-webkit-scrollbar { width: 3px; }
.chat-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,.04); border-radius: 2px; }

.chat-context {
  margin: 10px 14px 0;
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: var(--r-sm);
  overflow: hidden;
  flex-shrink: 0;
}
.chat-context-head {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 9px 14px;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--c-txt2);
  cursor: pointer;
  user-select: none;
  transition: background .2s;
}
.chat-context-head:hover { background: rgba(255,255,255,.02); }
.ctx-chevron {
  margin-left: auto;
  color: var(--c-txt3);
  transition: transform .25s;
}
.ctx-chevron--flip { transform: rotate(180deg); }
.chat-context-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  padding: 0 14px 10px;
}
.chat-context--collapsed .chat-context-list { display: none; }

.ctx-tag {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  background: rgba(255,255,255,.03);
  border: 1px solid rgba(255,255,255,.05);
  border-radius: 14px;
  font-size: 10.5px;
}
.ctx-dot { width: 4px; height: 4px; border-radius: 50%; flex-shrink: 0; }
.ctx-name { color: var(--c-txt2); font-weight: 500; }
.ctx-conf { color: var(--dc); font-weight: 600; font-family: var(--c-mono); }

.chat-msgs {
  flex: 1;
  padding: 10px 14px 12px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.chat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--c-txt3);
  font-size: 12px;
}

.chat-msg { display: flex; gap: 8px; }
.chat-msg--user { flex-direction: row-reverse; }
.chat-msg-avatar {
  width: 26px; height: 26px;
  border-radius: 50%;
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.chat-msg-bubble {
  max-width: 80%;
  padding: 9px 13px;
  border-radius: 12px;
  font-size: 12.5px;
  line-height: 1.7;
  color: var(--c-txt2);
  word-break: break-word;
}
.chat-msg--assistant .chat-msg-bubble {
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-left: 3px solid rgba(139,92,246,.30);
  border-top-left-radius: 4px;
}
.chat-msg--user .chat-msg-bubble {
  background: rgba(139,92,246,.12);
  border: 1px solid rgba(139,92,246,.16);
  border-top-right-radius: 4px;
  color: var(--c-txt);
}

.chat-msg-bubble :deep(p) { margin-bottom: 6px; }
.chat-msg-bubble :deep(p:last-child) { margin-bottom: 0; }
.chat-msg-bubble :deep(strong) { color: var(--c-txt); font-weight: 600; }
.chat-msg-bubble :deep(.chat-heading) {
  display: block;
  margin-top: 10px;
  margin-bottom: 3px;
  font-size: 13px;
  color: var(--c-gold);
  font-weight: 700;
}
.chat-msg-bubble :deep(.chat-heading:first-child) { margin-top: 0; }
.chat-msg-bubble :deep(.chat-hr) {
  border: none;
  border-top: 1px solid var(--c-border);
  margin: 8px 0;
}
.chat-msg-bubble :deep(.chat-li) {
  display: block;
  padding-left: 2px;
  margin-bottom: 3px;
}

.chat-cursor {
  color: var(--c-purple);
  animation: blink 1s step-end infinite;
}
@keyframes blink { 50% { opacity: 0; } }

.chat-foot { padding: 10px 14px 14px; border-top: 1px solid var(--c-border); flex-shrink: 0; }
.chat-err {
  font-size: 11px;
  color: var(--c-red);
  margin-bottom: 6px;
  padding: 5px 8px;
  background: rgba(239,68,68,.06);
  border-radius: var(--r-xs);
}
.chat-input-row { display: flex; gap: 6px; }
.chat-input {
  flex: 1;
  padding: 8px 12px;
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: 10px;
  color: var(--c-txt);
  font-size: 12.5px;
  font-family: var(--c-sans);
  transition: border-color .25s, box-shadow .25s;
}
.chat-input:focus {
  outline: none;
  border-color: rgba(139,92,246,.40);
  box-shadow: 0 0 0 3px rgba(139,92,246,.05);
}
.chat-input::placeholder { color: var(--c-txt3); font-size: 11.5px; }
.chat-input:disabled { opacity: .4; }

.chat-send {
  width: 34px; height: 34px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--c-border);
  border-radius: 10px;
  background: var(--c-bg);
  color: var(--c-txt3);
  cursor: pointer;
  transition: all .2s;
}
.chat-send:hover:not(:disabled) {
  border-color: var(--c-purple);
  background: rgba(139,92,246,.12);
  color: var(--c-purple);
}
.chat-send:disabled { opacity: .35; cursor: not-allowed; }
</style>
