from flask import Flask
import subprocess
import re
import json

hostfile = open('./inventory', 'r')
hosts = {}

#parse invenntory file and build list of hosts
regx = '\[([\w]+)\]([\w\s\d.]+)'
x = re.findall(regx, hostfile.read())
for d in x:
    groupName = d[0].replace('\n','')
    groupHosts = d[1].split('\n')
    groupHosts = list(filter(('').__ne__, groupHosts))
    hosts[groupName] = groupHosts

print(json.dumps(hosts))

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/gatherFacts')
def gatherFact():
    bashCommand = 'ansible-playbook ../ansible-playbook/collect_cisco_facts.yml'
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    #read facts file

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=4000)