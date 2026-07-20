<template>
  <div class="app-shell">
    <Sidebar />
    <div class="main-area">
      <StatusBar />
      <main class="content-view">
        <router-view v-slot="{ Component }">
          <transition name="view-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import StatusBar from './components/StatusBar.vue'
import { useSystemStore } from './stores/system'

const store = useSystemStore()
onMounted(() => store.startPolling(5000))
onUnmounted(() => store.stopPolling())
</script>

<style>
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  /* ========== 色板 ========== */
  --c-bg:       #0c0e14;
  --c-surface:  #13151d;
  --c-elevated: #181a24;
  --c-overlay:  #1e202c;

  --c-border:   rgba(255, 255, 255, 0.05);
  --c-border-h: rgba(255, 255, 255, 0.08);
  --c-border-f: rgba(255, 255, 255, 0.12);

  --c-txt:      #e8eaf0;
  --c-txt2:     #8b90a5;
  --c-txt3:     #515570;

  --c-green:    #10b981;
  --c-green-d:  #059669;
  --c-blue:     #3b82f6;
  --c-blue-d:   #2563eb;
  --c-purple:   #8b5cf6;
  --c-cyan:     #06b6d4;
  --c-gold:     #f59e0b;
  --c-red:      #ef4444;

  /* ========== 排版 ========== */
  --c-mono:  'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
  --c-sans:  'Inter', system-ui, -apple-system, sans-serif;

  /* ========== 圆角 ========== */
  --r-xs:  6px;
  --r-sm:  10px;
  --r-md:  14px;
  --r-lg:  20px;
  --r-xl:  28px;

  /* ========== 阴影 ========== */
  --shadow-sm:  0 1px 2px rgba(0,0,0,.4);
  --shadow-md:  0 4px 12px rgba(0,0,0,.35);
  --shadow-lg:  0 12px 40px rgba(0,0,0,.5);
  --shadow-glow: 0 0 0 1px rgba(16,185,129,.12), 0 0 32px rgba(16,185,129,.04);

  /* ========== 动效 ========== */
  --ease-out: cubic-bezier(.16, 1, .3, 1);
  --ease-in-out: cubic-bezier(.4, 0, .2, 1);
}

html, body {
  height: 100%;
  overflow: hidden;
  font-family: var(--c-sans);
  font-size: 14px;
  line-height: 1.6;
  background: var(--c-bg);
  color: var(--c-txt);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ========== 布局 ========== */
.app-shell { display: flex; height: 100vh; }
.main-area {
  flex: 1;
  margin-left: 250px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}
.content-view {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0;
}

/* ========== 页面切换动画 ========== */
.view-fade-enter-active,
.view-fade-leave-active {
  transition: opacity .22s var(--ease-out), transform .22s var(--ease-out);
}
.view-fade-enter-from { opacity: 0; transform: translateY(10px) scale(.995); }
.view-fade-leave-to   { opacity: 0; transform: translateY(-6px) scale(.995); }

/* ========== 滚动条 ========== */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.05); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,.10); }

/* ========== 全局组件基类 ========== */
.pg {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 32px 36px 36px;
  animation: pg-in .35s var(--ease-out);
}
@keyframes pg-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.pg-head {
  margin-bottom: 32px;
}
.pg-head h2 {
  font-size: 22px;
  font-weight: 700;
  color: var(--c-txt);
  letter-spacing: -0.02em;
  line-height: 1.2;
}
.pg-head p {
  font-size: 13px;
  color: var(--c-txt3);
  margin-top: 6px;
  letter-spacing: 0.01em;
}

/* ========== 通用卡片 ========== */
.card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--r-md);
  transition: border-color .25s var(--ease-out), box-shadow .25s var(--ease-out);
}
.card:hover {
  border-color: var(--c-border-h);
  box-shadow: var(--shadow-md);
}

/* ========== 通用按钮 ========== */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 20px;
  border: none;
  border-radius: var(--r-sm);
  font-size: 13px;
  font-weight: 600;
  font-family: var(--c-sans);
  cursor: pointer;
  transition: all .2s var(--ease-out);
  letter-spacing: 0.01em;
}
.btn:disabled { opacity: .45; cursor: not-allowed; }

.btn-primary {
  background: var(--c-green);
  color: #000;
}
.btn-primary:hover:not(:disabled) {
  background: #34d399;
  box-shadow: 0 0 20px rgba(16,185,129,.25);
}

.btn-ghost {
  background: transparent;
  border: 1px solid var(--c-border);
  color: var(--c-txt2);
}
.btn-ghost:hover:not(:disabled) {
  border-color: var(--c-border-f);
  color: var(--c-txt);
  background: rgba(255,255,255,.03);
}

.btn-danger {
  background: transparent;
  border: 1px solid rgba(239,68,68,.25);
  color: var(--c-red);
}
.btn-danger:hover:not(:disabled) {
  background: rgba(239,68,68,.08);
  border-color: rgba(239,68,68,.4);
}

/* ========== 输入框 ========== */
.input {
  width: 100%;
  padding: 10px 14px;
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: var(--r-sm);
  color: var(--c-txt);
  font-size: 14px;
  font-family: var(--c-mono);
  transition: border-color .2s var(--ease-out), box-shadow .2s var(--ease-out);
}
.input:focus {
  outline: none;
  border-color: var(--c-green);
  box-shadow: 0 0 0 3px rgba(16,185,129,.08);
}
.input::placeholder { color: var(--c-txt3); }

/* ========== 标签/徽章 ========== */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.03em;
}
.badge-green { background: rgba(16,185,129,.10); color: var(--c-green); }
.badge-gold  { background: rgba(245,158,11,.10); color: var(--c-gold); }
.badge-red   { background: rgba(239,68,68,.10);  color: var(--c-red); }
.badge-blue  { background: rgba(59,130,246,.10); color: var(--c-blue); }
</style>
