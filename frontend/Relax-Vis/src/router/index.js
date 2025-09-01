import { createRouter, createWebHistory } from 'vue-router'
import HelloWorld from '../components/HelloWorld.vue'
import GraphPage from '../components/GraphPage.vue'

const routes = [
  { path: '/', name: 'Home', component: HelloWorld },
  { path: '/graph', name: 'GraphPage', component: GraphPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
