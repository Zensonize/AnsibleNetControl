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
from termcolor import colored

hostfile = open('./inventory', 'r')
hostfile = hostfile.read()
hosts = {}

def sysTime():
    dt = datetime.now()
    ts = dt.strftime("[ %H:%M:%S.%f ]")
    return ts

#magenta
def dbQuery(q, qData):
    results = ""
    print (colored(sysTime(),'magenta'),'executing database query',q )
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
        print(colored(sysTime(),'red'),colored("Error: ",'red'), colored(error,'red'))
        connection = None
    finally:
        if(connection != None):
            cursor.close()
            connection.close()
            print(colored(sysTime(),'magenta'),"PostgreSQL connection is now closed")
            return results

#blue
def bashProcess(cmd):
    print(colored(sysTime(),'blue'), 'bash executing',cmd)
    process = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
    output, error = process.communicate()
    if(error):
        print(colored(sysTime(),'red'), colored('bash process error : ','red'),cmd, '\n', 'msg:',error)
    print(colored(sysTime(),'blue'), 'bash execution completed')
    return codecs.decode(output,'unicode_escape')

#blue
def bashProcessArgs(cmd):
    print(colored(sysTime(),'blue'), 'bash executing',cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if(error):
        print(sysTime(), 'bash process error : ',cmd, '\n', 'msg:',error)
    print(colored(sysTime(),'blue'), 'bash execution completed')
    return codecs.decode(output,'unicode_escape')

#cyan
def serverInit():   
    #parse invenntory file and build list of hosts
    print(colored(sysTime(),'cyan'),'initializing server')
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
    print(colored(sysTime(),'cyan'),'reading latest information from server')
    latest_fact = dbQuery('SELECT data from facts ORDER BY dateCreated DESC LIMIT 1',[])
    if(latest_fact != []):
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
            # print(sysTime,h,json.dumps(latest_fact[0][0]['facts']['nexus'][h]['ansible_network_resources'],indent=3,sort_keys=True))
            
            for v in latest_fact[0][0]['facts']['nexus'][h]['ansible_network_resources']['vlans']:
                hosts['nexus'][h]['vlans'][v['vlan_id']] = v
                if 'name' not in v:
                    hosts['nexus'][h]['vlans'][v['vlan_id']]['name'] = ''

            hosts['nexus'][h]['vlan_list'] = vlan_List
            # print(sysTime(),json.dumps(hosts['nexus'][h]['vlan_list'],indent=3,sort_keys=True))
            # print(sysTime(),json.dumps(hosts['nexus'][h]['vlans'],indent=3,sort_keys=True))

            #set default vlan to vlan 1 if not config
            for intf in hosts['nexus'][h]['interfaces']:
                if 'mode' in hosts['nexus'][h]['interfaces'][intf]:
                    if hosts['nexus'][h]['interfaces'][intf]['mode'] == 'access' and 'access_vlan' not in hosts['nexus'][h]['interfaces'][intf]:
                        hosts['nexus'][h]['interfaces'][intf]['access_vlan'] = '1'

            # new code version to support gather facts with network resources
            for i in latest_fact[0][0]['facts']['nexus'][h]['ansible_network_resources']['l2_interfaces']:
                if 'access' in i and 'trunk' in i:
                    print(sysTime(), 'WARNING conflict configuration at',i['name'],'\n',json.dumps(i,indent=3,sort_keys=True))
                if 'access' in i:
                    hosts['nexus'][h]['interfaces'][i['name']]['access_vlan'] = i['access']['vlan']
                if 'trunk' in i:
                    hosts['nexus'][h]['interfaces'][i['name']]['trunk'] = {}
                    if 'native_vlan' in i['trunk']:
                        hosts['nexus'][h]['interfaces'][i['name']]['trunk']['native_vlan'] = i['trunk']['native_vlan']
                    if 'allowed_vlans' in i['trunk']:
                        hosts['nexus'][h]['interfaces'][i['name']]['trunk']['allowed_vlans'] = i['trunk']['allowed_vlans']

            #     print(sysTime(),json.dumps(hosts['nexus'][h]['interfaces'][i['name']],indent=3,sort_keys=True))

    else:
        #if the database is empty force initial facts gathering then pull the data again
        gatherFacts()
        serverInit()     

    hosts['localhost']['os'] = 'Ubuntu:20.04'

#white on_magenta
def gatherFacts():
    #execute playbook to gather fact
    print(colored(sysTime(),'white','on_magenta'),'executing playbook', threading.get_ident())
    bashCommand = 'ansible-playbook ./ansible-playbook/collect_cisco_facts.yml'
    output = bashProcess(bashCommand)
    results = {}
    results['ansible_out'] = str(output)
    print(colored(sysTime(),'white','on_magenta'),'finished ansible playbook execution')

    #read playbook output and return as json object
    print(colored(sysTime(),'white','on_magenta'),'reading results from playbook execution')
    facts = {}
    for groupName in hosts:
        facts[groupName] = {}
        for device in hosts[groupName]['hosts']:

            filePath = '../temp/' + device + '-' + hosts[groupName]['os'] + '.json'
            try:
                factsfile = open(filePath, 'r')
                factsfile = json.loads(factsfile.read())
                facts[groupName][device] = factsfile['nx_fact']['ansible_facts']

                interfaceStats = factsfile['int_fact']

                mgmnt_regx = '(mgmt[\d]+).*\\n.*\\n\s*.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\s*(\d*\s*\w*\s*\w*\s*\w*)\s*(\d*\s*[\w/]*),\s*(\d*\s*[\w/]*)\s*(\d*\s*\w*\s*\w*\s*\w*)\s*(\d*\s*[\w/]*),\s*(\d*\s*[\w/]*)\s*(Rx)\s*(\d+)\s*(input packets)\s*(\d+)\s*(unicast packets)\s*(\d+)\s*(multicast packets)\s*(\d+)\s*(broadcast packets)\s*(\d+)\s*(bytes)\s*(Tx)\s*(\d+)\s*(output packets)\s*(\d+)\s*(unicast packets)\s*(\d+)\s*(multicast packets)\s*(\d+)\s*(broadcast packets)\s*(\d+)\s*(bytes)'

                intfacts = open('../temp/sh_int_temp.json', 'r')
                intfacts = json.loads(intfacts.read())

                # print(intfacts['int_fact'][1])
                mgmt_data = re.findall(mgmnt_regx, intfacts['int_fact'][1])
                
                for item in mgmt_data:
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats'] = {}
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']={}
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['ave']={}
                    # print(item[1])
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['ave']['name'] = str(item[1])
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['ave']['bps'] = item[2]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['ave']['pps'] = item[3]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['total_packets'] = item[8]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['unicast_packets'] = item[10]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['multicast_packets'] = item[12]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['broadcast_packets'] = item[14]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['total_bytes'] = item[16]

                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']={}
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['ave']={}
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['ave']['name'] = item[4]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['ave']['bps'] = item[5]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['ave']['pps'] = item[6]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['total_packets'] = item[19]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['unicast_packets'] = item[21]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['multicast_packets'] = item[23]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['broadcast_packets'] = item[25]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['total_bytes'] = item[27]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]

                    # print(sysTime(),item)

                    # print(json.dumps(facts[groupName][device]['ansible_net_interfaces'][item[0]], indent=3, sort_keys=True))

                interf_regx = '(Ethernet\d+/\d+).*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\s*(\d*\s*\w*\s*input\s*rate)\s*(\d*\s*[\w/]*),\\s*(\d\s*[\w/]*)\\n\s*(\d*\s*\w*\s*\w*\s*\w*)\s*(\d*\s*[\w/]*),\\s*(\d\s*[\w/]*)\\s*.*\\n.*\s*(RX)\s*(\d+)\s*(unicast packets)\s*(\d+)\s*(multicast packets)\s*(\d+)\s*(broadcast packets)\\n\s*(\d+)\s*(input packets)\s*(\d+)\s*(bytes)\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n\s*(TX)\s*(\d+)\s*(unicast packets)\s*(\d+)\s*(multicast packets)\s*(\d+)\s*(broadcast packets)\\n\s*(\d+)\s*(output packets)\s*(\d+)\s*(bytes)'
                interf_data = re.findall(interf_regx, intfacts['int_fact'][1])

                # print(sysTime(),len(interf_data))
                # print(interf_data[0])
                for item in interf_data:
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats'] = {}
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']={}
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']={}
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['ave']={}
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['ave']={}

                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['ave']['name'] = str(item[1])
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['ave']['bps'] = item[2]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['ave']['pps'] = item[3]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['ave']['name'] = item[4]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['ave']['bps'] = item[5]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['ave']['pps'] = item[6]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['unicast_packets'] = item[8]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['multicast_packets'] = item[10]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Rx']['broadcast_packets'] = item[12]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['total_packets'] = item[14]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['total_bytes'] = item[16]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['unicast_packets'] = item[19]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['multicast_packets'] = item[21]
                    facts[groupName][device]['ansible_net_interfaces'][item[0]]['stats']['Tx']['broadcast_packets'] = item[23]

                # print(json.dumps(facts[groupName][device]['ansible_net_interfaces']['Ethernet1/1'], indent=3, sort_keys=True))
            except FileNotFoundError as e:
                print(colored(sysTime(),'yellow'), colored(e,'yellow'))

    results['facts'] = facts
    results['hosts'] = hosts

    #put results to the database
    print(colored(sysTime(),'white','on_magenta'),'pushing data to database')
    qString = 'INSERT INTO facts (data) VALUES (%s)'
    qData = [json.dumps(results)]
    qResult = dbQuery(qString,qData)
    print(colored(sysTime(),'white','on_magenta'),'gatherFacts task Completed')

