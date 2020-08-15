<template>
    <div class="add-vlan-card">
        <div class="card border-dark mb-3 mr-3 ml-3">
            <!-- <form> -->
                <div class="card-header bg-dark text-white">Add Vlan</div>
                <div class="card-body text-dark">
                    <div class="row  pr-2 pl-2">
                        <div class="col">
                            <div class="form-group row mb-1">
                                <label for="input_vlan_id" class="col-sm-auto col-form-label">VLAN ID</label>
                                <div class="col">
                                    <input type="number" class="form-control" id="input_vlan_id" placeholder="VLAN ID" min=1 oninput="validity.valid||(value='');" v-model="edit_id">
                                </div>
                                <label for="input_vlan_name" class="col-sm-auto col-form-label">Name</label>
                                <div class="col">
                                    <input type="text" class="form-control" id="input_vlan_name" placeholder="Name" v-model="edit_name">
                                </div>
                            </div>
                            <div class="form-group row mb-1">
                                <label class="col-auto col-form-label">Access Interfaces</label>
                                <div class="col">
                                    <span class="badge badge-warning mr-1 ml-1 pointer" v-for="intf in access_interfaces" v-bind:key="intf" @click="removeInterfaceFromAccess(intf)">{{intf}}</span>
                                </div>
                            </div>
                            <div class="form-group row mb-1">
                                <label class="col-auto col-form-label">Trunk Interfaces</label>
                                <div class="col">
                                    <span class="badge badge-warning mr-1 ml-1 pointer" v-for="intf in trunk_interfaces" v-bind:key="intf" @click="removeInterfaceFromTrunk(intf)">{{intf}}</span>
                                </div>
                            </div>
                            <div class="form-group row mb-0">
                                <label class="col-auto col-form-label">Trunk Native</label>
                                <div class="col">
                                    <span class="badge badge-warning mr-1 ml-1 pointer" v-for="intf in trunk_native_interfaces" v-bind:key="intf" @click="removeInterfaceFromTrunkNative(intf)">{{intf}}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-footer pt-1 pb-1">
                    <div class="form-row pt-0 pb-0">
                        <div class="col">
                            <div class="form-group row mb-0">
                                <label class="col-sm-auto col-form-label pr-0">add interface</label>
                                <div class="col">
                                    <input class="form-control" type="text" placeholder="Interface Name" v-model="edit_interface" v-on:keyup.enter="addInterfaceToConfig()">
                                </div>
                                <label class="col-form-label col-sm-auto pr-md-0 pl-md-0">to</label>
                                <div class="col">
                                    <select class="form-control" v-model="edit_to">
                                        <option>Access</option>
                                        <option>Trunk</option>
                                        <option>Trunk Native</option>
                                    </select>
                                </div>
                                <div class="col-auto">
                                    <button class="btn btn-primary" @click="addInterfaceToConfig()">add</button>
                                    <button class="btn btn-success" @click="submitVlanConfig()">commit</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            <!-- </form> -->
        </div>
    </div>
</template>

