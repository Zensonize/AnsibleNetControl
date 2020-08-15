from flask import Flask, make_response
from flask import request
from flask import Response
from flask import jsonify
from flask_cors import CORS
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

# Bash execution -> grey on white
# Database execution -> magenta
# error -> red
# warning -> yellow
# html request task -> cyan
# general task -> no color mapping

hostData = {}
dashboardData = {}

def sysTime():
    dt = datetime.now()
    ts = dt.strftime("[ %H:%M:%S.%f ]")
    return ts

def bashProcess(cmd):
    print(colored(sysTime(),'grey', 'on_white'), 'bash executing',colored(cmd,'grey','on_white'))
    process = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if(error):
        print(colored(sysTime(),'red'), colored('bash process error : ','red'),cmd, '\n', 'msg:',error)

    print(colored(sysTime(),'grey', 'on_white'), 'bash execution completed')
    return codecs.decode(output,'unicode_escape')

def dbQuery(q,qData):
    results = ""
    print (colored(sysTime(),'magenta'),'Querying: ',q )

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

    except (Exception, psycopg2.Error) as error:
        print(colored(sysTime(),'red'),colored("Query Error: ",'red'), colored(error,'red'))
        connection = None

    finally:
        if(connection != None):
            cursor.close()
            connection.close()
            print(colored(sysTime(),'magenta'),"PostgreSQL connection is now closed")
            return results

def init_Hosts_From_Hostfile():
    try:
        host_file = open('./inventory', 'r')
        hf = host_file.read()
    except IOError:
        print(colored(sysTime(),'red'), 'error reading inventory file: file not exist')
    finally:
        host_file.close()
    print(sysTime(),'reading hostfile')

    #parsing host information from host file
    regx = '\[([\w]+)\]([\w\s\d.]+)'
    regx_results = re.findall(regx, hf)

    #matching host data
    for g in regx_results:
        groupName = g[0].replace('\n','')

        if groupName == 'localhost':
            continue

        else:
            hostData[groupName] = {}

            groupHosts = g[1].split('\n')
            groupHosts = list(filter(('').__ne__, groupHosts))
            for h in groupHosts:
                hostData[groupName][h] = {}

    #reading host os
    regx = '\[([\w]+):vars\][\w\s\d.]*ansible_network_os=([\w]+)'
    x = re.findall(regx, hf)
    for g in x:
        groupName = g[0].replace('\n','')
        for h in hostData[groupName]:
            hostData[groupName][h]['os'] = g[1]

def init_Hosts_From_Database_Cache():
    print(sysTime(),'reading latest information from server')
    latest_fact = dbQuery('SELECT data FROM facts ORDER BY dateCreated DESC LIMIT 1',[])

    if latest_fact != [] :
        for h in hostData['nexus']:
            hostData['nexus'][h]['interfaces'] = latest_fact[0][0]['facts']['nexus'][h]['ansible_net_interfaces']

            #parse vlan list
            vlan_list = []
            for v in latest_fact[0][0]['facts']['nexus'][h]['ansible_net_vlan_list']:
                vlan_list.append(int(v))

            hostData['nexus'][h]['vlans'] = {
                "vlan_list" : vlan_list,
                "vlan" : {}
            }

            #collect vlan facts and put it to hostData
            for v in latest_fact[0][0]['facts']['nexus'][h]['ansible_network_resources']['vlans']:
                hostData['nexus'][h]['vlans']['vlan'][v['vlan_id']] = v
                if 'name' not in v:
                    hostData['nexus'][h]['vlans']['vlan'][v['vlan_id']]['name'] = ''
            
            #add interface traffic to the interface data
            for intf in latest_fact[0][0]['facts']['nexus'][h]['ansible_network_resources']['l2_interfaces']:
                if 'access' in intf and 'trunk' in intf:
                    hostData['nexus'][h]['messages'] = []
                    hostData['nexus'][h]['messages'].append({
                        "type": "warning",
                        "msg": "conflict configuration at" + intf['name'],
                        "debug_dump" : json.dumps(intf,indent=3,sort_keys=True)
                    })
                    print(colored(sysTime(),'yellow'), colored('WARNING conflict configuration at','yellow'),colored(intf['name'],'yellow'),'\n',colored(json.dumps(intf,indent=3,sort_keys=True),'yellow'))
        
                hostData['nexus'][h]['interfaces'][intf['name']]['vlan'] = {}

                if 'access' in intf:
                    hostData['nexus'][h]['interfaces'][intf['name']]['vlan']['access_vlan'] = intf['access']['vlan']
                if 'trunk' in intf:
                    hostData['nexus'][h]['interfaces'][intf['name']]['vlan']['trunk'] = {}

                    if 'native_vlan' in intf['trunk']:
                        hostData['nexus'][h]['interfaces'][intf['name']]['vlan']['trunk']['native_vlan'] = intf['trunk']['native_vlan']
                    if 'allowed_vlans' in intf['trunk']:
                        hostData['nexus'][h]['interfaces'][intf['name']]['vlan']['trunk']['allowed_vlans'] = intf['trunk']['allowed_vlans']
                    if 'native_vlan' not in intf['trunk'] and 'allowed_vlans' in intf['trunk']:
                        hostData['nexus'][h]['interfaces'][intf['name']]['vlan']['trunk']['native_vlan'] = 1
            

            for intf,intf_d in hostData['nexus'][h]['interfaces'].items():
                if 'vlan' not in intf_d:
                    hostData['nexus'][h]['interfaces'][intf]['vlan'] = {
                        "access_vlan": 1
                    }

    else:
        gatherFacts_Forced()
        init_Hosts_From_Database_Cache()

