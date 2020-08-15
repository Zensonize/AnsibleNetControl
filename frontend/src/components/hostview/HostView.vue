<template>
    <div class="host-information ml-1 mr-1">
        <TrafficGraphCard v-bind:groupName="groupName" v-bind:hostName="hostName" v-bind:intf="'mgmt0'" v-if="$store.state.latestFacts[0] != undefined && $store.state.facts[0] != undefined"/>
        <VlanStatusTable v-bind:groupName="groupName" v-bind:hostName="hostName" v-if="$store.state.hosts[groupName] != undefined"/>
        <VlanTable v-bind:groupName="groupName" v-bind:hostName="hostName" v-if="$store.state.hosts[groupName] != undefined"/>
        <DeviceConfig v-bind:groupName="groupName" v-bind:hostName="hostName" v-if="$store.state.latestFacts[0] != undefined"/>
        <InterfacesTable v-bind:groupName="groupName" v-bind:hostName="hostName" v-bind:hostInformation="$store.state.hosts[groupName][hostName]" v-if="$store.state.hosts[groupName] != undefined"/>
    </div> 
</template>

<script>
    import InterfacesTable from './widgets/InterfacesTable'
    import DeviceConfig from './widgets/DeviceConfig'
    import VlanTable from './widgets/VlanTable'
    import VlanStatusTable from './widgets/VlanStatusTable'
    import TrafficGraphCard from './widgets/TrafficGraphCard'

    export default {
        created() {
            // console.log(this.$route)
        },
        data() {
            return {
                groupName: this.$route.params.group,
                hostName: this.$route.params.address
            }
        },
        components: {
            InterfacesTable,
            DeviceConfig,
            VlanTable,
            VlanStatusTable,
            TrafficGraphCard
        }
    }
</script>