<template>
    <div class="config-home">
        <div class="vlan table">
            <table class="table" v-for="(groups, index) in $store.state.hosts.hosts" v-bind:key="index" v-show="!index.includes('localhost')">
                <thead>
                    <tr>
                        <th scope="col" colspan="6">{{index}}</th>
                    </tr>
                    <tr class="table-header">
                        <th scope="col">Host</th>
                        <th scope="col">VLANS</th>
                    </tr>
                </thead>
                <tbody v-if="!index.includes('localhost')">
                    <tr v-for="(host,index) in groups.hosts" v-bind:key="index">
                        <td>{{host}}</td>
                        <td>{{groups[host]['vlan_list'].join(', ')}}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
