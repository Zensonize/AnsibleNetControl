import * as types from './mutation-types'
import store from '.'

function get_last_5_min() {

    var dateFormat = require('dateformat')
    var DateOptions = "yyyy-m-d hh:mm:ss"

    var d = new Date()
    var ms = Date.parse(d)
    ms = ms - ( 5 * 60 * 1000)
    d = new Date(ms)

    var tz = -new Date().getTimezoneOffset()/60
    var d = dateFormat(d, DateOptions)

    if (tz >= 0) {
        d += '+' + String(tz)
    }
    else {
        d += '-' + String(tz)
    }

    return d
}

function get_current_time() {
    var dateFormat = require('dateformat')
    var DateOptions = "yyyy-m-d hh:mm:ss"

    var d = new Date()

    var tz = -new Date().getTimezoneOffset()/60
    var d = dateFormat(d, DateOptions)

    if (tz >= 0) {
        d += '+' + String(tz)
    }
    else {
        d += '-' + String(tz)
    }

    return d
}

export const initHosts = ({commit}) => {
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');
    headers.append('Accept', 'application/json');
    headers.append('Origin','http://localhost:4000/hosts');

    fetch('http://localhost:4000/hosts', {
        method: 'GET',
        mode: 'cors',
        headers: headers
    })
    .then(response => {return response.json()})
    .then(result => commit(types.INIT_HOSTS, result))
}

export const initDashboard = ({commit}) => {
    let headers = new Headers()
    headers.append('Content-Type', 'application/json');
    headers.append('Accept', 'application/json');
    headers.append('Origin','http://localhost:4000/dashboard');
    fetch('http://localhost:4000/dashboard', {
        method: 'GET',
        mode: 'cors',
        headers: headers
    })
    .then(response => {return response.json()})
    .then(result => commit(types.INIT_DASHBOARD, result))
}

export const initFacts = ({commit}) => {
    let headers = new Headers()
    headers.append('Content-Type', 'application/json');
    headers.append('Accept', 'application/json');
    headers.append('Origin','http://localhost:4000/gatherFacts');

    var req_body = {
        "gathermode": "-",
        "lastQuery": get_last_5_min()
    }

    fetch('http:/localhost:4000/gatherFacts', {
        method: 'GET',
        mode: 'cors',
        headers: headers,
        body: JSON.stringify(req_body)
    })
    .then(response => response.json())
    .then(json => commit(types.INIT_FACTS, json))
    .then(commit(types.SAVE_FETCH_TIME,get_current_time()))
}

export const fetchFacts = ({commit}) => {
    let headers = new Headers()
    headers.append('Content-Type', 'application/json');
    headers.append('Accept', 'application/json');
    headers.append('Origin','http://localhost:4000/gatherFacts');

    var req_body = {
        "gathermode": "-",
        "lastQuery": store.lastFetchTime
    }

    fetch('http:/localhost:4000/gatherFacts', {
        method: 'GET',
        mode: 'cors',
        headers: headers,
        body: JSON.stringify(req_body)
    }).then(response => response.json())
    .then(json => commit(types.FETCH_FACTS, json))
    .then(commit(types.SAVE_FETCH_TIME,get_current_time()))
}