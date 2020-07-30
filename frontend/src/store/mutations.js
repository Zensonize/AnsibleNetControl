import * as types from './mutation-types'

export const mutations = {
    [types.INIT_FACTS] (state, payload) {
        state.facts.push(...payload)
    },
    [types.FETCH_FACTS] (state, payload) {
        state.facts.push(...payload)
        if (state.facts.length > 10){
            state.facts.splice(0,state.facts.length-10)
        }
    },
    [types.INIT_HOSTS] (state, payload) {
        state.hosts = payload
        console.log(state.hosts)
    },
    [types.INIT_DASHBOARD] (state, payload) {
        state.dashboard = payload
    },
    [types.SAVE_FETCH_TIME] (state, payload) {
        state.lastFetchTime = payload
    }
}