def gatherFactsThread():
    while True:
        print(sysTime(), 'i am thread: ', threading.get_ident)
        gatherFacts()
        time.sleep(60)

#on_blue
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
        print(colored(sysTime(),'white','on_blue'),'received request')
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

                print(colored(sysTime(),'white','on_blue'),'created vlan on switch traceback\n', output)
                #force gather facts to store changes
                print(colored(sysTime(),'white','on_blue'),'force updating facts to the database')
                gatherFacts()

                #update host vlan information
                print(colored(sysTime(),'white','on_blue'),'force refreshing host variable')
                serverInit()

                #add vlan to access interface
                output = bashProcessArgs(["ansible-playbook", "./ansible-playbook/nexus_add_vlan_to_access_port.yml"])
                print(colored(sysTime(),'white','on_blue'),'added vlan to access interface traceback\n', output)

                #add vlan to trunk interface
                output = bashProcessArgs(["ansible-playbook", "./ansible-playbook/nexus_add_vlan_to_trunk_port.yml"])
                print(colored(sysTime(),'white','on_blue'),'added vlan to trunk interface traceback\n', output)

                #force gather facts to store changes
                print(colored(sysTime(),'white','on_blue'),'force updating facts to the database')
                gatherFacts()

                #update host vlan information
                print(colored(sysTime(),'white','on_blue'),'force refreshing host variable')
                serverInit()

            if req['task'] == 'delete' and hosts[req['hostGroup']]['os'] ==  'nxos':
                
                #write config temp file
                conf_temp = open("../temp/config.json", "w")
                conf_temp.write(json.dumps(req, indent=3, sort_keys=True))
                conf_temp.close()

                #execute playbook
                print(colored(sysTime(),'white','on_blue'),'executing playbook to delete vlan')
                output = bashProcessArgs(["ansible-playbook", "./ansible-playbook/nexus_delete_vlan.yml"])
                print(colored(sysTime(),'white','on_blue'), 'finished executing playbook')

                #force gather facts to store changes
                print(colored(sysTime(),'white','on_blue'),'force updating facts to the database')
                gatherFacts()

                #update host vlan information
                print(colored(sysTime(),'white','on_blue'),'force refreshing host variable')
                serverInit()

        return json.dumps(hosts,indent=3,sort_keys=True)

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
        print (sysTime(), "Starting Thread: " + self.name)
        gatherFactsThread()
        print (sysTime(), "Exiting Thread" + self.name)

# thread1 = threader(1, "facts")
# thread1.start()

# print(json.dumps(hosts, indent=3, sort_keys=True))
mainThread()