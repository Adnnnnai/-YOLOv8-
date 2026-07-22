<template>
  <div class="chat-export">
    <button class="chat-export-btn" @click="exportPDF" title="导出 AI 诊断报告">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      <span>导出报告</span>
    </button>
  </div>
</template>

<script setup>
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  detections: { type: Array, default: () => [] },
})

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

async function exportPDF() {
  const scale = 2
  const el = document.createElement('div')
  el.style.cssText = 'position:fixed;left:-9999px;top:0;width:720px;padding:40px 48px;background:#0c0e14;color:#e8eaf0;font-family:Inter,PingFang SC,Microsoft YaHei,sans-serif;font-size:14px;line-height:1.8;'

  let html = `
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:28px;padding-bottom:20px;border-bottom:1px solid rgba(255,255,255,.08)">
      <div style="font-size:28px;font-weight:800">AgriVision</div>
      <div style="font-size:12px;color:#949cb0;margin-top:4px">AI 智能诊断报告</div>
    </div>
    <div style="font-size:12px;color:#6b7280;margin-bottom:24px">生成时间: ${new Date().toLocaleString('zh-CN')}</div>
  `

  if (props.detections.length) {
    html += `<div style="font-size:15px;font-weight:700;margin-bottom:10px;color:#f1f3f7">检测结果</div>`
    html += '<table style="width:100%;border-collapse:collapse;font-size:12px;font-family:JetBrains Mono,monospace;margin-bottom:28px"><thead><tr style="background:rgba(255,255,255,.03);border-bottom:1px solid rgba(255,255,255,.08)"><th style="padding:8px 12px;text-align:left;color:#949cb0">类别</th><th style="padding:8px 12px;text-align:left;color:#949cb0">置信度</th></tr></thead><tbody>'
    props.detections.forEach(d => {
      html += `<tr style="border-bottom:1px solid rgba(255,255,255,.04)"><td style="padding:7px 12px;color:#e8eaf0">${cnName(d.class_name)}</td><td style="padding:7px 12px;color:#10b981;font-weight:600">${(d.confidence*100).toFixed(1)}%</td></tr>`
    })
    html += '</tbody></table>'
  }

  html += '<div style="font-size:15px;font-weight:700;margin-bottom:16px;color:#f1f3f7;padding-top:20px;border-top:1px solid rgba(255,255,255,.08)">AI 诊断对话</div>'

  props.messages.forEach(m => {
    const roleLabel = m.role === 'assistant' ? 'AI 诊断' : '用户提问'
    const bg = m.role === 'assistant'
      ? 'background:rgba(139,92,246,.06);border-left:3px solid rgba(139,92,246,.25);'
      : 'background:rgba(6,182,212,.05);border-left:3px solid rgba(6,182,212,.20);'
    const text = m.content
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/\n/g, '<br/>')
    html += `
      <div style="margin-bottom:14px;padding:14px 18px;border-radius:10px;${bg}">
        <div style="font-size:11px;font-weight:600;color:#6b7280;margin-bottom:6px;text-transform:uppercase;letter-spacing:.05em">${roleLabel}</div>
        <div style="font-size:13px;color:#e8eaf0;line-height:1.8">${text}</div>
      </div>
    `
  })

  html += `<div style="margin-top:40px;padding-top:20px;border-top:1px solid rgba(255,255,255,.06);text-align:center;font-size:11px;color:#4b5168">智能农业病害检测系统 · AI 诊断报告</div>`

  el.innerHTML = html
  document.body.appendChild(el)

  try {
    const canvas = await html2canvas(el, { scale, backgroundColor: '#0c0e14', useCORS: true })
    document.body.removeChild(el)

    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageW = 210; const margin = 10
    const imgW = pageW - margin * 2
    const imgH = (canvas.height / canvas.width) * imgW

    let rem = imgH; let srcY = 0
    const pageH = 297 - margin * 2

    while (rem > 0) {
      const sliceH = Math.min(rem, pageH)
      const sc = document.createElement('canvas')
      sc.width = canvas.width; sc.height = Math.round(sliceH / imgH * canvas.height)
      const ctx = sc.getContext('2d')
      ctx.drawImage(canvas, 0, -Math.round(srcY / imgH * canvas.height), canvas.width, canvas.height)
      pdf.addImage(sc.toDataURL('image/png'), 'PNG', margin, margin, imgW, sliceH)
      rem -= sliceH; srcY += sliceH
      if (rem > 0) pdf.addPage()
    }

    pdf.save('AI诊断报告.pdf')
  } catch (e) {
    if (el.parentNode) document.body.removeChild(el)
    console.error('导出失败', e)
  }
}
</script>

<style scoped>
.chat-export {
  padding: 0 16px 4px;
  border-bottom: 1px solid var(--c-border);
}
.chat-export-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 12px;
  background: rgba(255,255,255,.02);
  color: var(--c-txt3);
  font-size: 11px;
  font-family: var(--c-sans);
  cursor: pointer;
  transition: all .2s;
}
.chat-export-btn:hover {
  border-color: rgba(139,92,246,.25);
  background: rgba(139,92,246,.06);
  color: var(--c-purple);
}
</style>
