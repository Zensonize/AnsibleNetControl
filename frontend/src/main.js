import Vue from 'vue'
import VueRouter from 'vue-router'

import store from './store'


Vue.use(VueRouter)

import App from './App.vue'
import Config from './components/Config.vue'
import DashBoard from './components/Dashboard.vue'

const routes = [
  {
    path: '/config/:type', component: Config
  },
  {
    path: '/', component: DashBoard
  }
]

const router = new VueRouter({
  routes
})

new Vue({
  el: '#app',
  router,
  store,
  render: h => h(App)
})
