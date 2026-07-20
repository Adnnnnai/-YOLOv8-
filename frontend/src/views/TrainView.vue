<template>
  <div class="pg">
    <div class="pg-head">
      <h2>训练任务</h2>
    </div>

    <div class="dash">
      <!-- 左侧控制台 -->
      <aside class="dash-side">
        <div class="ring-box">
          <svg viewBox="0 0 200 200" class="ring-svg">
            <defs>
              <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#10b981"/>
              </linearGradient>
            </defs>
            <circle cx="100" cy="100" r="82" fill="none" stroke="rgba(255,255,255,.025)" stroke-width="10"/>
            <circle cx="100" cy="100" r="82" fill="none" stroke="url(#ringGrad)" stroke-width="10"
                    stroke-linecap="round"
                    :stroke-dasharray="515"
                    :stroke-dashoffset="515 * (1 - animPct)"
                    transform="rotate(-90 100 100)"
                    style="transition: stroke-dashoffset 0.6s ease-in-out"/>
          </svg>
          <div class="ring-center">
            <span class="ring-val">{{ currentEpoch }}</span>
            <span class="ring-unit">轮</span>
          </div>
        </div>

        <div class="side-meta">
          <div class="side-item">
            <span class="side-item-lab">训练时长</span>
            <span class="side-item-val">{{ trainingTime }}</span>
          </div>
          <div class="side-item">
            <span class="side-item-lab">最终损失</span>
            <span class="side-item-val">{{ finalLoss }}</span>
          </div>
          <div class="side-item">
            <span class="side-item-lab">最佳 mAP@0.5</span>
            <span class="side-item-val" style="color:var(--c-green)">{{ bestMap }}</span>
          </div>
          <div class="side-item">
            <span class="side-item-lab">mAP@0.5-0.95</span>
            <span class="side-item-val">{{ bestMap95 }}</span>
          </div>
        </div>
      </aside>

      <!-- 右侧图表区 2x2 -->
      <div class="dash-charts">
        <div class="chart-card">
          <div class="chart-head">
            <span class="chart-title">损失率曲线</span>
            <div class="chart-legend">
              <span class="legend-item"><i style="background:#3b82f6"></i>边界框损失</span>
              <span class="legend-item"><i style="background:#f59e0b"></i>分类损失</span>
              <span class="legend-item"><i style="background:#8b5cf6"></i>DFL 损失</span>
            </div>
          </div>
          <svg viewBox="0 0 560 180" class="chart-svg" preserveAspectRatio="none">
            <defs>
              <linearGradient id="lossAreaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#3b82f6" stop-opacity=".12"/>
                <stop offset="100%" stop-color="#3b82f6" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <line x1="0" y1="45" x2="560" y2="45" stroke="rgba(255,255,255,.015)" stroke-width="1"/>
            <line x1="0" y1="90" x2="560" y2="90" stroke="rgba(255,255,255,.015)" stroke-width="1"/>
            <line x1="0" y1="135" x2="560" y2="135" stroke="rgba(255,255,255,.015)" stroke-width="1"/>
            <polygon :points="lossArea" fill="url(#lossAreaGrad)"/>
            <polyline :points="boxLossLine" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round"/>
            <polyline :points="clsLossLine" fill="none" stroke="#f59e0b" stroke-width="1.5" stroke-linecap="round" opacity=".6"/>
            <polyline :points="dflLossLine" fill="none" stroke="#8b5cf6" stroke-width="1.5" stroke-linecap="round" opacity=".6"/>
          </svg>
        </div>

        <div class="chart-card">
          <div class="chart-head">
            <span class="chart-title">mAP 曲线</span>
            <div class="chart-legend">
              <span class="legend-item"><i style="background:#10b981"></i>mAP@0.5</span>
              <span class="legend-item"><i style="background:#06b6d4"></i>mAP@0.5-0.95</span>
            </div>
          </div>
          <svg viewBox="0 0 560 180" class="chart-svg" preserveAspectRatio="none">
            <defs>
              <linearGradient id="mapAreaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#10b981" stop-opacity=".12"/>
                <stop offset="100%" stop-color="#10b981" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <line x1="0" y1="45" x2="560" y2="45" stroke="rgba(255,255,255,.015)" stroke-width="1"/>
            <line x1="0" y1="90" x2="560" y2="90" stroke="rgba(255,255,255,.015)" stroke-width="1"/>
            <line x1="0" y1="135" x2="560" y2="135" stroke="rgba(255,255,255,.015)" stroke-width="1"/>
            <polygon :points="mapArea" fill="url(#mapAreaGrad)"/>
            <polyline :points="map50Line" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round"/>
            <polyline :points="map95Line" fill="none" stroke="#06b6d4" stroke-width="1.5" stroke-linecap="round" opacity=".6"/>
          </svg>
        </div>

        <div class="chart-card">
          <div class="chart-head">
            <span class="chart-title">准确率 / 召回率</span>
            <div class="chart-legend">
              <span class="legend-item"><i style="background:#ec4899"></i>准确率</span>
              <span class="legend-item"><i style="background:#06b6d4"></i>召回率</span>
            </div>
          </div>
          <svg viewBox="0 0 560 180" class="chart-svg" preserveAspectRatio="none">
            <defs>
              <linearGradient id="prAreaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#ec4899" stop-opacity=".08"/>
                <stop offset="100%" stop-color="#ec4899" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <line x1="0" y1="45" x2="560" y2="45" stroke="rgba(255,255,255,.015)" stroke-width="1"/>
            <line x1="0" y1="90" x2="560" y2="90" stroke="rgba(255,255,255,.015)" stroke-width="1"/>
            <line x1="0" y1="135" x2="560" y2="135" stroke="rgba(255,255,255,.015)" stroke-width="1"/>
            <polygon :points="precisionArea" fill="url(#prAreaGrad)"/>
            <polyline :points="precisionLine" fill="none" stroke="#ec4899" stroke-width="2" stroke-linecap="round"/>
            <polyline :points="recallLine" fill="none" stroke="#06b6d4" stroke-width="1.5" stroke-linecap="round" opacity=".7"/>
          </svg>
        </div>

        <div class="chart-card">
          <div class="chart-head">
            <span class="chart-title">学习率</span>
          </div>
          <svg viewBox="0 0 560 180" class="chart-svg" preserveAspectRatio="none">
            <defs>
              <linearGradient id="lrAreaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#f59e0b" stop-opacity=".10"/>
                <stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <line x1="0" y1="45" x2="560" y2="45" stroke="rgba(255,255,255,.015)" stroke-width="1"/>
            <line x1="0" y1="90" x2="560" y2="90" stroke="rgba(255,255,255,.015)" stroke-width="1"/>
            <line x1="0" y1="135" x2="560" y2="135" stroke="rgba(255,255,255,.015)" stroke-width="1"/>
            <polygon :points="lrArea" fill="url(#lrAreaGrad)"/>
            <polyline :points="lrLine" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const trainName = ref('')
