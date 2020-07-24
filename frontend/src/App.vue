<template>
  <div id="app">
    <NavBar/>
    <router-view></router-view>
  </div>
</template>

<script>
  import NavBar from './components/Nav_Bar.vue'

  export default {
    name: 'app',
    data () {
      return {
        
      }
    },
    components: {
      NavBar
    }
  }
  </script>
