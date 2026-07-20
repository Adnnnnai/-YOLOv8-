import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSystemStore = defineStore('system', () => {
  const status = ref('就绪')
  const modelName = ref('best.pt')
  const modelVersion = ref('v1.0.0')
  const latency = ref(0)
  const gpuMem = ref('— / —')
  const gpuUtil = ref(0)
  const modelLoaded = ref(false)
  const numClasses = ref(29)
  const images = ref({ train: 0, val: 0, total: 0 })

  let pollTimer = null

  async function fetchStatus() {
    try {
      const res = await fetch('http://localhost:8080/api/v1/health')
      const data = await res.json()
      if (data.status === 'ok') {
        status.value = '就绪'
        modelLoaded.value = data.model_loaded ?? false
        modelName.value = data.model_name || localStorage.getItem('activeModel') || 'best.pt'
        modelVersion.value = localStorage.getItem('activeVersion') || 'v1.0.0'
        gpuMem.value = data.gpu_mem || '— / —'
        latency.value = data.latency_p50 ?? 0
        numClasses.value = data.num_classes ?? 29
        images.value = data.images || { train: 0, val: 0, total: 0 }
      }
    } catch {
        status.value = '离线'
      modelLoaded.value = false
    }
  }

  function startPolling(intervalMs = 5000) {
    fetchStatus()
    pollTimer = setInterval(fetchStatus, intervalMs)
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  return { status, modelName, modelVersion, latency, gpuMem, gpuUtil, modelLoaded, numClasses, images, fetchStatus, startPolling, stopPolling }
})
