<template>
    <div class="group-table" v-show="!groupName.includes('localhost')">
        <h1>{{groupName}}</h1>
        <HostTable v-for="(host,index) in hostList.hosts" v-bind:key="index" v-bind:hostName="host" v-bind:hostInformation="hostList[host]"/>
    </div>
</template>

<script>
import HostTable from './HostTable'

    export default {
        props: ['groupName','hostList','index'],
        data() {
            return {
                msg: "test"
            }
        },
        components: {
            HostTable
        }
    }
</script>