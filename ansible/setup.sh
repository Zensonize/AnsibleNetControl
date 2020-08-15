echo 'begin setup routine'
apt -y -qq update
apt -y -qq install ansible 
apt -y -qq install python3-pip 
apt -y -qq install libpq-dev python3-dev
apt -y -qq install xping
pip3 -q install flask
pip3 -q install flask-cors
pip3 -q install paramiko
pip3 -q install psycopg2-binary
pip3 install ansible
pip3 install termcolor
python3 --version
ls -l /etc/localtime
cat /etc/timezone
python3 python/index.py