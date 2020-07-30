<template>
    <div id="dashboard">
        <QuickInfo v-if="$store.state.dashboard != {}"/>
        <!-- <h1>Hello this is Dashboard</h1> -->
        <div class="container-md" v-if="$store.state.hosts != {}">
            <GroupTable v-for="(groups, index) in $store.state.hosts" v-bind:key="index" v-bind:index="index" v-bind:groupName="index" v-bind:hostList="$store.state.hosts[index]"/>
        </div>
        
        <!-- {{$store.state.hosts}} -->
    </div>
</template>

<script>
    import {mapActions} from 'vuex'

    import QuickInfo from './dashboard/QuickInfo.vue'
    import GroupTable from './dashboard/GroupTable'

    export default {
        components: {
            QuickInfo,
            GroupTable
        }
    }
</script>