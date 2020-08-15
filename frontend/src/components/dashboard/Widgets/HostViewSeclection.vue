<template>
    <!-- show list of vlans in each host -->
    <div class="host-selection">
        <div class="card border-0 mb-3 mr-3 ml-3">
            <div class="host-group" v-for="(group,group_index) in $store.state.hosts" v-bind:key="group_index">
                <div class="row">
                    <div class="col-6 col-sm-6 col-md-6 col-lg-4" v-for="(host,host_index) in group"
                        v-bind:key="host_index" @click="redirect(group_index,host_index)">
                        <div class="card config-host-card">
                            <div class="card-body">
                                <div class="row">
                                    <div class='col-0 pb-1 mr-2'>
                                        <h5 class="card-title"><span class="badge badge-primary">{{group_index}}</span></h5>
                                    </div>
                                    <div class="col-0">
                                        <h4 class="card-title">{{host_index}}</h4>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col">
                                        <h6 class="card-subtitle mb-2 text-muted">{{Object.size(host.interfaces)}}
                                            interfaces</h6>
                                    </div>
                                    <div class="col">
                                        <h6 class="card-subtitle mb-2 text-muted">{{host.vlans.vlan_list.length}} vlans
                                        </h6>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import {
        mapActions
    } from 'vuex'

    Object.size = function (obj) {
        var size = 0,
            key;
        for (key in obj) {
            if (obj.hasOwnProperty(key)) size++;
        }
        return size;
    };

    export default {
        methods: {
            redirect(hostGroup, hostAddress) {
                this.$router.push({
                    path: '/host/' + hostGroup + '/' + hostAddress
                })
            }
        },
        components: {

        }

    }

</script>
