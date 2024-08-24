#!/usr/bin/env bash

apt-get install python3-dotenv

working_dir="/opt/netmon"
if [ "$PWD" != "$working_dir" ]; then
    mkdir -p "$working_dir"
    mv main.py $working_dir
    mv netmon.cnf $working_dir
    touch "$working_dir/.env"
    mv netmon.service /etc/systemd/system
else
    touch "$working_dir/.env"
    mv netmon.service /etc/systemd/system
fi

systemctl daemon-reload
systemctl enable netmon
