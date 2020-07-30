import Vue from 'vue'
import VueRouter from 'vue-router'

import store from './store'


Vue.use(VueRouter)

import App from './App.vue'
import ConfigHost from './components/config/ConfigHost'
import ConfigHome from './components/config/ConfigHome'
import DashBoard from './components/Dashboard.vue'

const routes = [
  {
    path: '/config', component: ConfigHome
  },
  {
    path: '/config/:host/', component: ConfigHost,
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
