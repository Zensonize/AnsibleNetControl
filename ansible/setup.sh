echo 'begin setup routine'
apt -y -qq update 
echo $TZ > /etc/timezone && \ apt -y -qq install tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt -y -qq clean
rm /etc/localtime
apt -y -qq install ansible 
apt -y -qq install python3-pip 
apt -y -qq install libpq-dev python3-dev
pip3 -q install flask
pip3 -q install paramiko
pip3 -q install psycopg2-binary
pip3 install ansible
pip3 install termcolor
python3 --version
python3 python/index.py