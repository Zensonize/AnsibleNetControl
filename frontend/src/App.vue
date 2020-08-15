<template>
  <div id="app">
    <NavBar class="navbar-fixed-top"/>
    <div class="nav-padding"></div>
    <router-view ></router-view>
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
      this.initFactsV2(),
      this.initLatestFacts()
    },
    methods: mapActions([
      'initHosts',
      'initDashboard',
      'initFactsV2',
      'initLatestFacts'
    ]),
    components: {
      NavBar
    }
  }
  </script>
