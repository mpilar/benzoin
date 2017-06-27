cat <<'BOOTSTRAP' > bootstrap.sh

sudo apt install python3-pip mongodb-org -y && sudo pip3 install --upgrade pip boto3 pymongo

sudo tee /etc/systemd/system/mongodb.service <<'MONGOSERVICE'
[Unit]
Description=High-performance, schema-free document-oriented database
After=network-online.target
Requires=cloud-init.service

[Service]
User=mongodb
ExecStart=/usr/bin/mongod --quiet --journal --config /etc/mongod.conf

[Install]
WantedBy=multi-user.target
MONGOSERVICE

sudo systemctl daemon-reload
sudo systemctl unmask mongodb
sudo systemctl enable mongodb

mkdir -p /opt/backup
curl -s https://gist.githubusercontent.com/mpilar/09448c3e200b9c284fead42cb2b6de30/raw/833c3bde0fa8251ffc0acdd9beae5142e0cb6799/benzoin_validate.py | sudo tee /opt/backup/validator.py

sudo chown -R mongodb:mongodb /opt/backup

sudo tee /etc/systemd/system/validator.service <<VALIDATOR
[Unit]
Description=High-performance, schema-free document-oriented database
Requires=mongodb.service

[Service]
Type=oneshot
User=mongodb
ExecStart=/usr/bin/env python3 /opt/backup/validator.py /var/lib/cloud/instance/user-data.txt

[Install]
WantedBy=multi-user.target
VALIDATOR

sudo systemctl daemon-reload
sudo systemctl unmask validator
sudo systemctl enable validator

sudo tee /etc/mongod.conf <<MONGOCONF 
storage:
  dbPath: /mnt/mdb_data/data
  journal:
    enabled: true

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

net:
  port: 27017
  bindIp: 127.0.0.1
MONGOCONF

sudo systemctl stop mongodb
sudo systemctl start mongodb

BOOTSTRAP

chmod +x bootstrap.sh

./bootstrap.sh
