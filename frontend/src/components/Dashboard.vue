<template>
    <div id="dashboard">
        <QuickInfo/>
        <!-- <h1>Hello this is Dashboard</h1> -->
        <div class="container">
            <GroupTable v-for="(groups, index) in $store.state.hosts.hosts" v-bind:key="index" v-bind:index="index" v-bind:groupName="index" v-bind:hostList="$store.state.hosts.hosts[index]"/>
        </div>
        
        <!-- {{$store.state.hosts}} -->
    </div>
</template>

<script>
    import {mapActions} from 'vuex'

    import QuickInfo from './dashboard/QuickInfo.vue'
    import GroupTable from './dashboard/GroupTable'

    export default {
        created() {
            this.initHosts()
        },
        methods: mapActions([
            'initHosts'
        ]),
        components: {
            QuickInfo,
            GroupTable
        }
    }
</script>