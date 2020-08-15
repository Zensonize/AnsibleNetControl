import * as types from './mutation-types'

export const mutations = {
    [types.INIT_FACTS] (state, payload) {
        state.facts.push(...payload)
        console.log('init facts with')
        console.log(payload)
    },
    [types.FETCH_FACTS] (state, payload) {
        state.facts.push(...payload)
        if (state.facts.length > 10){
            state.facts.splice(0,state.facts.length-10)
        }
        console.log('updated facts with')
        console.log(payload)
    },
    [types.INIT_HOSTS] (state, payload) {
        state.hosts = payload

        console.log('init hosts data with')
        console.log(payload)
    },
    [types.INIT_DASHBOARD] (state, payload) {
        state.dashboard = payload

        console.log('init dashboard with')
        console.log(payload)
    },
    [types.SAVE_FETCH_TIME] (state, payload) {
        state.lastFetchTime = payload

        console.log('updated last fetch time with')
        console.log(payload)
    },
    [types.INIT_LATEST_FACTS] (state, payload) {
        state.latestFacts = payload

        console.log('init latest facts with')
        console.log(payload)
    }
}