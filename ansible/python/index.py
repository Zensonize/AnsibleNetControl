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
from datetime import datetime
import codecs

hostfile = open('./inventory', 'r')
hostfile = hostfile.read()
hosts = {}

def sysTime():
    dt = datetime.now()
    ts = dt.strftime("[ %H:%M:%S.%f ]")
    return ts

def dbQuery(q, qData):
    results = ""
    print (sysTime(),'executing database query',q )
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
        print(sysTime(),"Error: ", error)
        connection = None
    finally:
        if(connection != None):
            cursor.close()
            connection.close()
            print(sysTime(),"PostgreSQL connection is now closed")
            return results

def bashProcess(cmd):
    print(sysTime(), 'bash executing',cmd)
    process = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if(error):
        print(sysTime(), 'bash process error : ',cmd, '\n', 'msg:',error)
    return codecs.decode(output,'unicode_escape')

def bashProcessArgs(cmd):
    print(sysTime(), 'bash executing',cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if(error):
        print(sysTime(), 'bash process error : ',cmd, '\n', 'msg:',error)
    return codecs.decode(output,'unicode_escape')

def serverInit():   
    #parse invenntory file and build list of hosts
    print(sysTime(),'initializing server')
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

    #get interface list by reading cached file from the server
    latest_fact = dbQuery('SELECT data from facts ORDER BY dateCreated DESC LIMIT 1',[])
    # print(latest_fact[0][0]['facts']['nexus']['192.168.10.75']['ansible_net_config'])
    for h in hosts['nexus']['hosts']:
        
        hosts['nexus'][h] = {}
        hosts['nexus'][h]['interfaces'] = latest_fact[0][0]['facts']['nexus'][h]['ansible_net_interfaces']

        #parse vlan from range to list
        vlan_List = []
        hosts['nexus'][h]['vlan_list'] = latest_fact[0][0]['facts']['nexus'][h]['ansible_net_vlan_list']

        hosts['nexus'][h]['vlans'] = {}

        for v in hosts['nexus'][h]['vlan_list']:
            vlan_List.append(int(v))

        # collect vlan status
        # print(sysTime,json.dumps(latest_fact[0][0]['facts']['nexus'][h],indent=3,sort_keys=True))
        
        # for v in latest_fact[0][0]['facts']['nexus'][h]['ansible_network_resources']['vlans']:
        #     hosts['nexus'][h]['vlans'][v['vlan_id']] = v
        #     if 'name' not in v:
        #         hosts['nexus'][h]['vlans'][v['vlan_id']]['name'] = ''

        # hosts['nexus'][h]['vlan_list'] = vlan_List
        # print(sysTime(),json.dumps(hosts['nexus'][h]['vlan_list']))
        
        #read configuration and parse the access vlan of each access interface
        regx_access = "interface ([\w/]+)\\n  switchport access vlan ([\d]+)"
        access_interfaces = re.findall(regx_access,latest_fact[0][0]['facts']['nexus'][h]['ansible_net_config'])
        for aif in access_interfaces:
           hosts['nexus'][h]['interfaces'][aif[0]]['access_vlan'] = aif[1]
        
        #read configuration and parse the trunk vlan of each trunnk interface
        regx_trunk = "interface ([\w\d/]+)[\\n\s]*(switchport mode trunk)[\\n\s]*(switchport trunk native vlan )*([\d]+)*[\\n\s]*(switchport trunk allowed vlan )*([\d-])"
        trunk_interfaces = re.findall(regx_trunk,latest_fact[0][0]['facts']['nexus'][h]['ansible_net_config'])

        # read interface information from l2_interface
        for tif in trunk_interfaces:
            hosts['nexus'][h]['interfaces'][tif[0]]['trunk'] = {}
            hosts['nexus'][h]['interfaces'][tif[0]]['trunk']['native_vlan'] = tif[3]
            hosts['nexus'][h]['interfaces'][tif[0]]['trunk']['allowed_vlan'] = tif[5]

        for intf in hosts['nexus'][h]['interfaces']:
            if 'mode' in hosts['nexus'][h]['interfaces'][intf]:
                if hosts['nexus'][h]['interfaces'][intf]['mode'] == 'access' and 'access_vlan' not in hosts['nexus'][h]['interfaces'][intf]:
                    hosts['nexus'][h]['interfaces'][intf]['access_vlan'] = '1'

        # new code version to support gather facts with network resources
        # for i in latest_fact[0][0]['facts']['nexus'][h]['ansible_network_resources']['l2_interfaces']:
        #     if 'access' in i and 'trunk' in i:
        #         print(sysTime(), 'WARNING conflict configuration at',i['name'],'\n',json.dumps(i,indent=3,sort_keys=True))
        #     if 'access' in i:
        #         hosts['nexus'][h]['interfaces'][i['name']]['access_vlan'] = i['access']['vlan']
        #     if 'trunk' in i:
        #         hosts['nexus'][h]['interfaces'][i['name']]['trunk'] = {}
        #         if 'native_vlan' in i['trunk']:
        #             hosts['nexus'][h]['interfaces'][i['name']]['trunk']['native_vlan'] = i['trunk']['native_vlan']
        #         if 'allowed_vlans' in i['trunk']:
        #             hosts['nexus'][h]['interfaces'][i['name']]['trunk']['allowed_vlans'] = i['trunk']['allowed_vlans']

        #     print(sysTime(),json.dumps(hosts['nexus'][h]['interfaces'][i['name']],indent=3,sort_keys=True))
        
    hosts['localhost']['os'] = 'Ubuntu:20.04'

def gatherFacts():
    #execute playbook to gather fact
    print('\t',sysTime(),'executing playbook', threading.get_ident())
    bashCommand = 'ansible-playbook ./ansible-playbook/collect_cisco_facts.yml'
    output = bashProcess(bashCommand)
    results = {}
    results['ansible_out'] = str(output)
    print('\t',sysTime(),'finished ansible playbook execution')

    #read playbook output and return as json object
    print('\t',sysTime(),'reading results from playbook execution')
    facts = {}
    for groupName in hosts:
        facts[groupName] = {}
        for device in hosts[groupName]['hosts']:

            filePath = '../temp/' + device + '-' + hosts[groupName]['os'] + '.json'
            try:
                factsfile = open(filePath, 'r')
                factsfile = json.loads(factsfile.read())
                facts[groupName][device] = factsfile["ansible_facts"]
            except FileNotFoundError as e:
                print(sysTime(), e)

    results['facts'] = facts
    results['hosts'] = hosts

    #put results to the database
    print('\t',sysTime(),'pushing data to database')
    qString = 'INSERT INTO facts (data) VALUES (%s)'
    qData = [json.dumps(results)]
    qResult = dbQuery(qString,qData)
    print('\t',sysTime(),'gatherFacts task Completed')

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

    #     #update inventory.yml fil

    @app.route('/gatherFacts', methods=['GET'])
    def gatherFact():
        print(sysTime(),'received request')
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
    def predefVlanTask():
        print('received request')
        req = request.get_json()
        print(json.dumps(req))
        if req['hostGroup'] == 'nexus':
            if req['task'] == 'add' and hosts[req['hostGroup']]['os'] ==  'nxos':

                #write config temp file
                conf_temp = open("../temp/config.json", "w")
                conf_temp.write(json.dumps(req, indent=3, sort_keys=True))
                conf_temp.close()

                #create vlan on switch
                output = bashProcessArgs(["ansible-playbook", "./ansible-playbook/nexus_add_vlan.yml"])

                print(sysTime(),'created vlan on switch traceback\n', output)
                #force gather facts to store changes
                print(sysTime(),'force updating facts to the database')
                gatherFacts()

                #update host vlan information
                print(sysTime(),'force refreshing host variable')
                serverInit()

                #add vlan to access interface
                output = bashProcessArgs(["ansible-playbook", "./ansible-playbook/nexus_add_vlan_to_access_port.yml"])
                print(sysTime(),'added vlan to access interface traceback\n', output)

                #add vlan to trunk interface
                output = bashProcessArgs(["ansible-playbook", "./ansible-playbook/nexus_add_vlan_to_trunk_port.yml"])
                print(sysTime(),'added vlan to trunk interface traceback\n', output)

                #force gather facts to store changes
                print(sysTime(),'force updating facts to the database')
                gatherFacts()

                #update host vlan information
                print(sysTime(),'force refreshing host variable')
                serverInit()

            if req['task'] == 'delete' and hosts[req['hostGroup']]['os'] ==  'nxos':
                
                #write config temp file
                conf_temp = open("../temp/config.json", "w")
                conf_temp.write(json.dumps(req, indent=3, sort_keys=True))
                conf_temp.close()

                #execute playbook
                print(sysTime(),'executing playbook to delete vlan')
                output = bashProcessArgs(["ansible-playbook", "./ansible-playbook/nexus_delete_vlan.yml"])
                print(sysTime(), 'finished executing playbook')

                #force gather facts to store changes
                print(sysTime(),'force updating facts to the database')
                gatherFacts()

                #update host vlan information
                print(sysTime(),'force refreshing host variable')
                serverInit()

        return json.dumps({'result':'OK'})

    @app.route('/test/query', methods=['POST'])
    def testQuery():
        req = request.get_json()
        print(sysTime(),'received request', json.dumps(req))
        qResult = dbQuery(req['qString'],[])
        return json.dumps(qResult)

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

# thread1 = threader(1, "facts")
# thread1.start()

#print(json.dumps(hosts, indent=3, sort_keys=True))
mainThread()