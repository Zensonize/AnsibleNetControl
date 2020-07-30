<template>
    <div class="group-table">
        <h1>{{groupName}}</h1>
        <HostTable v-for="(host,index) in hostList" v-bind:key="index" v-bind:hostName="index" v-bind:hostInformation="host" v-bind:groupName="groupName"/>
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