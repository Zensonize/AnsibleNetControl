<template>
    <div class="DeviceConfig" >
        <div class="card border-dark mb-3 mr-3 ml-3">
            <div class="card-header bg-dark text-white">Current Trunk Interface VLAN Configuration</div>
            <div class="card-body text-dark p-0">
                <div class="table-responsive-md">
                    <table table class="table">
                        <thead>
                            <tr class="table-header">
                                <th scope="col">Interface</th>
                                <th scope="col">TrunkNative</th>
                                <th scope="col">Trunk Allowed</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="table-row" v-for="(intf_item,intf_index) in $store.state.hosts[groupName][hostName].interfaces" v-bind:key="intf_index">
                                <th scope="row" v-if="'trunk' in intf_item.vlan">{{intf_index}}</th>
                                <th scope="row" v-if="'trunk' in intf_item.vlan">{{intf_item.vlan.trunk.native_vlan}}</th>
                                <th scope="row" v-if="'trunk' in intf_item.vlan">{{intf_item.vlan.trunk.allowed_vlans}}</th>

                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>

<script>

    export default {
        props: ['groupName', 'hostName'],
    }
</script>