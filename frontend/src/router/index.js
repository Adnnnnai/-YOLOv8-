import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'topology',
    component: () => import('../views/TopologyView.vue'),
    meta: { title: '系统概览', icon: 'pipeline' },
  },
  {
    path: '/configs',
    name: 'configs',
    component: () => import('../views/ConfigsView.vue'),
    meta: { title: '配置中心', icon: 'sliders' },
  },
  {
    path: '/train',
    name: 'train',
    component: () => import('../views/TrainView.vue'),
    meta: { title: '训练任务', icon: 'rocket' },
  },
  {
    path: '/inference',
    name: 'inference',
    component: () => import('../views/InferenceView.vue'),
    meta: { title: '推理检测', icon: 'scan' },
  },
  {
    path: '/versions',
    name: 'versions',
    component: () => import('../views/VersionsView.vue'),
    meta: { title: '版本管理', icon: 'history' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
