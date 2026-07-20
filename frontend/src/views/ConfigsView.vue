<template>
  <div class="pg" style="display:flex;flex-direction:column;min-height:0;padding:32px 36px 36px">
    <div class="pg-head">
      <h2>配置中心</h2>
    </div>

    <!-- 主布局：左 Tab 栏 + 右表单 -->
    <div class="config-dash">
      <!-- 左侧 Tab 导航 -->
      <div class="config-side">
        <button
          v-for="t in tabs"
          :key="t.k"
          class="config-tab"
          :class="{ 'config-tab--active': active === t.k }"
          @click="switchTab(t.k)"
        >
          <span class="config-tab-icon" v-html="t.icon"></span>
          <span class="config-tab-label">{{ t.label }}</span>
        </button>
      </div>

      <!-- 右侧表单 -->
      <div class="config-body">
        <div class="form-card card" :class="{ 'form-card--dirty': dirty }">
          <div class="form-card-head">
            <span class="form-card-title">{{ currentTabLabel }}</span>
            <span class="badge badge-gold" v-if="dirty">未保存</span>
            <span class="badge badge-green" v-if="saved">已保存</span>
          </div>

          <div class="form-body">
            <div class="field" v-for="(v, k) in flatFields" :key="k">
              <label class="field-label">{{ k }}</label>
              <input class="input" v-model="flatFields[k]" @input="dirty = true; saved = false"
                     :type="typeof v === 'number' ? 'number' : 'text'"
                     :step="typeof v === 'number' && String(v).includes('.') ? 0.01 : 1" />
              <span class="field-type">{{ typeof v }}</span>
            </div>
          </div>
        </div>

        <transition name="bar-slide">
          <div class="savebar" v-if="dirty">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--c-gold)" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            <span>检测到未保存的配置改动</span>
            <div class="savebar-spacer"></div>
            <button class="btn btn-ghost" @click="reset">丢弃更改</button>
            <button class="btn btn-primary" @click="save">保存并应用</button>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import api from '../api'

const active = ref('paths')
const dirty = ref(false)
const saved = ref(false)

const tabs = [
  { k: 'paths',     label: '系统路径', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>' },
  { k: 'training',  label: '训练参数', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><path d="M12 2v6M12 16v6"/></svg>' },
  { k: 'inference', label: '推理参数', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>' },
  { k: 'server',    label: 'API 服务', icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>' },
]

const sectionCache = reactive({
  paths: {},
  training: {},
  inference: {},
  server: {},
})

const flatFields = reactive({})

const currentTabLabel = computed(() => tabs.find(t => t.k === active.value)?.label ?? '')

async function loadAll() {
  try {
    const { data } = await api.get('/config')
    const c = data.config || {}
    sectionCache.paths = flattenSection(c.paths || {})
    sectionCache.training = flattenSection(c.training || {})
    sectionCache.inference = flattenSection(c.inference || {})
    sectionCache.server = flattenSection(c.server || {})
    switchTab(active.value)
  } catch (e) {
    console.error('加载配置失败', e)
  }
}

function flattenSection(obj) {
  const result = {}
  Object.entries(obj).forEach(([k, v]) => {
    if (typeof v === 'object' && v !== null && !Array.isArray(v)) {
      Object.entries(v).forEach(([sk, sv]) => {
        result[`${k}.${sk}`] = sv
      })
    } else {
      result[k] = v
    }
  })
  return result
}

function switchTab(k) {
  active.value = k
  dirty.value = false
  saved.value = false
  Object.keys(flatFields).forEach(k => delete flatFields[k])
  Object.assign(flatFields, sectionCache[k] || {})
}

function reset() {
  Object.keys(flatFields).forEach(k => delete flatFields[k])
  Object.assign(flatFields, sectionCache[active.value] || {})
  dirty.value = false
}

async function save() {
  try {
    const updates = {}
    updates[active.value] = sectionCache[active.value]
    await api.put('/config', { updates })
    Object.assign(sectionCache[active.value], { ...flatFields })
    Object.keys(flatFields).forEach(k => delete flatFields[k])
    Object.assign(flatFields, sectionCache[active.value])
    saved.value = true
    dirty.value = false
    setTimeout(() => { saved.value = false }, 2000)
  } catch (e) {
    console.error('保存配置失败', e)
  }
}

loadAll()
</script>

<style scoped>
/* ====== 布局：左 Tab + 右表单 ====== */
.config-dash {
  flex: 1;
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 24px;
  min-height: 0;
}

/* ====== 左侧 Tab ====== */
.config-side {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.config-tab {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid transparent;
  border-radius: var(--r-sm);
  background: transparent;
  color: var(--c-txt3);
  font-size: 13.5px;
  font-weight: 500;
  font-family: var(--c-sans);
  cursor: pointer;
  transition: all .2s ease;
  text-align: left;
}
.config-tab:hover {
  color: var(--c-txt2);
  background: rgba(255,255,255,.02);
}
.config-tab--active {
  color: var(--c-green);
  background: var(--c-surface);
  border-color: var(--c-border);
  font-weight: 600;
}

.config-tab-icon {
  opacity: .40;
  flex-shrink: 0;
}
.config-tab:hover .config-tab-icon { opacity: .65; }
.config-tab--active .config-tab-icon { opacity: 1; }

/* ====== 右侧表单 ====== */
.config-body {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
}

.form-card {
  padding: 0;
  overflow: hidden;
  transition: border-color .25s ease, box-shadow .25s ease;
}
.form-card--dirty {
  border-color: rgba(245,158,11,.18);
  box-shadow: 0 0 0 1px rgba(245,158,11,.06), 0 0 40px rgba(245,158,11,.03);
}

.form-card-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 24px;
  border-bottom: 1px solid var(--c-border);
}
.form-card-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--c-txt);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-body {
  flex: 1;
  overflow-y: auto;
}

.field {
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.field + .field { border-top: 1px solid var(--c-border); }

.field-label {
  width: 180px;
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 500;
  color: var(--c-txt2);
  font-family: var(--c-mono);
  letter-spacing: 0.02em;
}

.field .input { flex: 1; }

.field-type {
  width: 52px;
  flex-shrink: 0;
  font-size: 10px;
  font-weight: 600;
  color: var(--c-txt3);
  font-family: var(--c-mono);
  text-align: right;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* ====== 保存栏 ====== */
.savebar {
  position: fixed;
  bottom: 0;
  left: 250px;
  right: 0;
  padding: 16px 36px;
  background: rgba(12,14,20,.96);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-top: 1px solid rgba(245,158,11,.15);
  display: flex;
  align-items: center;
  gap: 14px;
  z-index: 60;
  font-size: 14px;
  color: var(--c-gold);
  font-weight: 500;
}
.savebar-spacer { flex: 1; }

.bar-slide-enter-active,
.bar-slide-leave-active {
  transition: transform .35s var(--ease-out);
}
.bar-slide-enter-from,
.bar-slide-leave-to {
  transform: translateY(100%);
}
</style>