const totalEpochs = ref(0)
const animPct = ref(0)
const epochs = ref([])

const currentEpoch = computed(() => totalEpochs.value)
const pct = computed(() => totalEpochs.value > 0 ? 1 : 0)

const finalLoss = computed(() => {
  if (epochs.value.length === 0) return '—'
  const last = epochs.value[epochs.value.length - 1]
  return (last['train/box_loss'] ?? 0).toFixed(4)
})

const bestMap = computed(() => {
  if (epochs.value.length === 0) return '—'
  let best = 0
  epochs.value.forEach(e => { const v = e['metrics/mAP50(B)'] ?? 0; if (v > best) best = v })
  return best.toFixed(4)
})

const bestMap95 = computed(() => {
  if (epochs.value.length === 0) return '—'
  let best = 0
  epochs.value.forEach(e => { const v = e['metrics/mAP50-95(B)'] ?? 0; if (v > best) best = v })
  return best.toFixed(4)
})

const trainingTime = computed(() => {
  if (epochs.value.length === 0) return '—'
  const sec = epochs.value[epochs.value.length - 1]['time'] ?? 0
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = Math.floor(sec % 60)
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`
})

const boxLossLine = ref('')
const clsLossLine = ref('')
const dflLossLine = ref('')
const lossArea = ref('')
const map50Line = ref('')
const map95Line = ref('')
const mapArea = ref('')
const precisionLine = ref('')
const recallLine = ref('')
const precisionArea = ref('')
const lrLine = ref('')
const lrArea = ref('')

function polyline(rows, key, w = 560, h = 180, pad = 20) {
  if (rows.length < 2) return ''
  const vals = rows.map(r => r[key] ?? 0)
  const max = Math.max(...vals) * 1.06 || 1
  const min = Math.min(...vals) * 0.94
  const range = (max - min) || 1
  const n = rows.length
  return rows.map((r, i) => {
    const x = (i / (n - 1)) * w
    const y = h - pad - ((r[key] - min) / range) * (h - pad * 2)
    return `${x.toFixed(1)},${Math.max(pad, Math.min(h - pad, y)).toFixed(1)}`
  }).join(' ')
}

function polyarea(rows, key, w = 560, h = 180, pad = 20) {
  const l = polyline(rows, key, w, h, pad)
  if (!l) return `0,${h} ${w},${h}`
  return `${l} ${w},${h} 0,${h}`
}

onMounted(async () => {
  try {
    const { data } = await api.get('/train/results')
    epochs.value = data.epochs || []
    totalEpochs.value = data.total_epochs || 0
    trainName.value = data.train_name || ''

    // 进度环循环动画：0→满→0→满
    const runRing = () => {
      animPct.value = 0
      let dir = 1
      let p = 0
      const tick = () => {
        p += 0.008 * dir
        animPct.value = p
        if (p >= 1) { dir = -1 }
        if (p <= 0) { dir = 1 }
        requestAnimationFrame(tick)
      }
      requestAnimationFrame(tick)
    }
    runRing()

    boxLossLine.value = polyline(epochs.value, 'train/box_loss')
    clsLossLine.value = polyline(epochs.value, 'train/cls_loss')
    dflLossLine.value = polyline(epochs.value, 'train/dfl_loss')
    lossArea.value = polyarea(epochs.value, 'train/box_loss')

    map50Line.value = polyline(epochs.value, 'metrics/mAP50(B)')
    map95Line.value = polyline(epochs.value, 'metrics/mAP50-95(B)')
    mapArea.value = polyarea(epochs.value, 'metrics/mAP50(B)')

    precisionLine.value = polyline(epochs.value, 'metrics/precision(B)')
    recallLine.value = polyline(epochs.value, 'metrics/recall(B)')
    precisionArea.value = polyarea(epochs.value, 'metrics/precision(B)')

    lrLine.value = polyline(epochs.value, 'lr/pg0')
    lrArea.value = polyarea(epochs.value, 'lr/pg0')
  } catch (e) {
    console.error('加载训练数据失败', e)
  }
})
</script>

<style scoped>
/* ====== 整体栅格 ====== */
.dash {
  flex: 1;
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 20px;
  min-height: 0;
}

/* ====== 左侧控制台 ====== */
.dash-side {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.ring-box {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-md);
  padding: 28px 0 32px;
  display: flex;
  justify-content: center;
  position: relative;
}
.ring-svg { width: 180px; height: 180px; }
.ring-center {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}
.ring-val {
  font-size: 48px; font-weight: 700;
  font-family: var(--c-mono);
  color: var(--c-txt);
  line-height: 1;
}
.ring-unit {
  font-size: 13px;
  font-family: var(--c-mono);
  color: var(--c-txt3);
  margin-top: 6px;
  letter-spacing: 0.06em;
}

.side-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.side-item {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-sm);
  padding: 18px 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  transition: all .25s ease;
}
.side-item:hover {
  border-color: var(--c-border-h);
  box-shadow: var(--shadow-sm);
}
.side-item-lab {
  display: block;
  font-size: 11.5px;
  font-weight: 500;
  color: var(--c-txt3);
  margin-bottom: 6px;
  letter-spacing: 0.04em;
}
.side-item-val {
  display: block;
  font-size: 24px;
  font-weight: 700;
  font-family: var(--c-mono);
  color: var(--c-txt);
}

/* ====== 右侧图表区 ====== */
.dash-charts {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  min-height: 0;
}

.chart-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-md);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all .25s ease;
  min-height: 0;
}

.chart-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px 10px;
  flex-shrink: 0;
}
.chart-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--c-txt);
}

.chart-legend {
  display: flex;
  gap: 14px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  font-family: var(--c-mono);
  color: var(--c-txt3);
  letter-spacing: 0.02em;
}
.legend-item i {
  display: inline-block;
  width: 10px; height: 2px;
  border-radius: 2px;
}

.chart-svg {
  width: 100%;
  height: 100%;
  display: block;
  min-height: 0;
}
</style>
