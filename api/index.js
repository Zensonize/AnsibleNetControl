const express = require('express')
const bodyParser = require('body-parser')
const app = express()
const port = 3000
const { response } = require('express')
const got = require('got')
const { pool } = require('./pg')
const XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;

app.use(bodyParser.json())
app.use(
  bodyParser.urlencoded({
    extended: true,
  })
)

function httpGetAsync(theUrl, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", theUrl, true); // true for asynchronous 
    xmlHttp.setRequestHeader("Content-Type", "application/json");
    xmlHttp.send(null);

    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
}

//auto collect data every 1 minute


app.get('/', (request, response) => {
    response.json({ info: 'Node.js, Express, and Postgres API' })
})

app.get('/gatherFacts', (request, response) => {
    //force update
    console.log(request.body)

    if (request.body.gathermode === 'force'){
        //send request to ansible
        console.log("sending request to ansible server")
        httpGetAsync('http://ansible:4000/gatherFacts', function(ansible_facts){
            //put data to the database
            console.log("putting facts to the database")
            pool.query('INSERT INTO facts (data) VALUES ($1)',[ansible_facts], (er, re) => {
                if(er) {
                    console.log(er)
                    response.status(500).json({"msg":"error updating table"})
                } else {
                    //query updated data
                    console.log("querying facts from the database")
                    pool.query('SELECT * FROM facts', (er, re) => {
                        if(er) {
                            console.log(er)
                            response.status(500).json({"msg":"error querying the table"})
                        }
                        response.status(200).json(re.rows)
                    })
                }
            })
        })
    }
    else {
        //query the data from the database
        pool.query('SELECT factsID,dateCreated::text,data FROM facts WHERE dateCreated > $1::timestamptz',[request.body.lastQuery], (er, re) => {
            if(er) {
                console.log(er)
                response.status(500).json({"msg":"error querying the table"})
            }
            else {
                response.status(200).json(re.rows)
            }
        })
    }
    //pull data from db
})

app.listen(port, () => {
    console.log(`App running on port ${port}.`)
  })