<script>
    import {mapActions} from 'vuex'

    export default {
        

        props: ['groupName', 'hostName'],
        
        data() {
            return {
                access_interfaces: [],
                trunk_interfaces: [],
                trunk_native_interfaces: [],

                edit_id: "",
                edit_name: "",
                edit_interface: "",
                edit_to: "Access",
            }
        },
        methods: {
            ...mapActions([
                'initHosts',
                'initDashboard',
                'fetchFacts',
                'initFacts'
            ]),
            addInterfaceToConfig: function () {
                
                if (this.$store.state.latestFacts[0].data.facts[this.groupName][this.hostName].ansible_net_interfaces_list.includes(this.edit_interface)) {
                    if (!this.access_interfaces.includes(this.edit_interface) && !this.trunk_interfaces.includes(this.edit_interface) && !this.trunk_native_interfaces.includes(this.edit_interface)) {
                        if (this.edit_to == "Access") {
                            this.access_interfaces.push(this.edit_interface)
                        }
                        else if (this.edit_to == "Trunk") {
                            this.trunk_interfaces.push(this.edit_interface)
                        }
                        else if (this.edit_to == "Trunk Native") {
                            this.trunk_native_interfaces.push(this.edit_interface)
                        }
                    }
                }
                //validate interface
                //add interface to the option
            },
            removeInterfaceFromAccess: function (intf) {
                this.access_interfaces.splice(this.access_interfaces.indexOf(intf), 1)
            },
            removeInterfaceFromTrunk: function (intf) {
                this.trunk_interfaces.splice(this.trunk_interface.indexOf(intf),1)
            },
            removeInterfaceFromTrunkNative: function (intf) {
                this.trunk_native_interfaces.splice(this.trunk_native_interfaces.indexOf(intf),1)
            },
            submitVlanConfig: function() {
                var reqBody = {
                    "hostGroup": this.groupName,
                    "task": "add",
                    "vlan": this.edit_id,
                    "vlan_name": this.edit_name,
                    "hosts":{}
                }
                
                reqBody.hosts[this.hostName] = {
                    "access_interfaces": this.access_interfaces,
                    "trunk_interfaces": {}
                }

                var intf
                reqBody.hosts[this.hostName].trunk_interfaces = {}

                for (intf in this.trunk_interfaces){
                    if (this.$store.state.hosts[this.groupName][this.hostName].interfaces[this.trunk_interfaces[intf]].mode == "access") {
                        reqBody.hosts[this.hostName].trunk_interfaces[this.trunk_interfaces[intf]] = {
                            "allowed_vlans": this.$store.state.hosts[this.groupName][this.hostName].interfaces[this.trunk_interfaces[intf]].vlan.access_vlan + "," + this.edit_id,
                            "native_vlan": this.$store.state.hosts[this.groupName][this.hostName].interfaces[this.trunk_interfaces[intf]].vlan.access_vlan
                        }
                    }
                    else {
                        //build list of allowed vlan
                        reqBody.hosts[this.hostName].trunk_interfaces[this.trunk_interfaces[intf]] = {
                            "allowed_vlans": this.$store.state.hosts[this.groupName][this.hostName].interfaces[this.trunk_interfaces[intf]].vlan.trunk.allowed_vlans + ',' + this.edit_id,
                            "native_vlan": this.$store.state.hosts[this.groupName][this.hostName].interfaces[this.trunk_interfaces[intf]].vlan.trunk.native_vlan
                        }
                    }
                }

                for (intf in this.trunk_native_interfaces){
                    if (this.$store.state.hosts[this.groupName][this.hostName].interfaces[this.trunk_native_interfaces[intf]].mode == "access") {
                        if (this.$store.state.hosts[this.groupName][this.hostName].interfaces[this.trunk_native_interfaces[intf]].vlan.access_vlan == undefined){
                            reqBody.hosts[this.hostName].trunk_interfaces[this.trunk_native_interfaces[intf]] = {
                                "allowed_vlans": String(this.edit_id),
                                "native_vlan": parseInt(this.edit_id)
                            }
                        }

                        else {
                            reqBody.hosts[this.hostName].trunk_interfaces[this.trunk_native_interfaces[intf]] = {
                                "allowed_vlans": this.edit_id + ',' + this.$store.state.hosts[this.groupName][this.hostName].interfaces[this.trunk_native_interfaces[intf]].vlan.access_vlan,
                                "native_vlan": parseInt(this.edit_id)
                            }
                        }
                    }
                    else {

                        //build list of allowed vlan
                        reqBody.hosts[this.hostName].trunk_interfaces[this.trunk_native_interfaces[intf]] = {
                            "allowed_vlans": this.$store.state.hosts[this.groupName][this.hostName].interfaces[this.trunk_native_interfaces[intf]].vlan.trunk.allowed_vlans + ',' + this.edit_id,
                            "native_vlan": parseInt(this.edit_id)
                        }
                    }
                }

                console.log(reqBody)
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
                .then(response => response.json)
                .then(json => console.log(json))
                // .then(this.initHosts())
                // .then(this.initDashboard())
                // .then(this.initLatestFacts)
                // .then(this.initFacts())
            }
        }
        
    }
</script>