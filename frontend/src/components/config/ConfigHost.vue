<template>
    <div class="config-host">
        <VlanTableCard v-bind:groupName="groupName" v-bind:hostName="hostName" v-if="typeof($store.state.latestFacts[0]) != 'undefined'"/>
        <TrunkVlanTableCard v-bind:groupName="groupName" v-bind:hostName="hostName" v-if="typeof($store.state.hosts[groupName]) != 'undefined'"/>

        <AddVlanCard v-bind:groupName="groupName" v-bind:hostName="hostName" v-if="typeof($store.state.latestFacts[0]) != 'undefined'"/>
        <DeleteVlanCard v-bind:groupName="groupName" v-bind:hostName="hostName" v-if="typeof($store.state.hosts[groupName]) != 'undefined' && typeof($store.state.latestFacts[0]) != 'undefined'"/>
    </div>
</template>

<script>
    import VlanTableCard from './widgets/VlanTableCard'
    import AddVlanCard from './widgets/AddVlanCard'
    import DeleteVlanCard from './widgets/DeleteVlanCard'
    import TrunkVlanTableCard from './widgets/TrunkVlanTableCard'

    export default {
        data () {
            return {
                groupName: this.$route.params.group,
                hostName: this.$route.params.address
            }
        },
        components: {
            VlanTableCard,
            AddVlanCard,
            DeleteVlanCard,
            TrunkVlanTableCard
        }
    }
</script>