import * as types from './mutation-types'

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

export const initFacts = ({commit}) => {
    var dateFormat = require('dateformat')
    var DateOptions = "yyyy-m-d hh:mm:ss"
    var tz = -new Date().getTimezoneOffset()/60
    var d = dateFormat(new Date(), DateOptions)
    if (tz >= 0) {
        d += '+' + String(tz)
    }
    else {
        d += '-' + String(tz)
    }

    var req_body = {
        "gathermode": "-",
        "lastQuery": d
    }

    fetch('http://ansible:4000//gatherFacts', {
        method: 'GET',
        mode: 'no-cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(req_body)
    })
    .then(response => response.json())
    .then(json => commit(types.INIT_HOSTS, json))
}

export const fetchHosts = ({commit}) => {
    let headers = new Headers();
    headers.append('Content-Type', 'application/json');
    headers.append('Accept', 'application/json');
    headers.append('Origin','http://localhost:4000/hosts');
    fetch('http://ansible:4000/hosts', {
        method: 'GET',
        mode: 'no-cors'
    })
    .then(response => response.json())
    .then(json => commit(types.FETCH_HOSTS, json))
}

export const fetchFacts = ({commit}) => {
    var dateFormat = require('dateformat')
    var DateOptions = "yyyy-m-d hh:mm:ss"
    var currentTime = new Date()
    currentTime.setMinutes(currentTime.getMinutes() - 5)

    var tz = -currentTime.getTimezoneOffset()/60
    var d = dateFormat(currentTime, DateOptions)
    if (tz >= 0) {
        d += '+' + String(tz)
    }
    else {
        d += '-' + String(tz)
    }

    var req_body = {
        "gathermode": "-",
        "lastQuery": d
    }

    fetch('http://ansible:4000//gatherFacts', {
        method: 'GET',
        mode: 'no-cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(req_body)
    })
    .then(response => response.json())
    .then(json => commit(types.INIT_HOSTS, json))
}