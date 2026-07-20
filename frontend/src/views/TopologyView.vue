<template>
  <div class="pg" style="display:flex;flex-direction:column;min-height:0;padding:32px 36px 36px">
    <div class="pg-head">
      <h2>系统概览</h2>
      <div class="status-tag">
        <span class="status-dot"></span>
        <span>推理引擎就绪</span>
      </div>
    </div>

    <div class="hero-card">
      <div class="flow-row">
        <div class="flow-col" v-for="n in nodes" :key="n.title" :style="{'--ac': n.color}">
          <span class="flow-label">{{ n.title }}</span>
          <div class="flow-icon" :class="{ 'flow-icon--ripple': n.title === '推理舱' }" v-html="n.icon"></div>
        </div>
      </div>

      <div class="kpi-row">
        <div class="kpi" v-for="k in kpis" :key="k.label" :style="{'--kc': k.color}">
          <span class="kpi-val">{{ k.val }}</span>
          <span class="kpi-lab">{{ k.label }}</span>
        </div>
      </div>
    </div>

    <div class="bottom-row">
      <div class="info-card">
        <div class="info-card-head">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
          <h3>平台简介</h3>
        </div>
        <p>面向智慧农业的作物叶片病害自动检测平台，支持 <span class="hl">29 类</span> 常见病害的智能识别。上传叶片照片即可实时输出病害类型、置信度与精确位置，辅助快速诊断决策。</p>
      </div>

      <div class="info-card">
        <div class="info-card-head">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="1.6" stroke-linecap="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
          <h3>核心能力</h3>
        </div>
        <ul class="info-list">
          <li v-for="(item, i) in coreAbilities" :key="i" v-html="item"></li>
        </ul>
      </div>

      <div class="info-card">
        <div class="info-card-head">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" stroke-width="1.6" stroke-linecap="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          <h3>使用流程</h3>
        </div>
        <ol class="info-steps">
          <li v-for="(item, i) in steps" :key="i" v-html="item"></li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useSystemStore } from '../stores/system'

const store = useSystemStore()

const nodes = [
  { title: '数据源',  color: '#10b981', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>' },
  { title: '训练舱',  color: '#3b82f6', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="5"/></svg>' },
  { title: '推理舱',  color: '#8b5cf6', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>' },
  { title: 'API 网关', color: '#06b6d4', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>' },
]

const kpis = computed(() => [
  { val: store.images.total?.toLocaleString() || '—', label: '训练图片', color: '#10b981' },
  { val: store.numClasses,            label: '病害类别', color: '#3b82f6' },
  { val: '0.632',                     label: 'mAP @ 0.5', color: '#8b5cf6' },
  { val: store.latency > 0 ? store.latency + ' ms' : '—', label: '推理延迟', color: '#06b6d4' },
])

const coreAbilities = [
  '覆盖<span class="hl">苹果、番茄、玉米、葡萄</span>等主要农作物的 <span class="hl">29 类病害识别</span>',
  '单图<span class="hl">毫秒级</span>响应，支持<span class="hl">批量并行检测</span>',
  '检测结果<span class="hl">可视化标注</span>，边界框与类别标签叠加显示',
  '完整保留<span class="hl">训练曲线与权重版本</span>，支持<span class="hl">一键回滚</span>',
]

const steps = [
  '在<span class="hl">配置中心</span>检查推理参数',
  '进入<span class="hl">推理检测</span>上传叶片图片',
  '查看检测结果与可视化标注',
  '按需导出 CSV 检测报告',
]
</script>

<style scoped>
.pg-head {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 28px;
}
.pg-head h2 { margin: 0; }

.status-tag {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 4px 14px;
  border-radius: 20px;
  background: rgba(16,185,129,.07);
  border: 1px solid rgba(16,185,129,.16);
  font-size: 11.5px;
  font-weight: 600;
  color: var(--c-green);
}
.status-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--c-green);
  box-shadow: 0 0 8px rgba(16,185,129,.5);
}

/* ====== 主卡片 ====== */
.hero-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-lg);
  padding: 48px 48px 40px;
  margin-bottom: 24px;
}

/* ====== 流程 ====== */
.flow-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  margin-bottom: 40px;
}

.flow-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.flow-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--c-txt3);
  letter-spacing: 0.06em;
}

.flow-icon {
  width: 48px; height: 48px;
  border-radius: 14px;
  background: rgba(255,255,255,.025);
  border: 1px solid var(--c-border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ac);
  transition: all .3s ease;
  position: relative;
}
.flow-col:hover .flow-icon {
  transform: translateY(-2px);
  border-color: color-mix(in srgb, var(--ac) 25%, transparent);
  box-shadow: 0 8px 24px color-mix(in srgb, var(--ac) 18%, transparent);
}

.flow-icon--ripple::before,
.flow-icon--ripple::after {
  content: '';
  position: absolute;
  inset: -5px;
  border-radius: 18px;
  border: 1.5px solid rgba(139,92,246,.22);
  animation: rippleOut 2.4s ease-out infinite;
}
.flow-icon--ripple::after { animation-delay: 1.2s; }
@keyframes rippleOut {
  0%   { transform: scale(1);   opacity: .5; }
  100% { transform: scale(1.4); opacity: 0; }
}

/* ====== KPI ====== */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.kpi {
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: var(--r-sm);
  padding: 34px 20px;
  text-align: center;
  transition: all .3s ease;
}
.kpi:hover {
  transform: translateY(-2px);
  border-color: color-mix(in srgb, var(--kc) 25%, transparent);
  box-shadow: 0 8px 28px color-mix(in srgb, var(--kc) 10%, transparent);
}

.kpi-val {
  display: block;
  font-size: 40px;
  font-weight: 600;
  font-family: var(--c-mono);
  letter-spacing: -0.04em;
  line-height: 1;
  margin-bottom: 12px;
  color: var(--kc);
  text-shadow: 0 0 14px color-mix(in srgb, var(--kc) 28%, transparent);
}

.kpi-lab {
  font-size: 11.5px;
  font-weight: 500;
  font-family: var(--c-sans);
  color: var(--c-txt3);
  letter-spacing: 0.04em;
}

/* ====== 底部三列 ====== */
.bottom-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 24px;
}

.info-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-md);
  padding: 38px 38px 42px;
}

.info-card-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
}
.info-card-head h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--c-txt);
  margin: 0;
}

.info-card p {
  font-size: 14px;
  color: var(--c-txt2);
  line-height: 1.9;
}

.info-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.info-list li {
  font-size: 13.5px;
  color: var(--c-txt2);
  line-height: 1.75;
  padding-left: 18px;
  position: relative;
}
.info-list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  width: 5px; height: 5px;
  border-radius: 1px;
  background: var(--c-blue);
  transform: rotate(45deg);
  box-shadow: 0 0 6px rgba(59,130,246,.4);
}

.info-steps {
  list-style: none;
  counter-reset: step;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.info-steps li {
  counter-increment: step;
  font-size: 13.5px;
  color: var(--c-txt2);
  line-height: 1.75;
  padding-left: 34px;
  position: relative;
  min-height: 24px;
  display: flex;
  align-items: flex-start;
}
.info-steps li::before {
  content: counter(step);
  position: absolute;
  left: 0;
  top: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(139,92,246,.08);
  color: var(--c-purple);
  font-size: 11px;
  font-weight: 600;
  font-family: var(--c-mono);
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.hl {
  color: var(--c-green);
  font-weight: 600;
}
</style>
