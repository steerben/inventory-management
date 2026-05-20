import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import Inventory from './views/Inventory.vue'
import Orders from './views/Orders.vue'
import Demand from './views/Demand.vue'
import Spending from './views/Spending.vue'
import Reports from './views/Reports.vue'
import './styles/tokens.css'

// Route meta drives the sidebar: labelKey is resolved through useI18n() in AppSidebar,
// icon is a string key looked up in a local SVG map, order controls sidebar position.
// Keeping nav items derived from routes prevents the sidebar from drifting out of sync
// when routes are added or renamed.
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',          component: Dashboard, meta: { labelKey: 'nav.overview',        icon: 'home',          order: 1 } },
    { path: '/inventory', component: Inventory, meta: { labelKey: 'nav.inventory',       icon: 'package',       order: 2 } },
    { path: '/orders',    component: Orders,    meta: { labelKey: 'nav.orders',          icon: 'shopping-cart', order: 3 } },
    { path: '/demand',    component: Demand,    meta: { labelKey: 'nav.demandForecast',  icon: 'trending-up',   order: 4 } },
    { path: '/spending',  component: Spending,  meta: { labelKey: 'nav.finance',         icon: 'dollar-sign',   order: 5 } },
    { path: '/reports',   component: Reports,   meta: { labelKey: 'nav.reports',         icon: 'bar-chart',     order: 6 } }
  ]
})

const app = createApp(App)
app.use(router)
app.mount('#app')
