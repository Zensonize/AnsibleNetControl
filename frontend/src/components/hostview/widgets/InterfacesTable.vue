<template>
        <div class="card border-dark mb-3 mr-3 ml-3">
            <div class="card-header bg-dark text-white">Interface Statistics</div>
            <div class="card-body text-dark p-0">
                <div class="table-responsive-md">
                    <table table class="table">
                          <thead>
                            <tr class="table-header">
                                <th scope="col">Interface</th>
                                <th scope="col">State</th>
                                <th scope="col">Mode</th>
                                <th scope="col">Speed</th>
                                <th scope="col">Duplex</th>
                                <th scope="col">Rx</th>
                                <th scope="col">Tx</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="table-row" v-for="(item,index) in hostInformation.interfaces" v-bind:key="index">
                                <th scope="row">{{index}}</th>
                                <td>{{item.state}}</td>
                                <td>{{item.mode}}</td>
                                <td>{{item.speed}}</td>
                                <td>{{item.duplex}}</td>
                                <td>{{item.stats.Rx.ave.bps}}</td>
                                <td>{{item.stats.Tx.ave.bps}}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
</template>

<script>
    export default {
        props: ['groupName', 'hostName', 'hostInformation']

    }

</script>
