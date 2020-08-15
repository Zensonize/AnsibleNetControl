<template>
    <div id="dashboard">
        <QuickInfo v-if="$store.state.dashboard != {}"/>
        <HostViewSelection/>

    </div>
</template>

<script>
    import {mapActions} from 'vuex'

    import QuickInfo from './dashboard/QuickInfo.vue'
    import HostViewSelection from './dashboard/Widgets/HostViewSeclection'

    export default {
        components: {
            QuickInfo,
            HostViewSelection
        }
    }
</script>