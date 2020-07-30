<template>
  <div id="app">
    <NavBar/>
    <router-view></router-view>
  </div>
</template>

<script>
  import NavBar from './components/Nav_Bar.vue'
  import {mapActions} from 'vuex'

  export default {
    name: 'app',
    created() {
      this.initHosts()
      this.initDashboard()
    },
    methods: mapActions([
      'initHosts',
      'initDashboard'
    ]),
    components: {
      NavBar
    }
  }
  </script>
