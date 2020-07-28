<template>
    <div id="dashboard">
        <QuickInfo/>
        <h1>Hello this is Dashboard</h1>

        {{$store.state.hosts}}
    </div>
</template>

<script>
    import {mapActions} from 'vuex'

    import QuickInfo from './dashboard/QuickInfo.vue'

    export default {
        created() {
            this.initHosts()
        },
        methods: mapActions([
            'initHosts'
        ]),
        components: {
            QuickInfo
        }
    }
</script>