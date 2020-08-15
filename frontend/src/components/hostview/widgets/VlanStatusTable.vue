<template>
    <div class="DeviceConfig" >
        <div class="card border-dark mb-3 mr-3 ml-3">
            <div class="card-header bg-dark text-white">Current VLAN Status</div>
            <div class="card-body text-dark p-0">
                <div class="table-responsive-md">
                    <table table class="table">
                        <thead>
                            <tr class="table-header">
                                <th scope="col">ID</th>
                                <th scope="col">Name</th>
                                <th scope="col">Mode</th>
                                <th scope="col">State</th>
                                <th scope="col">Enabled</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="table-row" v-for="(vlan_item,vlan_index) in $store.state.hosts[groupName][hostName].vlans.vlan" v-bind:key="vlan_index">
                                <th scope="row">{{vlan_item.vlan_id}}</th>
                                <td>{{vlan_item.name}}</td>
                                <td>{{vlan_item.mode}}</td>
                                <td>{{vlan_item.state}}</td>
                                <td>{{vlan_item.enabled}}</td>
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