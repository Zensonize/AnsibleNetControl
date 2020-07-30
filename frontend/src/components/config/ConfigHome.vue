<template>
  <!-- show list of vlans in each host -->
  <div class="config">
      <h2>Config Home</h2>
      <div class="host-group" v-for="(group,index) in $store.state.hosts.hosts" v-bind:key="index">
          <div class="row">
              {{index}}
          </div>
          <div class="row">
            <div class="col-sm-6 col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h4 class="card-title">Host IP address</h4>
                        
                    </div>
                </div>
            </div>
          </div>
      </div>
  </div>
</template>

<script>
    import {mapActions} from 'vuex'

    export default {
        created() {
            this.initHosts()
        },
        methods: mapActions([
            'initHosts'
        ]),
    }

</script>
