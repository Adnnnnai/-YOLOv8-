<template>
  <div class="pg" style="display:flex;flex-direction:column;min-height:0;padding:32px 36px 36px">
    <div class="pg-head">
      <h2>版本管理</h2>
    </div>

    <div class="timeline">
      <div class="tl-track"></div>

      <div class="tl-item" v-for="v in vers" :key="v.id" :class="{ 'tl-item--active': v.active }">
        <div class="tl-node" :class="{ 'tl-node--active': v.active }">
          <div class="tl-dot"></div>
          <span class="tl-ripple" v-if="v.active"></span>
          <span class="tl-ripple2" v-if="v.active"></span>
        </div>

        <div class="tl-card card" :class="{ 'tl-card--active': v.active }">
          <div class="tl-card-top">
            <span class="tl-ver">{{ v.ver }}</span>
            <span class="badge" :class="v.active ? 'badge-green' : 'badge-red'">
              {{ v.active ? '使用中' : '历史版本' }}
            </span>
          </div>

          <div class="tl-time">{{ v.time }}</div>

          <div class="tl-stats">
            <div class="tl-stat">
              <span class="tl-stat-label">数据集</span>
              <span class="tl-stat-val">{{ v.dataset }}</span>
            </div>
            <div class="tl-stat">
              <span class="tl-stat-label">权重文件</span>
              <span class="tl-stat-val">{{ v.weightsFileName }}</span>
            </div>
            <div class="tl-stat">
              <span class="tl-stat-label">mAP</span>
              <span class="tl-stat-val" :class="{ 'tl-stat-val--hi': v.map50 !== '—' }">{{ v.map50 }}</span>
            </div>
          </div>

          <div class="tl-actions">
            <template v-if="!v.active">
              <button class="btn btn-primary btn-sm" v-if="confirmId !== v.id" @click="confirmId = v.id">
                切换至此版本
              </button>
              <button class="btn btn-danger btn-sm" v-if="confirmId === v.id" @click="roll(v)">
                确认回滚
              </button>
              <button class="btn btn-ghost btn-sm" v-if="confirmId === v.id" @click="confirmId = null">
                取消
              </button>
            </template>
            <span class="tl-current" v-if="v.active">当前服务中</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 回滚遮罩 -->
    <transition name="overlay-fade">
      <div class="overlay" v-if="overlay">
        <div class="overlay-card">
          <div class="overlay-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="1.5" stroke-linecap="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <h3>{{ overlayError ? '回滚失败' : '正在执行版本回滚' }}</h3>
          <p v-if="!overlayError">
            Predictor 单例重新加载权重文件<br/>
            <code>{{ weightName }}</code>
          </p>
          <p v-else class="overlay-error">{{ overlayError }}</p>
          <div class="overlay-bar" v-if="!overlayError"><div class="overlay-fill"></div></div>
          <span class="overlay-status" :class="{ 'overlay-status--err': overlayError }">
            {{ overlayError ? '失败' : '加载中 ···' }}
          </span>
          <button class="btn btn-primary" v-if="overlayError" @click="overlay = false" style="margin-top:16px">关闭</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const confirmId = ref(null)
const overlay  = ref(false)
const weightName = ref('')
const overlayError = ref('')
const currentModel = ref('—')

async function fetchActiveModel() {
  try {
    const { data } = await api.get('/health')
    currentModel.value = data.model_name || ''
  } catch (e) { /* ignore */ }
}

onMounted(() => fetchActiveModel())

const vers = ref([
  { id: 'v1.6', ver: 'v1.6 — AI 智能诊断助手 + 全局异常处理', time: '2026-07-22  17:45', dataset: 'PlantDoc', weights: 'runs/train/plantdoc_yolov8n/weights/best.pt', weight_path: 'runs/train/plantdoc_yolov8n/weights/best.pt',
    weightsFileName: 'best.pt',   map50: '0.632', active: true  },
  { id: 'v1.5', ver: 'v1.5 — Vue3全栈前端重构 + 后端API扩展', time: '2026-07-21  22:00', dataset: 'PlantDoc', weights: 'runs/train/plantdoc_yolov8n/weights/best.pt', weight_path: 'runs/train/plantdoc_yolov8n/weights/best.pt',
    weightsFileName: 'best.pt',   map50: '0.632', active: false },
  { id: 'v1.4', ver: 'v1.4 — FastAPI 后端接口',             time: '2026-07-20  03:45', dataset: 'PlantDoc', weights: 'runs/train/plantdoc_yolov8n/weights/best.pt', weight_path: 'runs/train/plantdoc_yolov8n/weights/best.pt',
    weightsFileName: 'best.pt',   map50: '0.632', active: false },
  { id: 'v1.3', ver: 'v1.3 — 推理模块与可视化',             time: '2026-07-20  03:00', dataset: 'PlantDoc', weights: 'runs/train/plantdoc_yolov8n/weights/epoch60.pt', weight_path: 'runs/train/plantdoc_yolov8n/weights/epoch60.pt',
    weightsFileName: 'epoch60.pt', map50: '0.587', active: false },
  { id: 'v1.2', ver: 'v1.2 — YOLOv8n 模型训练完成',         time: '2026-07-20  02:30', dataset: 'PlantDoc', weights: 'runs/train/plantdoc_yolov8n/weights/epoch80.pt', weight_path: 'runs/train/plantdoc_yolov8n/weights/epoch80.pt',
    weightsFileName: 'epoch80.pt', map50: '0.610', active: false },
  { id: 'v1.1', ver: 'v1.1 — 数据集下载与 YOLO 格式配置',   time: '2026-07-20  01:30', dataset: 'PlantDoc', weights: 'runs/train/plantdoc_yolov8n/weights/epoch50.pt', weight_path: 'runs/train/plantdoc_yolov8n/weights/epoch50.pt',
    weightsFileName: 'epoch50.pt', map50: '0.542', active: false },
  { id: 'v1.0', ver: 'v1.0 — 项目初始化与基础架构搭建',     time: '2026-07-20  01:00', dataset: '—',            weights: '—',          weight_path: '',
    weightsFileName: '—',         map50: '—',    active: false },
])

