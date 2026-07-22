<template>
  <div class="pg" style="display:flex;flex-direction:column;min-height:0;padding:32px 36px 36px">
    <div class="pg-head">
      <h2>推理检测</h2>
    </div>

    <!-- 两栏：上传 + 结果（单图模式） -->
    <div class="dual-panel" v-if="!batchMode">
      <div class="panel card" :class="{ 'panel--drag': hovering }" @dragover.prevent @drop.prevent="onDrop">
        <div class="panel-header">
          <span>输入图片</span>
          <div class="panel-header-right">
            <label class="batch-btn"><input type="file" accept="image/*" multiple hidden @change="onBatch" />多张上传</label>
            <button class="panel-action" v-if="src" @click="clear">清除</button>
          </div>
        </div>
        <div class="panel-body" v-if="!src">
          <div class="dropzone" @click="$refs.fileInput.click()" @dragover.prevent="hovering = true" @dragleave.prevent="hovering = false">
            <div class="dropzone-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
            </div>
            <span class="dropzone-main">拖拽图片到此处</span>
            <span class="dropzone-sub">或点击选择文件 · 支持多选批量</span>
          </div>
        </div>
        <div class="panel-body" v-else>
          <canvas ref="canvasRef" class="preview-canvas"></canvas>
        </div>
        <input type="file" ref="fileInput" accept="image/*" @change="onFile" hidden />
      </div>

      <div class="panel card">
        <div class="panel-header">
          <span>检测结果</span>
          <div class="panel-header-right">
            <span class="badge badge-green" v-if="dets.length">{{ dets.length }} 个目标</span>
            <span class="badge badge-blue" v-if="latency">延迟 {{ latency }}ms</span>
            <span class="panel-hint" v-else>等待检测 ···</span>
          </div>
        </div>
        <div class="panel-body" v-if="src">
          <canvas ref="resultCanvasRef" class="preview-canvas"></canvas>
        </div>
        <div class="panel-body panel-body--empty" v-else>
          <div class="empty-state">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" opacity=".3">
              <rect x="3" y="3" width="18" height="18" rx="3"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
            <span>上传图片后查看检测结果</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 单图检测列表 -->
    <div class="det-section" v-if="!batchMode && dets.length">
      <div class="det-section-header">
        <span>检测目标列表</span>
        <div style="display:flex;gap:8px;align-items:center">
          <button class="btn btn-ghost btn-sm" @click="exportCSV">导出 CSV</button>
          <button class="btn btn-ghost btn-sm" @click="exportPDF">导出 PDF</button>
          <button class="btn-chat-hero" @click="openChat">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 1 0 10 10H12V2z"/><path d="M12 2a10 10 0 0 1 10 10h-2a8 8 0 0 0-8-8V2z"/><circle cx="12" cy="12" r="3"/></svg>
            AI 智能诊断
          </button>
        </div>
      </div>
      <div class="det-row">
        <div class="det-card" v-for="(d, i) in dets" :key="i" :style="{'--dc': d.color}">
          <div class="det-bar" :style="{background: `var(--dc)`}"></div>
          <div class="det-info">
            <span class="det-name">{{ cnName(d.class_name) }}</span>
            <span class="det-conf">{{ (d.confidence * 100).toFixed(1) }}%</span>
            <span class="det-bbox">{{ d.bbox.map(v => Math.round(v)).join(', ') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量结果 -->
    <div class="batch-panel" v-if="batchMode">
      <div class="det-section-header">
        <span>批量检测结果 ({{ batchItems.length }} 张)</span>
        <div style="display:flex;gap:8px">
          <button class="btn btn-ghost btn-sm" @click="exportBatchCSV">导出全部 CSV</button>
          <button class="btn btn-ghost btn-sm" @click="exportBatchPDF">导出 PDF</button>
          <button class="btn btn-ghost btn-sm" @click="clear" style="color:var(--c-red)">关闭</button>
        </div>
      </div>

      <div class="batch-list">
        <div class="batch-row card" v-for="(item, i) in batchItems" :key="i">
          <div class="batch-thumb" @click="previewBatchImage(item.file)">
            <canvas :ref="el => setBatchCanvas(el, i)" class="batch-canvas"></canvas>
            <span class="batch-overlay">点击查看</span>
          </div>
          <div class="batch-content">
            <div class="batch-filename">{{ item.file.name }}</div>
            <div class="batch-summary">
              <span class="badge badge-green" v-if="item.detections.length">{{ item.detections.length }} 个目标</span>
              <span class="badge badge-red" v-if="item.error">{{ item.error }}</span>
              <span class="badge badge-blue" v-if="item.latency">延迟 {{ item.latency }}ms</span>
              <span class="batch-empty" v-if="!item.detections.length && !item.error">无检测目标</span>
            </div>
            <div class="batch-dets" v-if="item.detections.length">
              <div class="batch-det" v-for="(d, j) in item.detections" :key="j">
                <span class="batch-det-name">{{ cnName(d.class_name) }}</span>
                <span class="batch-det-conf">{{ (d.confidence * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
          <button class="btn-chat-batch" v-if="item.detections.length" @click="openBatchChat(i)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 1 0 10 10H12V2z"/><path d="M12 2a10 10 0 0 1 10 10h-2a8 8 0 0 0-8-8V2z"/><circle cx="12" cy="12" r="3"/></svg>
            AI 诊断
          </button>
        </div>
      </div>
    </div>

    <!-- 缩略图详情弹层 -->
    <transition name="ov">
      <div class="preview-overlay" v-if="previewMode" @click.self="closePreview">
        <button class="preview-close" @click="closePreview">←  返回批量结果</button>
        <div class="dual-panel" style="width:100%;margin-bottom:0">
          <div class="panel card">
            <div class="panel-header"><span>原图</span></div>
            <div class="panel-body"><canvas ref="previewCanvasRef" class="preview-canvas"></canvas></div>
          </div>
          <div class="panel card">
            <div class="panel-header">
              <span>标注结果</span>
              <span class="badge badge-green" v-if="previewDets.length">{{ previewDets.length }} 个目标</span>
            </div>
            <div class="panel-body"><canvas ref="previewResultRef" class="preview-canvas"></canvas></div>
          </div>
        </div>
        <div class="det-row" v-if="previewDets.length" style="margin-top:14px">
          <div class="det-card" v-for="(d, i) in previewDets" :key="i" :style="{'--dc': d.color}">
            <div class="det-bar" :style="{background: `var(--dc)`}"></div>
            <div class="det-info">
              <span class="det-name">{{ cnName(d.class_name) }}</span>
              <span class="det-conf">{{ (d.confidence * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <ChatPanel :open="showChat" :detections="chatDetections" :image-base64="chatImageB64" @close="showChat = false" />
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import ChatPanel from '../components/ChatPanel.vue'

const src = ref(null)
const dets = ref([])
const latency = ref(0)
const hovering = ref(false)
const canvasRef = ref(null)
const resultCanvasRef = ref(null)

const batchMode = ref(false)
const batchFiles = ref([])
const batchItems = ref([])

const previewMode = ref(false)
const previewFile = ref(null)
const previewDets = ref([])
const previewLatency = ref(0)
const previewCanvasRef = ref(null)
const previewResultRef = ref(null)

const showChat = ref(false)
const chatImageB64 = ref('')
const chatDetections = ref([])

function openChat() {
  chatImageB64.value = ''
  chatDetections.value = dets.value
  if (resultCanvasRef.value) {
    const full = resultCanvasRef.value.toDataURL('image/jpeg', 0.6)
    chatImageB64.value = full.split(',')[1] || full
  }
  showChat.value = true
}

function openBatchChat(idx) {
  const item = batchItems.value[idx]
  if (!item) return
  chatDetections.value = item.detections || []
  chatImageB64.value = ''
  if (batchCanvases.value[idx]) {
    const full = batchCanvases.value[idx].toDataURL('image/jpeg', 0.6)
    chatImageB64.value = full.split(',')[1] || full
  }
  showChat.value = true
}

const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316']

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

const batchCanvases = ref([])
function setBatchCanvas(el, i) {
  if (el) batchCanvases.value[i] = el
}

function clear() {
  src.value = null
  dets.value = []
  latency.value = 0
  batchMode.value = false
  batchFiles.value = []
  batchItems.value = []
  batchCanvases.value = []
  previewMode.value = false
}

function onFile(e) {
  const f = e.target.files[0]
  if (f) process(f)
}

function onDrop(e) {
  hovering.value = false
  const files = e.dataTransfer.files
  if (files.length === 1) process(files[0])
  else if (files.length > 1) batchDetect([...files])
}

function previewBatchImage(file) {
  const existing = batchItems.value.find(b => b.file.name === file.name)
  previewFile.value = URL.createObjectURL(file)
  previewDets.value = existing?.detections || []
  previewLatency.value = existing?.latency || 0
  previewMode.value = true
  nextTick(() => {
    const img = new Image()
    img.onload = () => { drawImageToCanvas(previewCanvasRef.value, img) }
    img.src = previewFile.value
    fetchAnnotated(file)
  })
}

async function fetchAnnotated(file) {
  const fd = new FormData()
  fd.append('file', file)
  try {
    const r = await fetch('http://localhost:8080/api/v1/detect/annotated', { method: 'POST', body: fd })
    const d = await r.json()
    previewDets.value = (d.detections || []).map((det, i) => ({ ...det, color: colors[i % colors.length] }))
    previewLatency.value = d.latency_ms || 0
    if (d.image_base64) {
      const annImg = new Image()
      annImg.onload = () => { drawImageToCanvas(previewResultRef.value, annImg) }
      annImg.src = 'data:image/jpeg;base64,' + d.image_base64
    }
  } catch (e) { console.error('标注接口失败', e) }
}

function closePreview() {
  previewMode.value = false
  previewFile.value = null
  previewDets.value = []
}

async function onBatch(e) {
  const files = [...e.target.files]
  if (files.length === 0) return
  if (files.length === 1) { process(files[0]); return }
  await batchDetect(files)
}

async function batchDetect(files) {
  batchMode.value = true
  batchFiles.value = files
  batchItems.value = files.map(f => ({ file: f, detections: [], latency: 0, error: '' }))

  nextTick(() => {
    files.forEach((f, i) => {
      const url = URL.createObjectURL(f)
      const img = new Image()
      img.onload = () => {
        const canvas = batchCanvases.value[i]
        if (canvas) {
          canvas.width = img.naturalWidth
          canvas.height = img.naturalHeight
          canvas.getContext('2d').drawImage(img, 0, 0)
        }
      }
      img.src = url
    })
  })

  const fd = new FormData()
  files.forEach(f => fd.append('files', f))
  try {
    const r = await fetch('http://localhost:8080/api/v1/detect/batch', { method: 'POST', body: fd })
    const data = await r.json()
    data.forEach((d, i) => {
      if (i < batchItems.value.length) {
        batchItems.value[i].detections = d.detections || []
        batchItems.value[i].latency = d.latency_ms || 0
        batchItems.value[i].error = d.error || ''
      }
    })
  } catch (e) {
    console.error('批量检测失败', e)
  }
}

async function process(file) {
  batchMode.value = false
  src.value = URL.createObjectURL(file)

  const img = new Image()
  img.onload = () => { drawImageToCanvas(canvasRef.value, img) }
  img.src = src.value

  const fd = new FormData()
  fd.append('file', file)
  try {
    const r = await fetch('http://localhost:8080/api/v1/detect/annotated', { method: 'POST', body: fd })
    const d = await r.json()
    dets.value = (d.detections || []).map((det, i) => ({ ...det, color: colors[i % colors.length] }))
    latency.value = d.latency_ms || 0
    if (d.image_base64) {
      const annImg = new Image()
      annImg.onload = () => { drawImageToCanvas(resultCanvasRef.value, annImg) }
      annImg.src = 'data:image/jpeg;base64,' + d.image_base64
    }
  } catch (e) {
    console.error('检测失败', e)
  }
}

function drawImageToCanvas(canvas, img) {
  if (!canvas || !canvas.parentElement) return
  const ctx = canvas.getContext('2d')
  canvas.width = img.naturalWidth
  canvas.height = img.naturalHeight
  const maxW = canvas.parentElement.clientWidth - 40
  const maxH = canvas.parentElement.clientHeight - 40
  const scale = Math.min(maxW / img.naturalWidth, maxH / img.naturalHeight, 1)
  canvas.style.width = (img.naturalWidth * scale) + 'px'
  canvas.style.height = (img.naturalHeight * scale) + 'px'
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.drawImage(img, 0, 0)
}

function exportCSV() {
  const rows = [['类别', '置信度', 'x1', 'y1', 'x2', 'y2']]
  dets.value.forEach(d => rows.push([cnName(d.class_name), d.confidence, ...d.bbox.map(v => Math.round(v))]))
  downloadCSV(rows, '单张检测.csv')
}

function exportBatchCSV() {
  const rows = [['文件名', '类别', '置信度', 'x1', 'y1', 'x2', 'y2']]
  batchItems.value.forEach(item => {
    item.detections.forEach(d => rows.push([item.file.name, cnName(d.class_name), d.confidence, ...d.bbox.map(v => Math.round(v))]))
  })
  downloadCSV(rows, '批量检测.csv')
}

function downloadCSV(rows, name) {
  const csv = '﻿' + rows.map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = name
  a.click()
}

async function exportPDF() {
  const scale = 2
  const reportEl = document.createElement('div')
  reportEl.style.cssText = `
    position:fixed;left:-9999px;top:0;
    width:720px;padding:40px 48px;
    background:#0c0e14;color:#e8eaf0;
    font-family:'Inter','PingFang SC','Microsoft YaHei',sans-serif;
    font-size:14px;line-height:1.8;
  `
  reportEl.innerHTML = `
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid rgba(255,255,255,.08)">
      <div style="font-size:28px;font-weight:800;">AgriVision</div>
      <div style="font-size:12px;color:#949cb0;margin-top:4px;">病害检测报告</div>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:24px;font-size:12px;color:#6b7280">
      <span>生成时间: ${new Date().toLocaleString('zh-CN')}</span>
      <span>共检测到 ${dets.value.length} 个目标  ·  推理耗时 ${latency.value}ms</span>
    </div>
    <div style="font-size:16px;font-weight:700;margin-bottom:16px;color:#f1f3f7">检测结果</div>
    <table style="width:100%;border-collapse:collapse;font-size:12px;font-family:'JetBrains Mono','Fira Code',monospace">
      <thead>
        <tr style="background:rgba(255,255,255,.03);border-bottom:1px solid rgba(255,255,255,.08)">
          <th style="padding:10px 14px;text-align:left;color:#949cb0;font-weight:600">类别</th>
          <th style="padding:10px 14px;text-align:left;color:#949cb0;font-weight:600">置信度</th>
          <th style="padding:10px 14px;text-align:left;color:#949cb0;font-weight:600">边框坐标</th>
        </tr>
      </thead>
      <tbody>
        ${dets.value.map(d => `
          <tr style="border-bottom:1px solid rgba(255,255,255,.04)">
            <td style="padding:8px 14px;color:#e8eaf0">${cnName(d.class_name)}</td>
            <td style="padding:8px 14px;color:#10b981;font-weight:600">${(d.confidence * 100).toFixed(1)}%</td>
            <td style="padding:8px 14px;color:#6b7280">${d.bbox.map(v => Math.round(v)).join(', ')}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `

  // 如果有标注图，插入
  if (resultCanvasRef.value) {
    const imgSrc = resultCanvasRef.value.toDataURL('image/jpeg', 0.9)
    reportEl.innerHTML += `
      <div style="margin-top:32px;padding-top:24px;border-top:1px solid rgba(255,255,255,.08)">
        <div style="font-size:16px;font-weight:700;margin-bottom:16px;color:#f1f3f7">可视化标注</div>
        <img src="${imgSrc}" style="max-width:100%;border-radius:8px;border:1px solid rgba(255,255,255,.06)" />
      </div>
    `
  }

  reportEl.innerHTML += `
    <div style="margin-top:40px;padding-top:20px;border-top:1px solid rgba(255,255,255,.06);text-align:center;font-size:11px;color:#4b5168">智能农业病害检测系统</div>
  `

  document.body.appendChild(reportEl)

  try {
    const canvas = await html2canvas(reportEl, { scale: scale, backgroundColor: '#0c0e14', useCORS: true })
    document.body.removeChild(reportEl)

    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageW = 210
    const margin = 10
    const imgW = pageW - margin * 2
    const imgH = (canvas.height / canvas.width) * imgW

    let remainingH = imgH
    let srcY = 0
    const pageContentH = 297 - margin * 2

    while (remainingH > 0) {
      const sliceH = Math.min(remainingH, pageContentH)
      const sliceCanvas = document.createElement('canvas')
      sliceCanvas.width = canvas.width
      sliceCanvas.height = Math.round(sliceH / imgH * canvas.height)
      const ctx = sliceCanvas.getContext('2d')
      ctx.drawImage(canvas, 0, -Math.round(srcY / imgH * canvas.height), canvas.width, canvas.height)
      const sliceData = sliceCanvas.toDataURL('image/png')
      pdf.addImage(sliceData, 'PNG', margin, margin, imgW, sliceH)
      remainingH -= sliceH
      srcY += sliceH
      if (remainingH > 0) pdf.addPage()
    }

    pdf.save('病害检测报告.pdf')
  } catch (e) {
    if (reportEl.parentNode) document.body.removeChild(reportEl)
    console.error('PDF导出失败', e)
  }
}

async function exportBatchPDF() {
  const scale = 2
  const reportEl = document.createElement('div')
  reportEl.style.cssText = `
    position:fixed;left:-9999px;top:0;
    width:720px;padding:40px 48px;
    background:#0c0e14;color:#e8eaf0;
    font-family:'Inter','PingFang SC','Microsoft YaHei',sans-serif;
    font-size:14px;line-height:1.8;
  `
  let html = `
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid rgba(255,255,255,.08)">
      <div style="font-size:28px;font-weight:800;">AgriVision</div>
      <div style="font-size:12px;color:#949cb0;margin-top:4px;">批量检测报告</div>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:24px;font-size:12px;color:#6b7280">
      <span>生成时间: ${new Date().toLocaleString('zh-CN')}</span>
      <span>检测图片: ${batchItems.value.length} 张</span>
    </div>
  `

  batchItems.value.forEach((item, idx) => {
    html += `
      <div style="margin-bottom:24px;padding:20px 24px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.05);border-radius:10px">
        <div style="display:flex;gap:16px">
    `
    // 尝试获取缩略图
    const thumbCanvas = batchCanvases.value[idx]
    if (thumbCanvas && thumbCanvas.width > 0) {
      const thumbSrc = thumbCanvas.toDataURL('image/jpeg', 0.7)
      html += `<img src="${thumbSrc}" style="width:120px;max-height:90px;object-fit:cover;border-radius:6px;flex-shrink:0" />`
    }
    html += `
        <div style="flex:1">
          <div style="font-size:15px;font-weight:700;color:#f1f3f7;margin-bottom:8px">${idx + 1}. ${item.file.name}</div>
    `
    if (item.detections.length > 0) {
      html += `<div style="font-size:12px;color:#10b981;margin-bottom:10px;font-family:'JetBrains Mono',monospace">共 ${item.detections.length} 个目标</div>`
      html += `<table style="width:100%;border-collapse:collapse;font-size:11px;font-family:'JetBrains Mono',monospace">
        <thead><tr style="background:rgba(255,255,255,.02);border-bottom:1px solid rgba(255,255,255,.06)">
          <th style="padding:6px 12px;text-align:left;color:#949cb0">类别</th>
          <th style="padding:6px 12px;text-align:left;color:#949cb0">置信度</th>
        </tr></thead>
        <tbody>
          ${item.detections.map(d => `
            <tr style="border-bottom:1px solid rgba(255,255,255,.03)">
              <td style="padding:5px 12px;color:#e8eaf0">${cnName(d.class_name)}</td>
              <td style="padding:5px 12px;color:#10b981;font-weight:600">${(d.confidence * 100).toFixed(1)}%</td>
            </tr>
          `).join('')}
        </tbody>
      </table>`
    } else if (item.error) {
      html += `<div style="font-size:12px;color:#ef4444">错误: ${item.error}</div>`
    } else {
      html += `<div style="font-size:12px;color:#6b7280">无检测目标</div>`
    }
    html += `        </div>
      </div>
    </div>`
  })

  html += `<div style="margin-top:36px;padding-top:20px;border-top:1px solid rgba(255,255,255,.06);text-align:center;font-size:11px;color:#4b5168">智能农业病害检测系统</div>`
  reportEl.innerHTML = html
  document.body.appendChild(reportEl)

  try {
    const canvas = await html2canvas(reportEl, { scale: scale, backgroundColor: '#0c0e14', useCORS: true })
    document.body.removeChild(reportEl)

    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageW = 210; const margin = 10
    const imgW = pageW - margin * 2
    const imgH = (canvas.height / canvas.width) * imgW

    let remainingH = imgH; let srcY = 0
    const pageContentH = 297 - margin * 2

    while (remainingH > 0) {
      const sliceH = Math.min(remainingH, pageContentH)
      const sliceCanvas = document.createElement('canvas')
      sliceCanvas.width = canvas.width
      sliceCanvas.height = Math.round(sliceH / imgH * canvas.height)
      const ctx = sliceCanvas.getContext('2d')
      ctx.drawImage(canvas, 0, -Math.round(srcY / imgH * canvas.height), canvas.width, canvas.height)
      pdf.addImage(sliceCanvas.toDataURL('image/png'), 'PNG', margin, margin, imgW, sliceH)
      remainingH -= sliceH; srcY += sliceH
      if (remainingH > 0) pdf.addPage()
    }

    pdf.save('批量检测报告.pdf')
  } catch (e) {
    if (reportEl.parentNode) document.body.removeChild(reportEl)
    console.error('PDF导出失败', e)
  }
}
</script>

<style scoped>
.dual-panel { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 22px; }
.panel { display: flex; flex-direction: column; overflow: hidden; padding: 0; }
.panel--drag { border-color: var(--c-green); box-shadow: 0 0 0 2px rgba(16,185,129,.10), 0 0 40px rgba(16,185,129,.06); }

.panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 20px; border-bottom: 1px solid var(--c-border);
  font-size: 12.5px; font-weight: 600; color: var(--c-txt2);
}
.panel-header-right { display: flex; align-items: center; gap: 10px; }
.panel-hint { font-size: 11px; color: var(--c-txt3); font-weight: 400; }
.btn-chat-hero {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 18px;
  border: 1px solid rgba(139,92,246,.30);
  border-radius: var(--r-sm);
  background: linear-gradient(135deg, rgba(139,92,246,.14) 0%, rgba(139,92,246,.04) 100%);
  color: #a78bfa;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--c-sans);
  cursor: pointer;
  transition: all .25s var(--ease-out);
  position: relative;
  overflow: hidden;
}
.btn-chat-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(139,92,246,.06), transparent 60%, rgba(139,92,246,.12));
  opacity: 0;
  transition: opacity .3s;
}
.btn-chat-hero::after {
  content: '';
  position: absolute;
  top: -50%; left: -50%;
  width: 200%; height: 200%;
  background: radial-gradient(circle, rgba(139,92,246,.20) 0%, transparent 60%);
  opacity: 0;
  transition: opacity .3s;
  animation: chatBtnGlow 2.4s ease-in-out infinite;
}
@keyframes chatBtnGlow {
  0%, 100% { opacity: 0; }
  50% { opacity: .6; }
}
.btn-chat-hero:hover {
  border-color: rgba(139,92,246,.55);
  color: #c4b5fd;
  box-shadow: 0 0 28px rgba(139,92,246,.18), 0 4px 16px rgba(139,92,246,.08);
  transform: translateY(-1px);
}
.btn-chat-hero:hover::before { opacity: 1; }
.btn-chat-hero:hover::after { opacity: 1; animation: none; }
.btn-chat-hero:active { transform: translateY(0); }
.btn-chat-batch {
  flex-shrink: 0;
  align-self: center;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  margin-left: 12px;
  border: 1px solid rgba(139,92,246,.25);
  border-radius: var(--r-sm);
  background: linear-gradient(135deg, rgba(139,92,246,.10) 0%, rgba(139,92,246,.03) 100%);
  color: #a78bfa;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--c-sans);
  cursor: pointer;
  transition: all .25s var(--ease-out);
  white-space: nowrap;
}
.btn-chat-batch:hover {
  border-color: rgba(139,92,246,.50);
  color: #c4b5fd;
  background: linear-gradient(135deg, rgba(139,92,246,.18) 0%, rgba(139,92,246,.06) 100%);
  box-shadow: 0 0 20px rgba(139,92,246,.14), 0 2px 10px rgba(139,92,246,.06);
  transform: translateY(-1px);
}
.btn-chat-batch:active { transform: translateY(0); }
.panel-action {
  border: none; background: transparent; color: var(--c-red);
  font-size: 12px; font-weight: 500; cursor: pointer;
  padding: 4px 10px; border-radius: var(--r-xs); transition: background .2s;
}
.panel-action:hover { background: rgba(239,68,68,.08); }
.batch-btn {
  font-size: 12px; color: var(--c-blue); cursor: pointer; font-weight: 500;
  padding: 4px 10px; border-radius: var(--r-xs);
}
.batch-btn:hover { background: rgba(59,130,246,.08); }

.panel-body { flex: 1; display: flex; align-items: center; justify-content: center; padding: 0; min-height: 0; overflow: hidden; }
.panel-body--empty { color: var(--c-txt3); min-height: 200px; }

.dropzone {
  display: flex; flex-direction: column; align-items: center; gap: 10px; cursor: pointer;
  padding: 60px 40px; border: 2px dashed rgba(255,255,255,.06); border-radius: var(--r-md);
  margin: 20px; width: calc(100% - 40px); height: calc(100% - 40px);
  justify-content: center; transition: border-color .25s, background .25s;
}
.dropzone:hover { border-color: rgba(16,185,129,.25); background: rgba(16,185,129,.02); }
.dropzone-icon { opacity: .50; margin-bottom: 4px; }
.dropzone-main { font-size: 14px; font-weight: 600; color: var(--c-txt2); }
.dropzone-sub { font-size: 12px; color: var(--c-txt3); }

.preview-canvas { max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 4px; }
.empty-state { display: flex; flex-direction: column; align-items: center; gap: 12px; color: var(--c-txt3); font-size: 13px; }

.det-section { margin-top: 18px; }
.det-section-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px; font-size: 13px; font-weight: 600; color: var(--c-txt2);
}
.btn-sm { padding: 5px 12px; font-size: 12px; }

.det-row { display: flex; flex-wrap: wrap; gap: 10px; }
.det-card { display: flex; align-items: stretch; background: var(--c-surface); border: 1px solid var(--c-border); border-radius: var(--r-sm); overflow: hidden; transition: all .2s var(--ease-out); }
.det-card:hover { border-color: var(--c-border-h); box-shadow: var(--shadow-sm); }
.det-bar { width: 3px; flex-shrink: 0; }
.det-info { display: flex; align-items: center; gap: 12px; padding: 10px 16px; }
.det-name { font-size: 13px; font-weight: 600; color: var(--c-txt); }
.det-conf { font-size: 13px; font-weight: 700; color: var(--dc); font-family: var(--c-mono); }
.det-bbox { font-size: 11px; color: var(--c-txt3); font-family: var(--c-mono); }

.batch-panel { margin-top: 8px; }
.batch-list { display: flex; flex-direction: column; gap: 12px; margin-top: 12px; }
.batch-row { display: flex; gap: 20px; padding: 16px; overflow: hidden; align-items: flex-start; }
.batch-thumb {
  width: 160px; height: 120px; flex-shrink: 0; position: relative;
  background: var(--c-bg); border-radius: var(--r-sm); overflow: hidden;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.batch-thumb:hover .batch-overlay { opacity: 1; }
.batch-canvas { max-width: 100%; max-height: 100%; object-fit: contain; }
.batch-overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,.55);
  color: var(--c-green); font-size: 12px; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity .2s;
}
.batch-content { flex: 1; min-width: 0; }
.batch-filename {
  font-size: 14px; font-weight: 600; color: var(--c-txt);
  word-break: break-all; margin-bottom: 8px;
}
.batch-summary { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.batch-empty { font-size: 12px; color: var(--c-txt3); }
.batch-dets { display: flex; flex-wrap: wrap; gap: 6px; }
.batch-det {
  display: flex; align-items: center; gap: 6px;
  padding: 4px 10px; background: rgba(255,255,255,.03);
  border: 1px solid var(--c-border); border-radius: 20px; font-size: 12px;
}
.batch-det-name { color: var(--c-txt2); font-weight: 500; }
.batch-det-conf { color: var(--c-green); font-family: var(--c-mono); font-weight: 600; font-size: 11px; }

.preview-overlay {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(4,6,14,.94); backdrop-filter: blur(10px);
  display: flex; flex-direction: column; align-items: center;
  padding: 30px 48px 48px; overflow-y: auto;
}
.preview-close {
  align-self: flex-end; margin-bottom: 10px;
  border: 1px solid var(--c-border); background: transparent;
  color: var(--c-txt2); font-size: 13px; padding: 8px 18px;
  border-radius: var(--r-sm); cursor: pointer; transition: all .2s;
  font-family: var(--c-sans);
}
.preview-close:hover { border-color: var(--c-txt3); color: var(--c-txt); }
.ov-enter-active,.ov-leave-active { transition: opacity .25s; }
.ov-enter-from,.ov-leave-to { opacity: 0; }
</style>
