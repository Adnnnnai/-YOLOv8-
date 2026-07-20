<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-icon">
        <svg width="28" height="28" viewBox="0 0 36 36" fill="none">
          <path d="M18 3L30.3 9.6v13.8L18 29.7 5.7 23.4V9.6L18 3z" stroke="#10b981" stroke-width="2"/>
          <path d="M18 11l5 3v7l-5 3-5-3v-7l5-3z" stroke="#f59e0b" stroke-width="1.4"/>
        </svg>
      </div>
      <div class="brand-text">
        <span class="brand-name">AgriVision</span>
        <span class="brand-sub">智能农业病害检测平台</span>
      </div>
    </div>

    <nav class="nav">
      <router-link
        v-for="m in menus"
        :key="m.to"
        :to="m.to"
        class="nav-item"
        active-class="nav-item--active"
      >
        <span class="nav-icon" v-html="m.icon"></span>
        <span class="nav-label">{{ m.label }}</span>
        <span class="nav-arrow"></span>
      </router-link>
    </nav>

    <div class="sidebar-foot">
      <div class="foot-status">
        <span class="foot-dot"></span>
        <span class="foot-text">系统就绪</span>
      </div>
      <span class="foot-ver">v1.5</span>
    </div>
  </aside>
</template>

<script setup>
const menus = [
  { to:'/',           label:'系统概览', icon:'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>' },
  { to:'/configs',   label:'配置中心', icon:'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="2.5"/><circle cx="12" cy="12" r="2.5"/><circle cx="12" cy="19" r="2.5"/></svg>' },
  { to:'/train',     label:'训练任务', icon:'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><path d="M12 2v6M12 16v6"/></svg>' },
  { to:'/inference', label:'推理检测', icon:'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5-5 5"/></svg>' },
  { to:'/versions',  label:'版本管理', icon:'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' },
]
</script>

<style scoped>
.sidebar {
  width: 250px;
  height: 100vh;
  position: fixed;
  z-index: 100;
  background: #0a0d16;
  border-right: 1px solid var(--c-border);
  display: flex;
  flex-direction: column;
  user-select: none;
}

/* ========== Brand ========== */
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 28px 20px 36px;
}
.brand-icon {
  flex-shrink: 0;
  width: 42px; height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(16,185,129,.06);
  border-radius: 12px;
  border: 1px solid rgba(16,185,129,.10);
}
.brand-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.brand-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--c-txt);
  letter-spacing: -0.01em;
  line-height: 1.2;
}
.brand-sub {
  font-size: 10.5px;
  color: var(--c-txt3);
  letter-spacing: 0.02em;
}

/* ========== Nav ========== */
.nav {
  flex: 1;
  padding: 0 14px;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  color: var(--c-txt3);
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 500;
  letter-spacing: 0.02em;
  transition: all .25s ease;
}

.nav-item:hover {
  color: var(--c-txt);
  background: rgba(255,255,255,.03);
}

.nav-item--active {
  color: #fff;
  background: linear-gradient(135deg, rgba(16,185,129,.12) 0%, rgba(16,185,129,.04) 100%);
  border: 1px solid rgba(16,185,129,.15);
  font-weight: 600;
  box-shadow: 0 0 20px rgba(16,185,129,.04), inset 0 1px 0 rgba(16,185,129,.06);
}

.nav-icon {
  flex-shrink: 0;
  opacity: .35;
  transition: all .25s ease;
}
.nav-item:hover .nav-icon { opacity: .7; }
.nav-item--active .nav-icon { opacity: 1; }

.nav-arrow {
  position: absolute;
  right: 14px;
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--c-green);
  opacity: 0;
  transform: scale(0);
  transition: all .25s ease;
  box-shadow: 0 0 6px rgba(16,185,129,.5);
}
.nav-item--active .nav-arrow {
  opacity: 1;
  transform: scale(1);
}

/* ========== Footer ========== */
.sidebar-foot {
  padding: 20px 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.foot-status {
  display: flex;
  align-items: center;
  gap: 7px;
}
.foot-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--c-green);
  box-shadow: 0 0 8px rgba(16,185,129,.5);
}
.foot-text {
  font-size: 11px;
  color: var(--c-txt3);
  letter-spacing: 0.02em;
}
.foot-ver {
  font-size: 11px;
  color: #2d3348;
  font-family: var(--c-mono);
}
</style>
