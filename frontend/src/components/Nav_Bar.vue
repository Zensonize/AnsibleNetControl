<template>
  <nav class="navbar navbar-expand-md navbar-light bg-light\">
    <router-link class='navbar-brand' to='/'>Ansible Net Control</router-link>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavDropdown"
      aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNavDropdown">
      <ul class="navbar-nav">
        <li class="nav-item active" v-show="section.length == 2">
            <router-link class='nav-link' to='/'>Dashboard</router-link>
        </li>
        <li class="nav-item" v-show="section.length != 2">
            <router-link class='nav-link' to='/'>Dashboard</router-link>
        </li>
        <li class="nav-item active dropdown" v-show="section.includes('config')">
          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Config</a>
          <div class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
            <router-link class='nav-link' to='/config/vlan'>VLAN</router-link>
          </div>
        </li>
        <li class="nav-item dropdown" v-show="!section.includes('config')">
          <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownMenuLink" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Config</a>
          <div class="dropdown-menu" aria-labelledby="navbarDropdownMenuLink">
            <router-link class='nav-link' to='/config/vlan'>VLAN</router-link>
          </div>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script>

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
            change() {
                this.type = this.$route.params.type
                this.section = this.$route.path.split('/')
            }
        }
    }
</script>