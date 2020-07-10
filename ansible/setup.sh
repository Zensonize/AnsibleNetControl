apt -y -qq update 
apt -y -qq install ansible 
apt -y -qq install python3-pip 
apt -y -qq install libpq-dev python3-dev
pip3 -q install flask
pip3 -q install paramiko
pip3 -q install psycopg2-binary
python3 --version
python3 python/index.py