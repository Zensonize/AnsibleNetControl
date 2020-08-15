<template>
  <nav class="navbar navbar-expand-sm navbar-dark fixed-top">
    <router-link class='navbar-brand' to='/'>Ansible Net Control</router-link>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavDropdown"
      aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNavDropdown">
      <ul class="navbar-nav">
        <li class="nav-item active" v-show="!section.includes('config')">
            <router-link class='nav-link' to='/'>Dashboard</router-link>
        </li>
        <li class="nav-item" v-show="section.includes('config')">
            <router-link class='nav-link' to='/'>Dashboard</router-link>
        </li>
        <li class="nav-item active" v-show="section.includes('config')">
            <router-link class='nav-link' to='/config'>Config</router-link>
        </li>
        <li class="nav-item" v-show="!section.includes('config')">
            <router-link class='nav-link' to='/config'>Config</router-link>
        </li>
        <li>
            <button class="btn btn-outline-light my-2 my-sm-0" @click="initFactsV2_forced()">ForceRefresh</button>
            <button class="btn btn-outline-light my-2 my-sm-0" @click="initLatestFacts()">RefreshFacts</button>
        </li>
        
      </ul>
    </div>
  </nav>
</template>

<script>
    import {mapActions} from 'vuex'

    export default {
        data() {
            return {
                type: this.$route.params.type,
                section: this.$route.path.split('/')
            }
        },
        watch: {
            $route: 'change'
        },
        methods: {
            ...mapActions([
                'initFactsV2_forced',
                'initLatestFacts'
            ]),

            change() {
                this.type = this.$route.params.type
                this.section = this.$route.path.split('/')
            }
            
        }
    }
</script>