def reachability_Check():

    dbData = {
        "host_status": {
            "offline": [],
            "online": [],
            "total_groups": 0,
            "total_hosts": 0
        }
    }

    print(sysTime(), 'pinging devices')

    stdout = bashProcess('ansible nexus -m ping')
    regx = '([\d.]+)\s*[|]\s*([\w!]+)'
    stdout = re.findall(regx, stdout)

    for h in stdout:
        
        if h[0] == '172.0.0.1':
            continue
        elif h[1] == 'SUCCESS':
            dbData['host_status']['online'].append(h[0])
        else:
            dbData['host_status']['offline'].append(h[0])

    dbData['host_status']['total_hosts'] = len(dbData['host_status']['online']) + len(dbData['host_status']['offline'])
    dbData['host_status']['total_groups'] = len(hostData)

    if len(dbData['host_status']['offline']) > 0:
        dbData['network_status'] = "Attention"
    else:
        dbData['network_status'] = "Ok"

    print(sysTime(), 'updated liveliness information')
    print(json.dumps(dbData, indent=3, sort_keys=True))
    return dbData

def gatherFacts_Forced():
    #execute playbook to gather fact
    print(sysTime(), 'executing playbook')
    stdout = bashProcess('ansible-playbook ./ansible-playbook/collect_cisco_facts.yml')

    print(sysTime(),'finished ansible playbook execution')

    #read playbook output and return as json object
    print(sysTime(),'reading results from playbook execution')

    facts = {}

    for g in hostData:
        facts[g] = {}
        for h in hostData[g]:
            try:
                filePath = '../temp/' + h + '-' + hostData[g][h]['os'] + '.json'
                factsfile = open(filePath, 'r')
                factsfile = json.loads(factsfile.read())
                facts[g][h] = factsfile['nx_fact']['ansible_facts']

                interfaceStats = factsfile['int_fact']

                mgmnt_regx = '(mgmt[\d]+).*\\n.*\\n\s*.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\s*(\d*\s*\w*\s*\w*\s*\w*)\s*(\d*\s*[\w/]*),\s*(\d*\s*[\w/]*)\s*(\d*\s*\w*\s*\w*\s*\w*)\s*(\d*\s*[\w/]*),\s*(\d*\s*[\w/]*)\s*(Rx)\s*(\d+)\s*(input packets)\s*(\d+)\s*(unicast packets)\s*(\d+)\s*(multicast packets)\s*(\d+)\s*(broadcast packets)\s*(\d+)\s*(bytes)\s*(Tx)\s*(\d+)\s*(output packets)\s*(\d+)\s*(unicast packets)\s*(\d+)\s*(multicast packets)\s*(\d+)\s*(broadcast packets)\s*(\d+)\s*(bytes)'
                mgmt_data = re.findall(mgmnt_regx, factsfile['int_fact'][1])

                for item in mgmt_data:
                    facts[g][h]['ansible_net_interfaces'][item[0]]['stats'] = {
                        "Rx": {
                            "ave": {
                                "name": str(item[1]),
                                "bps": item[2],
                                "pps": item[3]
                            },
                            "total_packets": item[8],
                            "unicast_packets": item[10],
                            "multicast_packets": item[12],
                            "broadcast_packets": item[14],
                            "total_bytes": item[16]
                        },
                        "Tx": {
                            "ave": {
                                "name": str(item[4]),
                                "bps": item[5],
                                "pps": item[6]
                            },
                            "total_packets": item[19],
                            "unicast_packets": item[21],
                            "multicast_packets": item[23],
                            "broadcast_packets": item[25],
                            "total_bytes": item[27]
                        }
                    }
                
                interf_regx = '(Ethernet\d+/\d+).*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\s*(\d*\s*\w*\s*input\s*rate)\s*(\d*\s*[\w/]*),\\s*(\d\s*[\w/]*)\\n\s*(\d*\s*\w*\s*\w*\s*\w*)\s*(\d*\s*[\w/]*),\\s*(\d\s*[\w/]*)\\s*.*\\n.*\s*(RX)\s*(\d+)\s*(unicast packets)\s*(\d+)\s*(multicast packets)\s*(\d+)\s*(broadcast packets)\\n\s*(\d+)\s*(input packets)\s*(\d+)\s*(bytes)\\n.*\\n.*\\n.*\\n.*\\n.*\\n.*\\n\s*(TX)\s*(\d+)\s*(unicast packets)\s*(\d+)\s*(multicast packets)\s*(\d+)\s*(broadcast packets)\\n\s*(\d+)\s*(output packets)\s*(\d+)\s*(bytes)'
                interf_data = re.findall(interf_regx, factsfile['int_fact'][1])

                for item in interf_data:
                    facts[g][h]['ansible_net_interfaces'][item[0]]['stats'] = {
                        "Rx": {
                            "ave": {
                                "name": str(item[1]),
                                "bps": item[2],
                                "pps": item[3]
                            },
                            "total_packets": item[14],
                            "unicast_packets": item[8],
                            "multicast_packets": item[10],
                            "broadcast_packets": item[12],
                            "total_bytes": item[16]
                        },
                        "Tx": {
                            "ave": {
                                "name": str(item[4]),
                                "bps": item[5],
                                "pps": item[6]
                            },
                            "total_packets": item[25],
                            "unicast_packets": item[19],
                            "multicast_packets": item[21],
                            "broadcast_packets": item[23],
                            "total_bytes": item[27]
                        }
                    }

            except FileNotFoundError as e:
                print(colored(sysTime(),'red'), colored(e,'red'))
            except KeyError as e:
                print(colored(sysTime(),'red'), colored(e, 'red'), colored('traceback','red'), colored(json.dumps(hostData[groupName],indent=3),'red'))

    results = {
        "facts": facts,
        "hosts": hostData,
        'ansible_out': str(stdout)
    }

    #put data to the database
    print(sysTime(), 'pushing facts data to the database')
    qResult = dbQuery('INSERT INTO facts (data) VALUES (%s)',[json.dumps(results)])
    print(sysTime(),'gatherFacts task Completed')

    #update host information from newly fetched data
    print(sysTime(),'updating Host information')
    init_Hosts_From_Database_Cache()

