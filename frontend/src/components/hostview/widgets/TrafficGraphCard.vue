<template>
    <div class="DeviceConfig">
        <div class="card border-dark mb-3 mr-3 ml-3">
            <div class="card-header bg-dark text-white">Traffic Graph of {{intf}}</div>
            <div class="card-body text-dark">
                <TrafficGraph v-bind:chartdata="chartdata" v-bind:options="options"/>
            </div>
        </div>
    </div>
</template>

<script>
    import TrafficGraph from './TrafficGraph'

    export default {

        props: ['groupName', 'hostName', 'intf'],
        data() {
            return {
                chartdata: {
                    labels: [],
                    datasets: [
                        {
                            label: "",
                            borderColor: '#264C72',
                            backgroundColor: 'rgba(38, 76, 114, 0.3)',
                            data: [],
                            
                        },
                        {
                            label: "",
                            borderColor: "#3F7FBF",
                            backgroundColor: 'rgba(63, 127, 191, 0.3)',
                            data: []
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            }
        },
        methods: {
            prepareGraphData: function() {
                var idx;
                // console.log(this.$store.state.facts)
                for (idx in this.$store.state.facts) {
                    this.chartdata.labels.push(this.$store.state.facts[idx].dateCreated.split(' ')[1].split('.')[0])
                    if (this.$store.state.facts[idx].data.hosts[this.groupName][this.hostName].interfaces[this.intf].stats == undefined){
                        this.chartdata.datasets[0].data.push(0)
                        this.chartdata.datasets[1].data.push(0)
                    }
                    else{
                        this.chartdata.datasets[0].data.push(this.$store.state.facts[idx].data.hosts[this.groupName][this.hostName].interfaces[this.intf].stats.Rx.ave.bps.split(' ')[0])
                        this.chartdata.datasets[1].data.push(this.$store.state.facts[idx].data.hosts[this.groupName][this.hostName].interfaces[this.intf].stats.Tx.ave.bps.split(' ')[0])
                    }
                    
                }

            }
        },
        created() {
            this.chartdata.datasets[0].label = this.intf + ' - RX'
            this.chartdata.datasets[1].label = this.intf + ' - TX'
            this.prepareGraphData()
        },
        mounted() {
            
        },
        components: {
            TrafficGraph
        }

    }

</script>
