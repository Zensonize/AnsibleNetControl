import Vue from 'vue'
import VueRouter from 'vue-router'

import store from './store'


Vue.use(VueRouter)

import App from './App.vue'
import ConfigHost from './components/config/ConfigHost'
import ConfigHome from './components/config/ConfigHome'
import DashBoard from './components/Dashboard'
import HostView from './components/hostview/HostView'

const routes = [
  {
    path: '/config', 
    component: ConfigHome,
    name: 'configHome'
  },
  {
    path: '/config/:group/:address/', 
    component: ConfigHost,
    name: 'configHost'
  },
  {
    path: '/', 
    component: DashBoard,
    name: 'Dashboard'
  },
  {
    path: '/host/:group/:address', 
    component: HostView,
    name: 'HostView'
  },
  {
    path: '*',
    redirect: '/'
  }
]

const router = new VueRouter({
  base: process.env.BASE_URL,
  routes
})

new Vue({
  el: '#app',
  router,
  store,
  render: h => h(App)
})
