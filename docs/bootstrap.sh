cat <<'BOOTSTRAP' > bootstrap.sh

if ! sudo blkid /dev/xvdb > /dev/null ; then
sudo mkfs -t ext4 /dev/xvdb
sudo mkfs -t ext4 /dev/xvdc
sudo mkfs -t ext4 /dev/xvdd
else
echo "Volumes already formatted"
fi

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927

echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list

sudo apt-get update  && sudo apt-get upgrade -y ;

sudo apt-get install python3-pip mongodb-org -y ;

pip3 install --upgrade pip boto3

sudo install -o mongodb -g mongodb -d /mnt/mdb_data /mnt/mdb_journal /mnt/mdb_backup

if ! grep mdb_data /etc/fstab ; then
sudo tee -a /etc/fstab <<FSTAB
UUID=`sudo blkid /dev/xvdb | sed -n 's/.* UUID=\"\([^\"]*\)\".*/\1/p'` /mnt/mdb_data	 ext4	defaults,nofail	0 0
UUID=`sudo blkid /dev/xvdc | sed -n 's/.* UUID=\"\([^\"]*\)\".*/\1/p'` /mnt/mdb_journal	 ext4	defaults,nofail	0 0
UUID=`sudo blkid /dev/xvdd | sed -n 's/.* UUID=\"\([^\"]*\)\".*/\1/p'` /mnt/mdb_backup	 ext4	defaults,nofail	0 0
FSTAB
else
echo "Volumes already in fstab"
fi

sudo mount -a

sudo install -o mongodb -g mongodb -d /mnt/mdb_data/data /mnt/mdb_journal/journal /mnt/mdb_backup/backup

if [ ! -f /mnt/mdb_data/journal ]; then 
sudo ln -s /mnt/mdb_journal/journal /mnt/mdb_data/data/journal
fi

sudo tee /etc/systemd/system/mongodb.service <<'MONGOSERVICE'
[Unit]
Description=High-performance, schema-free document-oriented database
After=network-online.target
Requires=cloud-init.service

[Service]
User=mongodb
ExecStart=/usr/bin/mongod --quiet --journal --config /etc/mongod.conf --replSet "demoSet"

[Install]
WantedBy=multi-user.target
MONGOSERVICE

sudo systemctl unmask mongodb
sudo systemctl enable mongodb

if ! grep mdb /etc/hosts > /dev/null ; then
sudo tee -a /etc/hosts <<'HOSTSFILE'
172.31.18.217 mdb1
172.31.18.139 mdb2
172.31.19.191 mdb3
HOSTSFILE
else
echo "mdb hosts already present in hostsfile"; 
fi

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
  bindIp: `curl http://169.254.169.254/latest/meta-data/local-ipv4`
MONGOCONF

sudo systemctl stop mongodb
sudo systemctl start mongodb

BOOTSTRAP

chmod +x bootstrap.sh

./bootstrap.sh



################
rs.initiate()
rs.add('mdb2')
rs.add('mdb3')

cfg = rs.conf()
cfg.members[2].priority = 0
rs.reconfig(cfg)
