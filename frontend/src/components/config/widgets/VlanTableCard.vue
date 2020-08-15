<template>
    <div class="DeviceConfig" >
        <div class="card border-dark mb-3 mr-3 ml-3">
            <div class="card-header bg-dark text-white">Current VLAN Configuration</div>
            <div class="card-body text-dark p-0">
                <div class="table-responsive-md">
                    <table table class="table">
                        <thead>
                            <tr class="table-header">
                                <th scope="col">ID</th>
                                <th scope="col">Name</th>
                                <th scope="col">Interfaces</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="table-row" v-for="(vlan_item,vlan_index) in $store.state.hosts[groupName][hostName].vlans.vlan" v-bind:key="vlan_index">
                                <th scope="row">{{vlan_item.vlan_id}}</th>
                                <td>{{vlan_item.name}}</td>
                                <td>
                                    <div class="row">
                                        <div class="" v-for="(intf_item,intf_index) in $store.state.hosts[groupName][hostName].interfaces" v-bind:key="intf_index" v-if>
                                            <span class="badge badge-success mr-1 ml-1" v-if="intf_item.vlan.access_vlan != undefined && intf_item.vlan.access_vlan == vlan_item.vlan_id && intf_item.state == 'up'">{{intf_index}}</span>
                                            <span class="badge badge-dark mr-1 ml-1" v-if="intf_item.vlan.access_vlan != undefined && intf_item.vlan.access_vlan == vlan_item.vlan_id && intf_item.state == 'down'">{{intf_index}}</span>
                                        </div>
                                    </div>
                                </td>
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