class threader (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print(sysTime(), 'starting thread', self.name)
        if self.name == 'facts':
            while True:
                print(sysTime(), 'gather facts thread executing playbook')
                gatherFacts_Forced()
                time.sleep(300)
        elif self.name == 'liveliness':
            while True:
                print(sysTime(), 'liveliness thread executing playbook')
                dashboardData = reachability_Check()
                time.sleep(120)

#web activity
def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

app = Flask(__name__)
CORS(app)

#main thread
init_Hosts_From_Hostfile()
init_Hosts_From_Database_Cache()
dashboardData = reachability_Check()

thread1 = threader(1,'facts')
thread2 = threader(2,'liveliness')

# thread1.start()
# thread2.start()

@app.route('/', methods=['GET','OPTIONS'])
def home():
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    elif request.method == 'GET':
        return _corsify_actual_response(jsonify({"msg":"hello"}))
    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))

@app.route('/hosts', methods=['GET','OPTIONS'])
def getHosts():
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    elif request.method == 'GET':
        return _corsify_actual_response(jsonify(hostData))
    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))

@app.route('/dashboard', methods=['GET','OPTIONS'])
def getDashboard():
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    elif request.method == 'GET':
        print(json.dumps(dashboardData, indent=3, sort_keys=True))
        return _corsify_actual_response(jsonify(dashboardData))
    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))

