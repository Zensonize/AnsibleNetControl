<template>
    <div class="quick-info" v-if="typeof($store.state.dashboard.host_status) != 'undefined'">
        <div class="row">
            <div class="col-12" v-if="$store.state.dashboard.network_status == 'Attention'">
                <h1 class='status_title'>Your System Needs </h1>
                <h1 class='status_stat attention'>Attention</h1>
            </div>
            <div class="col-12" v-if="$store.state.dashboard.network_status == 'Ok'">
                <h1 class='status_title'>Every thing is </h1>
                <h1 class='status_stat ok'>Ok</h1>
            </div>
        </div>
        <div class="container-fluid">
            <div class="quick-info-items row">
                <div class="col-3 col-sm-3">
                    <div class="card border-0">
                        <div class="card-body">
                            <h5 class="card-title">{{$store.state.dashboard.host_status.total_groups}}</h5>
                            <p>groups</p>
                        </div>
                    </div>
                </div>
                <div class="col-3 col-sm-3">
                    <div class="card border-0">
                        <div class="card-body">
                            <h5 class="card-title">{{$store.state.dashboard.host_status.total_hosts}}</h5>
                            <p>hosts</p>
                        </div>
                    </div>
                </div>
                <div class="col-3 col-sm-3">
                    <div class="card border-0">
                        <div class="card-body">
                            <h5 class="card-title">{{$store.state.dashboard.host_status.online.length}}</h5>
                            <p>online</p>
                        </div>
                    </div>
                </div>
                <div class="col-3 col-sm-3">
                    <div class="card border-0">
                        <div class="card-body">
                            <h5 class="card-title">{{$store.state.dashboard.host_status.offline.length}}</h5>
                            <p>offline</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                msg: "test"
            }
        }
    }
</script>