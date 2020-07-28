<template>
    <div class="row quick-info">
        <div class="col-sm">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">{{$store.state.hosts.dashboard.total_groups}}</h5>
                    <p>groups</p>
                </div>
            </div>
        </div>
        <div class="col-sm">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">{{$store.state.hosts.dashboard.total_hosts}}</h5>
                    <p>hosts</p>
                </div>
            </div>
        </div>
        <div class="col-sm">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">{{$store.state.hosts.dashboard.host_status.online.length}}</h5>
                    <p>online</p>
                </div>
            </div>
        </div>
        <div class="col-sm">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">{{$store.state.hosts.dashboard.host_status.offline.length}}</h5>
                    <p>offline</p>
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