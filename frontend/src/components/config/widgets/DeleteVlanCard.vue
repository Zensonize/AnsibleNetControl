<template>
    <div class="add-vlan-card">
        <div class="card border-dark mb-3 mr-3 ml-3">
            <div class="card-header bg-dark text-white">Delete Vlan</div>
            <div class="card-body text-dark">
                <div class="row  pr-2 pl-2">
                    <div class="col">
                        <div class="form-group row mb-1">
                            <label class="col-auto col-form-label">Delete Vlan</label>
                            <div class="col">
                                <select class="form-control" v-model="delete_vlan">
                                    <option v-for="(vlan_item,vlan_index) in $store.state.hosts[groupName][hostName].vlans.vlan" v-bind:key="vlan_index">{{vlan_index}}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-footer pt-1 pb-1">
                <button class="btn btn-success" v-if="delete_vlan == 1" disabled>commit</button>
                <button class="btn btn-success" @click="submitVlanConfig()" v-if="delete_vlan != 1">commit</button>
            </div>
        </div>
    </div>
</template>

<script>
    import {mapActions} from 'vuex'

    export default {
        

        props: ['groupName', 'hostName'],
        created() {
            this.delete_vlan = this.$store.state.latestFacts[0].data.facts[this.groupName][this.hostName].ansible_net_vlan_list[0]
        },
        data() {
            return {
                delete_vlan: ""
            }
        },
        methods: {
            ...mapActions([
                'initHosts',
                'initDashboard',
                'fetchFacts',
                'initFacts'
            ]),
            submitVlanConfig: function() {
                var reqBody = {
                    "hostGroup": this.groupName,
                    "task": "delete",
                    "vlan": this.delete_vlan,
                    "hosts":{
                        
                    }
                }
                reqBody.hosts[this.hostName] = {
                    "access_interfaces":[],
                    "trunk_interfaces": {}
                }

                var intf

                for (intf in this.$store.state.hosts[this.groupName][this.hostName].interfaces) {
                    if (this.$store.state.hosts[this.groupName][this.hostName].interfaces[intf].mode == "access" && this.$store.state.hosts[this.groupName][this.hostName].interfaces[intf].vlan.access_vlan == this.delete_vlan) {
                        reqBody.hosts[this.hostName].access_interfaces.push(intf)
                    }
                    if (this.$store.state.hosts[this.groupName][this.hostName].interfaces[intf].mode == "trunk") {
                        var allowedList = []

                        if (this.$store.state.hosts[this.groupName][this.hostName].interfaces[intf].vlan.trunk.native_vlan == this.delete_vlan) {
                            allowedList = this.$store.state.hosts[this.groupName][this.hostName].interfaces[intf].vlan.trunk.allowed_vlans.split(',')
                            allowedList.splice(allowedList.indexOf(String(this.delete_vlan)),1)

                            reqBody.hosts[this.hostName].trunk_interfaces[intf] = {
                                "allowed_vlans": allowedList.toString(),
                                "native_vlan": 1
                            }
                        } else {
                            allowedList = this.$store.state.hosts[this.groupName][this.hostName].interfaces[intf].vlan.trunk.allowed_vlans.split(',')
                            if (allowedList.includes(this.delete_vlan.toString())){
                                allowedList.splice(allowedList.indexOf(String(this.delete_vlan)),1)

                                reqBody.hosts[this.hostName].trunk_interfaces[intf] = {
                                    "allowed_vlans": allowedList.toString(),
                                    "native_vlan": this.$store.state.hosts[this.groupName][this.hostName].interfaces[intf].vlan.trunk.native_vlan
                                }
                            }
                        }
                    }
                    
                }
                console.log("request execution")

                origin = 'http://localhost:4040/config/' + this.hostGroup + '/' + this.hostName
                let headers = new Headers();
                headers.append('Content-Type', 'application/json');
                headers.append('Accept', 'application/json');
                headers.append('Origin',origin);

                fetch('http://localhost:4000/config/vlan', {
                    method: 'POST',
                    mode: 'cors',
                    headers: headers,
                    body: JSON.stringify(reqBody)
                })
                .then(response => console.log(response))
                // .then(this.initHosts())
                // .then(this.initDashboard())
                // .then(this.initLatestFacts)
                // .then(this.initFacts())

                // console.log(reqBody)
            }
            
            
        }
        
    }
</script>