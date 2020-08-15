<template>
    <div class="DeviceConfig" >
        <div class="card border-dark mb-3 mr-3 ml-3">
            <div class="card-header bg-dark text-white">Device Configuration</div>
            <div class="card-body text-dark">
                <div class="config_text" v-html="$store.state.latestFacts[0].data.facts[groupName][hostName].ansible_net_config.split('\n').join('<br>')"></div>
            </div>
        </div>
    </div>
</template>

<script>

    export default {
        props: ['groupName', 'hostName'],
    }
</script>