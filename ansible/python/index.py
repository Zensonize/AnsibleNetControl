from flask import Flask
from flask import request
import subprocess
import re
import json
import logging
import psycopg2
from psycopg2 import Error

hostfile = open('./inventory', 'r')
hostfile = hostfile.read()
hosts = {}

def dbQuery(q, qData):
    try:
        connection = psycopg2.connect(
            user = "me",
            password = "password",
            host = "db",
            port = "5432",
            database = "ansibru"
        )
        cursor = connection.cursor()
        if len(qData) == 0:
            cursor.execute(q)
            connection.commit()
        else:
            cursor.execute(q, qData)
            connection.commit()

        results = cursor.fetchall()
        return results

    except(Exception, psycopg2.Error) as error:
        app.logger.info("Error connecting to PostgreSQL database", error)
        connection = None
    finally:
        if(connection != None):
            cursor.close()
            connection.close()
            app.logger.info("PostgreSQL connection is now closed")

#parse invenntory file and build list of hosts
regx = '\[([\w]+)\]([\w\s\d.]+)'
x = re.findall(regx, hostfile)
for h in x:
    groupName = h[0].replace('\n','')
    groupHosts = h[1].split('\n')
    groupHosts = list(filter(('').__ne__, groupHosts))
    hosts[groupName] = {}
    hosts[groupName]['hosts'] = groupHosts

#get the device os
regx = '\[([\w]+):vars\][\w\s\d.]*ansible_network_os=([\w]+)'
x = re.findall(regx, hostfile)
for h in x:
    groupName = h[0].replace('\n','')
    hosts[groupName]['os'] = h[1]

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/hosts')
def getHosts():
    return json.dumps(hosts)

# @app.route('/hosts/add', methods=['POST'])
# def addHosts():
#     #add received host to the host list
#     req = request.json
#     if req.group in hosts:
#         hosts[req.group]['hosts'].append(req.hosts)
#     else:
#         hosts[req.group] = {}
#         hosts[req.group]['hosts'] = [req.hosts]
#         hosts[req.group]['os'] = [req.os]
#     #update inventory file
#     for g in hosts:

#     #update inventory.yml file

@app.route('/gatherFacts', methods=['GET'])
def gatherFact():
    app.logger.info('received request')
    req = request.get_json()
    app.logger.info(json.dumps(req))
    if req['gathermode'] == 'force':
        #execute playbook to gather fact
        bashCommand = 'ansible-playbook ./ansible-playbook/collect_cisco_facts.yml'
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        results = {}
        results['ansible_out'] = str(output)
        app.logger.info('finished ansible playbook execution')
        # app.logger.info(output)

        #read playbook output and return as json object
        app.logger.info('reading results from playbook execution')
        facts = {}
        for groupName in hosts:
            facts[groupName] = {}
            for device in hosts[groupName]['hosts']:
                filePath = '../temp/' + device + '-' + hosts[groupName]['os'] + '.json'
                factsfile = open(filePath, 'r')
                factsfile = json.loads(factsfile.read())
                facts[groupName][device] = factsfile["ansible_facts"]
        results['facts'] = facts
        results['hosts'] = hosts

        #put results to the database
        qString = 'INSERT INTO facts (data) VALUES (%s)'
        qData = [results]
        qResult = dbQuery(qString,qData)

    #query data from the database
    qString = 'SELECT factsID,dateCreated::text,data FROM facts WHERE dateCreated > %s::timestamptz'
    qData = [req['lastQuery']]
    qResult = dbQuery(qString,qData)
    return json.dumps(qResult)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=4000,debug=True)