@app.route('/gatherFacts', methods=['POST','OPTIONS'])
def gatherFact():
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    elif request.method == 'POST':
        print(colored(sysTime(), 'cyan'), 'received gather facts request')
        req = request.get_json()
        
        if req['gathermode'] == 'force':
            gatherFacts_Forced()

        #query data from the database
        if req['query_limit'] == '1':
            qResult = dbQuery('SELECT factsID,dateCreated::text,data FROM facts ORDER BY dateCreated DESC LIMIT 1',[])
        else:
            qResult = dbQuery('SELECT factsID,dateCreated::text,data FROM facts WHERE dateCreated > %s::timestamptz ORDER BY dateCreated DESC',[req['lastQuery']])
    
        if qResult == []:
            qResult = dbQuery('SELECT factsID,dateCreated::text,data FROM facts ORDER BY dateCreated DESC LIMIT 12',[])

        #format results to array of objects
        result = []
        for row in qResult:
            temp = {
                "factsID" : row[0],
                "dateCreated" : row[1],
                "data" : row[2]
            }
            result.append(temp)

        return _corsify_actual_response(jsonify(result))

    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))

@app.route('/gatherFactsV2', methods=['POST','OPTIONS'])
def gatherFactV2():
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    elif request.method == 'POST':
        print(colored(sysTime(), 'cyan'), 'received gather facts request')
        req = request.get_json()
        
        if req['gathermode'] == 'force':
            gatherFacts_Forced()

        #query data from the database
        if req['query_limit'] == '1':
            qResult = dbQuery('SELECT factsID,dateCreated::text,data FROM facts ORDER BY dateCreated DESC LIMIT 1',[])
        else:    
            qResult = dbQuery('SELECT factsID,dateCreated::text,data FROM facts ORDER BY dateCreated DESC LIMIT 12',[])

        #format results to array of objects
        result = []
        for row in qResult:
            temp = {
                "factsID" : row[0],
                "dateCreated" : row[1],
                "data" : row[2]
            }
            result.append(temp)

        return _corsify_actual_response(jsonify(result))

    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))

@app.route('/config/vlan', methods=['POST','OPTIONS'])
def vlanConfig():
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    elif request.method == 'POST':
        print(colored(sysTime,'cyan'), 'received vlan configuration request')
        req = request.get_json()
        print(json.dumps(req, indent=3,sort_keys=True))

        if req['hostGroup'] == 'nexus':
            if req['task'] == 'add':

                #write temp file to pass to ansible playbook execution
                print(colored(sysTime(),'cyan'), 'writing temp file for ansible execution')
                conf_temp = open("../temp/config.json", "w")
                conf_temp.write(json.dumps(req, indent=3, sort_keys=True))
                conf_temp.close()

                #create vlan on switch
                output = bashProcess("ansible-playbook ./ansible-playbook/nexus_add_vlan.yml")
                print(colored(sysTime(),'cyan'),'created vlan on switch traceback\n', output)

                # #force gather facts to store changes
                # print(colored(sysTime(),'cyan'),'force updating facts to the database')
                # gatherFacts_Forced()

                # #update host vlan information
                # print(colored(sysTime(),'cyan'),'force refreshing host variable')
                # init_Hosts_From_Database_Cache()

                # #add vlan to access interface
                output = bashProcess("ansible-playbook ./ansible-playbook/nexus_add_vlan_to_access_port.yml")
                print(colored(sysTime(),'cyan'),'added vlan to access interface traceback\n', output)

                # #add vlan to trunk interface
                output = bashProcess("ansible-playbook ./ansible-playbook/nexus_add_vlan_to_trunk_port.yml")
                print(colored(sysTime(),'cyan'),'added vlan to trunk interface traceback\n', output)

                #force gather facts to store changes
                print(colored(sysTime(),'cyan'),'force updating facts to the database')
                gatherFacts_Forced()

                #update host vlan information
                print(colored(sysTime(),'cyan'),'force refreshing host variable')
                init_Hosts_From_Database_Cache()

            elif req['task'] == 'delete':
                #write config temp file
                print(colored(sysTime(),'cyan'), 'writing temp file for ansible execution')
                conf_temp = open("../temp/config.json", "w")
                conf_temp.write(json.dumps(req, indent=3, sort_keys=True))
                conf_temp.close()

                #execute playbook
                print(colored(sysTime(),'cyan'),'executing playbook to delete vlan')
                output = bashProcess("ansible-playbook ./ansible-playbook/nexus_delete_vlan.yml")
                print(colored(sysTime(),'cyan'),'deleted vlan on switch traceback\n', output)
                print(colored(sysTime(),'cyan'), 'finished executing playbook')

                #force gather facts to store changes
                print(colored(sysTime(),'cyan'),'force updating facts to the database')
                gatherFacts_Forced()

                #update host vlan information
                print(colored(sysTime(),'cyan'),'force refreshing host variable')
                init_Hosts_From_Database_Cache()

        re = {
            'hosts': hostData,
            'dashboard': dashboardData
        }
        return _corsify_actual_response(jsonify(re))

    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=4000,debug=True)