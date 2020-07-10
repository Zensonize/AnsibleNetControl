from flask import Flask
from flask import request
import subprocess
import re
import json
import logging
import psycopg2
from psycopg2 import Error
import threading
import time

hostfile = open('./inventory', 'r')
hostfile = hostfile.read()
hosts = {}

def dbQuery(q, qData):
    results = ""
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

        if 'SELECT' in q:
            results = cursor.fetchall()

    except(Exception, psycopg2.Error) as error:
        print("Error: ", error)
        connection = None
    finally:
        if(connection != None):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is now closed")
            return results

def bashProcess(cmd):
    bashCommand = 'ansible-playbook ./ansible-playbook/collect_cisco_facts.yml'
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if(error):
        print(error)
    return output

def serverInit():   
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

def gatherFacts():
    #execute playbook to gather fact
    print('executing playbook' , threading.get_ident())
    bashCommand = 'ansible-playbook ./ansible-playbook/collect_cisco_facts.yml'
    output = bashProcess(bashCommand)
    results = {}
    results['ansible_out'] = str(output)
    print('finished ansible playbook execution')
    # print(output)

    #read playbook output and return as json object
    print('reading results from playbook execution')
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
    print('pushing data to database')
    qString = 'INSERT INTO facts (data) VALUES (%s)'
    qData = [json.dumps(results)]
    qResult = dbQuery(qString,qData)
    print('done')

def gatherFactsThread():
    while True:
        print('i am: ', threading.get_ident())
        gatherFacts()
        time.sleep(60)


def mainThread():
    serverInit()

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
        print('received request')
        req = request.get_json()
        print(json.dumps(req))
        if req['gathermode'] == 'force':
            gatherFacts()

        #query data from the database
        qString = 'SELECT factsID,dateCreated::text,data FROM facts WHERE dateCreated > %s::timestamptz'
        qData = [req['lastQuery']]
        qResult = dbQuery(qString,qData)
        return json.dumps(qResult)

    @app.route('/config/predef/vlan', methods=['POST'])
    def addVlan():
        print('received request')
        req = request.get_json()
        print(json.dumps(req))

        if req['hosts'] == 'all':
            if req['task'] == 'add' and hosts[req['hostGroup']]['os'] ==  'nxos':
                bashCommand = 'ansible-playbook ./ansible-playbook/add_vlan.yml'
                output = bashProcess(bashCommand)

        return json.dumps({'result':'OK'})

    if __name__ == '__main__':
        app.run(host='0.0.0.0',port=4000,debug=True)

class threader (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print ("Starting " + self.name)
        gatherFactsThread()
        print ("Exiting " + self.name)

thread1 = threader(1, "facts")
thread1.start()

mainThread()