async function roll(v) {
  if (confirmId.value !== v.id) return
  if (!v.weight_path) { confirmId.value = null; return }

  weightName.value = v.weights
  overlay.value = true
  overlayError.value = ''

  try {
    const { data } = await api.post('/model/rollback', { weight_path: v.weight_path })
    if (data.success) {
      overlay.value = false
      confirmId.value = null
      localStorage.setItem('activeModel', data.active_model)
      await fetchActiveModel()
    }
  } catch (e) {
    overlayError.value = e.response?.data?.detail || e.message || '回滚请求失败'
  }
}
</script>

<style scoped>
.timeline { position: relative; padding-left: 40px; }
.tl-track { position: absolute; left: 19px; top: 8px; bottom: 8px; width: 1px; background: linear-gradient(180deg, var(--c-border) 0%, var(--c-border-h) 20%, var(--c-border) 80%, transparent 100%); }
.tl-item { position: relative; margin-bottom: 24px; }
.tl-item:last-child { margin-bottom: 0; }

.tl-node { position: absolute; left: -30px; top: 18px; width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; }
.tl-dot { width: 11px; height: 11px; border-radius: 50%; background: #1e293b; border: 2px solid var(--c-bg); transition: all .35s var(--ease-out); position: relative; z-index: 1; }
.tl-node--active .tl-dot { background: var(--c-green); box-shadow: 0 0 14px rgba(16,185,129,.40); }

.tl-ripple,.tl-ripple2 {
  position: absolute; inset: -4px; border-radius: 50%;
  border: 1px solid rgba(16,185,129,.25);
  animation: rippleOut 2.2s var(--ease-out) infinite;
}
.tl-ripple2 { animation-delay: 1.1s; }
@keyframes rippleOut {
  0%   { transform: scale(.7); opacity: .6; }
  100% { transform: scale(2.8); opacity: 0; }
}

.tl-card { padding: 20px 24px; transition: all .35s var(--ease-out); }
.tl-card:hover { transform: translateY(-2px); }
.tl-card--active { border-color: rgba(16,185,129,.15); box-shadow: var(--shadow-glow); }

.tl-card-top { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.tl-ver { font-size: 15px; font-weight: 700; color: var(--c-txt); letter-spacing: -0.01em; }
.tl-time { font-size: 11.5px; color: var(--c-txt3); font-family: var(--c-mono); margin-bottom: 14px; letter-spacing: 0.02em; }

.tl-stats { display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 16px; }
.tl-stat { display: flex; flex-direction: column; gap: 2px; }
.tl-stat-label { font-size: 10px; font-weight: 600; color: var(--c-txt3); text-transform: uppercase; letter-spacing: 0.05em; }
.tl-stat-val { font-size: 13px; font-weight: 500; color: var(--c-txt2); font-family: var(--c-mono); }
.tl-stat-val--hi { color: var(--c-green); }

.tl-actions { display: flex; gap: 8px; align-items: center; }
.btn-sm { padding: 6px 14px; font-size: 12px; }
.tl-current { font-size: 12px; color: var(--c-txt3); font-weight: 500; padding: 6px 0; }

/* Overlay */
.overlay { position: fixed; inset: 0; z-index: 200; background: rgba(4,6,16,.90); display: flex; align-items: center; justify-content: center; backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); }
.overlay-card { background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-lg); padding: 48px 44px; text-align: center; max-width: 440px; width: 90%; }
.overlay-icon { margin-bottom: 16px; }
.overlay-card h3 { font-size: 19px; font-weight: 700; color: var(--c-txt); margin-bottom: 12px; }
.overlay-card p { font-size: 13px; color: var(--c-txt2); line-height: 1.8; margin-bottom: 24px; }
.overlay-card code { color: var(--c-gold); background: rgba(245,158,11,.08); padding: 2px 8px; border-radius: 4px; font-family: var(--c-mono); font-size: 12px; }
.overlay-error { color: var(--c-red) !important; }
.overlay-bar { height: 3px; background: rgba(255,255,255,.05); border-radius: 2px; overflow: hidden; margin-bottom: 16px; }
.overlay-fill { height: 100%; width: 100%; background: linear-gradient(90deg, var(--c-blue), var(--c-green)); animation: barFill 2s linear forwards; }
@keyframes barFill { 0% { width: 0; } 100% { width: 100%; } }
.overlay-status { font-size: 14px; font-weight: 600; color: var(--c-gold); font-family: var(--c-mono); animation: softBlink 1.3s ease-in-out infinite; }
.overlay-status--err { color: var(--c-red); animation: none; }
@keyframes softBlink { 0%,100%{ opacity: 1; } 50%{ opacity: .35; } }
.overlay-fade-enter-active,.overlay-fade-leave-active { transition: opacity .3s var(--ease-out); }
.overlay-fade-enter-from,.overlay-fade-leave-to { opacity: 0; }
</style>
